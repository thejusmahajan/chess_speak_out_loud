/**
 * Goethe B2 Exam Engine & Orchestrator.
 */

class GoetheExamEngine {
  constructor() {
    this.config = null;
    this.currentStepIndex = 0; // 0: welcome, 1: lesen, 2: hoeren, 3: schreiben, 4: sprechen, 5: scorecard
    this.steps = ['welcome', 'lesen', 'hoeren', 'schreiben', 'sprechen', 'scorecard'];
    
    this.timerMode = 'sprint'; // 'sprint' or 'official'
    this.timerInterval = null;
    this.secondsRemaining = 0;
    
    // User responses
    this.answers = {
      lesen_answer: null,
      hoeren_answer: null,
      schreiben_text: '',
      sprechen_audio_base64: null,
      sprechen_mime_type: 'audio/webm',
    };
    
    this.moduleData = {};
    this.hoerenPlayCount = 0;
    this.hoerenMaxPlays = 2;
    
    this.audioRecorder = null;
  }

  async init() {
    this._bindEvents();
    await this._loadConfig();
    this.audioRecorder = new GoetheAudioRecorder();
    this._renderStep('welcome');
  }

  async _loadConfig() {
    try {
      const res = await fetch('/api/exam/config');
      this.config = await res.json();
    } catch (e) {
      console.error('Failed to load exam config:', e);
    }
  }

  _bindEvents() {
    // Mode toggles
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.timerMode = e.target.dataset.mode;
        // Update timer if active
        if (this.currentStepIndex >= 1 && this.currentStepIndex <= 4) {
          this._initModuleTimer(this.steps[this.currentStepIndex]);
        }
      });
    });

    // Mic check in welcome
    const testMicBtn = document.getElementById('testMicBtn');
    if (testMicBtn) {
      testMicBtn.addEventListener('click', async () => {
        testMicBtn.textContent = 'Prüfe...';
        const ok = await this.audioRecorder.checkPermission();
        if (ok) {
          testMicBtn.textContent = '✓ Mikrofon bereit';
          testMicBtn.style.background = 'rgba(16, 185, 129, 0.2)';
          testMicBtn.style.color = '#10b981';
          testMicBtn.style.borderColor = '#10b981';
        } else {
          testMicBtn.textContent = '✕ Zugriff verweigert';
          testMicBtn.style.color = '#f43f5e';
        }
      });
    }

    // Start exam button
    const startBtn = document.getElementById('startExamBtn');
    if (startBtn) {
      startBtn.addEventListener('click', () => {
        this.goToStep(1); // Lesen
      });
    }

    // View last result button
    const viewLastBtn = document.getElementById('viewLastResultBtn');
    if (viewLastBtn) {
      viewLastBtn.addEventListener('click', async () => {
        try {
          const res = await fetch('/api/exam/latest-result');
          if (!res.ok) throw new Error('Kein vorheriges Ergebnis gefunden.');
          const report = await res.json();
          this._renderScorecard(report);
          this.goToStep(5); // Scorecard
        } catch (err) {
          alert('Hinweis: ' + err.message);
        }
      });
    }

    // Navigation buttons
    document.getElementById('prevModuleBtn')?.addEventListener('click', () => this.prevStep());
    document.getElementById('nextModuleBtn')?.addEventListener('click', () => this.nextStep());
    document.getElementById('finishExamBtn')?.addEventListener('click', () => this.submitExam());

    // Word count in Schreiben
    const editor = document.getElementById('writingTextarea');
    if (editor) {
      editor.addEventListener('input', (e) => {
        this.answers.schreiben_text = e.target.value;
        this._updateWordCount(e.target.value);
      });
    }

    // Audio recording button in Sprechen
    const recBtn = document.getElementById('recordAudioBtn');
    if (recBtn) {
      recBtn.addEventListener('click', async () => {
        if (!this.audioRecorder.isRecording) {
          await this.audioRecorder.start();
          recBtn.classList.add('recording');
          document.getElementById('recBtnText').textContent = 'Aufnahme stoppen';
        } else {
          const recData = await this.audioRecorder.stop();
          recBtn.classList.remove('recording');
          document.getElementById('recBtnText').textContent = 'Erneut aufnehmen';
          if (recData) {
            this.answers.sprechen_audio_base64 = recData.base64;
            this.answers.sprechen_mime_type = recData.mimeType;
          }
        }
      });
    }

    // Listening TTS synthesis fallback
    document.getElementById('ttsListenBtn')?.addEventListener('click', () => {
      this._speakListeningPassage();
    });
  }

  async goToStep(stepIndex) {
    if (stepIndex < 0 || stepIndex >= this.steps.length) return;
    this.currentStepIndex = stepIndex;
    const stepName = this.steps[stepIndex];

    // Load module content if not cached
    if (['lesen', 'hoeren', 'schreiben', 'sprechen'].includes(stepName) && !this.moduleData[stepName]) {
      try {
        const res = await fetch(`/api/exam/module/${stepName}`);
        this.moduleData[stepName] = await res.json();
      } catch (e) {
        console.error('Failed to load module data:', e);
      }
    }

    this._renderStep(stepName);
    this._updateProgressPills();
    this._initModuleTimer(stepName);
  }

  nextStep() {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.goToStep(this.currentStepIndex + 1);
    }
  }

  prevStep() {
    if (this.currentStepIndex > 0) {
      this.goToStep(this.currentStepIndex - 1);
    }
  }

  _renderStep(stepName) {
    document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
    const target = document.getElementById(`view-${stepName}`);
    if (target) target.classList.add('active');

    // Bottom Navigation Bar visibility
    const navBar = document.getElementById('moduleNavBar');
    if (navBar) {
      navBar.style.display = (stepName === 'welcome' || stepName === 'scorecard') ? 'none' : 'flex';
    }

    const prevBtn = document.getElementById('prevModuleBtn');
    const nextBtn = document.getElementById('nextModuleBtn');
    const finishBtn = document.getElementById('finishExamBtn');

    if (stepName === 'sprechen') {
      if (nextBtn) nextBtn.style.display = 'none';
      if (finishBtn) finishBtn.style.display = 'block';
    } else {
      if (nextBtn) nextBtn.style.display = 'block';
      if (finishBtn) finishBtn.style.display = 'none';
    }

    if (prevBtn) {
      prevBtn.disabled = (stepName === 'lesen');
    }

    // Bind specific module views
    if (stepName === 'lesen') this._renderLesen();
    else if (stepName === 'hoeren') this._renderHoeren();
    else if (stepName === 'schreiben') this._renderSchreiben();
    else if (stepName === 'sprechen') this._renderSprechen();
  }

  _updateProgressPills() {
    const pills = document.querySelectorAll('.step-pill');
    pills.forEach((pill, idx) => {
      pill.classList.remove('active', 'completed');
      if (idx === this.currentStepIndex) {
        pill.classList.add('active');
      } else if (idx < this.currentStepIndex) {
        pill.classList.add('completed');
      }
    });
  }

  _initModuleTimer(moduleName) {
    clearInterval(this.timerInterval);
    const timerBox = document.getElementById('timerBox');
    const timerDisplay = document.getElementById('timerDisplay');

    if (moduleName === 'welcome' || moduleName === 'scorecard') {
      if (timerBox) timerBox.style.display = 'none';
      return;
    }

    if (timerBox) timerBox.style.display = 'flex';

    // Find duration from config
    let duration = 180; // default 3 min
    if (this.config && this.config.modules) {
      const mod = this.config.modules.find(m => m.id === moduleName);
      if (mod) {
        duration = (this.timerMode === 'official') ? mod.official_duration_seconds : mod.sprint_duration_seconds;
      }
    }

    this.secondsRemaining = duration;
    this._updateTimerDisplay();

    this.timerInterval = setInterval(() => {
      this.secondsRemaining--;
      this._updateTimerDisplay();

      if (this.secondsRemaining <= 0) {
        clearInterval(this.timerInterval);
        // Time expired notification
        alert(`Die Zeit für das Modul '${moduleName.toUpperCase()}' ist abgelaufen! Weiter zum nächsten Schritt.`);
        this.nextStep();
      }
    }, 1000);
  }

  _updateTimerDisplay() {
    const timerDisplay = document.getElementById('timerDisplay');
    const timerBox = document.getElementById('timerBox');
    if (!timerDisplay) return;

    const mins = String(Math.floor(this.secondsRemaining / 60)).padStart(2, '0');
    const secs = String(this.secondsRemaining % 60).padStart(2, '0');
    timerDisplay.textContent = `${mins}:${secs}`;

    if (timerBox) {
      if (this.secondsRemaining <= 60) {
        timerBox.classList.add('warning');
      } else {
        timerBox.classList.remove('warning');
      }
    }
  }

  _renderLesen() {
    const data = this.moduleData['lesen'];
    if (!data) return;

    document.getElementById('lesenTitle').textContent = data.title;
    document.getElementById('lesenInstruction').textContent = data.instruction;

    const textBox = document.getElementById('lesenText');
    textBox.innerHTML = data.text.split('\n\n').map(p => `<p>${p}</p>`).join('');

    const q = data.question;
    document.getElementById('lesenPrompt').textContent = q.prompt;

    const optList = document.getElementById('lesenOptions');
    optList.innerHTML = q.options.map(opt => `
      <div class="option-item ${this.answers.lesen_answer === opt.id ? 'selected' : ''}" data-opt="${opt.id}">
        <span class="option-letter">${opt.id}</span>
        <span class="option-text">${opt.text}</span>
      </div>
    `).join('');

    optList.querySelectorAll('.option-item').forEach(item => {
      item.addEventListener('click', () => {
        optList.querySelectorAll('.option-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        this.answers.lesen_answer = item.dataset.opt;
      });
    });
  }

  _renderHoeren() {
    const data = this.moduleData['hoeren'];
    if (!data) return;

    document.getElementById('hoerenTitle').textContent = data.title;
    document.getElementById('hoerenInstruction').textContent = data.instruction;

    const audioPlayer = document.getElementById('hoerenAudioPlayer');
    if (audioPlayer) {
      audioPlayer.src = data.audio_url || '/content/audio/hoeren_sample.wav';
      audioPlayer.onerror = () => {
        // Fallback to wav if mp3 not yet generated
        audioPlayer.src = '/content/audio/hoeren_sample.wav';
      };
      audioPlayer.onplay = () => {
        this.hoerenPlayCount++;
        const badge = document.getElementById('hoerenPlayCountBadge');
        if (badge) badge.textContent = `Wiedergabe: ${this.hoerenPlayCount} / ${this.hoerenMaxPlays}`;
      };
    }

    const q = data.question;
    document.getElementById('hoerenPrompt').textContent = q.prompt;

    const optList = document.getElementById('hoerenOptions');
    optList.innerHTML = q.options.map(opt => `
      <div class="option-item ${this.answers.hoeren_answer === opt.id ? 'selected' : ''}" data-opt="${opt.id}">
        <span class="option-letter">${opt.id}</span>
        <span class="option-text">${opt.text}</span>
      </div>
    `).join('');

    optList.querySelectorAll('.option-item').forEach(item => {
      item.addEventListener('click', () => {
        optList.querySelectorAll('.option-item').forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        this.answers.hoeren_answer = item.dataset.opt;
      });
    });
  }

  _speakListeningPassage() {
    const data = this.moduleData['hoeren'];
    if (!data || !data.transcript_preview) return;

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(data.transcript_preview);
      utterance.lang = 'de-DE';
      utterance.rate = 0.95; // realistic examination speaking rate
      
      const voices = window.speechSynthesis.getVoices();
      const deVoice = voices.find(v => v.lang.startsWith('de'));
      if (deVoice) utterance.voice = deVoice;

      window.speechSynthesis.speak(utterance);
      this.hoerenPlayCount++;
      const badge = document.getElementById('hoerenPlayCountBadge');
      if (badge) badge.textContent = `Wiedergabe (TTS): ${this.hoerenPlayCount} / ${this.hoerenMaxPlays}`;
    } else {
      alert('Web Speech API wird in diesem Browser nicht unterstützt.');
    }
  }

  _renderSchreiben() {
    const data = this.moduleData['schreiben'];
    if (!data) return;

    document.getElementById('schreibenTitle').textContent = data.title;
    document.getElementById('schreibenInstruction').textContent = data.instruction;

    const guidelinesUl = document.getElementById('schreibenGuidelines');
    guidelinesUl.innerHTML = data.guidelines.map(g => `<li>${g}</li>`).join('');

    const editor = document.getElementById('writingTextarea');
    if (editor) {
      editor.value = this.answers.schreiben_text || '';
      this._updateWordCount(editor.value);
    }
  }

  _updateWordCount(text) {
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;

    document.getElementById('wordCountNum').textContent = words;
    document.getElementById('charCountNum').textContent = chars;

    const indicator = document.getElementById('wordCountIndicator');
    if (indicator) {
      if (words < 120) {
        indicator.textContent = 'Zu kurz (< 120 Wörter)';
        indicator.className = 'count-indicator short';
      } else if (words <= 180) {
        indicator.textContent = 'Optimal (~150 Wörter)';
        indicator.className = 'count-indicator good';
      } else {
        indicator.textContent = 'Umfangreich (> 180 Wörter)';
        indicator.className = 'count-indicator short';
      }
    }
  }

  _renderSprechen() {
    const data = this.moduleData['sprechen'];
    if (!data) return;

    document.getElementById('sprechenTitle').textContent = data.title;
    document.getElementById('sprechenInstruction').textContent = data.instruction;

    const guidelinesUl = document.getElementById('sprechenGuidelines');
    guidelinesUl.innerHTML = data.guidelines.map(g => `<li>${g}</li>`).join('');

    // Idle canvas visualizer
    if (this.audioRecorder) {
      this.audioRecorder._drawIdleVisualizer();
    }
  }

  async submitExam() {
    // If currently recording, stop first
    if (this.audioRecorder && this.audioRecorder.isRecording) {
      const recData = await this.audioRecorder.stop();
      if (recData) {
        this.answers.sprechen_audio_base64 = recData.base64;
        this.answers.sprechen_mime_type = recData.mimeType;
      }
    }

    // Show loading overlay
    const overlay = document.getElementById('evalLoadingOverlay');
    if (overlay) overlay.classList.add('active');

    const payload = {
      timer_mode: this.timerMode,
      lesen_answer: this.answers.lesen_answer,
      hoeren_answer: this.answers.hoeren_answer,
      schreiben_text: this.answers.schreiben_text,
      sprechen_audio_base64: this.answers.sprechen_audio_base64,
      sprechen_mime_type: this.answers.sprechen_mime_type,
    };

    try {
      const res = await fetch('/api/exam/submit-complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const report = await res.json();
      if (overlay) overlay.classList.remove('active');
      this._renderScorecard(report);
      this.goToStep(5); // Scorecard
    } catch (err) {
      if (overlay) overlay.classList.remove('active');
      alert('Fehler bei der Examensevaluierung: ' + err.message);
    }
  }

  _renderScorecard(report) {
    const certBanner = document.getElementById('certBanner');
    const certStamp = document.getElementById('certStamp');
    const certSummary = document.getElementById('certSummary');

    const isPass = report.all_modules_passed;
    certBanner.className = `certificate-banner ${isPass ? 'pass' : 'fail'}`;
    certStamp.className = `cert-stamp ${isPass ? 'pass' : 'fail'}`;
    certStamp.textContent = report.overall_result;

    certSummary.innerHTML = `
      Durchschnitt: <strong>${report.average_percentage}%</strong> (Mindestanforderung: 60% in jedem Modul).<br>
      Status: ${isPass 
        ? '🎉 Herzlichen Glückwunsch! Sie haben alle 4 Module des Goethe-Zertifikat B2 bestanden.' 
        : '⚠️ Sie haben mindestens ein Modul nicht bestanden (unter 60%). Überprüfen Sie die Detailanalysen unten.'}
    `;

    // 1. Lesen Card
    const l = report.modules.lesen;
    document.getElementById('cardLesenScore').textContent = `${l.score} / ${l.max_score} (${l.percentage}%)`;
    document.getElementById('cardLesenScore').className = `module-score-pill ${l.passed ? 'pass' : 'fail'}`;
    document.getElementById('cardLesenFeedback').innerHTML = `
      <div class="feedback-box">
        Ihre Antwort: <strong>${l.user_answer || 'Keine'}</strong> | Richtige Lösung: <strong>${l.correct_answer}</strong><br>
        <em>${l.explanation}</em>
      </div>
    `;

    // 2. Hören Card
    const h = report.modules.hoeren;
    document.getElementById('cardHoerenScore').textContent = `${h.score} / ${h.max_score} (${h.percentage}%)`;
    document.getElementById('cardHoerenScore').className = `module-score-pill ${h.passed ? 'pass' : 'fail'}`;
    document.getElementById('cardHoerenFeedback').innerHTML = `
      <div class="feedback-box">
        Ihre Antwort: <strong>${h.user_answer || 'Keine'}</strong> | Richtige Lösung: <strong>${h.correct_answer}</strong><br>
        <em>${h.explanation}</em>
      </div>
    `;

    // 3. Schreiben Card
    const s = report.modules.schreiben;
    const sEval = s.evaluation || {};
    document.getElementById('cardSchreibenScore').textContent = `${s.score} / ${s.max_score} (${s.percentage}%)`;
    document.getElementById('cardSchreibenScore').className = `module-score-pill ${s.passed ? 'pass' : 'fail'}`;
    
    let sRubricHtml = '';
    if (sEval.scores) {
      sRubricHtml = `
        <div class="rubric-scores-row">
          <div class="rubric-pill"><span>Aufgabe:</span> <strong>${sEval.scores.aufgabenerfuellung || 0}/25</strong></div>
          <div class="rubric-pill"><span>Kohärenz:</span> <strong>${sEval.scores.koharenz || 0}/25</strong></div>
          <div class="rubric-pill"><span>Wortschatz:</span> <strong>${sEval.scores.wortschatz || 0}/25</strong></div>
          <div class="rubric-pill"><span>Korrektheit:</span> <strong>${sEval.scores.korrektheit || 0}/25</strong></div>
        </div>
      `;
    }

    let sCorrectionsHtml = '';
    if (sEval.corrections && sEval.corrections.length > 0) {
      sCorrectionsHtml = sEval.corrections.slice(0, 3).map(c => `
        <div class="correction-item">
          <div class="wrong">${c.original || ''}</div>
          <div class="right">→ ${c.corrected || ''}</div>
          <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">${c.explanation || ''}</div>
        </div>
      `).join('');
    }

    document.getElementById('cardSchreibenFeedback').innerHTML = `
      <div class="feedback-box">
        <div>Wortanzahl: <strong>${sEval.word_count || 0}</strong> (${sEval.word_count_verdict || 'N/A'}) | GER: <strong>${sEval.cefr_level_estimate || 'B2'}</strong></div>
        ${sRubricHtml}
        <p style="margin: 8px 0; color: #cbd5e1;">${sEval.examiner_feedback || ''}</p>
        ${sCorrectionsHtml}
      </div>
    `;

    // 4. Sprechen Card (Gemini Audio)
    const sp = report.modules.sprechen;
    const spEval = sp.evaluation || {};
    document.getElementById('cardSprechenScore').textContent = `${sp.score} / ${sp.max_score} (${sp.percentage}%)`;
    document.getElementById('cardSprechenScore').className = `module-score-pill ${sp.passed ? 'pass' : 'fail'}`;

    let spRubricHtml = '';
    if (spEval.scores) {
      spRubricHtml = `
        <div class="rubric-scores-row">
          <div class="rubric-pill"><span>Aufgabe:</span> <strong>${spEval.scores.aufgabenerfuellung || 0}/6</strong></div>
          <div class="rubric-pill"><span>Flüssigkeit:</span> <strong>${spEval.scores.koherenz_fluessigkeit || 0}/6</strong></div>
          <div class="rubric-pill"><span>Wortschatz:</span> <strong>${spEval.scores.wortschatz_ausdruck || 0}/6</strong></div>
          <div class="rubric-pill"><span>Grammatik:</span> <strong>${spEval.scores.korrektheit_grammatik || 0}/6</strong></div>
          <div class="rubric-pill" style="grid-column: span 2;"><span>Aussprache & Intonation:</span> <strong>${spEval.scores.aussprache_intonation || 0}/6</strong></div>
        </div>
      `;
    }

    let spCorrectionsHtml = '';
    if (spEval.corrections && spEval.corrections.length > 0) {
      spCorrectionsHtml = spEval.corrections.slice(0, 3).map(c => `
        <div class="correction-item">
          <div class="wrong">Gesagt: "${c.spoken || ''}"</div>
          <div class="right">Korrektur: "${c.corrected || ''}"</div>
          <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">${c.explanation || ''}</div>
        </div>
      `).join('');
    }

    let redemittelHtml = '';
    if (spEval.recommended_redemittel && spEval.recommended_redemittel.length > 0) {
      redemittelHtml = `
        <div style="margin-top: 10px; background: rgba(59, 130, 246, 0.08); padding: 10px; border-radius: 6px;">
          <div style="font-size: 0.8rem; color: var(--accent-cyan); font-weight: 600; margin-bottom: 4px;">Empfohlene B2-Redemittel:</div>
          <ul style="padding-left: 18px; font-size: 0.82rem; color: #93c5fd;">
            ${spEval.recommended_redemittel.map(r => `<li>${r}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    document.getElementById('cardSprechenFeedback').innerHTML = `
      <div class="feedback-box">
        <div style="margin-bottom: 6px;">GER Einstufung: <strong>${spEval.cefr_level_estimate || 'B2'}</strong></div>
        <div class="transcript-quote"><strong>Transkript Ihrer Audioaufnahme:</strong><br>"${spEval.transcript || 'Kein Transkript verfügbar'}"</div>
        ${spRubricHtml}
        <p style="margin: 8px 0; color: #cbd5e1;">${spEval.examiner_summary || ''}</p>
        ${spCorrectionsHtml}
        ${redemittelHtml}
      </div>
    `;
  }
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
  window.examEngine = new GoetheExamEngine();
  window.examEngine.init();
});

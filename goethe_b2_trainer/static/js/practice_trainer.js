/**
 * Goethe-Zertifikat B2 Practice Trainer — Frontend Controller.
 * Handles interactive workouts for:
 * 1. Simple: fill blank single, match following, odd one out, incorrect spelling.
 * 2. Intermediate: fill blank multi, match multiple, jumbled sentence, find mistake.
 * 3. Difficult: answer question, write next sentence (AI evaluation).
 */

class GoethePracticeTrainer {
  constructor() {
    this.categories = [];
    this.questions = [];
    this.currentTier = 'simple';
    this.currentQIndex = 0;
    
    // State storage
    this.submissions = {};
    this.evalResults = {};
    
    // Ephemeral interaction state
    this.matchingSelectedLeft = null;
    this.jumbledConstructedTokens = [];
    this.mistakeSelectedWord = null;

    // Load persisted state if exists
    this._loadPersistedState();
  }

  async init() {
    await this._loadData();
    this._renderTierSelector();
    this._renderQuestionNav();
    this._renderCurrentQuestion();
    this._updateScoreHeader();
  }

  _loadPersistedState() {
    try {
      const saved = localStorage.getItem('goethe_b2_practice_state');
      if (saved) {
        const parsed = JSON.parse(saved);
        this.submissions = parsed.submissions || {};
        this.evalResults = parsed.evalResults || {};
      }
    } catch (e) {
      console.warn('Could not read practice local storage', e);
    }
  }

  _persistState() {
    try {
      localStorage.setItem('goethe_b2_practice_state', JSON.stringify({
        submissions: this.submissions,
        evalResults: this.evalResults,
      }));
    } catch (e) {
      console.warn('Could not save practice local storage', e);
    }
  }

  async _loadData() {
    try {
      const [catRes, qRes] = await Promise.all([
        fetch('/api/practice/categories'),
        fetch('/api/practice/questions')
      ]);
      const catData = await catRes.json();
      const qData = await qRes.json();

      this.categories = catData.tiers || [];
      this.questions = qData.questions || [];
    } catch (err) {
      console.error('Failed to load practice data:', err);
    }
  }

  _renderTierSelector() {
    const container = document.getElementById('practiceTiersBar');
    if (!container) return;

    container.innerHTML = this.categories.map(tier => {
      const isActive = (tier.id === this.currentTier);
      return `
        <button class="tier-tab-btn tier-${tier.id} ${isActive ? 'active' : ''}" data-tier="${tier.id}">
          <div>
            <div class="tier-tab-title">${tier.title}</div>
            <div class="tier-tab-desc">${tier.description}</div>
          </div>
          <span class="tier-tab-badge ${tier.id}">${tier.badge}</span>
        </button>
      `;
    }).join('');

    container.querySelectorAll('.tier-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tierId = btn.getAttribute('data-tier');
        this.selectTier(tierId);
      });
    });
  }

  selectTier(tierId) {
    this.currentTier = tierId;
    this._renderTierSelector();
    
    // Jump to first question of that tier
    const firstIdx = this.questions.findIndex(q => q.tier === tierId);
    if (firstIdx !== -1) {
      this.selectQuestion(firstIdx);
    }
  }

  _renderQuestionNav() {
    const navStrip = document.getElementById('questionsNavStrip');
    if (!navStrip) return;

    navStrip.innerHTML = this.questions.map((q, idx) => {
      const isActive = (idx === this.currentQIndex);
      const evalRes = this.evalResults[q.id];
      let statusClass = '';
      if (evalRes) {
        statusClass = evalRes.is_correct ? 'done-correct' : 'done-incorrect';
      }

      return `
        <button class="q-nav-pill ${isActive ? 'active' : ''} ${statusClass}" data-qidx="${idx}">
          <span class="q-pill-dot"></span>
          <span>${idx + 1}. ${this._shortQuestionName(q.type)}</span>
        </button>
      `;
    }).join('');

    navStrip.querySelectorAll('.q-nav-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-qidx'), 10);
        this.selectQuestion(idx);
      });
    });
  }

  _shortQuestionName(type) {
    switch (type) {
      case 'fill_blank_single': return 'Einzellücke';
      case 'match_following': return 'Nomen-Verb';
      case 'odd_one_out': return 'Unpassend';
      case 'incorrect_spelling': return 'Rechtschreibung';
      case 'fill_blank_multi': return 'Mehrfachlücke';
      case 'match_multiple': return 'Mehrfachauswahl';
      case 'jumbled_sentence': return 'Schüttelsatz';
      case 'find_mistake': return 'Fehlerkorrektur';
      case 'answer_question': return 'Textfrage';
      case 'write_next_sentence': return 'Folgesatz';
      default: return 'Übung';
    }
  }

  selectQuestion(index) {
    if (index < 0 || index >= this.questions.length) return;
    this.currentQIndex = index;
    const q = this.questions[index];
    if (q.tier !== this.currentTier) {
      this.currentTier = q.tier;
      this._renderTierSelector();
    }
    this._renderQuestionNav();
    this._renderCurrentQuestion();
  }

  _renderCurrentQuestion() {
    const q = this.questions[this.currentQIndex];
    if (!q) return;

    const workoutArea = document.getElementById('practiceWorkoutCard');
    if (!workoutArea) return;

    // Reset ephemeral interaction state for fresh renders
    this.matchingSelectedLeft = null;
    this.mistakeSelectedWord = null;

    let widgetHtml = '';
    switch (q.type) {
      case 'fill_blank_single':
        widgetHtml = this._buildWidgetFillBlankSingle(q);
        break;
      case 'match_following':
        widgetHtml = this._buildWidgetMatchFollowing(q);
        break;
      case 'odd_one_out':
        widgetHtml = this._buildWidgetOddOneOut(q);
        break;
      case 'incorrect_spelling':
        widgetHtml = this._buildWidgetIncorrectSpelling(q);
        break;
      case 'fill_blank_multi':
        widgetHtml = this._buildWidgetFillBlankMulti(q);
        break;
      case 'match_multiple':
        widgetHtml = this._buildWidgetMatchMultiple(q);
        break;
      case 'jumbled_sentence':
        widgetHtml = this._buildWidgetJumbledSentence(q);
        break;
      case 'find_mistake':
        widgetHtml = this._buildWidgetFindMistake(q);
        break;
      case 'answer_question':
        widgetHtml = this._buildWidgetAnswerQuestion(q);
        break;
      case 'write_next_sentence':
        widgetHtml = this._buildWidgetWriteNextSentence(q);
        break;
      default:
        widgetHtml = `<p>Unbekannte Übung.</p>`;
    }

    const evalResult = this.evalResults[q.id];
    let feedbackHtml = '';
    if (evalResult) {
      feedbackHtml = this._buildFeedbackCard(evalResult, q);
    }

    workoutArea.innerHTML = `
      <div class="practice-workout-header">
        <div>
          <div class="workout-meta-tags">
            <span class="workout-tag tier-tab-badge ${q.tier}">${q.tier}</span>
            <span class="workout-tag cefr">${q.cefr_focus || 'B2 Goethe Focus'}</span>
          </div>
          <h3 class="workout-title">${q.title}</h3>
        </div>
        <div style="font-size:0.85rem; color:var(--text-muted); font-weight:600;">
          Übung ${this.currentQIndex + 1} von ${this.questions.length}
        </div>
      </div>

      <div class="practice-instruction-banner">
        <strong>Aufgabe:</strong> ${q.instruction}
      </div>

      <div class="widget-body" id="currentWidgetBody">
        ${widgetHtml}
      </div>

      <div id="workoutFeedbackArea">
        ${feedbackHtml}
      </div>
    `;

    this._bindCurrentWidgetEvents(q);
  }

  // ---------------------------------------------------------------------------
  // WIDGET BUILDERS
  // ---------------------------------------------------------------------------

  _buildWidgetFillBlankSingle(q) {
    const existingVal = this.submissions[q.id] || '';
    const formattedSentence = q.context_sentence.replace('_____', `<span class="blank-spot">_____</span>`);
    return `
      <div class="blank-single-box">
        <div class="context-sentence-quote">${formattedSentence}</div>
        <div class="input-action-row">
          <label style="font-weight:600; color:var(--text-secondary);">${q.target_label || 'Fehlendes Wort'}:</label>
          <input type="text" class="styled-text-input" id="inputFillSingle" placeholder="Präposition hier eingeben..." value="${this._escapeHtml(existingVal)}">
          <button class="btn-primary" id="btnSubmitPractice">Antwort prüfen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetMatchFollowing(q) {
    const pairs = this.submissions[q.id] || {};
    return `
      <div class="match-interactive-box">
        <p style="font-size:0.88rem; color:var(--text-secondary); margin-bottom:12px;">
          Klicken Sie zuerst auf ein Nomen links und anschließend auf das passende Funktionsverb rechts, um das Paar zu verbinden.
        </p>
        <div class="match-columns-grid">
          <div>
            <div class="match-col-header">1. Nomen / Wendung</div>
            <div id="matchLeftCol">
              ${q.left_items.map(l => {
                const pairedR = pairs[l.id];
                const rightItem = pairedR ? q.right_items.find(r => r.id === pairedR) : null;
                const isPaired = !!pairedR;
                return `
                  <div class="match-item-card ${isPaired ? 'paired' : ''}" data-left-id="${l.id}">
                    <span>${l.text}</span>
                    ${rightItem ? `<span class="match-pair-tag">➔ ${rightItem.text}</span>` : ''}
                  </div>
                `;
              }).join('')}
            </div>
          </div>
          <div>
            <div class="match-col-header">2. Funktionsverb</div>
            <div id="matchRightCol">
              ${q.right_items.map(r => `
                <div class="match-item-card" data-right-id="${r.id}">
                  <span>${r.text}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px;">
          <button class="btn-secondary" id="btnResetMatching" style="padding:8px 16px;">Zuordnungen zurücksetzen</button>
          <button class="btn-primary" id="btnSubmitPractice">Zuordnung überprüfen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetOddOneOut(q) {
    const selected = this.submissions[q.id] || '';
    return `
      <div>
        <div class="options-grid-selectable">
          ${q.options.map(opt => {
            const isChecked = (selected === opt.id);
            return `
              <div class="option-select-card ${isChecked ? 'active' : ''}" data-opt-id="${opt.id}">
                <div class="opt-id-circle">${opt.id}</div>
                <div>
                  <div class="option-word-title">${opt.word}</div>
                  <div class="option-word-desc">${opt.desc || ''}</div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
        <div style="margin-top:20px; display:flex; justify-content:flex-end;">
          <button class="btn-primary" id="btnSubmitPractice">Auswahl bestätigen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetIncorrectSpelling(q) {
    const selected = this.submissions[q.id] || '';
    return `
      <div>
        <div class="options-grid-selectable">
          ${q.options.map(opt => {
            const isChecked = (selected === opt.id);
            return `
              <div class="option-select-card ${isChecked ? 'active' : ''}" data-opt-id="${opt.id}">
                <div class="opt-id-circle">${opt.id}</div>
                <div>
                  <div class="option-word-title">${opt.word}</div>
                  <div class="option-word-desc" style="color:var(--text-muted); font-size:0.8rem;">Wort auf Rechtschreibung prüfen</div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
        <div style="margin-top:20px; display:flex; justify-content:flex-end;">
          <button class="btn-primary" id="btnSubmitPractice">Falsch geschriebenes Wort prüfen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetFillBlankMulti(q) {
    const sub = this.submissions[q.id] || {};
    const b1Val = sub.blank1 || '';
    const b2Val = sub.blank2 || '';
    const sentenceWithInputs = q.sentence_template
      .replace('{blank1}', `<input type="text" class="inline-blank-input" id="blankMulti1" placeholder="Lücke 1" value="${this._escapeHtml(b1Val)}">`)
      .replace('{blank2}', `<input type="text" class="inline-blank-input" id="blankMulti2" placeholder="Lücke 2" value="${this._escapeHtml(b2Val)}">`);

    return `
      <div>
        <div class="multi-blank-editor-box">
          ${sentenceWithInputs}
        </div>
        <div style="margin-top:20px; display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:0.85rem; color:var(--text-muted);">${q.hint || ''}</span>
          <button class="btn-primary" id="btnSubmitPractice">Konnektor überprüfen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetMatchMultiple(q) {
    const selected = this.submissions[q.id] || [];
    return `
      <div>
        <div class="multi-select-list">
          ${q.options.map(opt => {
            const isChecked = selected.includes(opt.id);
            return `
              <label class="multi-check-item ${isChecked ? 'selected' : ''}" data-opt-id="${opt.id}">
                <input type="checkbox" value="${opt.id}" ${isChecked ? 'checked' : ''}>
                <div class="multi-verb-name">${opt.id}) ${opt.verb}</div>
                <div class="multi-verb-example"><em>Beispiel:</em> ${opt.example || ''}</div>
              </label>
            `;
          }).join('')}
        </div>
        <div style="margin-top:20px; display:flex; justify-content:flex-end;">
          <button class="btn-primary" id="btnSubmitPractice">Mehrfachauswahl überprüfen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetJumbledSentence(q) {
    const assembledTokens = this.submissions[q.id] || [];
    // Calculate remaining bank tokens
    const bankTokens = [...q.scrambled_tokens];
    assembledTokens.forEach(t => {
      const idx = bankTokens.indexOf(t);
      if (idx !== -1) bankTokens.splice(idx, 1);
    });

    return `
      <div class="jumbled-interactive-area">
        <div style="font-size:0.88rem; font-weight:600; color:var(--text-secondary);">
          Ihr konstruierter Satz (Klicken Sie ein Wort an, um es zu entfernen):
        </div>
        <div class="constructed-sentence-zone" id="jumbledConstructedZone">
          ${assembledTokens.length === 0 ? '<span style="color:var(--text-muted); font-size:0.9rem;">(Klicken Sie unten auf die Satzglieder, um sie hier in Reihe anzuordnen...)</span>' : ''}
          ${assembledTokens.map((tok, i) => `
            <div class="word-token-chip" data-token-idx="${i}">${tok}</div>
          `).join('')}
        </div>

        <div style="font-size:0.88rem; font-weight:600; color:var(--text-secondary); margin-top:8px;">
          Verfügbare Satzglieder (Klicken zum Hinzufügen):
        </div>
        <div class="scrambled-bank-zone" id="jumbledBankZone">
          ${bankTokens.map((tok) => `
            <div class="word-token-chip">${tok}</div>
          `).join('')}
        </div>

        <div class="jumbled-controls-row" style="margin-top:14px; justify-content:space-between;">
          <button class="btn-secondary" id="btnResetJumbled">Zurücksetzen</button>
          <button class="btn-primary" id="btnSubmitPractice">Satzbau prüfen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetFindMistake(q) {
    const sub = this.submissions[q.id] || {};
    const selectedWord = sub.selected_word || '';
    const correction = sub.correction || '';

    return `
      <div>
        <div class="find-mistake-sentence">
          ${q.sentence_words.map(w => {
            const isFlagged = (selectedWord.toLowerCase() === w.word.toLowerCase());
            return `
              <span class="sentence-click-token ${isFlagged ? 'flagged-error' : ''}" data-word="${this._escapeHtml(w.word)}">${w.word}</span>
            `;
          }).join(' ')}
        </div>

        <div class="mistake-correction-prompt" style="margin-top:18px;">
          <div>
            <label style="font-size:0.85rem; font-weight:600; color:var(--text-muted); display:block; margin-bottom:4px;">
              Markiertes fehlerhaftes Wort:
            </label>
            <strong id="flaggedWordDisplay" style="color:var(--accent-rose); font-size:1.1rem;">
              ${selectedWord ? `"${selectedWord}"` : '(Kein Wort ausgewählt - bitte oben anklicken)'}
            </strong>
          </div>
          <div style="flex-grow:1; max-width:360px; margin-left:auto;">
            <label style="font-size:0.85rem; font-weight:600; color:var(--text-muted); display:block; margin-bottom:4px;">
              Geben Sie die grammatisch korrekte Form ein:
            </label>
            <input type="text" class="styled-text-input" id="inputMistakeCorrection" placeholder="Korrekte Form z.B. deren..." value="${this._escapeHtml(correction)}">
          </div>
        </div>

        <div style="margin-top:20px; display:flex; justify-content:flex-end;">
          <button class="btn-primary" id="btnSubmitPractice">Korrektur prüfen</button>
        </div>
      </div>
    `;
  }

  _buildWidgetAnswerQuestion(q) {
    const existing = this.submissions[q.id] || '';
    return `
      <div>
        <div class="reading-callout-box">
          <div style="font-weight:700; color:var(--text-primary); margin-bottom:6px;">📖 Lesetext: Jobsharing im modernen Arbeitsalltag</div>
          ${q.reading_passage}
        </div>

        <div style="font-weight:700; color:#38bdf8; font-size:1.05rem; margin-bottom:10px;">
          ❓ ${q.question_prompt}
        </div>

        <textarea class="practice-textarea" id="textDifficultAnswer" placeholder="Verfassen Sie hier Ihre Begründung in 1–2 vollständigen Sätzen...">${this._escapeHtml(existing)}</textarea>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px;">
          <span style="font-size:0.85rem; color:var(--text-muted);">
            Evaluation: Kriterien- & KI-basierte B2-Bewertung (Aufgabenerfüllung, Kohärenz, Satzbau).
          </span>
          <button class="btn-primary" id="btnSubmitPractice" style="background:var(--gradient-gold); color:#0f172a; font-weight:700;">
            ✨ Mit KI / B2-Kriterien auswerten
          </button>
        </div>
      </div>
    `;
  }

  _buildWidgetWriteNextSentence(q) {
    const existing = this.submissions[q.id] || '';
    return `
      <div>
        <div class="context-sentence-quote" style="border-left:4px solid var(--accent-rose); margin-bottom:14px;">
          <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:4px; text-transform:uppercase; font-weight:700;">
            Vorgegebener Satzanfang:
          </div>
          "${q.lead_in_sentence}"
        </div>

        <div style="margin-bottom:8px;">
          <span style="font-size:0.85rem; font-weight:600; color:var(--text-secondary);">
            Klicken Sie auf ein B2-Redemittel, um es direkt als Satzbeginn einzufügen:
          </span>
          <div class="redemittel-pills-row">
            <span class="redemittel-pill" data-connector="Andererseits ">Andererseits ...</span>
            <span class="redemittel-pill" data-connector="Allerdings birgt dies ">Allerdings birgt dies ...</span>
            <span class="redemittel-pill" data-connector="Demgegenüber steht jedoch ">Demgegenüber steht jedoch ...</span>
            <span class="redemittel-pill" data-connector="Auf der anderen Seite ">Auf der anderen Seite ...</span>
          </div>
        </div>

        <textarea class="practice-textarea" id="textDifficultNextSentence" placeholder="Schreiben Sie hier den vollständigen, kontrastierenden Folgesatz...">${this._escapeHtml(existing)}</textarea>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px;">
          <span style="font-size:0.85rem; color:var(--text-muted);">
            Tipp: Beachten Sie die Verbstellung nach Satzverbindern (Inversion nach Konnektoradverbien).
          </span>
          <button class="btn-primary" id="btnSubmitPractice" style="background:var(--gradient-gold); color:#0f172a; font-weight:700;">
            ✨ Mit KI / B2-Kriterien auswerten
          </button>
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // FEEDBACK DISPLAY
  // ---------------------------------------------------------------------------

  _buildFeedbackCard(evalRes, q) {
    const isPass = evalRes.is_correct;
    const score = evalRes.score || 0;
    const maxScore = evalRes.max_score || 10;
    
    let correctionsHtml = '';
    if (evalRes.corrections && evalRes.corrections.length > 0) {
      correctionsHtml = `
        <div style="margin-top:10px;">
          <strong style="font-size:0.85rem; color:var(--text-secondary);">Gefundene Verbesserungen:</strong>
          ${evalRes.corrections.map(c => `
            <div class="correction-item" style="margin-top:6px;">
              <span class="wrong">${this._escapeHtml(c.original || '')}</span> ➔ <span class="right">${this._escapeHtml(c.corrected || '')}</span>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">${this._escapeHtml(c.explanation || '')}</div>
            </div>
          `).join('')}
        </div>
      `;
    }

    let modelAnswerHtml = '';
    if (evalRes.model_answer) {
      modelAnswerHtml = `
        <div class="model-solution-box" style="margin-top:10px;">
          <strong>Goethe B2 Musterlösung:</strong><br>
          ${evalRes.model_answer}
        </div>
      `;
    }

    const nextIdx = this.currentQIndex + 1;
    const hasNext = (nextIdx < this.questions.length);

    return `
      <div class="practice-feedback-card ${isPass ? 'pass' : 'fail'}">
        <div class="feedback-status-row">
          <div class="feedback-status-title" style="color: ${isPass ? 'var(--accent-emerald)' : 'var(--accent-rose)'};">
            <span>${isPass ? '✓ Richtig / Bestanden' : '✕ Überarbeiten / Teilerfolg'}</span>
          </div>
          <div class="feedback-score-pill" style="background:${isPass ? 'rgba(16,185,129,0.2)' : 'rgba(244,63,94,0.2)'}; color:${isPass ? '#34d399' : '#fb7185'};">
            ${score} / ${maxScore} Punkte
          </div>
        </div>

        <div style="font-weight:600; font-size:1.02rem; color:var(--text-primary);">
          ${evalRes.feedback || ''}
        </div>

        ${evalRes.explanation ? `<div class="feedback-explanation">${evalRes.explanation}</div>` : ''}

        ${correctionsHtml}
        ${modelAnswerHtml}

        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:10px;">
          ${hasNext ? `
            <button class="btn-primary" id="btnNextPracticeQuestion">
              Nächste Übung (${nextIdx + 1}) ➔
            </button>
          ` : `
            <button class="btn-primary" onclick="alert('Herzlichen Glückwunsch! Sie haben alle 10 B2-Übungen absolviert.');">
              🎉 Alle Übungen abgeschlossen!
            </button>
          `}
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // INTERACTION EVENT BINDINGS
  // ---------------------------------------------------------------------------

  _bindCurrentWidgetEvents(q) {
    const submitBtn = document.getElementById('btnSubmitPractice');

    // 1. Single blank
    if (q.type === 'fill_blank_single') {
      const input = document.getElementById('inputFillSingle');
      input?.focus();
      input?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') submitBtn?.click();
      });
      submitBtn?.addEventListener('click', () => {
        const val = input ? input.value : '';
        this.submissions[q.id] = val;
        this._submitEvaluation(q.id, val);
      });
    }

    // 2. Match following
    else if (q.type === 'match_following') {
      const leftCards = document.querySelectorAll('#matchLeftCol .match-item-card');
      const rightCards = document.querySelectorAll('#matchRightCol .match-item-card');

      leftCards.forEach(lc => {
        lc.addEventListener('click', () => {
          leftCards.forEach(c => c.classList.remove('selected'));
          lc.classList.add('selected');
          this.matchingSelectedLeft = lc.getAttribute('data-left-id');
        });
      });

      rightCards.forEach(rc => {
        rc.addEventListener('click', () => {
          if (!this.matchingSelectedLeft) {
            alert('Bitte wählen Sie zuerst einen Eintrag aus der linken Spalte aus.');
            return;
          }
          const rightId = rc.getAttribute('data-right-id');
          if (!this.submissions[q.id]) this.submissions[q.id] = {};
          this.submissions[q.id][this.matchingSelectedLeft] = rightId;
          this._renderCurrentQuestion();
        });
      });

      document.getElementById('btnResetMatching')?.addEventListener('click', () => {
        this.submissions[q.id] = {};
        this._renderCurrentQuestion();
      });

      submitBtn?.addEventListener('click', () => {
        const pairs = this.submissions[q.id] || {};
        this._submitEvaluation(q.id, pairs);
      });
    }

    // 3. Odd one out
    else if (q.type === 'odd_one_out') {
      const optCards = document.querySelectorAll('.option-select-card');
      optCards.forEach(card => {
        card.addEventListener('click', () => {
          optCards.forEach(c => c.classList.remove('active'));
          card.classList.add('active');
          const optId = card.getAttribute('data-opt-id');
          this.submissions[q.id] = optId;
        });
      });

      submitBtn?.addEventListener('click', () => {
        const sel = this.submissions[q.id];
        if (!sel) {
          alert('Bitte wählen Sie eine Option aus.');
          return;
        }
        this._submitEvaluation(q.id, sel);
      });
    }

    // 4. Incorrect spelling
    else if (q.type === 'incorrect_spelling') {
      const optCards = document.querySelectorAll('.option-select-card');
      optCards.forEach(card => {
        card.addEventListener('click', () => {
          optCards.forEach(c => c.classList.remove('active'));
          card.classList.add('active');
          const optId = card.getAttribute('data-opt-id');
          this.submissions[q.id] = optId;
        });
      });

      submitBtn?.addEventListener('click', () => {
        const sel = this.submissions[q.id];
        if (!sel) {
          alert('Bitte wählen Sie das verdächtige Wort aus.');
          return;
        }
        this._submitEvaluation(q.id, sel);
      });
    }

    // 5. Multi blank
    else if (q.type === 'fill_blank_multi') {
      submitBtn?.addEventListener('click', () => {
        const b1 = document.getElementById('blankMulti1')?.value || '';
        const b2 = document.getElementById('blankMulti2')?.value || '';
        const sub = { blank1: b1, blank2: b2 };
        this.submissions[q.id] = sub;
        this._submitEvaluation(q.id, sub);
      });
    }

    // 6. Match multiple
    else if (q.type === 'match_multiple') {
      const checkItems = document.querySelectorAll('.multi-check-item');
      checkItems.forEach(item => {
        const chk = item.querySelector('input[type="checkbox"]');
        item.addEventListener('click', (e) => {
          if (e.target !== chk) {
            chk.checked = !chk.checked;
          }
          item.classList.toggle('selected', chk.checked);
          
          const selected = [];
          document.querySelectorAll('.multi-check-item input[type="checkbox"]:checked').forEach(c => {
            selected.push(c.value);
          });
          this.submissions[q.id] = selected;
        });
      });

      submitBtn?.addEventListener('click', () => {
        const selected = this.submissions[q.id] || [];
        this._submitEvaluation(q.id, selected);
      });
    }

    // 7. Jumbled sentence
    else if (q.type === 'jumbled_sentence') {
      const bankChips = document.querySelectorAll('#jumbledBankZone .word-token-chip');
      const constructedChips = document.querySelectorAll('#jumbledConstructedZone .word-token-chip');

      bankChips.forEach(chip => {
        chip.addEventListener('click', () => {
          const tok = chip.textContent.trim();
          if (!this.submissions[q.id]) this.submissions[q.id] = [];
          this.submissions[q.id].push(tok);
          this._renderCurrentQuestion();
        });
      });

      constructedChips.forEach(chip => {
        chip.addEventListener('click', () => {
          const idx = parseInt(chip.getAttribute('data-token-idx'), 10);
          if (this.submissions[q.id] && idx >= 0) {
            this.submissions[q.id].splice(idx, 1);
            this._renderCurrentQuestion();
          }
        });
      });

      document.getElementById('btnResetJumbled')?.addEventListener('click', () => {
        this.submissions[q.id] = [];
        this._renderCurrentQuestion();
      });

      submitBtn?.addEventListener('click', () => {
        const tokens = this.submissions[q.id] || [];
        if (tokens.length === 0) {
          alert('Bitte ordnen Sie zuerst die Satzglieder an.');
          return;
        }
        this._submitEvaluation(q.id, tokens);
      });
    }

    // 8. Find mistake
    else if (q.type === 'find_mistake') {
      const wordTokens = document.querySelectorAll('.find-mistake-sentence .sentence-click-token');
      const corrInput = document.getElementById('inputMistakeCorrection');
      const displaySpan = document.getElementById('flaggedWordDisplay');

      wordTokens.forEach(tok => {
        tok.addEventListener('click', () => {
          wordTokens.forEach(t => t.classList.remove('flagged-error'));
          tok.classList.add('flagged-error');
          const cleanWord = tok.getAttribute('data-word').replace(/[,.]/g, '');
          this.mistakeSelectedWord = cleanWord;
          if (displaySpan) displaySpan.textContent = `"${cleanWord}"`;
          corrInput?.focus();
        });
      });

      submitBtn?.addEventListener('click', () => {
        const sub = {
          selected_word: this.mistakeSelectedWord || (this.submissions[q.id] && this.submissions[q.id].selected_word) || '',
          correction: corrInput ? corrInput.value.trim() : '',
        };
        if (!sub.selected_word) {
          alert('Bitte klicken Sie auf das fehlerhafte Wort im Satz.');
          return;
        }
        this.submissions[q.id] = sub;
        this._submitEvaluation(q.id, sub);
      });
    }

    // 9. Difficult: Answer question
    else if (q.type === 'answer_question') {
      submitBtn?.addEventListener('click', () => {
        const textarea = document.getElementById('textDifficultAnswer');
        const val = textarea ? textarea.value.trim() : '';
        if (!val) {
          alert('Bitte formulieren Sie Ihre Antwort im Textfeld.');
          return;
        }
        this.submissions[q.id] = val;
        this._submitEvaluation(q.id, val);
      });
    }

    // 10. Difficult: Write next sentence
    else if (q.type === 'write_next_sentence') {
      const textarea = document.getElementById('textDifficultNextSentence');

      document.querySelectorAll('.redemittel-pill').forEach(pill => {
        pill.addEventListener('click', () => {
          const conn = pill.getAttribute('data-connector');
          if (textarea) {
            textarea.value = conn + textarea.value;
            textarea.focus();
          }
        });
      });

      submitBtn?.addEventListener('click', () => {
        const val = textarea ? textarea.value.trim() : '';
        if (!val) {
          alert('Bitte schreiben Sie einen Folgesatz im Textfeld.');
          return;
        }
        this.submissions[q.id] = val;
        this._submitEvaluation(q.id, val);
      });
    }

    // Bind next question button inside feedback card if rendered
    document.getElementById('btnNextPracticeQuestion')?.addEventListener('click', () => {
      this.selectQuestion(this.currentQIndex + 1);
    });
  }

  // ---------------------------------------------------------------------------
  // EVALUATION API SUBMISSION
  // ---------------------------------------------------------------------------

  async _submitEvaluation(questionId, submissionPayload) {
    const feedbackArea = document.getElementById('workoutFeedbackArea');
    const submitBtn = document.getElementById('btnSubmitPractice');

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Wird ausgewertet...';
    }

    try {
      const res = await fetch('/api/practice/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: questionId,
          submission: submissionPayload,
        }),
      });

      if (!res.ok) {
        throw new Error(`Fehler bei der Auswertung: Status ${res.status}`);
      }

      const result = await res.json();
      this.evalResults[questionId] = result;
      this._persistState();

      // Re-render question nav and score
      this._renderQuestionNav();
      this._updateScoreHeader();

      // Render feedback card
      const q = this.questions[this.currentQIndex];
      if (feedbackArea) {
        feedbackArea.innerHTML = this._buildFeedbackCard(result, q);
        // Bind next question button
        document.getElementById('btnNextPracticeQuestion')?.addEventListener('click', () => {
          this.selectQuestion(this.currentQIndex + 1);
        });
      }
    } catch (err) {
      console.error('Practice evaluation error:', err);
      if (feedbackArea) {
        feedbackArea.innerHTML = `
          <div class="practice-feedback-card fail">
            <strong>Auswertungsfehler:</strong> ${err.message}
          </div>
        `;
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Antwort prüfen';
      }
    }
  }

  _updateScoreHeader() {
    let earned = 0;
    let completedCount = 0;

    Object.values(this.evalResults).forEach(res => {
      if (res && typeof res.score === 'number') {
        earned += res.score;
        completedCount++;
      }
    });

    const scoreDisplay = document.getElementById('practiceScoreDisplay');
    if (scoreDisplay) {
      scoreDisplay.textContent = `${earned} / 100`;
    }

    const completedDisplay = document.getElementById('practiceCompletedDisplay');
    if (completedDisplay) {
      completedDisplay.textContent = `${completedCount} von ${this.questions.length} beantwortet`;
    }
  }

  _escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}

// Global instance attached to window for coordination
window.goethePracticeTrainer = new GoethePracticeTrainer();

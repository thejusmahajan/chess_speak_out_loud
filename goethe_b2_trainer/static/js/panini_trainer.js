/**
 * Pāṇini-Kanon B1 → B2 — Frontend Controller.
 * Sūtrapāṭha, Gaṇapāṭha, Prakriyā & Abhyāsa Curriculum Orchestrator.
 */

class PaniniTrainer {
  constructor() {
    this.currentSubView = 'today'; // 'today', 'sutras', 'prakriya', 'ganapatha', 'schedule'
    this.overview = null;
    this.todayData = null;
    this.sutras = [];
    this.lists = {};
    this.flashcards = [];
    this.transformations = [];
    this.nominalstilMatrix = [];
    this.errorHuntItems = [];
    this.translations = [];
    this.topics = [];
    this.scheduleData = [];
    this.progress = null;

    // Ephemeral UI states
    this.activeFilterAdhyaya = 'all';
    this.activeFilterWeek = 'all';
    this.activePrakriyaTab = 'transform'; // 'transform', 'error_hunt', 'matrix', 'translations'
    this.activeListFilter = 'all'; // Default to Alle Listen for full flashcard coverage
    this.ganapathaMode = 'cards'; // Default to 'cards' (3D flashcards) so clicking 'Karteikarten' shows flashcards
    this.ganapathaSearch = '';
    this.currentCardIndex = 0;
    this.cardIsFlipped = false;
    this.coveredCards = {}; // sutra_id -> boolean
    this._keyboardAttached = false;
  }

  async init() {
    await this.loadAllData();
    this.renderHeader();
    this.renderSubViewNav();
    this.renderActiveSubView();
    this.setupKeyboardNavigation();
  }

  async loadAllData() {
    try {
      const [
        overviewRes,
        todayRes,
        sutrasRes,
        listsRes,
        flashcardsRes,
        transRes,
        errorRes,
        translatRes,
        topicsRes,
        schedRes,
        progRes
      ] = await Promise.all([
        fetch('/api/panini/overview').then(r => r.json()),
        fetch('/api/panini/today').then(r => r.json()),
        fetch('/api/panini/sutras').then(r => r.json()),
        fetch('/api/panini/lists').then(r => r.json()),
        fetch('/api/panini/flashcards').then(r => r.json()),
        fetch('/api/panini/transformations').then(r => r.json()),
        fetch('/api/panini/error-hunt').then(r => r.json()),
        fetch('/api/panini/translations').then(r => r.json()),
        fetch('/api/panini/topics').then(r => r.json()),
        fetch('/api/panini/schedule').then(r => r.json()),
        fetch('/api/panini/progress').then(r => r.json()),
      ]);

      this.overview = overviewRes;
      this.todayData = todayRes;
      this.sutras = sutrasRes.sutras || [];
      this.lists = listsRes || {};
      this.flashcards = flashcardsRes.cards || [];
      this.transformations = transRes.transformations || [];
      this.nominalstilMatrix = transRes.nominalstil_matrix || [];
      this.errorHuntItems = errorRes || [];
      this.translations = translatRes || [];
      this.topics = topicsRes || [];
      this.scheduleData = schedRes.schedule || [];
      this.progress = progRes;
    } catch (err) {
      console.error('Failed to load Pāṇini data:', err);
    }
  }

  renderHeader() {
    const container = document.getElementById('paniniHeaderCard');
    if (!container || !this.overview || !this.progress) return;

    const summary = this.overview.progress_summary;
    const masteredCount = summary.sutras_mastered_count || 0;
    const totalSutras = summary.total_sutras || 22;
    const pct = Math.round((masteredCount / totalSutras) * 100);

    container.innerHTML = `
      <div class="panini-header-top">
        <div class="panini-badge-cluster">
          <span class="panini-om-badge">🕉️ Pāṇini-Kanon</span>
          <span class="panini-level-badge">B1 ➔ B2 Curriculum</span>
          <span class="panini-streak-badge">🔥 ${this.progress.streak_days || 1} Tage Streak</span>
        </div>
        <div class="panini-progress-stats">
          <div class="stat-pill">
            <span class="stat-label">Woche &amp; Tag</span>
            <span class="stat-value">Woche ${this.progress.current_week || 1}, Tag ${this.progress.current_day || 1}</span>
          </div>
          <div class="stat-pill">
            <span class="stat-label">Gemeisterte Sūtras</span>
            <span class="stat-value">${masteredCount} / ${totalSutras} (${pct}%)</span>
          </div>
          <div class="stat-pill">
            <span class="stat-label">Karteikarten</span>
            <span class="stat-value">${this.progress.flashcard_stats?.mastered || 0} / ${this.flashcards.length}</span>
          </div>
        </div>
      </div>
      <div class="panini-progress-bar-wrap">
        <div class="panini-progress-fill" style="width: ${Math.max(5, pct)}%;"></div>
      </div>
      <div class="panini-paribhasa-banner">
        <span class="paribhasa-icon">💡</span>
        <em>„${this.overview.paribhasas ? this.overview.paribhasas[0] : 'Das Register folgt der Situation.'}“</em>
      </div>
    `;
  }

  renderSubViewNav() {
    const nav = document.getElementById('paniniSubNav');
    if (!nav) return;

    const tabs = [
      { id: 'today', label: '📅 Heute (Tagesplan)', icon: '☀️' },
      { id: 'sutras', label: '📜 Sūtrapāṭha (22 Sūtras)', icon: '📖' },
      { id: 'prakriya', label: '🔄 Prakriyā (Übungen)', icon: '⚡' },
      { id: 'ganapatha', label: '🗂️ Gaṇapāṭha (Karteikarten)', icon: '🃏' },
      { id: 'schedule', label: '🗓️ 12-Wochen-Plan', icon: '🎯' },
    ];

    nav.innerHTML = tabs.map(t => `
      <button type="button" class="panini-nav-btn ${this.currentSubView === t.id ? 'active' : ''}" 
              data-subview="${t.id}"
              onclick="window.paniniTrainer.switchSubView('${t.id}')">
        <span class="btn-icon">${t.icon}</span>
        <span class="btn-label">${t.label}</span>
      </button>
    `).join('');

    nav.querySelectorAll('.panini-nav-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const sub = btn.getAttribute('data-subview');
        if (sub) this.switchSubView(sub);
      });
    });
  }

  switchSubView(subviewId) {
    this.currentSubView = subviewId;
    this.renderSubViewNav();
    this.renderActiveSubView();
  }

  renderActiveSubView() {
    const container = document.getElementById('paniniSubViewContent');
    if (!container) return;

    try {
      switch (this.currentSubView) {
        case 'today':
          this.renderTodayView(container);
          break;
        case 'sutras':
          this.renderSutrasView(container);
          break;
        case 'prakriya':
          this.renderPrakriyaView(container);
          break;
        case 'ganapatha':
          this.renderGanapathaView(container);
          break;
        case 'schedule':
          this.renderScheduleView(container);
          break;
        default:
          this.renderTodayView(container);
      }
    } catch (err) {
      console.error('[PaniniTrainer] Error rendering subview:', this.currentSubView, err);
      container.innerHTML = `
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 8px; padding: 24px; color: #fca5a5; margin: 20px 0;">
          <h3 style="color: #ef4444; margin-bottom: 8px;">Fehler beim Laden dieser Ansicht (${this.currentSubView})</h3>
          <p style="font-family: monospace; white-space: pre-wrap; font-size: 0.9rem;">${err.message}\n${err.stack || ''}</p>
        </div>
      `;
    }
  }

  // ===========================================================================
  // SUB-VIEW 1: HEUTE (DAILY WORKOUT)
  // ===========================================================================
  renderTodayView(container) {
    if (!this.todayData) {
      container.innerHTML = `<div class="panini-loading">Lade Tagesplan...</div>`;
      return;
    }

    const { week, day, focus, active_sutra, week_sutras, transformation_drill, error_hunt_item, topic, checklist } = this.todayData;

    container.innerHTML = `
      <div class="panini-today-grid">
        
        <!-- Left: Today's Focus Card & Active Sūtra -->
        <div class="today-left-col">
          
          <div class="today-hero-card">
            <div class="hero-top">
              <span class="day-badge">Woche ${week} · Tag ${day}</span>
              <span class="focus-badge">Fokus: ${focus}</span>
              <button class="btn-advance-day" id="btnAdvanceDay" title="Nächsten Lerntag freischalten">Nächster Tag ➔</button>
            </div>
            <h3>Tagesprogramm: Fundament legen &amp; laut sprechen</h3>
            <p>Jeder Tag verbindet 20 Min Sūtra-Vertiefung, 15 Min Gaṇapāṭha-Karteikarten, Hören/Lesen und aktive Sprechpraxis.</p>
          </div>

          <!-- Active Sūtra Workout -->
          ${active_sutra ? `
            <div class="today-sutra-spotlight">
              <div class="spotlight-header">
                <div>
                  <span class="sutra-num-badge">Sūtra ${active_sutra.number}</span>
                  <h4>${active_sutra.title}</h4>
                </div>
                <button class="btn-toggle-mastered ${this.isSutraMastered(active_sutra.id) ? 'mastered' : ''}" 
                        onclick="window.paniniTrainer.toggleSutraMastered('${active_sutra.id}')">
                  ${this.isSutraMastered(active_sutra.id) ? '✓ Gemeistert' : 'Als gemeistert markieren'}
                </button>
              </div>

              <div class="sutra-rule-box">
                <span class="rule-icon">📌</span>
                <p><strong>Regel:</strong> ${active_sutra.rule}</p>
              </div>

              <!-- Mustersätze -->
              <div class="spotlight-examples">
                <h5>Udāharaṇa ✓ (Mustersätze – laut sprechen!)</h5>
                <ul class="example-list">
                  ${(active_sutra.examples_correct || []).map(ex => `
                    <li class="example-item">
                      <span class="check-icon">✓</span>
                      <span>${ex}</span>
                    </li>
                  `).join('')}
                </ul>
              </div>

              <!-- Śākhā Sentence Writing Box -->
              <div class="today-sakha-card">
                <div class="sakha-header">
                  <span class="sakha-badge">🌿 Śākhā (Tagesübung)</span>
                  <span class="sakha-hint">Gemini AI / Goethe B2 Evaluation</span>
                </div>
                <p class="sakha-prompt">${active_sutra.exercise_prompt}</p>

                <!-- Liste 1 Quick Selection & Reference Bar -->
                <div class="today-list1-helper">
                  <div class="helper-top-row">
                    <span class="helper-title">📖 Verben aus Liste 1 (Dhātupāṭha) für heute:</span>
                    <button type="button" class="btn-open-full-list" onclick="window.paniniTrainer.openGanapathaList('list_1')">
                      📚 Ganze Liste 1 öffnen (170 Einträge) ➔
                    </button>
                  </div>
                  <div class="verb-chips-row">
                    <span class="chips-hint">Klicken zum Einfügen:</span>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('denken an', 'an + A')">denken an (+ A)</button>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('zweifeln an', 'an + D')">zweifeln an (+ D)</button>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('warten auf', 'auf + A')">warten auf (+ A)</button>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('bestehen auf', 'auf + D')">bestehen auf (+ D)</button>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('leiden unter', 'unter + D')">leiden unter (+ D)</button>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('sich interessieren für', 'für + A')">sich interessieren für (+ A)</button>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('abhängen von', 'von + D')">abhängen von (+ D)</button>
                    <button type="button" class="verb-chip" onclick="window.paniniTrainer.insertVerbTemplate('sich beschäftigen mit', 'mit + D')">sich beschäftigen mit (+ D)</button>
                  </div>
                </div>

                <textarea id="todaySakhaInput" class="panini-textarea" placeholder="Wählen Sie oben ein Verb aus Liste 1 oder schreiben Sie Ihre Sätze über Sache und Person..."></textarea>
                <div class="sakha-actions">
                  <button class="btn-submit-sakha" id="btnSubmitTodaySakha" onclick="window.paniniTrainer.submitSakha('${active_sutra.id}', 'todaySakhaInput', 'todaySakhaFeedback')">
                    Satz bewerten lassen ➔
                  </button>
                  <span class="sakha-sub-note">Bewertung nach B2-Syntax, Kasus, Rektion &amp; Register</span>
                </div>
                <div id="todaySakhaFeedback" class="sakha-eval-result"></div>
              </div>

            </div>
          ` : '<p>Kein aktives Sūtra für heute.</p>'}

          <!-- Today's Transformation Quick-Drill -->
          ${transformation_drill ? `
            <div class="today-quick-drill-card">
              <div class="drill-header">
                <span class="drill-badge">🔄 Hin und zurück (Übung 1)</span>
                <span class="drill-title">Transformation: Schlicht ➔ Gehoben</span>
              </div>
              <div class="drill-body">
                <div class="drill-prompt-box">
                  <label>Schlicht (Verbalstil / B1-Gespräch):</label>
                  <p>„${transformation_drill.schlicht}“</p>
                </div>
                <div class="drill-input-box">
                  <label>Ihre gehobene B2-Umformung (Nominalstil):</label>
                  <input type="text" id="todayTransformInput" class="panini-input" placeholder="Formulieren Sie im gehobenen Nominalstil...">
                </div>
                <div class="drill-actions">
                  <button class="btn-primary" onclick="window.paniniTrainer.submitTransformation('${transformation_drill.id}', 'schlicht_to_gehoben', 'todayTransformInput', 'todayTransformFeedback')">
                    Transformation prüfen
                  </button>
                  <button class="btn-secondary" onclick="window.paniniTrainer.revealTransformation('${transformation_drill.id}', 'todayTransformFeedback')">
                    Musterlösung anzeigen
                  </button>
                </div>
                <div id="todayTransformFeedback" class="drill-eval-result"></div>
              </div>
            </div>
          ` : ''}

        </div>

        <!-- Right: Daily Checklist & Speaking/Discussion Topic -->
        <div class="today-right-col">

          <!-- Abhyāsa-Krama: Daily Checklist -->
          <div class="checklist-card">
            <div class="checklist-header">
              <h4>📋 Tages-Checkliste (Abhyāsa-Krama)</h4>
              <span class="checklist-sub">12-Wochen-Erfolgsroutine</span>
            </div>
            <ul class="checklist-items">
              <li class="checklist-item ${checklist?.sutras ? 'checked' : ''}">
                <input type="checkbox" id="chk_sutras" ${checklist?.sutras ? 'checked' : ''} 
                       onchange="window.paniniTrainer.toggleChecklistItem('sutras', this.checked)">
                <label for="chk_sutras">
                  <strong>20 Min:</strong> Sūtras lernen &amp; Śākhā-Satz bilden
                </label>
              </li>
              <li class="checklist-item ${checklist?.flashcards ? 'checked' : ''}">
                <input type="checkbox" id="chk_flashcards" ${checklist?.flashcards ? 'checked' : ''}
                       onchange="window.paniniTrainer.toggleChecklistItem('flashcards', this.checked)">
                <label for="chk_flashcards" style="display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 8px;">
                  <span><strong>15 Min:</strong> Gaṇapāṭha-Karteikarten aus Teil B</span>
                  <button type="button" class="btn-micro-jump" style="font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border-color); background: rgba(245,158,11,0.15); color: #fbbf24; cursor: pointer; white-space: nowrap;" onclick="event.preventDefault(); window.paniniTrainer.openGanapathaCards('list_1')">🃏 Karten üben ➔</button>
                </label>
              </li>
              <li class="checklist-item ${checklist?.listening_reading ? 'checked' : ''}">
                <input type="checkbox" id="chk_listening" ${checklist?.listening_reading ? 'checked' : ''}
                       onchange="window.paniniTrainer.toggleChecklistItem('listening_reading', this.checked)">
                <label for="chk_listening">
                  <strong>45–60 Min:</strong> Hören &amp; Lesen (Tagesschau, DW, ZEIT)
                </label>
              </li>
              <li class="checklist-item ${checklist?.speaking ? 'checked' : ''}">
                <input type="checkbox" id="chk_speaking" ${checklist?.speaking ? 'checked' : ''}
                       onchange="window.paniniTrainer.toggleChecklistItem('speaking', this.checked)">
                <label for="chk_speaking">
                  <strong>30 Min:</strong> Sprechen (Vortrag mit Aufnahmegerät)
                </label>
              </li>
              <li class="checklist-item ${checklist?.recitation ? 'checked' : ''}">
                <input type="checkbox" id="chk_recitation" ${checklist?.recitation ? 'checked' : ''}
                       onchange="window.paniniTrainer.toggleChecklistItem('recitation', this.checked)">
                <label for="chk_recitation">
                  <strong>5 Min:</strong> Sūtras vom Vortag auswendig aufsagen
                </label>
              </li>
            </ul>
          </div>

          <!-- Speaking Topic of the Week -->
          ${topic ? `
            <div class="today-topic-card">
              <div class="topic-header">
                <span class="topic-badge">🎙️ Sprech- &amp; Schreibthema #${topic.id}</span>
                <h4>${topic.title}</h4>
              </div>
              <p class="topic-desc">${topic.description}</p>
              <div class="topic-prompts">
                <strong>Leitfragen:</strong>
                <ul>
                  ${(topic.prompts || []).map(p => `<li>${p}</li>`).join('')}
                </ul>
              </div>
              <div class="topic-links">
                <button class="btn-primary" onclick="window.paniniTrainer.openExamSimulatorWithTopic('${topic.title}')">
                  Im Prüfungssimulator vortragen / schreiben ➔
                </button>
              </div>
            </div>
          ` : ''}

          <!-- Quick Navigation to Other Sūtras of this Week -->
          <div class="week-sutras-card">
            <h4>Sūtras dieser Woche (${week_sutras ? week_sutras.length : 0})</h4>
            <div class="week-sutra-pills">
              ${(week_sutras || []).map(s => `
                <div class="week-sutra-pill ${s.id === active_sutra?.id ? 'active' : ''} ${this.isSutraMastered(s.id) ? 'mastered' : ''}"
                     onclick="window.paniniTrainer.viewSutraInModal('${s.id}')">
                  <span class="pill-num">${s.number}</span>
                  <span class="pill-name">${s.title}</span>
                  ${this.isSutraMastered(s.id) ? '<span class="pill-check">✓</span>' : ''}
                </div>
              `).join('')}
            </div>
          </div>

        </div>

      </div>
    `;

    // Bind advance day button
    const advBtn = document.getElementById('btnAdvanceDay');
    if (advBtn) {
      advBtn.addEventListener('click', () => this.advanceDay());
    }
  }

  // ===========================================================================
  // SUB-VIEW 2: SŪTRAPĀṬHA (ALL 22 SŪTRAS)
  // ===========================================================================
  renderSutrasView(container) {
    const adhyayas = this.overview?.adhyayis || [];

    container.innerHTML = `
      <div class="sutras-view-wrap">
        
        <!-- Filter Controls -->
        <div class="sutras-filter-bar">
          <div class="filter-group">
            <label>Adhyāya:</label>
            <select id="selAdhyaya" class="panini-select" onchange="window.paniniTrainer.filterSutras()">
              <option value="all">Alle Adhyāyas (I bis IX)</option>
              ${adhyayas.map(a => `
                <option value="${a.id}" ${this.activeFilterAdhyaya === a.id ? 'selected' : ''}>
                  ${a.id}. ${a.title}
                </option>
              `).join('')}
            </select>
          </div>
          <div class="filter-group">
            <label>Woche:</label>
            <select id="selWeek" class="panini-select" onchange="window.paniniTrainer.filterSutras()">
              <option value="all">Alle Wochen (1 bis 8)</option>
              ${[1, 2, 3, 4, 5, 6, 7, 8].map(w => `
                <option value="${w}" ${this.activeFilterWeek === String(w) ? 'selected' : ''}>Woche ${w}</option>
              `).join('')}
            </select>
          </div>
          <div class="sutra-recitation-toggle">
            <button class="btn-recite-toggle" onclick="window.paniniTrainer.toggleAllCoverMode()">
              👁️ Rezitations-Modus (Texte abdecken)
            </button>
          </div>
        </div>

        <!-- Sūtras Accordion List -->
        <div class="sutras-accordion-list" id="sutrasAccordionList">
          ${this.renderSutrasListHTML()}
        </div>

      </div>
    `;
  }

  filterSutras() {
    const selA = document.getElementById('selAdhyaya');
    const selW = document.getElementById('selWeek');
    if (selA) this.activeFilterAdhyaya = selA.value;
    if (selW) this.activeFilterWeek = selW.value;

    const listContainer = document.getElementById('sutrasAccordionList');
    if (listContainer) {
      listContainer.innerHTML = this.renderSutrasListHTML();
    }
  }

  renderSutrasListHTML() {
    let filtered = [...this.sutras];
    if (this.activeFilterAdhyaya !== 'all') {
      filtered = filtered.filter(s => s.adhyaya === this.activeFilterAdhyaya);
    }
    if (this.activeFilterWeek !== 'all') {
      const w = parseInt(this.activeFilterWeek);
      filtered = filtered.filter(s => (s.weeks || []).includes(w));
    }

    if (filtered.length === 0) {
      return `<div class="empty-state">Keine Sūtras für diese Filterkombination gefunden.</div>`;
    }

    return filtered.map(s => {
      const isMastered = this.isSutraMastered(s.id);
      const isCovered = !!this.coveredCards[s.id];

      return `
        <div class="sutra-card ${isMastered ? 'is-mastered' : ''} ${isCovered ? 'covered' : ''}" id="card_${s.id}">
          
          <div class="sutra-card-head" onclick="window.paniniTrainer.toggleSutraCard('${s.id}')">
            <div class="sutra-head-left">
              <span class="sutra-tag">Sūtra ${s.number}</span>
              <span class="adhyaya-badge">Adhyāya ${s.adhyaya}</span>
              <h4 class="sutra-title">${s.title}</h4>
            </div>
            <div class="sutra-head-right">
              <button class="btn-cover-mode" onclick="event.stopPropagation(); window.paniniTrainer.toggleCardCover('${s.id}')" title="Aufsage-Modus (Text verdecken)">
                ${isCovered ? '👁️ Aufdecken' : '🙈 Abdecken'}
              </button>
              <button class="btn-master-toggle ${isMastered ? 'mastered' : ''}" 
                      onclick="event.stopPropagation(); window.paniniTrainer.toggleSutraMastered('${s.id}')">
                ${isMastered ? '✓ Gemeistert' : 'Als gemeistert markieren'}
              </button>
              <span class="accordion-chevron">▾</span>
            </div>
          </div>

          <div class="sutra-card-body" id="body_${s.id}">
            
            <!-- 1. Sūtra Rule -->
            <div class="sutra-section sutra-rule-section">
              <div class="sec-label">Sūtra (Regel):</div>
              <div class="sec-content rule-text ${isCovered ? 'blur-text' : ''}">${s.rule}</div>
            </div>

            <!-- 2. Udāharaṇa (Correct Models) -->
            <div class="sutra-section sutra-model-section">
              <div class="sec-label">Udāharaṇa ✓ (Mustersätze – laut sprechen!):</div>
              <ul class="model-sentences ${isCovered ? 'blur-text' : ''}">
                ${(s.examples_correct || []).map(ex => `
                  <li><span class="mark">✓</span> <span>${ex}</span></li>
                `).join('')}
              </ul>
            </div>

            <!-- 3. Apaśabda (Errors & Corrections) -->
            ${s.examples_wrong && s.examples_wrong.length ? `
              <div class="sutra-section sutra-error-section">
                <div class="sec-label">Apaśabda ✗ (Typische Fehler &amp; Berichtigung):</div>
                <div class="error-grid ${isCovered ? 'blur-text' : ''}">
                  ${s.examples_wrong.map(err => `
                    <div class="error-row">
                      <div class="error-wrong">✗ ${err.wrong}</div>
                      <div class="error-correct">➔ ✓ ${err.correct}</div>
                    </div>
                  `).join('')}
                </div>
              </div>
            ` : ''}

            <!-- 4. Vṛtti (Explanation) -->
            <div class="sutra-section sutra-vritti-section">
              <div class="sec-label">Vṛtti (Erklärung &amp; Feinheiten):</div>
              <div class="sec-content vritti-text">${(s.explanation || '').replace(/\n/g, '<br>')}</div>
            </div>

            <!-- 5. Śākhā (Branch / Daily Application Exercise) -->
            <div class="sutra-section sutra-sakha-section">
              <div class="sec-label">🌿 Śākhā (Aus der Regel wachsende Praxis):</div>
              <p class="sakha-task-prompt"><strong>Aufgabe:</strong> ${s.exercise_prompt}</p>
              
              <div class="sakha-write-area">
                <textarea id="input_${s.id}" class="panini-textarea" placeholder="Bilden Sie Ihren Satz nach dieser Regel und lassen Sie ihn von der Gemini B2 KI begutachten..."></textarea>
                <div class="sakha-actions">
                  <button class="btn-submit-sakha" onclick="window.paniniTrainer.submitSakha('${s.id}', 'input_${s.id}', 'eval_${s.id}')">
                    Śākhā mit Gemini B2 auswerten ➔
                  </button>
                  <span class="sakha-sub-note">Sofortige Prüfung auf B2-Grammatik, Rektion, Wortstellung &amp; Register</span>
                </div>
                <div id="eval_${s.id}" class="sakha-eval-result"></div>
              </div>

            </div>

          </div>

        </div>
      `;
    }).join('');
  }

  toggleSutraCard(sutraId) {
    const card = document.getElementById(`card_${sutraId}`);
    if (card) {
      card.classList.toggle('open');
    }
  }

  toggleCardCover(sutraId) {
    this.coveredCards[sutraId] = !this.coveredCards[sutraId];
    const card = document.getElementById(`card_${sutraId}`);
    if (card) {
      card.classList.toggle('covered', this.coveredCards[sutraId]);
      const btn = card.querySelector('.btn-cover-mode');
      if (btn) btn.innerHTML = this.coveredCards[sutraId] ? '👁️ Aufdecken' : '🙈 Abdecken';
      card.querySelectorAll('.rule-text, .model-sentences, .error-grid').forEach(el => {
        el.classList.toggle('blur-text', this.coveredCards[sutraId]);
      });
    }
  }

  toggleAllCoverMode() {
    const anyCovered = Object.values(this.coveredCards).some(v => v);
    const targetState = !anyCovered;
    this.sutras.forEach(s => {
      this.coveredCards[s.id] = targetState;
    });
    const listContainer = document.getElementById('sutrasAccordionList');
    if (listContainer) {
      listContainer.innerHTML = this.renderSutrasListHTML();
    }
  }

  // ===========================================================================
  // SUB-VIEW 3: PRAKRIYĀ (EXERCISES & DRILLS)
  // ===========================================================================
  renderPrakriyaView(container) {
    container.innerHTML = `
      <div class="prakriya-view-wrap">
        
        <!-- Prakriya Nav Pills -->
        <div class="prakriya-pills-bar">
          <button class="prakriya-pill-btn ${this.activePrakriyaTab === 'transform' ? 'active' : ''}" 
                  onclick="window.paniniTrainer.setPrakriyaTab('transform')">
            🔄 Übung 1: Hin und zurück (13 Transformationen)
          </button>
          <button class="prakriya-pill-btn ${this.activePrakriyaTab === 'error_hunt' ? 'active' : ''}"
                  onclick="window.paniniTrainer.setPrakriyaTab('error_hunt')">
            🔍 Übung 2: Fehlerjagd (10 Sätze)
          </button>
          <button class="prakriya-pill-btn ${this.activePrakriyaTab === 'matrix' ? 'active' : ''}"
                  onclick="window.paniniTrainer.setPrakriyaTab('matrix')">
            📐 Sūtra 20: Nominalstil-Matrix
          </button>
          <button class="prakriya-pill-btn ${this.activePrakriyaTab === 'translations' ? 'active' : ''}"
                  onclick="window.paniniTrainer.setPrakriyaTab('translations')">
            🌐 Übung 3: Übersetzung &amp; Register
          </button>
        </div>

        <div class="prakriya-tab-content" id="prakriyaTabContent">
          ${this.renderPrakriyaContentHTML()}
        </div>

      </div>
    `;
  }

  setPrakriyaTab(tabName) {
    this.activePrakriyaTab = tabName;
    document.querySelectorAll('.prakriya-pill-btn').forEach(b => b.classList.remove('active'));
    this.renderPrakriyaView(document.getElementById('paniniSubViewContent'));
  }

  renderPrakriyaContentHTML() {
    switch (this.activePrakriyaTab) {
      case 'transform':
        return this.renderTransformationsHTML();
      case 'error_hunt':
        return this.renderErrorHuntHTML();
      case 'matrix':
        return this.renderMatrixHTML();
      case 'translations':
        return this.renderTranslationsHTML();
      default:
        return this.renderTransformationsHTML();
    }
  }

  renderTransformationsHTML() {
    return `
      <div class="transform-intro">
        <h4>Übung 1 – Hin und zurück: Registerwechsel Schlicht ↔ Gehoben</h4>
        <p>B2 verlangt den souveränen Wechsel zwischen dem natürlichen Verbalstil des Gesprächs und dem präzisen Nominalstil formeller Texte. Trainieren Sie beide Richtungen!</p>
      </div>
      <div class="transform-cards-list">
        ${this.transformations.map(t => {
          const isMastered = (this.progress?.transformations_mastered || []).includes(t.id);
          return `
            <div class="transform-card ${isMastered ? 'mastered' : ''}">
              <div class="trans-head">
                <span class="trans-id">Satz ${t.number} (${t.id})</span>
                <span class="trans-sutras">Relevante Sūtras: ${(t.sutras || []).join(', ')}</span>
                ${isMastered ? '<span class="trans-mastered-badge">✓ Gemeistert</span>' : ''}
              </div>
              <div class="trans-split">
                <!-- Direction A: Schlicht zu Gehoben -->
                <div class="trans-col">
                  <h5>Richtung A: Verbalstil ➔ Gehobener Nominalstil</h5>
                  <div class="prompt-text"><strong>Vorlage:</strong> „${t.schlicht}“</div>
                  <input type="text" id="trans_in_gehoben_${t.id}" class="panini-input" placeholder="Formulieren Sie im gehobenen Nominalstil...">
                  <div class="trans-btns">
                    <button class="btn-primary" onclick="window.paniniTrainer.submitTransformation('${t.id}', 'schlicht_to_gehoben', 'trans_in_gehoben_${t.id}', 'trans_eval_${t.id}')">
                      Prüfen
                    </button>
                    <button class="btn-secondary" onclick="window.paniniTrainer.revealTransformation('${t.id}', 'trans_eval_${t.id}')">
                      Lösung
                    </button>
                  </div>
                </div>
                <!-- Direction B: Gehoben zu Schlicht -->
                <div class="trans-col">
                  <h5>Richtung B: Gehobener Nominalstil ➔ Verbalstil (Gespräch)</h5>
                  <div class="prompt-text"><strong>Vorlage:</strong> „${t.gehoben}“</div>
                  <input type="text" id="trans_in_schlicht_${t.id}" class="panini-input" placeholder="Formulieren Sie im natürlichen Verbalstil...">
                  <div class="trans-btns">
                    <button class="btn-primary" onclick="window.paniniTrainer.submitTransformation('${t.id}', 'gehoben_to_schlicht', 'trans_in_schlicht_${t.id}', 'trans_eval_${t.id}')">
                      Prüfen
                    </button>
                    <button class="btn-secondary" onclick="window.paniniTrainer.revealTransformation('${t.id}', 'trans_eval_${t.id}')">
                      Lösung
                    </button>
                  </div>
                </div>
              </div>
              <div id="trans_eval_${t.id}" class="trans-feedback-box"></div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  renderErrorHuntHTML() {
    return `
      <div class="error-hunt-intro">
        <h4>Übung 2 – Fehlerjagd: Finde den Fehler und nenne das Sūtra</h4>
        <p>Jeder Satz enthält genau einen grammatischen Fehler. Korrigieren Sie den Satz und geben Sie die Nummer des verletzten Sūtras an.</p>
      </div>
      <div class="error-hunt-list">
        ${this.errorHuntItems.map(item => {
          const isDone = (this.progress?.error_hunt_completed || []).includes(item.id);
          return `
            <div class="error-hunt-card ${isDone ? 'done' : ''}">
              <div class="eh-head">
                <span class="eh-num">Satz ${item.number}</span>
                <span class="eh-focus">Fokus: ${item.focus}</span>
                ${isDone ? '<span class="trans-mastered-badge">✓ Gelöst</span>' : ''}
              </div>
              <div class="eh-sentence-box">
                <span class="eh-wrong-mark">✗</span>
                <span class="eh-wrong-text">„${item.wrong}“</span>
              </div>
              <div class="eh-inputs-row">
                <input type="text" id="eh_corr_${item.id}" class="panini-input eh-corr-input" placeholder="Ihre vollständige Korrektur...">
                <input type="number" id="eh_sutra_${item.id}" class="panini-input eh-sutra-input" placeholder="Sūtra-Nr. (1-22)" min="1" max="22">
                <button class="btn-primary" onclick="window.paniniTrainer.submitErrorHunt('${item.id}', 'eh_corr_${item.id}', 'eh_sutra_${item.id}', 'eh_eval_${item.id}')">
                  Prüfen
                </button>
                <button class="btn-secondary" onclick="window.paniniTrainer.revealErrorHunt('${item.id}', 'eh_eval_${item.id}')">
                  Lösung
                </button>
              </div>
              <div id="eh_eval_${item.id}" class="eh-eval-box"></div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  renderMatrixHTML() {
    return `
      <div class="matrix-intro">
        <h4>Sūtra 20: Die Nominalstil-Transformationsmatrix</h4>
        <p>Die präpositionale Wortgruppe ersetzt den Nebensatz: Das Verb wird zum Nomen, das Akkusativobjekt zum Genitiv, und das Subjekt zum Agens mit <em>durch + A</em>.</p>
      </div>
      <div class="matrix-table-wrap">
        <table class="panini-matrix-table">
          <thead>
            <tr>
              <th>Bedeutung</th>
              <th>Verbalstil (Nebensatz mit Konjunktion)</th>
              <th>Nominalstil (Präposition + Nomen)</th>
            </tr>
          </thead>
          <tbody>
            ${this.nominalstilMatrix.map(row => `
              <tr>
                <td><span class="matrix-badge">${row.bedeutung}</span></td>
                <td><strong>${row.verbalstil}</strong></td>
                <td><span class="matrix-nominal">${row.nominalstil}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  renderTranslationsHTML() {
    return `
      <div class="translations-intro">
        <h4>Übung 3 – Übersetzung und Registerwechsel</h4>
        <p>Formulieren Sie den englischen Gedankengang auf Deutsch – erst schlicht im Gespräch, dann gehoben in einem formellen Bericht.</p>
      </div>
      <div class="translations-list">
        ${this.translations.map(tr => `
          <div class="translation-card">
            <div class="tr-head">
              <span class="tr-num">Satz ${tr.number}</span>
              <span class="tr-focus">Fokus: ${tr.focus}</span>
            </div>
            <div class="tr-english-box">
              <span class="flag">🇬🇧</span>
              <strong>${tr.english}</strong>
            </div>
            <div class="tr-solutions-grid">
              <div class="tr-sol-col">
                <span class="sol-badge verbal">1. Schlicht (Gespräch)</span>
                <p>„${tr.schlicht}“</p>
              </div>
              <div class="tr-sol-col">
                <span class="sol-badge nominal">2. Gehoben (Bericht)</span>
                <p>„${tr.gehoben}“</p>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  // ===========================================================================
  // ===========================================================================
  // SUB-VIEW 4: GAṆAPĀṬHA (REFERENCE LISTS & FLASHCARDS)
  // ===========================================================================
  getActiveCards() {
    if (!this.flashcards || !this.flashcards.length) return [];
    if (!this.activeListFilter || this.activeListFilter === 'all') {
      return this.flashcards;
    }
    return this.flashcards.filter(c => c.list === this.activeListFilter);
  }

  renderGanapathaView(container) {
    if (!container) container = document.getElementById('paniniSubViewContent');
    if (!container) return;

    const listEntries = Object.entries(this.lists || {});
    const activeCards = this.getActiveCards();
    const totalCardsCount = (this.flashcards || []).length;

    container.innerHTML = `
      <div class="ganapatha-view-wrap">
        
        <!-- Header Controls: Mode Switcher & List Selector -->
        <div class="ganapatha-header-controls">
          <div class="ganapatha-mode-pills">
            <button class="g-mode-btn ${this.ganapathaMode === 'cards' ? 'active' : ''}" 
                    onclick="window.paniniTrainer.setGanapathaMode('cards')">
              🃏 3D-Karteikarten (${activeCards.length} Karten)
            </button>
            <button class="g-mode-btn ${this.ganapathaMode === 'reference' ? 'active' : ''}" 
                    onclick="window.paniniTrainer.setGanapathaMode('reference')">
              📖 Vollständiges Nachschlagewerk &amp; Tabellen
            </button>
          </div>

          <div class="ganapatha-filter-row">
            <div class="list-select-group">
              <label>Liste:</label>
              <select id="selGanapathaList" class="panini-select" onchange="window.paniniTrainer.changeGanapathaList(this.value)">
                <option value="all" ${this.activeListFilter === 'all' ? 'selected' : ''}>
                  🌟 Alle Listen (${totalCardsCount} Karten gesamt)
                </option>
                ${listEntries.map(([lid, ldata]) => {
                  const cnt = (this.flashcards || []).filter(c => c.list === lid).length;
                  return `
                    <option value="${lid}" ${this.activeListFilter === lid ? 'selected' : ''}>
                      ${ldata?.title || lid} (${cnt} Karten)
                    </option>
                  `;
                }).join('')}
              </select>
            </div>

            ${this.ganapathaMode === 'reference' ? `
              <div class="list-search-group">
                <input type="text" id="inputListSearch" class="panini-input" 
                       placeholder="🔍 Suchen nach Verb, Präposition, Kasus (z.B. warten, an, Dativ)..." 
                       value="${this.ganapathaSearch || ''}"
                       oninput="window.paniniTrainer.onListSearch(this.value)">
              </div>
            ` : ''}
          </div>
        </div>

        <!-- Mode Content Area -->
        <div class="ganapatha-mode-content">
          ${this.ganapathaMode === 'cards' 
            ? this.renderFlashcardsDeckHTML() 
            : this.renderReferenceListHTML()}
        </div>

      </div>
    `;
  }

  setGanapathaMode(mode) {
    this.ganapathaMode = mode;
    this.renderGanapathaView(document.getElementById('paniniSubViewContent'));
  }

  changeGanapathaList(listId) {
    this.activeListFilter = listId;
    this.currentCardIndex = 0;
    this.cardIsFlipped = false;
    this.renderGanapathaView(document.getElementById('paniniSubViewContent'));
  }

  onListSearch(query) {
    this.ganapathaSearch = query;
    const refContainer = document.querySelector('.ganapatha-mode-content');
    if (refContainer && this.ganapathaMode === 'reference') {
      refContainer.innerHTML = this.renderReferenceListHTML();
    }
  }

  openGanapathaList(listId) {
    this.currentSubView = 'ganapatha';
    this.activeListFilter = listId;
    this.ganapathaMode = 'reference';
    this.ganapathaSearch = '';
    this.renderSubViewNav();
    this.renderActiveSubView();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  openGanapathaCards(listId) {
    this.currentSubView = 'ganapatha';
    this.activeListFilter = listId || 'all';
    this.ganapathaMode = 'cards';
    this.currentCardIndex = 0;
    this.cardIsFlipped = false;
    this.renderSubViewNav();
    this.renderActiveSubView();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  insertVerbTemplate(verb, prep) {
    const input = document.getElementById('todaySakhaInput');
    if (!input) return;
    const prepName = prep.split(' ')[0];
    const isVowel = prepName.startsWith('a') || prepName.startsWith('u') || prepName.startsWith('ü');
    const r = isVowel ? 'r' : '';
    const template = `\nVerb: ${verb} [${prep}]\n- Sache: Ich ... ${prepName} ... (Frage: Wo${r}${prepName} ...? -> Antwort: Da${r}${prepName} ...)\n- Person: Ich ... ${prepName} ... (Frage: ${prepName} wen/wem ...? -> Antwort: ... ${prepName} ihn/ihm)\n`;
    if (input.value.trim()) {
      input.value += template;
    } else {
      input.value = template.trim();
    }
    input.focus();
  }

  useVerbInSakha(verb, prep) {
    this.currentSubView = 'today';
    this.renderSubViewNav();
    this.renderActiveSubView();
    setTimeout(() => {
      this.insertVerbTemplate(verb, prep);
      const el = document.getElementById('todaySakhaInput');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  }

  // ===========================================================================
  // REFERENCE LIST RENDERERS
  // ===========================================================================
  renderReferenceListHTML() {
    switch (this.activeListFilter) {
      case 'all':
        return `
          <div class="all-reference-lists">
            ${this.renderList1ReferenceHTML()}
            <hr class="list-separator" style="margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, rgba(255,255,255,0.15));">
            ${this.renderList2ReferenceHTML()}
            <hr class="list-separator" style="margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, rgba(255,255,255,0.15));">
            ${this.renderList3ReferenceHTML()}
            <hr class="list-separator" style="margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, rgba(255,255,255,0.15));">
            ${this.renderList4ReferenceHTML()}
            <hr class="list-separator" style="margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, rgba(255,255,255,0.15));">
            ${this.renderList5ReferenceHTML()}
            <hr class="list-separator" style="margin: 32px 0; border: none; border-top: 1px dashed var(--border-color, rgba(255,255,255,0.15));">
            ${this.renderList6ReferenceHTML()}
          </div>
        `;
      case 'list_1':
        return this.renderList1ReferenceHTML();
      case 'list_2':
        return this.renderList2ReferenceHTML();
      case 'list_3':
        return this.renderList3ReferenceHTML();
      case 'list_4':
        return this.renderList4ReferenceHTML();
      case 'list_5':
        return this.renderList5ReferenceHTML();
      case 'list_6':
        return this.renderList6ReferenceHTML();
      default:
        return this.renderList1ReferenceHTML();
    }
  }

  renderList1ReferenceHTML() {
    const ldata = this.lists['list_1'];
    if (!ldata) return '<p>Liste 1 nicht geladen.</p>';
    const q = (this.ganapathaSearch || '').toLowerCase().trim();

    const verben = ldata.items.verben || {};
    const adjektive = ldata.items.adjektive || {};
    const nomen = ldata.items.nomen || [];

    const verbGroups = Object.entries(verben).map(([prepCase, verbList]) => {
      const filtered = q ? verbList.filter(v => v.toLowerCase().includes(q) || prepCase.toLowerCase().includes(q)) : verbList;
      return { prepCase, verbs: filtered };
    }).filter(g => g.verbs.length > 0);

    const adjGroups = Object.entries(adjektive).map(([prepCase, adjList]) => {
      const filtered = q ? adjList.filter(a => a.toLowerCase().includes(q) || prepCase.toLowerCase().includes(q)) : adjList;
      return { prepCase, adjs: filtered };
    }).filter(g => g.adjs.length > 0);

    const filteredNomen = q ? nomen.filter(n => n.toLowerCase().includes(q)) : nomen;

    return `
      <div class="reference-list-content">
        <div class="ref-list-intro">
          <h3>📖 Liste 1 – Dhātupāṭha: Verben, Adjektive und Nomen mit festen Präpositionen</h3>
          <p>Das Fundament für <strong>Sūtra 1 (Das Präpositionalobjekt)</strong> und <strong>Sūtra 2 (Pronominaladverb)</strong>. Wählen Sie ein beliebiges Verb und klicken Sie auf <em>„In Śākhā üben“</em>, um sofort eigene Sätze im Tagesplan zu bilden.</p>
        </div>

        <!-- Section 1: Verbs -->
        <div class="ref-category-card">
          <div class="ref-cat-header">
            <span class="cat-pill">Teil 1</span>
            <h4>Verben mit festen Präpositionen (126 Verben)</h4>
          </div>
          <div class="prep-groups-grid">
            ${verbGroups.map(g => `
              <div class="prep-group-box">
                <div class="prep-badge-case">${g.prepCase}</div>
                <ul class="prep-verb-list">
                  ${g.verbs.map(v => `
                    <li class="prep-item">
                      <span class="verb-text">${v}</span>
                      <button class="btn-use-sakha" title="In Śākhā-Übung einfügen" onclick="window.paniniTrainer.useVerbInSakha('${v}', '${g.prepCase}')">
                        ✍️ In Śākhā
                      </button>
                    </li>
                  `).join('')}
                </ul>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Section 2: Adjectives -->
        <div class="ref-category-card">
          <div class="ref-cat-header">
            <span class="cat-pill">Teil 2</span>
            <h4>Adjektive mit festen Präpositionen (23 Adjektive)</h4>
          </div>
          <div class="prep-groups-grid">
            ${adjGroups.map(g => `
              <div class="prep-group-box">
                <div class="prep-badge-case">${g.prepCase}</div>
                <ul class="prep-verb-list">
                  ${g.adjs.map(a => `
                    <li class="prep-item">
                      <span class="verb-text">${a}</span>
                      <button class="btn-use-sakha" title="In Śākhā-Übung einfügen" onclick="window.paniniTrainer.useVerbInSakha('${a}', '${g.prepCase}')">
                        ✍️ In Śākhā
                      </button>
                    </li>
                  `).join('')}
                </ul>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Section 3: Nouns -->
        <div class="ref-category-card">
          <div class="ref-cat-header">
            <span class="cat-pill">Teil 3</span>
            <h4>Nomen mit festen Präpositionen (21 Nomen)</h4>
          </div>
          <div class="nomen-chips-grid">
            ${filteredNomen.map(n => `
              <div class="nomen-chip-item">
                <span class="nomen-name">${n}</span>
                <button class="btn-use-sakha" title="In Śākhā-Übung einfügen" onclick="window.paniniTrainer.useVerbInSakha('${n}', 'Nomen')">
                  ✍️ In Śākhā
                </button>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  renderList2ReferenceHTML() {
    const ldata = this.lists['list_2'];
    if (!ldata) return '<p>Liste 2 nicht geladen.</p>';
    const q = (this.ganapathaSearch || '').toLowerCase().trim();
    const groups = Object.entries(ldata.items || {});

    return `
      <div class="reference-list-content">
        <div class="ref-list-intro">
          <h3>📖 Liste 2 – Nomen-Verb-Verbindungen (Funktionsverbgefüge)</h3>
          <p>Das Kernstück für <strong>Sūtra 3</strong>: Hier trägt das Nomen die Bedeutung und das Verb die Grammatik. Für gehobene B2-Berichte und Briefe.</p>
        </div>
        <div class="nvv-groups-grid">
          ${groups.map(([verbHead, items]) => {
            const filtered = q ? items.filter(it => it.toLowerCase().includes(q) || verbHead.toLowerCase().includes(q)) : items;
            if (filtered.length === 0) return '';
            return `
              <div class="nvv-group-box">
                <div class="nvv-head-badge">Verb: ${verbHead}</div>
                <div class="nvv-items-list">
                  ${filtered.map(item => {
                    const nvv = item.split('(')[0].trim();
                    const simple = item.split('(')[1]?.replace(')', '').trim() || '';
                    return `
                      <div class="nvv-item-row">
                        <div class="nvv-rich"><strong>${nvv}</strong></div>
                        <div class="nvv-simple">➔ schlicht: <em>${simple}</em></div>
                      </div>
                    `;
                  }).join('')}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  renderList3ReferenceHTML() {
    const ldata = this.lists['list_3'];
    if (!ldata) return '<p>Liste 3 nicht geladen.</p>';
    const q = (this.ganapathaSearch || '').toLowerCase().trim();
    const items = (ldata.items || []).filter(it => !q || JSON.stringify(it).toLowerCase().includes(q));
    const zweiteilig = (ldata.zweiteilig || []).filter(z => !q || z.toLowerCase().includes(q));

    return `
      <div class="reference-list-content">
        <div class="ref-list-intro">
          <h3>📖 Liste 3 – Konnektoren nach Bedeutung und Klasse</h3>
          <p>Verknüpft mit <strong>Sūtra 8</strong> und <strong>Sūtra 9</strong>: Wechseln Sie flexibel zwischen Nebensatz (Subjunktion), Hauptsatz (Konnektoraladverb) und Nominalstil (Präposition).</p>
        </div>
        <div class="ref-category-card">
          <table class="panini-matrix-table">
            <thead>
              <tr>
                <th>Bedeutung</th>
                <th>Subjunktion (Verb am Ende)</th>
                <th>Konnektoraladverb (Pos. 1 / Inversion)</th>
                <th>Präposition (Nominalstil)</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(row => `
                <tr>
                  <td><span class="matrix-badge">${row.bedeutung}</span></td>
                  <td><strong>${row.subjunktion}</strong></td>
                  <td><span>${row.adverb}</span></td>
                  <td><span class="matrix-nominal">${row.praeposition}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <div class="ref-category-card">
          <div class="ref-cat-header">
            <h4>Zweiteilige Doppelkonnektoren</h4>
          </div>
          <div class="nomen-chips-grid">
            ${zweiteilig.map(z => `
              <div class="nomen-chip-item">
                <span class="nomen-name"><strong>${z}</strong></span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  renderList4ReferenceHTML() {
    const ldata = this.lists['list_4'];
    if (!ldata) return '<p>Liste 4 nicht geladen.</p>';
    const q = (this.ganapathaSearch || '').toLowerCase().trim();
    const prep = (ldata.items?.praepositionen || []).filter(p => !q || p.toLowerCase().includes(q));
    const wendungen = (ldata.items?.feste_wendungen || []).filter(w => !q || w.toLowerCase().includes(q));
    const verben = (ldata.items?.verben || []).filter(v => !q || v.toLowerCase().includes(q));

    return `
      <div class="reference-list-content">
        <div class="ref-list-intro">
          <h3>📖 Liste 4 – Genitiv im B2-Register</h3>
          <p>Fundament für <strong>Sūtra 6</strong>: Der Genitiv lebt in formellen Texten nach festen Präpositionen, Funktionswendungen und edlen Verben.</p>
        </div>
        <div class="ref-category-card">
          <div class="ref-cat-header"><h4>Präpositionen mit Genitiv</h4></div>
          <div class="nomen-chips-grid">
            ${prep.map(p => `<div class="nomen-chip-item"><span class="nomen-name"><strong>${p}</strong></span></div>`).join('')}
          </div>
        </div>
        <div class="ref-category-card">
          <div class="ref-cat-header"><h4>Feste Wendungen mit Genitiv</h4></div>
          <div class="nomen-chips-grid">
            ${wendungen.map(w => `<div class="nomen-chip-item"><span class="nomen-name"><strong>${w}</strong></span></div>`).join('')}
          </div>
        </div>
        <div class="ref-category-card">
          <div class="ref-cat-header"><h4>Verben mit obligatorischem Genitivobjekt</h4></div>
          <div class="nomen-chips-grid">
            ${verben.map(v => `<div class="nomen-chip-item"><span class="nomen-name"><strong>${v}</strong></span></div>`).join('')}
          </div>
        </div>
      </div>
    `;
  }

  renderList5ReferenceHTML() {
    const ldata = this.lists['list_5'];
    if (!ldata) return '<p>Liste 5 nicht geladen.</p>';
    const q = (this.ganapathaSearch || '').toLowerCase().trim();
    const groups = Object.entries(ldata.items || {});

    return `
      <div class="reference-list-content">
        <div class="ref-list-intro">
          <h3>📖 Liste 5 – n-Deklination (Schwache Maskulina)</h3>
          <p>Fundament für <strong>Sūtra 5</strong>: Diese Nomen enden im Akkusativ, Dativ und Genitiv obligatorisch auf <em>-(e)n</em> (z.B. <em>den Kollegen, Herrn Weber</em>).</p>
        </div>
        <div class="nvv-groups-grid">
          ${groups.map(([grp, nouns]) => {
            const filtered = q ? nouns.filter(n => n.toLowerCase().includes(q)) : nouns;
            if (filtered.length === 0) return '';
            return `
              <div class="nvv-group-box">
                <div class="nvv-head-badge">${grp}</div>
                <div class="nomen-chips-grid" style="margin-top: 10px;">
                  ${filtered.map(n => `<div class="nomen-chip-item"><span class="nomen-name"><strong>${n}</strong></span></div>`).join('')}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  renderList6ReferenceHTML() {
    const ldata = this.lists['list_6'];
    if (!ldata) return '<p>Liste 6 nicht geladen.</p>';
    const q = (this.ganapathaSearch || '').toLowerCase().trim();
    const sections = Object.entries(ldata.items || {});

    return `
      <div class="reference-list-content">
        <div class="ref-list-intro">
          <h3>📖 Liste 6 – Redemittel für Vortrag, Diskussion und Vorstellungsgespräch</h3>
          <p>Unentbehrliche Textbausteine für <strong>Modul 3 (Schreiben)</strong> und <strong>Modul 4 (Sprechen)</strong>.</p>
        </div>
        <div class="nvv-groups-grid">
          ${sections.map(([sec, phrases]) => {
            const filtered = q ? phrases.filter(p => p.toLowerCase().includes(q)) : phrases;
            if (filtered.length === 0) return '';
            return `
              <div class="nvv-group-box">
                <div class="nvv-head-badge">${sec.replace(/_/g, ' ').toUpperCase()}</div>
                <ul class="prep-verb-list" style="margin-top: 10px;">
                  ${filtered.map(p => `
                    <li class="prep-item" style="display: block; padding: 8px 12px; margin-bottom: 6px; background: rgba(255,255,255,0.03); border-radius: 6px;">
                      „${p}“
                    </li>
                  `).join('')}
                </ul>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  renderFlashcardsDeckHTML() {
    const activeCards = this.getActiveCards();
    if (!activeCards || activeCards.length === 0) {
      return `
        <div class="flashcard-deck-container">
          <div style="text-align: center; padding: 48px 24px; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
            <div style="font-size: 2.8rem; margin-bottom: 12px;">🃏</div>
            <h4 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 8px;">Keine Karteikarten vorhanden</h4>
            <p style="color: var(--text-secondary); max-width: 400px; margin: 0 auto 16px;">
              Für die gewählte Liste wurden derzeit keine Karten gefunden. Wählen Sie eine andere Liste oder «Alle Listen».
            </p>
            <button class="fc-btn" onclick="window.paniniTrainer.changeGanapathaList('all')">🌟 Alle Listen laden</button>
          </div>
        </div>
      `;
    }

    if (this.currentCardIndex >= activeCards.length || this.currentCardIndex < 0) {
      this.currentCardIndex = 0;
    }
    const currentCard = activeCards[this.currentCardIndex];
    const progressPct = Math.round(((this.currentCardIndex + 1) / activeCards.length) * 100);

    return `
      <div class="flashcard-deck-container">
        <div class="flashcard-counter-bar">
          <span id="fcCardCountDisplay">Karte ${this.currentCardIndex + 1} von ${activeCards.length}</span>
          <span class="fc-category-badge" id="fcCategoryDisplay">${currentCard?.category || ''}</span>
        </div>

        <!-- Progress bar -->
        <div style="width: 100%; height: 4px; background: rgba(255, 255, 255, 0.08); border-radius: 2px; overflow: hidden;">
          <div id="fcProgressBar" style="width: ${progressPct}%; height: 100%; background: var(--gradient-gold); transition: width 0.3s cubic-bezier(0.4,0,0.2,1);"></div>
        </div>

        <!-- Flip Card -->
        <div class="flashcard-card-scene" onclick="window.paniniTrainer.flipCurrentCard()">
          <div class="flashcard-card-inner ${this.cardIsFlipped ? 'is-flipped' : ''}" id="flashcardInner">
            <!-- Front -->
            <div class="flashcard-face flashcard-front">
              <div class="fc-side-label">VORDERSEITE (Frage / Lücke)</div>
              <div class="fc-main-text" id="fcFrontText">${currentCard?.front || 'Keine Karten vorhanden.'}</div>
              <div class="fc-tap-hint">👆 Klicken zum Umdrehen · [Leertaste]</div>
            </div>
            <!-- Back -->
            <div class="flashcard-face flashcard-back">
              <div class="fc-side-label">RÜCKSEITE (Lösung)</div>
              <div class="fc-main-text" id="fcBackText">${(currentCard?.back || '').replace(/\n/g, '<br>')}</div>
              <div class="fc-tap-hint">✓ Laut sprechen &amp; verinnerlichen!</div>
            </div>
          </div>
        </div>

        <!-- Flashcard Controls -->
        <div class="flashcard-controls">
          <button class="fc-btn fc-btn-prev" onclick="window.paniniTrainer.prevCard()" title="Vorherige Karte (Pfeil links)">◂ Vorherige</button>
          <button class="fc-btn fc-btn-flip" onclick="window.paniniTrainer.flipCurrentCard()" title="Umdrehen (Leertaste)">🔄 Umdrehen</button>
          <button class="fc-btn fc-btn-known" onclick="window.paniniTrainer.markCardKnown()" title="Als gewusst markieren (Taste G)">✓ Gewusst</button>
          <button class="fc-btn fc-btn-next" onclick="window.paniniTrainer.nextCard()" title="Nächste Karte (Pfeil rechts)">Nächste ▸</button>
          <button class="fc-btn fc-btn-shuffle" onclick="window.paniniTrainer.shuffleCards()" title="Karten mischen (Taste S)">🔀 Mischen</button>
        </div>

        <div style="text-align: center; font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">
          Tastatur: <strong>[Leertaste]</strong> Umdrehen &middot; <strong>[← / →]</strong> Navigieren &middot; <strong>[G]</strong> Gewusst &middot; <strong>[S]</strong> Mischen
        </div>
      </div>
    `;
  }

  flipCurrentCard() {
    this.cardIsFlipped = !this.cardIsFlipped;
    const inner = document.getElementById('flashcardInner');
    if (inner) {
      inner.classList.toggle('is-flipped', this.cardIsFlipped);
    }
  }

  nextCard() {
    const cards = this.getActiveCards();
    if (cards.length === 0) return;
    this.currentCardIndex = (this.currentCardIndex + 1) % cards.length;
    this.cardIsFlipped = false;
    this.updateFlashcardDisplay();
  }

  prevCard() {
    const cards = this.getActiveCards();
    if (cards.length === 0) return;
    this.currentCardIndex = (this.currentCardIndex - 1 + cards.length) % cards.length;
    this.cardIsFlipped = false;
    this.updateFlashcardDisplay();
  }

  async markCardKnown() {
    try {
      const res = await fetch('/api/panini/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'log_flashcards', data: { reviewed: 1, mastered: 1 } })
      });
      if (res.ok) {
        this.progress = await res.json();
        this.renderHeader();
      }
    } catch (e) {
      console.warn('Failed to save flashcard progress:', e);
    }
    this.nextCard();
  }

  shuffleCards() {
    const list = this.activeListFilter;
    const relevantIndices = [];
    this.flashcards.forEach((card, idx) => {
      if (!list || list === 'all' || card.list === list) {
        relevantIndices.push(idx);
      }
    });
    for (let i = relevantIndices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const idxA = relevantIndices[i];
      const idxB = relevantIndices[j];
      const temp = this.flashcards[idxA];
      this.flashcards[idxA] = this.flashcards[idxB];
      this.flashcards[idxB] = temp;
    }
    this.currentCardIndex = 0;
    this.cardIsFlipped = false;
    this.renderGanapathaView(document.getElementById('paniniSubViewContent'));
  }

  updateFlashcardDisplay() {
    const cards = this.getActiveCards();
    if (!cards || cards.length === 0) return;
    if (this.currentCardIndex >= cards.length || this.currentCardIndex < 0) {
      this.currentCardIndex = 0;
    }
    const card = cards[this.currentCardIndex];
    if (!card) return;

    const countDisp = document.getElementById('fcCardCountDisplay');
    const catDisp = document.getElementById('fcCategoryDisplay');
    const frontText = document.getElementById('fcFrontText');
    const backText = document.getElementById('fcBackText');
    const inner = document.getElementById('flashcardInner');
    const progBar = document.getElementById('fcProgressBar');

    if (countDisp) countDisp.innerText = `Karte ${this.currentCardIndex + 1} von ${cards.length}`;
    if (catDisp) catDisp.innerText = card.category || '';
    if (frontText) frontText.innerText = card.front;
    if (backText) backText.innerHTML = (card.back || '').replace(/\n/g, '<br>');
    if (inner) inner.classList.toggle('is-flipped', this.cardIsFlipped);
    if (progBar && progBar.style) {
      const pct = Math.round(((this.currentCardIndex + 1) / cards.length) * 100);
      progBar.style.width = `${pct}%`;
    }
  }

  setupKeyboardNavigation() {
    if (this._keyboardAttached) return;
    this._keyboardAttached = true;

    window.addEventListener('keydown', (e) => {
      if (this.currentSubView !== 'ganapatha' || this.ganapathaMode !== 'cards') return;
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable)) return;

      if (e.code === 'Space') {
        e.preventDefault();
        this.flipCurrentCard();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        this.nextCard();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        this.prevCard();
      } else if (e.key === 'g' || e.key === 'G') {
        e.preventDefault();
        this.markCardKnown();
      } else if (e.key === 's' || e.key === 'S') {
        e.preventDefault();
        this.shuffleCards();
      }
    });
  }

  // ===========================================================================
  // SUB-VIEW 5: 12-WOCHEN-PLAN & THEMEN
  // ===========================================================================
  renderScheduleView(container) {
    container.innerHTML = `
      <div class="schedule-view-wrap">
        
        <div class="schedule-intro">
          <h4>Der 12-Wochen-Kanonischer Übungsplan (Abhyāsa-Krama)</h4>
          <p>Wochen 1–8 decken alle 22 Sūtras und 6 Gaṇapāṭha-Listen systematisch ab. Wochen 9–12 konsolidieren das Wissen durch wöchentliche Goethe-Modellprüfungen.</p>
        </div>

        <div class="schedule-grid">
          ${this.scheduleData.map(entry => {
            const isCurrent = (this.progress?.current_week === entry.week);
            return `
              <div class="schedule-week-card ${isCurrent ? 'current-week' : ''}">
                <div class="sw-head">
                  <span class="sw-label">${entry.label}</span>
                  ${isCurrent ? '<span class="sw-current-badge">Aktuelle Woche</span>' : ''}
                </div>
                <div class="sw-focus"><strong>Fokus:</strong> ${entry.focus}</div>
                <div class="sw-sutras">
                  <strong>Sūtras:</strong>
                  ${entry.sutras && entry.sutras.length ? entry.sutras.map(sid => {
                    const s = this.sutras.find(x => x.id === sid);
                    return `<span class="sutra-pill-tag">${s ? `Sūtra ${s.number}` : sid}</span>`;
                  }).join(' ') : '<em>Konsolidierung / Übungssatz</em>'}
                </div>
                <div class="sw-lists">
                  <strong>Listen:</strong> ${(entry.lists || []).join(', ') || 'Alle Listen im Wechsel'}
                </div>
                <div class="sw-action">
                  <button class="btn-jump-week" onclick="window.paniniTrainer.jumpToWeek(${entry.week})">
                    Zu Woche ${entry.week} springen ➔
                  </button>
                </div>
              </div>
            `;
          }).join('')}
        </div>

      </div>
    `;
  }

  // ===========================================================================
  // EVALUATION & API ACTIONS
  // ===========================================================================
  async submitSakha(sutraId, inputId, outputId) {
    const input = document.getElementById(inputId);
    const output = document.getElementById(outputId);
    if (!input || !output) return;

    const userText = input.value.trim();
    if (!userText) {
      output.innerHTML = `<div class="alert warning">Bitte schreiben Sie zuerst einen Satz.</div>`;
      return;
    }

    output.innerHTML = `
      <div class="panini-eval-loading">
        <div class="spinner-small"></div>
        <span>Gemini AI analysiert Ihren B2-Satz nach Sūtra-Regel &amp; Goethe-Kriterien...</span>
      </div>
    `;

    try {
      const res = await fetch('/api/panini/evaluate-sakha', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sutra_id: sutraId, user_text: userText })
      });
      const data = await res.json();
      this.renderSakhaFeedback(output, data);
      await this.refreshProgress();
    } catch (err) {
      output.innerHTML = `<div class="alert danger">Fehler bei der Auswertung: ${err.message}</div>`;
    }
  }

  renderSakhaFeedback(container, data) {
    const isPass = data.is_correct;
    const score = data.score;
    const cefr = data.cefr_level || 'B2';
    const feedback = data.feedback || '';
    const strengths = data.strengths || [];
    const corrections = data.corrections || [];
    const improved = data.improved_version || '';

    container.innerHTML = `
      <div class="eval-card ${isPass ? 'pass' : 'fail'}">
        <div class="eval-top-bar">
          <span class="eval-level-badge ${isPass ? 'b2' : 'b1'}">Niveau: ${cefr}</span>
          <span class="eval-score-badge">${score} / 10 Punkte</span>
        </div>
        <div class="eval-feedback-text">${feedback}</div>
        
        ${strengths.length ? `
          <div class="eval-strengths">
            <strong>Stärken:</strong>
            <ul>${strengths.map(s => `<li>✓ ${s}</li>`).join('')}</ul>
          </div>
        ` : ''}

        ${corrections.length ? `
          <div class="eval-corrections">
            <strong>Korrekturen &amp; Hinweise:</strong>
            <table class="corr-table">
              <thead><tr><th>Original</th><th>Korrektur</th><th>Erklärung</th></tr></thead>
              <tbody>
                ${corrections.map(c => `
                  <tr>
                    <td class="orig">✗ ${c.original}</td>
                    <td class="corr">✓ ${c.corrected}</td>
                    <td class="expl">${c.explanation}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : ''}

        ${improved ? `
          <div class="eval-improved-box">
            <strong>Polierte B2/C1-Musterfassung:</strong>
            <p>„${improved}“</p>
          </div>
        ` : ''}
      </div>
    `;
  }

  async submitTransformation(id, direction, inputId, outputId) {
    const input = document.getElementById(inputId);
    const output = document.getElementById(outputId);
    if (!input || !output) return;

    const userText = input.value.trim();
    if (!userText) {
      output.innerHTML = `<div class="alert warning">Bitte tragen Sie Ihre Umformung ein.</div>`;
      return;
    }

    try {
      const res = await fetch('/api/panini/evaluate-transformation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, direction, user_text: userText })
      });
      const data = await res.json();
      output.innerHTML = `
        <div class="eval-card ${data.passed ? 'pass' : 'fail'}">
          <div class="eval-top-bar">
            <span>Score: ${data.score} / 10</span>
            <span>${data.passed ? '✓ Erfolgreich transformiert' : 'Noch Optimierungsbedarf'}</span>
          </div>
          <p>${data.feedback}</p>
          <div class="target-box">
            <strong>Offizieller Mustersatz:</strong>
            <p>„${data.target_model}“</p>
          </div>
        </div>
      `;
      await this.refreshProgress();
    } catch (err) {
      output.innerHTML = `<div class="alert danger">Fehler: ${err.message}</div>`;
    }
  }

  revealTransformation(id, outputId) {
    const output = document.getElementById(outputId);
    const item = this.transformations.find(t => t.id === id);
    if (!output || !item) return;

    output.innerHTML = `
      <div class="eval-card info">
        <p><strong>Schlicht (Verbalstil):</strong> „${item.schlicht}“</p>
        <p><strong>Gehoben (Nominalstil):</strong> „${item.gehoben}“</p>
      </div>
    `;
  }

  async submitErrorHunt(id, corrInputId, sutraInputId, outputId) {
    const corrIn = document.getElementById(corrInputId);
    const sutraIn = document.getElementById(sutraInputId);
    const output = document.getElementById(outputId);
    if (!corrIn || !output) return;

    const userCorrection = corrIn.value.trim();
    const sutraIdentified = sutraIn ? sutraIn.value.trim() : null;

    if (!userCorrection) {
      output.innerHTML = `<div class="alert warning">Bitte Korrektur eingeben.</div>`;
      return;
    }

    try {
      const res = await fetch('/api/panini/evaluate-error-hunt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, user_correction: userCorrection, sutra_identified: sutraIdentified })
      });
      const data = await res.json();
      output.innerHTML = `
        <div class="eval-card ${data.passed ? 'pass' : 'fail'}">
          <div class="eval-top-bar">
            <span>Punkte: ${data.score} / 10</span>
            <span>Sūtra ${data.sutra_identified_correctly ? '✓ Richtig erkannt' : `(Erwartet: Sūtra ${data.expected_sutra_number})`}</span>
          </div>
          <p><strong>Offizielle Berichtigung:</strong> ✓ „${data.official_correction}“</p>
          ${data.explanation ? `<p><em>${data.explanation}</em></p>` : ''}
        </div>
      `;
      await this.refreshProgress();
    } catch (err) {
      output.innerHTML = `<div class="alert danger">Fehler: ${err.message}</div>`;
    }
  }

  revealErrorHunt(id, outputId) {
    const output = document.getElementById(outputId);
    const item = this.errorHuntItems.find(t => t.id === id);
    if (!output || !item) return;

    output.innerHTML = `
      <div class="eval-card info">
        <p><strong>Berichtigung:</strong> ✓ „${item.correct}“</p>
        <p><strong>Verletztes Sūtra:</strong> Sūtra ${item.sutra_number}</p>
        ${item.explanation ? `<p><em>${item.explanation}</em></p>` : ''}
      </div>
    `;
  }

  async toggleSutraMastered(sutraId) {
    try {
      await fetch('/api/panini/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'toggle_sutra_mastered', data: { sutra_id: sutraId } })
      });
      await this.refreshProgress();
      this.renderHeader();
      this.renderActiveSubView();
    } catch (err) {
      console.error('Error toggling sutra mastered:', err);
    }
  }

  async toggleChecklistItem(itemId, isChecked) {
    try {
      await fetch('/api/panini/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'update_checklist', data: { item_id: itemId, completed: isChecked } })
      });
      await this.refreshProgress();
    } catch (err) {
      console.error('Error updating checklist:', err);
    }
  }

  async advanceDay() {
    try {
      await fetch('/api/panini/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'advance_day' })
      });
      await this.loadAllData();
      this.renderHeader();
      this.renderActiveSubView();
    } catch (err) {
      console.error('Error advancing day:', err);
    }
  }

  async jumpToWeek(weekNum) {
    try {
      await fetch('/api/panini/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'set_week', data: { week: weekNum } })
      });
      this.currentSubView = 'today';
      await this.loadAllData();
      this.renderHeader();
      this.renderSubViewNav();
      this.renderActiveSubView();
    } catch (err) {
      console.error('Error jumping week:', err);
    }
  }

  async refreshProgress() {
    try {
      const [progRes, overRes] = await Promise.all([
        fetch('/api/panini/progress').then(r => r.json()),
        fetch('/api/panini/overview').then(r => r.json()),
      ]);
      this.progress = progRes;
      this.overview = overRes;
      this.renderHeader();
    } catch (err) {
      console.error('Failed to refresh progress:', err);
    }
  }

  isSutraMastered(sutraId) {
    return (this.progress?.sutras_mastered || []).includes(sutraId);
  }

  viewSutraInModal(sutraId) {
    this.currentSubView = 'sutras';
    this.renderSubViewNav();
    this.renderActiveSubView();
    setTimeout(() => {
      const card = document.getElementById(`card_${sutraId}`);
      if (card) {
        card.classList.add('open');
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  }

  openExamSimulatorWithTopic(topicTitle) {
    const tabExam = document.getElementById('tabExamSimulator');
    if (tabExam) tabExam.click();
  }
}

// Global initialization
window.addEventListener('DOMContentLoaded', () => {
  window.paniniTrainer = new PaniniTrainer();
});

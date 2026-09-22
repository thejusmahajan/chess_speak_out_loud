"""
Goethe-Zertifikat B2 Exam Modules & Sample Data.
Includes authentic B2 tasks for Lesen, Hören, Schreiben, and Sprechen.
"""

EXAM_CONFIG = {
    "title": "Goethe-Zertifikat B2 Prüfungssimulator",
    "version": "1.0.0",
    "official_pass_percentage": 60.0,
    "modules": [
        {
            "id": "lesen",
            "name": "Lesen (Reading)",
            "official_duration_seconds": 65 * 60,  # 65 min
            "sprint_duration_seconds": 3 * 60,      # 3 min test
            "max_points": 30,
            "description": "Leseverstehen: Verstehen von authentischen Texten aus Zeitungen, Berichten und Fachzeitschriften.",
        },
        {
            "id": "hoeren",
            "name": "Hören (Listening)",
            "official_duration_seconds": 40 * 60,  # ~40 min
            "sprint_duration_seconds": 3 * 60,      # 3 min test
            "max_points": 30,
            "max_playbacks": 2,
            "description": "Hörverstehen: Verstehen von Gesprächen, Radiointerviews und Vorträgen zu aktuellen Themen.",
        },
        {
            "id": "schreiben",
            "name": "Schreiben (Writing)",
            "official_duration_seconds": 75 * 60,  # 75 min
            "sprint_duration_seconds": 5 * 60,      # 5 min test
            "max_points": 100,
            "target_words": 150,
            "description": "Schriftlicher Ausdruck: Verfassen eines Diskussionsbeitrags für ein Internetforum.",
        },
        {
            "id": "sprechen",
            "name": "Sprechen (Speaking)",
            "official_duration_seconds": 15 * 60,  # 15 min
            "sprint_duration_seconds": 3 * 60,      # 3 min test
            "max_points": 30,
            "target_duration_seconds": 120,        # 2 minutes of speech
            "description": "Mündlicher Ausdruck: Halten einer strukturierten Kurzpräsentation zu einem aktuellen Thema.",
        },
    ],
}

# Module Content: 1 Barebone Question for each of the 4 modules
MODULE_CONTENT = {
    "lesen": {
        "title": "Teil 1: Zeitungsartikel – Die Viertagewoche: Ein Modell mit Zukunft?",
        "instruction": "Lesen Sie den folgenden Text. Wählen Sie bei der folgenden Aufgabe die richtige Lösung (A, B, C oder D).",
        "text": """Immer mehr europäische Unternehmen erproben derzeit alternative Arbeitszeitmodelle, allen voran die sogenannte Viertagewoche bei vollem Lohnausgleich nach dem 100-80-100-Prinzip: 100 Prozent der Leistung in 80 Prozent der Zeit bei 100 Prozent Gehalt. Befürworter betonen die spürbare Steigerung des Wohlbefindens der Mitarbeiter und eine sinkende Zahl von Krankentagen. Eine britische Pilotstudie mit über 60 Firmen ergab, dass die Produktivität in den meisten Betrieben trotz reduzierter Stunden stabil blieb oder sogar leicht anstieg.

Kritiker aus Wirtschaft und Industrie verweisen jedoch auf die branchenspezifischen Grenzen dieses Modells. Während Angestellte im Dienstleistungssektor oder in der IT durch konzentrierteres Arbeiten und die Automatisierung von Routineprozessen dieselbe Arbeitsmenge in vier Tagen bewältigen können, stößt das Konzept in Branchen mit kontinuierlicher Präsenzpflicht – wie etwa in der Pflege, im Handwerk oder in der Gastronomie – an harte personelle Grenzen. Ein flächendeckender freier Tag würde hier zwangsläufig zu gravierenden Engpässen oder untragbaren Mehrkosten durch zusätzliches Personal führen.

Ein weiterer Aspekt, der in der Debatte häufig übersehen wird, ist die potenzielle Arbeitsverdichtung. Wenn Beschäftigte dieselbe Arbeitslast in kürzerer Zeit bewältigen müssen, kann dies paradoxerweise zu erhöhtem Leistungsdruck und Stress führen, anstatt zur erhofften Erholung. Die Viertagewoche erfordert daher zwingend eine tiefgreifende Reform interner Abläufe, wie die drastische Reduktion ineffizienter Besprechungen und eine klare Priorisierung der Aufgaben.""",
        "question": {
            "id": "lesen_q1",
            "prompt": "Welche zentrale Herausforderung bei der Einführung der Viertagewoche wird im Text hervorgehoben?",
            "options": [
                {
                    "id": "A",
                    "text": "Mitarbeiter sind grundsätzlich nicht bereit, bei vollem Lohnausgleich mehr Verantwortung zu übernehmen.",
                },
                {
                    "id": "B",
                    "text": "In Berufen mit ständiger Präsenzpflicht führt das Modell ohne zusätzliches Personal zu personellen Engpässen.",
                },
                {
                    "id": "C",
                    "text": "Studien zeigen, dass die Produktivität in IT-Unternehmen bei reduzierter Arbeitszeit sofort abfällt.",
                },
                {
                    "id": "D",
                    "text": "Die Gehälter müssen proportional zur verkürzten Arbeitszeit um mindestens 20 Prozent gekürzt werden.",
                },
            ],
            "correct_option": "B",
            "explanation": "Im zweiten Absatz wird ausdrücklich betont, dass in Branchen mit kontinuierlicher Präsenzpflicht (Pflege, Gastronomie) das Konzept an harte personelle Grenzen stößt und ohne zusätzliche Kräfte zu gravierenden Engpässen führt.",
        },
    },
    "hoeren": {
        "title": "Teil 1: Radiobericht – Digitale Erreichbarkeit im Feierabend",
        "instruction": "Sie hören einen kurzen Expertenbericht im Radio. Sie hören den Text zweimal. Wählen Sie danach die richtige Lösung (A, B oder C).",
        "audio_url": "/content/audio/hoeren_sample.mp3",
        "transcript_preview": """Moderator: 'Willkommen bei Campus & Karriere. Immer mehr Arbeitnehmer klagen über das Phänomen der ständigen Erreichbarkeit. Dienstliche E-Mails am Sonntagabend oder Nachrichten in Messenger-Gruppen nach Feierabend sind für viele Normalität geworden. Wir sprechen dazu mit der Arbeitspsychologin Dr. Sabine Becker. Frau Dr. Becker, wie schädlich ist dieser Trend wirklich?'

Dr. Becker: 'Nun, das eigentliche Problem ist nicht einmal die Zeit, die man mit dem Beantworten einer kurzen E-Mail verbringt. Es ist vielmehr die sogenannte antizipatorische Erschöpfung: Das ständige innerliche Bereithalten verhindert, dass der Parasympathikus – also unser Erholungsnervensystem – aktiv wird. Wer ständig damit rechnet, angerufen zu werden, bleibt auch auf dem Sofa im Alarmzustand. Für eine echte Regeneration ist eine klare psychologische Trennung zwischen Arbeitszeit und Freizeit unabdingbar. Unternehmen, die hier verbindliche Ruhezeiten festlegen, verzeichnen langfristig nachweislich weniger Burnout-Fälle.'""",
        "question": {
            "id": "hoeren_q1",
            "prompt": "Was bezeichnet Dr. Becker als die primäre Ursache für Erschöpfung durch ständige Erreichbarkeit?",
            "options": [
                {
                    "id": "A",
                    "text": "Die rein zeitliche Dauer, die das Verfassen dienstlicher Antworten in Anspruch nimmt.",
                },
                {
                    "id": "B",
                    "text": "Die dauerhafte innere Erwartungshaltung und Anspannung, die die Erholungsphase verhindert.",
                },
                {
                    "id": "C",
                    "text": "Die schlechte technische Ausstattung privater Smartphones der Mitarbeiter.",
                },
            ],
            "correct_option": "B",
            "explanation": "Dr. Becker erklärt, dass nicht die Zeit für die Antwort das Problem ist, sondern die 'antizipatorische Erschöpfung' – das ständige innere Bereithalten im Alarmzustand, wodurch keine echte Erholung eintritt.",
        },
    },
    "schreiben": {
        "title": "Teil 1: Diskussionsbeitrag in einem Forum – Plastikfreie Verpackungen",
        "instruction": "Schreiben Sie einen zusammenhängenden Text für ein Online-Gästebuch / Diskussionsforum. Verfassen Sie ca. 150 Wörter. Gehen Sie auf alle vier Leitpunkte ein!",
        "prompt": """In einem Internetforum diskutieren Menschen über das Thema:
"Verpackungsfreies Einkaufen: Brauchen wir Supermärkte ohne Plastik?"

Schreiben Sie einen Beitrag für dieses Forum:
1. Äußern Sie Ihre Meinung zu unverpackten Lebensmitteln und plastikfreien Supermärkten.
2. Nennen Sie Gründe, warum Plastikverpackungen im heutigen Handel immer noch so weit verbreitet sind.
3. Nennen Sie andere Möglichkeiten, wie Verbraucher im täglichen Leben Plastikmüll reduzieren können.
4. Beschreiben Sie Vor- oder Nachteile dieser Alternativen.

Achten Sie auf:
- Einen logischen Aufbau mit Einleitung, Hauptteil und Schluss
- Vielfältigen Wortschatz und B2-Konnektoren (z.B. meiner Ansicht nach, zwar... aber, infolgedessen, darüber hinaus)
- Korrekte Grammatik und Rechtschreibung
- Richtwert: ca. 150 Wörter.""",
        "guidelines": [
            "Eigene Meinung zu plastikfreien Supermärkten äußern",
            "Gründe für die weite Verbreitung von Plastikverpackungen nennen",
            "Andere konkrete Möglichkeiten zur Müllvermeidung im Alltag anführen",
            "Vor- oder Nachteile dieser Alternativen abwägen",
        ],
    },
    "sprechen": {
        "title": "Teil 1: Ein Thema präsentieren (Kurzvortrag)",
        "instruction": "Sie sollen Ihren Mitstudierenden / der Prüfungskommission ein Thema präsentieren. Sprechen Sie frei ca. 2 bis 3 Minuten. Nutzen Sie die Leitpunkte zur Gliederung.",
        "prompt": """Thema: "Sollten Universitätsvorlesungen dauerhaft online stattfinden?"

Strukturieren Sie Ihre Präsentation anhand der folgenden fünf Schritte:
1. **Einleitung**: Stellen Sie das Thema kurz vor und erklären Sie dessen Relevanz.
2. **Eigene Erfahrung**: Berichten Sie von Ihren persönlichen Erfahrungen mit Online-Unterricht oder digitalen Meetings.
3. **Situation im Heimatland**: Beschreiben Sie, wie Online-Lernen an Universitäten in Ihrem Heimatland gehandhabt wird.
4. **Vor- und Nachteile**: Nennen Sie wesentliche Argumente dafür und dagegen (z.B. zeitliche Flexibilität vs. Mangel an sozialem Austausch).
5. **Fazit / Eigene Meinung**: Ziehen Sie eine Schlussfolgerung und begründen Sie Ihren persönlichen Standpunkt.

Sprechzeit: ca. 2 Minuten (mindestens 60 Sekunden, maximal 3 Minuten).""",
        "guidelines": [
            "1. Einleitung & Thema vorstellen",
            "2. Eigene Erfahrung schildern",
            "3. Situation im Heimatland beschreiben",
            "4. Vor- und Nachteile abwägen",
            "5. Eigenes Fazit & Ausblick formulieren",
        ],
    },
}

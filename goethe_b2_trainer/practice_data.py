"""
Goethe-Zertifikat B2 — Practice Trainer Data & Validation Module.
Contains authentic CEFR B2 exercises for:
1. Simple (Einfach): 1-word blank, match the following, odd one out, incorrectly spelled word.
2. Intermediate (Mittelstufe): 2+ words blank, match with multiple correct, jumbled words to sentence, find simple grammar mistake.
3. Difficult (Fortgeschritten): answer questions correctly, write the next sentence in full.
"""

from typing import Dict, Any, List

PRACTICE_TIERS = [
    {
        "id": "simple",
        "title": "Stufe 1: Einfach (Grundlagen B2)",
        "badge": "Einfach",
        "color": "emerald",
        "description": "Feste Präpositionen, Nomen-Verb-Verbindungen, Wortfelder & Rechtschreibung.",
        "exercise_count": 4,
    },
    {
        "id": "intermediate",
        "title": "Stufe 2: Mittelstufe (Satzgefüge & Rektion)",
        "badge": "Mittelstufe",
        "color": "gold",
        "description": "Zweiteilige Konnektoren, Mehrfachrektion, Schüttelsätze & Fehleridentifikation.",
        "exercise_count": 4,
    },
    {
        "id": "difficult",
        "title": "Stufe 3: Fortgeschritten (Produktion & Kohärenz)",
        "badge": "Fortgeschritten",
        "color": "rose",
        "description": "Präzise Textbeantwortung & stilsichere Satzfortführung mit KI-Bewertung.",
        "exercise_count": 2,
    },
]

PRACTICE_QUESTIONS: Dict[str, Dict[str, Any]] = {
    # --------------------------------------------------------------------------
    # TIER 1: SIMPLE (EINFACH)
    # --------------------------------------------------------------------------
    "q1_simple_fill_single": {
        "id": "q1_simple_fill_single",
        "tier": "simple",
        "type": "fill_blank_single",
        "title": "1. Lückentext: Einzelwort einsetzen",
        "instruction": "Ergänzen Sie die passende Präposition in der Lücke. Achten Sie auf die feste Rektion des Verbs.",
        "context_sentence": "Viele Berufstätige klagen darüber, dass sie Beruf und Familie kaum noch miteinander vereinbaren können. Arbeitsmarkt-Experten weisen deshalb mit Nachdruck _____ die Notwendigkeit flexibler Arbeitszeitmodelle hin.",
        "target_label": "Fehlendes Wort (Präposition)",
        "accepted_answers": ["auf"],
        "hint": "Das Verb heißt 'hinweisen' und verlangt eine feste Präposition mit Akkusativ.",
        "explanation": "Richtig ist 'auf'. Die feste Nomen-Verb- bzw. Verb-Präposition-Verbindung lautet 'hinweisen auf + Akkusativ' (jemanden auf einen Umstand oder eine Notwendigkeit aufmerksam machen).",
        "cefr_focus": "Rektion der Verben (hinweisen auf + Akk)",
    },

    "q2_simple_match_following": {
        "id": "q2_simple_match_following",
        "tier": "simple",
        "type": "match_following",
        "title": "2. Zuordnungsübung: Nomen-Verb-Verbindungen",
        "instruction": "Ordnen Sie jedem Nomen das passende Funktionsverb zu, um eine korrekte B2-Nomen-Verb-Verbindung zu bilden.",
        "left_items": [
            {"id": "L1", "text": "eine Entscheidung"},
            {"id": "L2", "text": "zur Verfügung"},
            {"id": "L3", "text": "in Betracht"},
            {"id": "L4", "text": "Kritik"},
        ],
        "right_items": [
            {"id": "R1", "text": "treffen"},
            {"id": "R2", "text": "stellen"},
            {"id": "R3", "text": "ziehen"},
            {"id": "R4", "text": "üben (an)"},
        ],
        "correct_pairs": {
            "L1": "R1",  # eine Entscheidung treffen
            "L2": "R2",  # zur Verfügung stellen
            "L3": "R3",  # in Betracht ziehen
            "L4": "R4",  # Kritik üben an
        },
        "explanation": "Offizielle B2-Nomen-Verb-Verbindungen:\n• eine Entscheidung treffen (= sich entscheiden)\n• zur Verfügung stellen (= bereitstellen / anbieten)\n• in Betracht ziehen (= erwägen / berücksichtigen)\n• Kritik üben an (+ Dat.) (= kritisieren)",
        "cefr_focus": "Funktionsverbgefüge (Nomen-Verb-Verbindungen)",
    },

    "q3_simple_odd_one_out": {
        "id": "q3_simple_odd_one_out",
        "tier": "simple",
        "type": "odd_one_out",
        "title": "3. Unpassendes Wort: Welches Wort gehört nicht dazu?",
        "instruction": "Wählen Sie das Verb aus, das bedeutungsmäßig oder semantisch NICHT in diese Reihe passt.",
        "options": [
            {"id": "A", "word": "senken", "desc": "etwas reduzieren oder herabsetzen"},
            {"id": "B", "word": "drosseln", "desc": "eine Leistung oder Zufuhr vermindern / bremsen"},
            {"id": "C", "word": "verringern", "desc": "eine Menge oder Anzahl kleiner machen"},
            {"id": "D", "word": "steigern", "desc": "etwas vermehren, anheben oder verstärken"},
        ],
        "correct_option": "D",
        "explanation": "'steigern' ist das Antonym (Gegenteil). Die Verben 'senken', 'drosseln' und 'verringern' bedeuten alle 'weniger machen / reduzieren', während 'steigern' 'erhöhen / vergrößern' bedeutet.",
        "cefr_focus": "B2 Wortfeld Synonyme & Antonyme (Wirtschaft / Tendenzen)",
    },

    "q4_simple_incorrect_spelling": {
        "id": "q4_simple_incorrect_spelling",
        "tier": "simple",
        "type": "incorrect_spelling",
        "title": "4. Rechtschreibfehler: Falsch geschriebenes Wort finden",
        "instruction": "In welchem der vier hervorgehobenen B2-Substantive bzw. Wörter hat sich ein orthografischer Fehler eingeschlichen?",
        "options": [
            {"id": "A", "word": "der Rhythmus", "is_correct_spelling": True},
            {"id": "B", "word": "das Repertoir", "is_correct_spelling": False, "correct_spelling": "das Repertoire"},
            {"id": "C", "word": "der Widerstand", "is_correct_spelling": True},
            {"id": "D", "word": "endgültig", "is_correct_spelling": True},
        ],
        "correct_option": "B",
        "explanation": "B ist falsch geschrieben! Das aus dem Französischen entlehnte Bildungs- und Fachwort heißt im Deutschen 'das Repertoire' (mit Endung '-e'). 'Rhythmus' (mit rh und th), 'Widerstand' (mit einfachem i, da es von 'wider = gegen' kommt) und 'endgültig' (von 'Ende', mit d) sind korrekt.",
        "cefr_focus": "B2 Orthografie: Fremdwörter, Dehnungs-h & Präfixe (wider vs. wieder)",
    },

    # --------------------------------------------------------------------------
    # TIER 2: INTERMEDIATE (MITTELSTUFE)
    # --------------------------------------------------------------------------
    "q5_inter_fill_multi": {
        "id": "q5_inter_fill_multi",
        "tier": "intermediate",
        "type": "fill_blank_multi",
        "title": "5. Mehrfachlücke: Zweiteiligen Konnektor einsetzen",
        "instruction": "Setzen Sie den passenden zweiteiligen Doppelkonnektor ein, der eine aufzählende Ergänzung mit Steigerung ausdrückt.",
        "sentence_template": "Das neue Förderprogramm stärkt {blank1} die individuellen Fachkompetenzen der Beschäftigten, {blank2} verbessert es auch das Betriebsklima nachhaltig.",
        "blanks": [
            {
                "id": "blank1",
                "label": "Lücke 1 (z. B. 2 Wörter)",
                "accepted": ["nicht nur"],
            },
            {
                "id": "blank2",
                "label": "Lücke 2 (z. B. 2 Wörter)",
                "accepted": ["sondern auch", "sondern"],
            },
        ],
        "hint": "Gesucht ist das Doppel-Bindewort: 'nicht nur ... sondern auch'.",
        "explanation": "Richtig ist das Paar 'nicht nur ... sondern auch'. Dieser kopulative Doppelkonnektor verbindet zwei positive Aspekte und erfordert im zweiten Hauptsatz nach 'sondern' bzw. vor 'verbessert' entsprechende Inversion oder Normalstellung.",
        "cefr_focus": "Zweiteilige Konnektoren (Doppelkonnektoren B2)",
    },

    "q6_inter_match_multiple": {
        "id": "q6_inter_match_multiple",
        "tier": "intermediate",
        "type": "match_multiple",
        "title": "6. Mehrfachauswahl: Rektion von Verben mit 'an + Dativ'",
        "instruction": "Welche der folgenden Verben bilden eine feste Verbindung mit der Präposition 'an' und verlangen den DATIV (+ Dat.)? Wählen Sie alle zutreffenden Verben aus.",
        "options": [
            {"id": "A", "verb": "teilnehmen", "governs": "an + Dat.", "is_correct": True, "example": "an einer Konferenz teilnehmen"},
            {"id": "B", "verb": "zweifeln", "governs": "an + Dat.", "is_correct": True, "example": "an der Richtigkeit der Aussage zweifeln"},
            {"id": "C", "verb": "denken", "governs": "an + Akk.", "is_correct": False, "example": "an die Zukunft denken (Akkusativ!)"},
            {"id": "D", "verb": "leiden", "governs": "an + Dat.", "is_correct": True, "example": "an einer chronischen Krankheit leiden (Zustand = Dativ)"},
            {"id": "E", "verb": "sich erinnern", "governs": "an + Akk.", "is_correct": False, "example": "sich an den Vorfall erinnern (Akkusativ!)"},
        ],
        "correct_selection": ["A", "B", "D"],
        "explanation": "Korrekt sind A, B und D!\n• teilnehmen an + Dativ\n• zweifeln an + Dativ\n• leiden an + Dativ (bei Krankheiten; bei Missständen: leiden unter + Dat.)\n\nC und E verlangen hingegen den AKKUSATIV: 'denken an + Akk.' und 'sich erinnern an + Akk.'.",
        "cefr_focus": "Feste Präpositionen mit Dativ vs. Akkusativ",
    },

    "q7_inter_jumbled_sentence": {
        "id": "q7_inter_jumbled_sentence",
        "tier": "intermediate",
        "type": "jumbled_sentence",
        "title": "7. Schüttelsatz: Sinnvollen B2-Satz konstruieren",
        "instruction": "Bringen Sie die durcheinandergewürfelten Satzglieder in die korrekte grammatische Reihenfolge. Achten Sie auf Nebensatz-Wortstellung und die Inversion im nachfolgenden Hauptsatz.",
        "scrambled_tokens": [
            "kontinuierlich",
            "verzichten",
            "die",
            "Obwohl",
            "steigen,",
            "Preise",
            "meisten",
            "Verbraucher",
            "Bio-Produkte.",
            "hochwertige",
            "nicht",
            "auf"
        ],
        "target_sentence": "Obwohl die Preise kontinuierlich steigen, verzichten die meisten Verbraucher nicht auf hochwertige Bio-Produkte.",
        "acceptable_variants": [
            "Obwohl die Preise kontinuierlich steigen, verzichten die meisten Verbraucher nicht auf hochwertige Bio-Produkte.",
            "Verzichten die meisten Verbraucher nicht auf hochwertige Bio-Produkte, obwohl die Preise kontinuierlich steigen."
        ],
        "explanation": "Grammatikregel: In einem Konzessivsatz mit 'Obwohl' steht das finite Verb am Satzende ('steigen'). Wenn der Nebensatz voransteht, beginnt der anschließende Hauptsatz direkt mit dem finiten Verb ('verzichten'), gefolgt vom Subjekt ('die meisten Verbraucher') und der Negations- und Präpositionalergänzung ('nicht auf hochwertige Bio-Produkte').",
        "cefr_focus": "Satzbau, Verbletztstellung im Nebensatz & Inversion im Hauptsatz",
    },

    "q8_inter_find_mistake": {
        "id": "q8_inter_find_mistake",
        "tier": "intermediate",
        "type": "find_mistake",
        "title": "8. Fehlerkorrektur: Grammatikfehler im Satz identifizieren",
        "instruction": "Im folgenden Satz befindet sich genau ein grammatischer Fehler. Klicken Sie das fehlerhafte Wort an und geben Sie die korrekte Form ein.",
        "sentence_words": [
            {"index": 0, "word": "Die"},
            {"index": 1, "word": "Abteilungsleiterin,"},
            {"index": 2, "word": "dessen", "is_error": True, "correction": "deren"},
            {"index": 3, "word": "Vorschlag"},
            {"index": 4, "word": "von"},
            {"index": 5, "word": "allen"},
            {"index": 6, "word": "Kollegen"},
            {"index": 7, "word": "gelobt"},
            {"index": 8, "word": "wurde,"},
            {"index": 9, "word": "übernimmt"},
            {"index": 10, "word": "das"},
            {"index": 11, "word": "Großprojekt."},
        ],
        "error_word": "dessen",
        "correction": "deren",
        "explanation": "Fehler: 'dessen' ist das maskuline bzw. neutrale Genitiv-Relativpronomen. Da das Bezugswort jedoch feminin ist ('Die Abteilungsleiterin'), muss das feminine Relativpronomen im Genitiv verwendet werden: 'deren Vorschlag'.",
        "cefr_focus": "Genitiv-Relativsätze (dessen vs. deren)",
    },

    # --------------------------------------------------------------------------
    # TIER 3: DIFFICULT (FORTGESCHRITTEN)
    # --------------------------------------------------------------------------
    "q9_diff_answer_question": {
        "id": "q9_diff_answer_question",
        "tier": "difficult",
        "type": "answer_question",
        "title": "9. Textverständnis: Offene Frage präzise beantworten",
        "instruction": "Lesen Sie den Fachauszug zum Thema 'Jobsharing' und beantworten Sie die Frage in 1–2 vollständigen, grammatisch anspruchsvollen Sätzen.",
        "reading_passage": """In modernen Unternehmen gewinnt das Arbeitszeitmodell des 'Jobsharing' zunehmend an Beliebtheit. Dabei teilen sich zwei qualifizierte Fachkräfte eine Vollzeitstelle samt Führungsverantwortung. Während Befürworter die gegenseitige Ergänzung der Kompetenzen und eine signifikante Erhöhung der Arbeitszufriedenheit betonen, verweisen Arbeitspsychologen auf ernsthafte Herausforderungen: Das Modell erfordert einen kontinuierlichen und disziplinierten Kommunikationsaufwand. Verläuft die Übergabe unvollständig, drohen gravierende Informationsverluste und Verzögerungen bei operativen Entscheidungen.""",
        "question_prompt": "Welche wesentliche Herausforderung und welches daraus resultierende Risiko sehen Arbeitspsychologen beim Modell des 'Jobsharing'?",
        "evaluation_criteria": [
            "Nennung des hohen Kommunikations- bzw. Abstimmungsaufwands",
            "Nennung des Risikos von Informationsverlusten oder Verzögerungen bei Entscheidungen",
            "Grammatische Korrektheit auf B2-Niveau (korrekte Nebensätze, Passiv oder Nomen-Verb-Verbindungen)",
        ],
        "model_answer": "Arbeitspsychologen betonen, dass Jobsharing einen kontinuierlichen und zeitintensiven Kommunikationsaufwand erfordert. Sollte dieser Abstimmungsprozess lückenhaft sein, besteht das erhebliche Risiko von Informationsverlusten sowie verzögerten betrieblichen Entscheidungen.",
        "cefr_focus": "Schriftliche Synthese, Textanalyse & Formulierung von Kausalzusammenhängen",
    },

    "q10_diff_write_next_sentence": {
        "id": "q10_diff_write_next_sentence",
        "tier": "difficult",
        "type": "write_next_sentence",
        "title": "10. Satzfortführung: Vollständigen Folgesatz verfassen",
        "instruction": "Führen Sie den folgenden Satz mit einem grammatisch komplexen, inhaltlich schlüssigen Folgesatz fort. Nutzen Sie dazu ein passendes adversatives oder konzessives Gegenstück (z. B. 'Andererseits...', 'Allerdings...', 'Demgegenüber...').",
        "lead_in_sentence": "Einerseits ermöglicht die Einführung flexibler Gleitzeitmodelle den Beschäftigten eine spürbar bessere Vereinbarkeit von Familie und Beruf,",
        "question_prompt": "Schreiben Sie den nächsten Satz (oder den zweiten Satzteil), der die Gegenperspektive / Schattenseiten (z. B. Gefahr der Selbstausbeutung, Verschwimmen der Grenzen zwischen Freizeit und Arbeit) stilsicher auf B2-Niveau darstellt.",
        "evaluation_criteria": [
            "Verwendung eines passenden B2-Konnektors (z. B. 'andererseits', 'auf der anderen Seite', 'jedoch', 'allerdings')",
            "Inhaltliche Passung (Schattenseiten wie Überstunden, Erreichbarkeitsdruck, Entgrenzung)",
            "Korrekte Verbstellung (Hauptsatz-Inversion nach 'Andererseits' oder Nebensatzstruktur)",
        ],
        "model_answer": "Andererseits birgt diese Flexibilität die Gefahr einer Entgrenzung der Arbeitszeit, da viele Arbeitnehmer dazu neigen, auch am Wochenende dienstliche Aufgaben zu erledigen.",
        "cefr_focus": "Textkohärenz, zweiteilige Argumentation & Satzverknüpfung",
    },
}


def sanitize_for_client(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strips raw answer keys for the client where appropriate, while preserving
    layout, options, and tokens needed for interactive widgets.
    """
    sanitized = {k: v for k, v in question_data.items() if k not in ["accepted_answers", "correct_pairs", "correct_selection"]}
    
    # If match_multiple, remove is_correct flag from options
    if question_data.get("type") == "match_multiple" and "options" in sanitized:
        sanitized["options"] = [
            {"id": opt["id"], "verb": opt["verb"], "example": opt.get("example", "")}
            for opt in question_data["options"]
        ]
        
    # If incorrect_spelling, remove is_correct_spelling / correct_spelling
    if question_data.get("type") == "incorrect_spelling" and "options" in sanitized:
        sanitized["options"] = [
            {"id": opt["id"], "word": opt["word"]}
            for opt in question_data["options"]
        ]
        
    # If find_mistake, remove is_error and correction from words
    if question_data.get("type") == "find_mistake" and "sentence_words" in sanitized:
        sanitized["sentence_words"] = [
            {"index": w["index"], "word": w["word"]}
            for w in question_data["sentence_words"]
        ]
        
    return sanitized


def evaluate_objective_question(question_id: str, submission: Any) -> Dict[str, Any]:
    """
    Evaluates submissions for Tier 1 and Tier 2 objective questions.
    Returns: { "is_correct": bool, "score": int, "max_score": 10, "feedback": str, "explanation": str }
    """
    q = PRACTICE_QUESTIONS.get(question_id)
    if not q:
        return {"is_correct": False, "score": 0, "max_score": 10, "feedback": "Frage nicht gefunden."}

    q_type = q.get("type")

    # 1. Fill blank single
    if q_type == "fill_blank_single":
        user_val = str(submission or "").strip().lower()
        accepted = [ans.lower() for ans in q["accepted_answers"]]
        is_correct = user_val in accepted
        return {
            "is_correct": is_correct,
            "score": 10 if is_correct else 0,
            "max_score": 10,
            "user_answer": user_val,
            "correct_answer": q["accepted_answers"][0],
            "feedback": "Hervorragend! Die Präposition ist vollkommen korrekt." if is_correct else f"Leider nicht ganz richtig. Die gesuchte Präposition lautet '{q['accepted_answers'][0]}'.",
            "explanation": q["explanation"],
        }

    # 2. Match following
    elif q_type == "match_following":
        # submission expected: { "L1": "R1", "L2": "R2", ... }
        user_pairs = submission if isinstance(submission, dict) else {}
        correct_pairs = q["correct_pairs"]
        num_correct = sum(1 for l, r in user_pairs.items() if correct_pairs.get(l) == r)
        total_pairs = len(correct_pairs)
        is_all_correct = (num_correct == total_pairs)
        score = int(round((num_correct / total_pairs) * 10))
        return {
            "is_correct": is_all_correct,
            "score": score,
            "max_score": 10,
            "matches_correct": num_correct,
            "total_matches": total_pairs,
            "correct_pairs": correct_pairs,
            "feedback": "Perfekt! Alle 4 Nomen-Verb-Verbindungen wurden korrekt zugeordnet." if is_all_correct else f"{num_correct} von {total_pairs} Paaren richtig zugeordnet.",
            "explanation": q["explanation"],
        }

    # 3. Odd one out
    elif q_type == "odd_one_out":
        user_choice = str(submission or "").strip().upper()
        target = q["correct_option"]
        is_correct = (user_choice == target)
        return {
            "is_correct": is_correct,
            "score": 10 if is_correct else 0,
            "max_score": 10,
            "user_answer": user_choice,
            "correct_answer": target,
            "feedback": "Ausgezeichnet! Sie haben das Antonym treffsicher erkannt." if is_correct else f"Nicht ganz. Richtig wäre Option {target} ('{next(o['word'] for o in q['options'] if o['id'] == target)}').",
            "explanation": q["explanation"],
        }

    # 4. Incorrect spelling
    elif q_type == "incorrect_spelling":
        user_choice = str(submission or "").strip().upper()
        target = q["correct_option"]
        is_correct = (user_choice == target)
        return {
            "is_correct": is_correct,
            "score": 10 if is_correct else 0,
            "max_score": 10,
            "user_answer": user_choice,
            "correct_answer": target,
            "feedback": "Sehr gut beobachtet! Das Wort war fehlerhaft geschrieben." if is_correct else f"Leider falsch. Das fehlerhafte Wort war Option {target}.",
            "explanation": q["explanation"],
        }

    # 5. Fill blank multi
    elif q_type == "fill_blank_multi":
        # submission: { "blank1": "nicht nur", "blank2": "sondern auch" }
        user_dict = submission if isinstance(submission, dict) else {}
        b1_user = str(user_dict.get("blank1", "")).strip().lower()
        b2_user = str(user_dict.get("blank2", "")).strip().lower()
        
        b1_ok = any(b1_user == acc.lower() for acc in q["blanks"][0]["accepted"])
        b2_ok = any(b2_user == acc.lower() for acc in q["blanks"][1]["accepted"])
        
        is_all_correct = b1_ok and b2_ok
        score = 10 if is_all_correct else (5 if (b1_ok or b2_ok) else 0)
        return {
            "is_correct": is_all_correct,
            "score": score,
            "max_score": 10,
            "feedback": "Großartig! Der zweiteilige Konnektor wurde perfekt eingesetzt." if is_all_correct else "Mindestens eine Lücke weicht ab. Sehen Sie sich die Musterlösung an.",
            "correct_answers": {
                "blank1": q["blanks"][0]["accepted"][0],
                "blank2": q["blanks"][1]["accepted"][0],
            },
            "explanation": q["explanation"],
        }

    # 6. Match multiple (multi select)
    elif q_type == "match_multiple":
        # submission: list of selected IDs, e.g. ["A", "B", "D"]
        user_list = [str(x).strip().upper() for x in (submission if isinstance(submission, list) else [])]
        correct_set = set(q["correct_selection"])
        user_set = set(user_list)
        is_exact = (user_set == correct_set)
        
        # Calculate partial score
        correct_hits = len(user_set.intersection(correct_set))
        false_hits = len(user_set - correct_set)
        score = max(0, int(round((correct_hits / len(correct_set)) * 10 - false_hits * 3)))
        
        return {
            "is_correct": is_exact,
            "score": 10 if is_exact else score,
            "max_score": 10,
            "correct_selection": q["correct_selection"],
            "feedback": "Hervorragend! Sie beherrschen die Rektion mit Dativ und Akkusativ exakt." if is_exact else "Nicht alle Verben mit 'an + Dativ' wurden exakt ausgewählt.",
            "explanation": q["explanation"],
        }

    # 7. Jumbled sentence
    elif q_type == "jumbled_sentence":
        # submission: list of tokens or full reconstructed string
        if isinstance(submission, list):
            assembled = " ".join(submission).strip()
        else:
            assembled = str(submission or "").strip()
            
        # Normalize punctuation spacing for comparison
        norm_user = " ".join(assembled.split()).lower()
        norm_target = " ".join(q["target_sentence"].split()).lower()
        
        is_exact = (norm_user == norm_target)
        if not is_exact and "acceptable_variants" in q:
            for variant in q["acceptable_variants"]:
                if norm_user == " ".join(variant.split()).lower():
                    is_exact = True
                    break

        return {
            "is_correct": is_exact,
            "score": 10 if is_exact else 0,
            "max_score": 10,
            "assembled_sentence": assembled,
            "target_sentence": q["target_sentence"],
            "feedback": "Ausgezeichnet! Satzbau, Verbstellung und Inversion stimmen exakt." if is_exact else "Die Satzstellung weicht ab. Achten Sie auf die Verbletztstellung im Nebensatz und die Hauptsatz-Inversion.",
            "explanation": q["explanation"],
        }

    # 8. Find mistake
    elif q_type == "find_mistake":
        # submission: { "selected_word": "dessen", "correction": "deren" }
        user_dict = submission if isinstance(submission, dict) else {}
        selected_word = str(user_dict.get("selected_word", "")).strip().lower()
        user_corr = str(user_dict.get("correction", "")).strip().lower()
        
        target_error = q["error_word"].lower()
        target_corr = q["correction"].lower()
        
        word_spotted = (selected_word == target_error)
        corr_ok = (user_corr == target_corr)
        
        is_correct = word_spotted and corr_ok
        score = 10 if is_correct else (5 if word_spotted else 0)
        return {
            "is_correct": is_correct,
            "score": score,
            "max_score": 10,
            "target_error": q["error_word"],
            "target_correction": q["correction"],
            "feedback": "Hervorragend! Sie haben den Genitiv-Relativfehler erkannt und präzise korrigiert." if is_correct else (
                "Sie haben das fehlerhafte Wort gefunden, die Korrektur weicht jedoch ab." if word_spotted else "Das fehlerhafte Wort wurde nicht richtig identifiziert."
            ),
            "explanation": q["explanation"],
        }

    return {"is_correct": False, "score": 0, "max_score": 10, "feedback": "Unbekannter Fragentyp."}

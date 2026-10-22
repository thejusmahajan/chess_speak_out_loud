"""
Pāṇini-Kanon B1 → B2 — Structured Data Module.

Encodes all content from "Der Pāṇini-Kanon B1 → B2 – berichtigte und erweiterte Fassung"
into structured Python data for the B2 trainer application.

Source: goethe_b2_trainer/knowledge/Der Pāṇini-Kanon B1 → B2 – berichtigte und erweiterte Fassung.md
Author credit: @Thejus, Sep 25, 2026
"""

from typing import Dict, Any, List

# =============================================================================
# TEIL A – SŪTRAPĀṬHA: 22 Grammar Rules
# =============================================================================

ADHYAYAS = [
    {"id": "I", "title": "Kāraka: Valenz und Rektion", "subtitle": "Das Verb bestimmt, welche Kasus und Präpositionen um es herum stehen."},
    {"id": "II", "title": "Vibhakti: die Endungen", "subtitle": "Adjektivendungen, n-Deklination und Genitiv."},
    {"id": "III", "title": "Vākya: der Satzbau", "subtitle": "Pronomen stehen vorn, Konnektoren bestimmen die Verbposition."},
    {"id": "IV", "title": "Karmaṇi und bhāve: Passiv und Passiversatz", "subtitle": "Vorgangspassiv, Zustandspassiv und modale Ersatzformen."},
    {"id": "V", "title": "Viśeṣaṇa: Attribute", "subtitle": "Partizipien und Relativsätze verdichten Information am Nomen."},
    {"id": "VI", "title": "Lakāra: Modus und Modalität", "subtitle": "Konjunktiv II, Konjunktiv I und Vermutungen."},
    {"id": "VII", "title": "Samāsa und Liṅga: Wortbildung und Nominalstil", "subtitle": "Komposita, Genus und die Umformung zwischen Verbal- und Nominalstil."},
    {"id": "VIII", "title": "Tumun: Infinitivsätze", "subtitle": "Infinitiv mit zu, um...zu, ohne...zu, (an)statt...zu."},
    {"id": "IX", "title": "Vāk: die gesprochene Sprache", "subtitle": "Modalpartikeln machen gesprochenes Deutsch natürlich."},
]

SUTRAS: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # ADHYĀYA I – Kāraka: Valenz und Rektion
    # =========================================================================
    "sutra_01": {
        "id": "sutra_01",
        "number": 1,
        "adhyaya": "I",
        "title": "Das Präpositionalobjekt",
        "rule": "Präposition und Kasus gehören zum Verb, Adjektiv oder Nomen und werden mit ihm als Einheit gelernt.",
        "examples_correct": [
            "„Niemand zweifelt an der Notwendigkeit dieser Schritte, sofern die Beschäftigten nicht unverhältnismäßig unter den Sparmaßnahmen leiden.“ (Vorlage III.2)",
            "„Sie interessiert sich für maschinelles Lernen und ist mit ihrer Stelle sehr zufrieden.“",
        ],
        "examples_wrong": [
            {"wrong": "Ich bin interessiert in Datenanalyse.", "correct": "Ich interessiere mich für Datenanalyse. / Ich bin an Datenanalyse interessiert."},
            {"wrong": "Ich warte für eine Antwort.", "correct": "Ich warte auf eine Antwort."},
        ],
        "explanation": "Die Präposition lässt sich selten logisch ableiten und weicht oft vom Englischen ab. Dasselbe Verb ändert mit der Präposition seine Bedeutung: bestehen aus + D (sich zusammensetzen), bestehen auf + D (insistieren), bestehen in + D (Das Problem besteht darin, dass …). Ebenso unterscheiden sich leiden unter + D (Belastungen, Umstände) und leiden an + D (Krankheiten).\n\nBei Wechselpräpositionen legt das Verb den Kasus fest. Faustregeln: über → fast immer A (sprechen über); vor und unter → D (warnen vor, leiden unter); auf → meist A (warten auf), aber D bei bestehen auf, beruhen auf, basieren auf. Bei an und in hilft keine Regel: denken an + A, aber zweifeln an + D.",
        "exercise_prompt": "Täglich fünf Einträge aus Liste 1 (Teil B). Zu jedem zwei eigene Sätze bilden, einen über eine Sache und einen über eine Person, und beide laut sprechen. Dann die passende Frage stellen (Sūtra 2).",
        "weeks": [1, 2],
        "lists_referenced": ["list_1"],
    },
    "sutra_02": {
        "id": "sutra_02",
        "number": 2,
        "adhyaya": "I",
        "title": "Pronominaladverb und Korrelat",
        "rule": "Für Sachen steht da(r)- + Präposition, für Fragen nach Sachen wo(r)- + Präposition, für Personen Präposition + Pronomen. Folgt ein Nebensatz oder Infinitiv, kündigt da(r)- ihn im Hauptsatz an (Korrelat).",
        "examples_correct": [
            "„Wirtschaftsexperten weisen mit Nachdruck darauf hin, dass der künftige Erfolg eines Betriebs maßgeblich von dessen Innovationsbereitschaft abhängt.“ (Vorlage III.1)",
            "„Worauf kommt es bei dieser Stelle an? – Es kommt vor allem darauf an, ob man komplexe Daten verständlich erklären kann.“",
            "„Ich freue mich darauf, Sie persönlich kennenzulernen.“",
            "„Mit wem arbeiten Sie zusammen? – Mit Frau Weber; mit ihr arbeite ich seit Jahren zusammen.“",
        ],
        "examples_wrong": [
            {"wrong": "Ich denke oft an es.", "correct": "Ich denke oft daran."},
            {"wrong": "Das ist meine Kollegin; ich arbeite gern damit.", "correct": "… ich arbeite gern mit ihr."},
            {"wrong": "Mit was arbeiten Sie?", "correct": "Womit arbeiten Sie? (mit was ist umgangssprachlich)"},
        ],
        "explanation": "Beginnt die Präposition mit einem Vokal, wird -r- eingeschoben: darauf, daran, worüber, aber damit, wovon. Das Korrelat ist bei manchen Verben nötig (darauf hinweisen, darauf ankommen, darauf achten, darauf bestehen), bei anderen kann es fehlen (Ich freue mich [darüber], dass …). Bei trennbaren Verben steht der Verbzusatz am Ende des Hauptsatzes, direkt vor dem Komma: weisen … darauf hin, dass …\n\nZu III.1: Dessen und deren zeigen bevorzugt auf das zuletzt genannte passende Nomen, das nicht Subjekt ist, hier eines Betriebs. Possessivpronomen (sein, ihr) zeigen bevorzugt auf das Subjekt. Von seiner Innovationsbereitschaft wäre hier ebenfalls verständlich; dessen macht den Bezug nur eindeutiger.",
        "exercise_prompt": "Zehn Verben aus Liste 1, je drei Formen: Frage (Worauf …?), kurze Antwort (… darauf.), Satz mit Korrelat (… darauf, dass … oder … darauf, … zu …).",
        "weeks": [1, 2],
        "lists_referenced": ["list_1"],
    },
    "sutra_03": {
        "id": "sutra_03",
        "number": 3,
        "adhyaya": "I",
        "title": "Nomen-Verb-Verbindungen",
        "rule": "In einer Nomen-Verb-Verbindung trägt das Nomen die Bedeutung und das Verb die Grammatik; die Verbindung ist fest und wird als Ganzes gelernt.",
        "examples_correct": [
            "„Die Geschäftsleitung hat nach eingehender Prüfung sämtlicher Unterlagen den Entschluss gefasst, die veralteten Produktionsanlagen unverzüglich außer Betrieb zu setzen.“ (Vorlage I.1, berichtigt)",
            "„Anstatt bloße Kritik an den bestehenden Missständen zu üben, sollten alle Beteiligten konstruktive Alternativen zur Diskussion stellen.“ (Vorlage I.2)",
        ],
        "examples_wrong": [
            {"wrong": "eine Entscheidung machen", "correct": "eine Entscheidung treffen"},
            {"wrong": "eine Frage fragen", "correct": "eine Frage stellen"},
            {"wrong": "die Produktionsmethoden außer Betrieb setzen", "correct": "die Produktionsanlagen außer Betrieb setzen oder die Produktionsmethoden aufgeben: Außer Betrieb setzt man Anlagen und Maschinen, keine Methoden."},
        ],
        "explanation": "Viele Verbindungen bilden Reihen aus Zustand, Eintreten und Herbeiführen: in Kraft sein – in Kraft treten – in Kraft setzen; ebenso zur Diskussion stehen / stellen, zur Verfügung stehen / stellen, außer Betrieb sein / setzen. Das einfache Verb bleibt korrekt und ist im Gespräch oft natürlicher: Die Geschäftsleitung hat beschlossen, … ist gutes Deutsch, keine B1-Schwäche.\n\nZu den Endungen in I.1 und I.2: Unterlagen hat in allen vier Kasus dieselbe Form; das -n ist die Pluralendung, den Genitiv zeigt allein sämtlicher. In den bestehenden Missständen markiert nur das -n von Missständen den Dativ Plural. Das -en von bestehenden ist die schwache Endung, die nach bestimmtem Artikel im Plural immer steht (die bestehenden Missstände, Nominativ).",
        "exercise_prompt": "Jede Verbindung aus Liste 2 in beide Richtungen umformen: Wir haben entschieden, … ↔ Wir haben die Entscheidung getroffen, … Dann einen Satz mit dem Gegenstück bilden (stellen ↔ stehen).",
        "weeks": [1, 2],
        "lists_referenced": ["list_2"],
    },

    # =========================================================================
    # ADHYĀYA II – Vibhakti: die Endungen
    # =========================================================================
    "sutra_04": {
        "id": "sutra_04",
        "number": 4,
        "adhyaya": "II",
        "title": "Adjektivendungen: die Signalregel",
        "rule": "Das Signal für Genus und Kasus muss einmal erscheinen: Zeigt es das Wort vor dem Adjektiv, endet das Adjektiv auf -e oder -en; zeigt es kein Wort davor, trägt das Adjektiv das Signal selbst.",
        "examples_correct": [
            "„Ein guter Ansatz allein reicht nicht; die besten Ideen brauchen ein erfahrenes Team und viel geduldige Arbeit.“",
            "„Trotz anfänglicher Bedenken erweist sich die Methode als eine ohne großen Aufwand durchführbare Lösung.“ (Vorlage IV.2, geglättet: anfänglicher = stark, G Plural; großen = stark, A maskulin)",
        ],
        "examples_wrong": [
            {"wrong": "mit großer Aufwand", "correct": "mit großem Aufwand (D maskulin, stark: -em)"},
            {"wrong": "die neue Ideen", "correct": "die neuen Ideen (nach Artikel im Plural immer -en)"},
            {"wrong": "deren innovativen Ansatz (als Dativ)", "correct": "deren innovativem Ansatz (Vorlage VI.1)"},
        ],
        "explanation": "Die Tabelle ist nur die ausgeschriebene Signalregel; wer die Regel beherrscht, kann jede Zelle selbst ableiten. Prüffrage bei jedem Adjektiv: Zeigt das Wort davor schon Genus und Kasus? Ja → -e oder -en. Nein → das Adjektiv zeigt sie selbst. Nach dessen/deren lautet die Antwort immer „nein“, denn diese Wörter zeigen den Besitzer, nicht den Kasus des folgenden Nomens.\n\nDrei Fälle:\n- Schwach, nach der/die/das/dieser/jeder/welcher/alle/beide: -e im Nominativ Singular und im Akkusativ Singular feminin und neutrum, sonst überall -en.\n- Gemischt, nach ein/kein/mein/dein/sein/ihr/unser/euer: wie schwach, außer wo das Artikelwort keine Endung hat (Nom. Sg. maskulin: ein guter; Nom./Akk. Sg. neutrum: ein gutes).\n- Stark, ohne Artikelwort: Das Adjektiv nimmt die Endung von dieser/diese/dieses. Einzige Ausnahme: Genitiv Singular maskulin und neutrum auf -en (trotz starken Regens).",
        "exercise_prompt": "Jeden Tag zehn Wortgruppen durch alle vier Kasus deklinieren, jeweils mit der, mit ein und ohne Artikelwort: der frische Kaffee – ein frischer Kaffee – frischer Kaffee. Dann in einem Zeitungsartikel zehn Adjektivendungen markieren und jede mit der Prüffrage begründen.",
        "weeks": [1, 2],
        "lists_referenced": [],
    },
    "sutra_05": {
        "id": "sutra_05",
        "number": 5,
        "adhyaya": "II",
        "title": "Die n-Deklination",
        "rule": "Schwache Maskulina enden außer im Nominativ Singular in allen Formen auf -(e)n: der Kollege – den, dem, des Kollegen.",
        "examples_correct": [
            "„Ich habe mit dem neuen Kollegen gesprochen und den Kunden sofort informiert.“",
            "„Bitte leiten Sie die Unterlagen an Herrn Weber weiter.“",
            "„Die Meinung des Experten war eindeutig.“",
        ],
        "examples_wrong": [
            {"wrong": "Ich habe den Kollege gefragt.", "correct": "Ich habe den Kollegen gefragt."},
            {"wrong": "Geben Sie das bitte Herr Weber.", "correct": "… Herrn Weber."},
        ],
        "explanation": "Dazu gehören (1) maskuline Personen- und Tierbezeichnungen auf -e: der Kollege, Kunde, Experte, Biologe, Löwe; (2) Maskulina auf -ant, -and, -ent, -ist, -at, meist Personen: der Praktikant, Doktorand, Student, Journalist, Kandidat; (3) einzelne Wörter: der Mensch, Nachbar, Held, Herr (Singular Herrn, Plural Herren). Eine Sondergruppe hat im Genitiv -ns: der Name – des Namens, ebenso Gedanke, Glaube, Wille, Buchstabe.",
        "exercise_prompt": "Liste 5 laut durchgehen: der Kollege – den Kollegen – dem Kollegen – des Kollegen. Dann eine E-Mail an eine erfundene Personalabteilung schreiben, in der fünf dieser Nomen im Akkusativ, Dativ oder Genitiv stehen.",
        "weeks": [1, 2],
        "lists_referenced": ["list_5"],
    },
    "sutra_06": {
        "id": "sutra_06",
        "number": 6,
        "adhyaya": "II",
        "title": "Der Genitiv",
        "rule": "Im geschriebenen Deutsch lebt der Genitiv als Attribut (die Prüfung der Unterlagen), nach bestimmten Präpositionen (wegen, trotz, während, aufgrund, innerhalb, angesichts …) und nach wenigen Verben (bedürfen, sich bedienen).",
        "examples_correct": [
            "„Aufgrund der hohen Nachfrage wird das Seminar innerhalb eines Monats wiederholt.“",
            "„Angesichts der Lage bedarf es einer schnellen Entscheidung.“",
        ],
        "examples_wrong": [
            {"wrong": "wegen dem Wetter", "correct": "schriftlich: wegen des Wetters (der Dativ ist umgangssprachlich)"},
            {"wrong": "während dem Studium", "correct": "während des Studiums"},
            {"wrong": "die Qualität von dem Produkt", "correct": "besser: die Qualität des Produkts"},
        ],
        "explanation": "Maskulina und Neutra bekommen im Genitiv Singular -s oder -es (des Betriebs, des Monats), schwache Maskulina -(e)n (Sūtra 5). Feminina und Pluralformen bleiben unverändert; den Genitiv zeigen dort nur Artikel und Adjektiv (sämtlicher Unterlagen, trotz anfänglicher Bedenken). Kann kein Artikel den Kasus zeigen, ersetzt von + D den Genitiv: die Lösung von Problemen. Den Genitiv verlangen auch im Rahmen, im Laufe, im Falle, mithilfe, anhand (Liste 4).",
        "exercise_prompt": "Fünf weil-Sätze in Wortgruppen mit wegen oder aufgrund umformen (weil die Nachfrage hoch ist → aufgrund der hohen Nachfrage) und wieder zurück (Sūtra 20).",
        "weeks": [1, 2],
        "lists_referenced": ["list_4"],
    },

    # =========================================================================
    # ADHYĀYA III – Vākya: der Satzbau
    # =========================================================================
    "sutra_07": {
        "id": "sutra_07",
        "number": 7,
        "adhyaya": "III",
        "title": "Die Ordnung im Mittelfeld",
        "rule": "Unbetonte Pronomen stehen vorn im Mittelfeld, in der Folge Nominativ – Akkusativ – Dativ; dann folgen die Nomen, im Normalfall Dativ vor Akkusativ; Neues und Betontes steht am Ende.",
        "examples_correct": [
            "„Können Sie mir die Unterlagen bis Freitag schicken? – Ja, ich schicke sie Ihnen morgen.“",
            "„Gestern hat sich der Kunde bei uns beschwert.“ und „Gestern hat der Kunde sich bei uns beschwert.“ (beides korrekt)",
            "„…, weil er sich damit beschäftigt.“",
        ],
        "examples_wrong": [
            {"wrong": "Ich schicke Ihnen sie morgen.", "correct": "Ich schicke sie Ihnen morgen."},
            {"wrong": "…, weil sich er damit beschäftigt.", "correct": "…, weil er sich damit beschäftigt."},
            {"wrong": "…, weil er mit den neuen Abläufen sich befasst.", "correct": "…, weil er sich mit den neuen Abläufen befasst."},
        ],
        "explanation": "Sich verhält sich wie ein unbetontes Pronomen: Es steht möglichst weit vorn im Mittelfeld, aber hinter einem Subjektpronomen (weil er sich …). Ist das Subjekt ein Nomen, darf sich davor oder danach stehen: je intensiver sich die Fachkräfte … und je intensiver die Fachkräfte sich … sind beide korrekt (Vorlage II.1). Zu vermeiden ist nur die späte Stellung direkt vor dem Verb, hinter anderen Satzgliedern. Für Angaben gilt als Tendenz: temporal – kausal – modal – lokal (Ich fahre morgen wegen der Konferenz mit dem Zug nach Berlin.).",
        "exercise_prompt": "Zehn Sätze mit zwei Objekten bilden und Schritt für Schritt pronominalisieren: Ich schicke dem Kunden das Angebot. → Ich schicke es dem Kunden. → Ich schicke ihm das Angebot. → Ich schicke es ihm.",
        "weeks": [3, 4],
        "lists_referenced": [],
    },
    "sutra_08": {
        "id": "sutra_08",
        "number": 8,
        "adhyaya": "III",
        "title": "Konnektoren und ihre Position",
        "rule": "Jeder Konnektor gehört zu einer von drei Klassen: Position 0 (keine Inversion), Position 1 (das Verb folgt direkt) oder Subjunktion (das Verb steht am Ende).",
        "examples_correct": [
            "„Die Daten sind unvollständig; deshalb verschieben wir die Analyse, obwohl der Kunde drängt.“",
            "„Wir verschieben die Analyse, denn die Daten sind unvollständig.“",
        ],
        "examples_wrong": [
            {"wrong": "…, deshalb die Analyse ist unvollständig.", "correct": "…, deshalb ist die Analyse unvollständig."},
            {"wrong": "…, weil die Daten sind unvollständig.", "correct": "…, weil die Daten unvollständig sind. (im Gespräch verbreitet, in der Prüfung ein Fehler)"},
            {"wrong": "Trotzdem er müde war, arbeitete er weiter.", "correct": "Obwohl er müde war, … oder Er war müde; trotzdem arbeitete er weiter."},
        ],
        "explanation": "Die drei Klassen:\n- Position 0: und, aber, oder, denn, sondern\n- Position 1: deshalb, deswegen, daher, darum, trotzdem, dennoch, außerdem, zudem, folglich, somit, stattdessen, allerdings, jedoch, dann, danach\n- Subjunktion: weil, da, obwohl, wenn, falls, sofern, sobald, solange, während, nachdem, bevor, seit(dem), bis, als, ob, indem, sodass, damit, ohne dass, (an)statt dass\n\nDie Klasse bestimmt die Wortstellung, die Bedeutung bestimmt die Wahl. Adverbien der Position 1 können auch im Mittelfeld stehen: Die Analyse ist deshalb unvollständig.",
        "exercise_prompt": "Denselben Zusammenhang in jeder Klasse ausdrücken, die für seine Bedeutung besetzt ist (Liste 3): …, weil … / …, denn … / …, deshalb …",
        "weeks": [3, 4],
        "lists_referenced": ["list_3"],
    },
    "sutra_09": {
        "id": "sutra_09",
        "number": 9,
        "adhyaya": "III",
        "title": "Zweiteilige Konnektoren",
        "rule": "Zweiteilige Konnektoren verbinden zwei gleichwertige Teile; je + Komparativ leitet einen Nebensatz ein (Verb am Ende), desto oder umso + Komparativ steht auf Position 1 des Hauptsatzes (Verb direkt danach).",
        "examples_correct": [
            "„Je intensiver sich die Fachkräfte mit den neuen Arbeitsabläufen befassen, desto nachhaltiger lässt sich die Fehlerquote im laufenden Betrieb verringern.“ (Vorlage II.1)",
            "„Das Konzept stärkt nicht nur das Verantwortungsbewusstsein der Abteilungen, sondern es leistet zugleich einen wesentlichen Beitrag zur Standortsicherung.“ (Vorlage II.2)",
            "„Die Stelle erfordert sowohl Programmierkenntnisse als auch statistisches Wissen.“",
            "„Ich habe weder eine Antwort bekommen, noch hat sich jemand telefonisch gemeldet.“",
            "„Zwar ist die Methode aufwendig, aber sie liefert zuverlässige Ergebnisse.“",
        ],
        "examples_wrong": [
            {"wrong": "Je mehr ich übe, desto ich spreche besser.", "correct": "…, desto besser spreche ich."},
            {"wrong": "Je ich mehr übe, …", "correct": "Je mehr ich übe, … (der Komparativ folgt direkt auf je)"},
            {"wrong": "sowohl … und auch", "correct": "sowohl … als auch"},
        ],
        "explanation": "Desto und umso sind austauschbar. Der Komparativ gehört fest zu je und zu desto: Je mehr Daten wir haben, desto genauer wird das Modell. In II.2 besetzt sondern Position 0, es Position 1 und leistet Position 2; bei gleichem Subjekt kann es entfallen: …, sondern leistet auch … Dagegen: Nicht nur … sondern auch ergänzt, nicht …, sondern korrigiert (nicht teuer, sondern günstig).\n\nWeitere Paare: entweder … oder, einerseits … andererseits, nicht …, sondern.",
        "exercise_prompt": "Zu jedem Paar drei Sätze über das eigene Fachgebiet oder den Alltag bilden. Dann in einem Kurzvortrag von zwei Minuten zu einem Thema aus Teil D mindestens drei Paare verwenden.",
        "weeks": [3, 4],
        "lists_referenced": ["list_3"],
    },

    # =========================================================================
    # ADHYĀYA IV – Karmaṇi und bhāve: Passiv und Passiversatz
    # =========================================================================
    "sutra_10": {
        "id": "sutra_10",
        "number": 10,
        "adhyaya": "IV",
        "title": "Das Vorgangspassiv",
        "rule": "Vorgangspassiv = werden + Partizip II; im Perfekt und Plusquamperfekt heißt das Partizip von werden hier worden, nicht geworden.",
        "examples_correct": [
            "„Die Prüfberichte sind von der Fachkommission bereits vor Monaten vorgelegt worden.“",
            "„Der Antrag wurde durch einen Formfehler verzögert.“",
        ],
        "examples_wrong": [
            {"wrong": "Der Bericht ist gestern geschrieben geworden.", "correct": "… geschrieben worden."},
            {"wrong": "Das Problem wurde gelöst worden.", "correct": "Das Problem wurde gelöst. oder Das Problem ist gelöst worden."},
        ],
        "explanation": "Die Formen:\n- Präsens: Die Anlage wird stillgelegt.\n- Präteritum: Die Anlage wurde stillgelegt.\n- Perfekt: Die Anlage ist stillgelegt worden.\n- Plusquamperfekt: Die Anlage war stillgelegt worden.\n- Mit Modalverb: Die Anlage muss stillgelegt werden. / Die Anlage musste stillgelegt werden.\n- Unpersönlich (bhāve): Am Sonntag wird nicht gearbeitet. / Es wird nicht gearbeitet.\n\nDen Handelnden nennt von + D (von der Fachkommission); durch + A nennt eher Mittel oder Ursache (durch einen Formfehler). Das Platzhalter-es des unpersönlichen Passivs steht nur auf Position 1 und fällt weg, sobald ein anderes Satzglied dort steht.",
        "exercise_prompt": "Fünf Aktivsätze aus der eigenen Arbeit in alle Passivformen setzen: Wir werten die Daten aus. → Die Daten werden ausgewertet. → … wurden ausgewertet. → … sind ausgewertet worden. → … müssen ausgewertet werden.",
        "weeks": [3, 4],
        "lists_referenced": [],
    },
    "sutra_11": {
        "id": "sutra_11",
        "number": 11,
        "adhyaya": "IV",
        "title": "Das Zustandspassiv",
        "rule": "Zustandspassiv = sein + Partizip II; es beschreibt das Ergebnis eines Vorgangs, nicht den Vorgang selbst.",
        "examples_correct": [
            "Vorgang: „Die Tür wird um 20 Uhr geschlossen.“ Ergebnis: „Die Tür ist geschlossen.“",
            "„Das Problem ist gelöst; die Anlage ist seit März stillgelegt.“",
        ],
        "examples_wrong": [
            {"wrong": "Der Brief ist gestern von meiner Kollegin geschrieben.", "correct": "Der Brief wurde gestern von meiner Kollegin geschrieben. (ein Vorgang mit Zeitpunkt und handelnder Person verlangt das Vorgangspassiv)"},
        ],
        "explanation": "Vorgangspassiv: Etwas geschieht (wird geschlossen). Zustandspassiv: Etwas ist das Ergebnis (ist geschlossen). Deshalb steht beim Zustandspassiv selten ein Handelnder mit von.\n\nZu Vorlage VII.1: Lässt man in wäre … vermieden worden das worden weg, entsteht nicht das Aktiv, sondern das Zustandspassiv (wäre vermieden). Das Aktiv von vermeiden bildet die Vergangenheit mit haben: Die Verantwortlichen hätten den Schaden vermieden.",
        "exercise_prompt": "Zu zehn Verben je ein Satzpaar bilden: Vorgang (Das Büro wird geöffnet.) und Ergebnis (Das Büro ist geöffnet.).",
        "weeks": [3, 4],
        "lists_referenced": [],
    },
    "sutra_12": {
        "id": "sutra_12",
        "number": 12,
        "adhyaya": "IV",
        "title": "Passiversatz und modaler Infinitiv",
        "rule": "sein + zu + Infinitiv = Passiv mit müssen oder können; sich lassen + Infinitiv = Passiv mit können; Adjektive auf -bar = „kann … werden“; haben + zu + Infinitiv = aktives müssen.",
        "examples_correct": [
            "„Die gravierenden Mängel im Brandschutzkonzept sind bis Ende des Monats ausnahmslos zu beheben, da andernfalls mit empfindlichen Bußgeldern zu rechnen ist.“ (Vorlage IV.1)",
            "„Trotz anfänglicher Bedenken erweist sich die Methode als eine ohne großen Aufwand durchführbare Lösung.“ (Vorlage IV.2, geglättet)",
            "„Die Fehlerquote lässt sich deutlich verringern.“",
            "„Bewerber haben die Unterlagen bis zum 30. November einzureichen.“",
        ],
        "examples_wrong": [
            {"wrong": "Die Mängel sind zu beheben werden.", "correct": "Die Mängel sind zu beheben."},
            {"wrong": "Das lässt sich gemacht werden.", "correct": "Das lässt sich machen."},
        ],
        "explanation": "Sein + zu trägt die Passivbedeutung schon in sich; ein zusätzliches werden ist falsch. Ob müssen oder können gemeint ist, zeigt der Kontext: Die Mängel sind zu beheben (müssen), Der Text ist leicht zu verstehen (können). In IV.1 steht die Form zweimal: persönlich (Die Mängel sind zu beheben = Sie müssen behoben werden) und unpersönlich (Mit Bußgeldern ist zu rechnen = Man muss mit Bußgeldern rechnen).\n\n-bar ersetzt einen Relativsatz: eine durchführbare Lösung = eine Lösung, die man durchführen kann. Sich erweisen als verlangt den Nominativ (als eine … Lösung). Das Gerundiv ist die attributive Form: die zu behebenden Mängel = die Mängel, die behoben werden müssen.",
        "exercise_prompt": "Jeden Inhalt in vier Fassungen sagen: Man muss die Mängel beheben. → Die Mängel müssen behoben werden. → Die Mängel sind zu beheben. → als Attribut: die zu behebenden Mängel.",
        "weeks": [3, 4],
        "lists_referenced": [],
    },

    # =========================================================================
    # ADHYĀYA V – Viśeṣaṇa: Attribute
    # =========================================================================
    "sutra_13": {
        "id": "sutra_13",
        "number": 13,
        "adhyaya": "V",
        "title": "Partizipien als Attribut",
        "rule": "Partizip I = aktiv und gleichzeitig (die steigenden Preise = die Preise, die steigen); Partizip II = passiv und abgeschlossen (die vorgelegten Berichte = die Berichte, die vorgelegt worden sind), bei Verben mit sein-Perfekt aktiv und abgeschlossen (die gestiegenen Preise = die Preise, die gestiegen sind).",
        "examples_correct": [
            "„Die von der Fachkommission bereits vor Monaten vorgelegten, von den Behörden jedoch weitgehend ignorierten Prüfberichte erfordern eine sofortige Neubewertung.“ (Vorlage V.1)",
            "„Die seit Jahren steigenden Kosten belasten vor allem kleine Betriebe.“",
        ],
        "examples_wrong": [
            {"wrong": "die gestiegende Preise", "correct": "die gestiegenen Preise (Partizip II; nach Artikel im Plural -en)"},
            {"wrong": "eine gut bezahlende Stelle", "correct": "eine gut bezahlte Stelle (die Stelle wird bezahlt, sie bezahlt nicht)"},
        ],
        "explanation": "Das erweiterte Partizipialattribut ist ein zusammengezogener Relativsatz zwischen Artikel und Nomen. Lesestrategie: Steht nach dem Artikel zuerst eine Präposition, ein Adverb oder eine Wortgruppe in einem anderen Kasus, beginnt ein erweitertes Attribut; man sucht das Nomen, das zum Artikel passt, und direkt davor das Partizip.\n\nAuf B2 muss man solche Attribute vor allem sicher verstehen. Beim Sprechen und Schreiben genügt ein kurzes Attribut (die vorgelegten Berichte); ein Relativsatz ist immer korrekt. Die Reihenfolge von Urheber und Zeitangabe ist frei.",
        "exercise_prompt": "In einem Fachartikel drei Partizipialattribute markieren und in Relativsätze auflösen; umgekehrt drei eigene Relativsätze zu kurzen Attributen verdichten.",
        "weeks": [5, 6],
        "lists_referenced": [],
    },
    "sutra_14": {
        "id": "sutra_14",
        "number": 14,
        "adhyaya": "V",
        "title": "Relativsätze: Präposition, Genitiv, was und wo(r)-",
        "rule": "Das Relativpronomen richtet sich in Genus und Numerus nach dem Bezugswort, im Kasus nach seiner Rolle im Relativsatz; eine Präposition steht davor; im Genitiv heißt es dessen (maskulin, neutrum) oder deren (feminin, Plural), und das folgende Adjektiv trägt die starke Endung.",
        "examples_correct": [
            "„Die Projektleiterin, deren innovativem Ansatz das Team diesen Erfolg verdankt, übernimmt künftig die gesamte Entwicklungsabteilung.“ (Vorlage VI.1)",
            "„Es handelt sich um eine Krise, zu deren nachhaltiger Überwindung die Regierung tiefgreifende Reformen einleiten muss.“ (Vorlage VI.2)",
            "„Das Projekt, an dem ich zurzeit arbeite, wird von einer Stiftung gefördert.“",
            "„Das ist alles, worüber wir gesprochen haben.“ und „Sie hat die Stelle bekommen, was mich sehr freut.“",
        ],
        "examples_wrong": [
            {"wrong": "die Projektleiterin, derer Ansatz …", "correct": "deren Ansatz (derer steht nur vor einem Relativsatz: die Zahl derer, die …)"},
            {"wrong": "das Projekt, wo ich arbeite", "correct": "das Projekt, an dem ich arbeite (wo nur für Orte: die Stadt, in der / wo ich wohne)"},
            {"wrong": "alles, das ich weiß", "correct": "alles, was ich weiß"},
        ],
        "explanation": "Deren in VI.1 bezieht sich auf die Projektleiterin und bleibt unverändert, gleich welches Nomen folgt. Den Kasus dieses Nomens (Dativ, verlangt von jmdm. etw. verdanken) zeigt allein das Adjektiv: innovativem. Ebenso in VI.2: zu verlangt den Dativ, deren verweist auf Krise, nachhaltiger trägt die starke Endung (D feminin).\n\nWas steht nach alles, etwas, nichts, das Einzige, das Beste und nach einem ganzen Satz; mit Präposition wird daraus wo(r)-: alles, worüber wir gesprochen haben. Wer …, (der) verallgemeinert: Wer viel liest, schreibt besser.",
        "exercise_prompt": "Zu fünf Nomen aus dem eigenen Fachgebiet je zwei Relativsätze bilden, einen mit Präposition und einen mit dessen/deren + Adjektiv; dazu drei Sätze mit was oder wo(r)-.",
        "weeks": [5, 6],
        "lists_referenced": [],
    },

    # =========================================================================
    # ADHYĀYA VI – Lakāra: Modus und Modalität
    # =========================================================================
    "sutra_15": {
        "id": "sutra_15",
        "number": 15,
        "adhyaya": "VI",
        "title": "Konjunktiv II",
        "rule": "Gegenwart: würde + Infinitiv, bei sein, haben, den Modalverben und einigen häufigen Verben die eigene Form (wäre, hätte, könnte, müsste, dürfte, wüsste, käme, gäbe, ginge); Vergangenheit: hätte/wäre + Partizip II; Passiv der Vergangenheit: wäre + Partizip II + worden.",
        "examples_correct": [
            "„Hätten die Verantwortlichen die Risiken rechtzeitig in Betracht gezogen, so wäre der verheerende Schaden mit Sicherheit vermieden worden.“ (Vorlage VII.1)",
            "„Wenn ich mehr Zeit hätte, würde ich öfter Fachartikel auf Deutsch lesen.“",
            "„Wir hätten das Problem früher erkennen können.“",
            "„Er tut so, als hätte er die E-Mail nicht bekommen.“ und „…, als ob er die E-Mail nicht bekommen hätte.“",
            "„Könnten Sie mir bitte die Unterlagen schicken?“",
        ],
        "examples_wrong": [
            {"wrong": "Wenn ich Zeit hätte, ich würde kommen.", "correct": "…, würde ich kommen."},
            {"wrong": "Wir hätten das Problem früher erkennen gekonnt.", "correct": "… erkennen können."},
            {"wrong": "…, dass wir das Problem früher erkennen können hätten.", "correct": "…, dass wir das Problem früher hätten erkennen können."},
            {"wrong": "Wenn ich das gewusst würde, …", "correct": "Wenn ich das gewusst hätte, …"},
        ],
        "explanation": "In VII.1 fehlt wenn; das finite Verb (Hätten) steht am Satzanfang (uneingeleiteter Konditionalsatz). Der Hauptsatz schließt mit so oder dann an (so wäre …) oder direkt mit dem Verb (…, wäre der Schaden …). Wäre steht dort auf Position 2, am Satzende steht vermieden worden.\n\nMit Modalverb steht in der Vergangenheit ein doppelter Infinitiv (hätten … erkennen können); im Nebensatz steht hätte davor. Irreale Vergleiche: als ob + Verb am Ende oder als + Verb direkt danach (als hätte er …).",
        "exercise_prompt": "Täglich drei irreale Sätze über den eigenen Werdegang: Gegenwart (Wenn ich … hätte, würde ich …), Vergangenheit (Hätte ich …, wäre ich …), mit Modalverb (Ich hätte … können).",
        "weeks": [5, 6],
        "lists_referenced": [],
    },
    "sutra_16": {
        "id": "sutra_16",
        "number": 16,
        "adhyaya": "VI",
        "title": "Konjunktiv I und indirekte Rede",
        "rule": "Konjunktiv I = Infinitivstamm + Endung (er habe, komme, könne, werde; bei sein: er sei); ist er nicht vom Indikativ zu unterscheiden, nimmt man den Konjunktiv II (sie hätten statt sie haben), und ist auch dieser nicht eindeutig, würde + Infinitiv (sie würden arbeiten).",
        "examples_correct": [
            "„Der Vorstand erklärte, die Umstrukturierung sei unausweichlich und bedürfe der uneingeschränkten Unterstützung aller Mitarbeiter.“ (Vorlage VII.2)",
            "„Die Sprecherin sagte, man habe die Fehler inzwischen behoben und werde die Ergebnisse im Januar veröffentlichen.“",
            "„Die Kollegen berichteten, sie hätten keine Zeit gehabt.“",
            "„Er fragte, ob die Stelle noch frei sei.“ und „Sie sagte, ich solle die Unterlagen schicken.“",
        ],
        "examples_wrong": [
            {"wrong": "Sie sagten, sie haben keine Zeit.", "correct": "schriftlich: …, sie hätten keine Zeit."},
            {"wrong": "Er sagte, dass er sei krank.", "correct": "Er sagte, dass er krank sei. oder Er sagte, er sei krank."},
            {"wrong": "… und bedürfe die Unterstützung", "correct": "… und bedürfe der Unterstützung (bedürfen + G)"},
        ],
        "explanation": "Die indirekte Rede kennt nur drei Zeitstufen: Gegenwart (sei, habe), Vergangenheit (sei gewesen, habe gemacht, eine Form für Präteritum, Perfekt und Plusquamperfekt) und Zukunft (werde machen). Fragen schließt man mit ob oder dem Fragewort an, Aufforderungen mit sollen oder mögen. Im Gespräch benutzen viele den Indikativ oder würde; in Berichten und Nachrichten zeigt der Konjunktiv I Distanz. Bedürfen verlangt den Genitiv; unpersönlich: Es bedarf weiterer Untersuchungen.",
        "exercise_prompt": "Eine kurze Nachrichtenmeldung hören oder lesen und in drei Sätzen indirekt wiedergeben. Dann ein Gespräch vom Vortag in indirekter Rede zusammenfassen.",
        "weeks": [5, 6],
        "lists_referenced": [],
    },
    "sutra_17": {
        "id": "sutra_17",
        "number": 17,
        "adhyaya": "VI",
        "title": "Vermutung",
        "rule": "Vermutungen über die Gegenwart drückt werden + Infinitiv aus, über die Vergangenheit werden + Partizip II + haben/sein, meist mit wohl; die Modalverben stufen die Sicherheit ab: muss (fast sicher) – dürfte (wahrscheinlich) – kann/könnte (möglich) – kann nicht (ausgeschlossen).",
        "examples_correct": [
            "„Sie wird wohl noch in der Besprechung sein.“",
            "„Er wird den Zug verpasst haben.“",
            "„Das dürfte der Grund für die Verzögerung sein.“",
            "„Das muss ein Missverständnis sein.“ und „Das kann nicht stimmen.“",
        ],
        "examples_wrong": [
            {"wrong": "Er wird den Zug verpasst.", "correct": "Er wird den Zug verpasst haben."},
            {"wrong": "Das darf der Grund sein.", "correct": "Das dürfte der Grund sein. (darf = Erlaubnis; nur dürfte drückt Vermutung aus)"},
        ],
        "explanation": "Werden + Infinitiv drückt nicht nur Zukunft aus, sondern besonders mit wohl, sicher, wahrscheinlich auch eine Vermutung über die Gegenwart. Für die Zukunft genügt oft das Präsens mit Zeitangabe (Morgen schicke ich Ihnen die Daten.). Vermutungen über die Vergangenheit brauchen den Infinitiv Perfekt: Er dürfte schon angekommen sein.",
        "exercise_prompt": "Zu fünf Fotos oder Schlagzeilen je drei Vermutungen in drei Sicherheitsstufen formulieren; eine gute Übung für die Diskussion in der mündlichen Prüfung.",
        "weeks": [5, 6],
        "lists_referenced": ["list_2"],
    },

    # =========================================================================
    # ADHYĀYA VII – Samāsa und Liṅga: Wortbildung und Nominalstil
    # =========================================================================
    "sutra_18": {
        "id": "sutra_18",
        "number": 18,
        "adhyaya": "VII",
        "title": "Samāsa: Komposita",
        "rule": "Das letzte Glied eines Kompositums (Grundwort) bestimmt Genus und Wortart, die vorderen Glieder bestimmen es näher; nach -ung, -heit, -keit, -schaft, -ion, -tät, -ling steht das Fugen-s.",
        "examples_correct": [
            "die Produktion + die Anlage → die Produktionsanlage; die Forschung + das Projekt → das Forschungsprojekt; die Gesundheit + das System → das Gesundheitssystem; die Wirtschaft + die Lage → die Wirtschaftslage",
            "der Standort + die Sicherung → die Standortsicherung (Vorlage II.2, ohne Fugenelement)",
        ],
        "examples_wrong": [
            {"wrong": "der Forschungprojekt", "correct": "das Forschungsprojekt (Genus vom Grundwort, Fugen-s nach -ung)"},
        ],
        "explanation": "Auch nach Arbeit, Geburt, Liebe steht meist ein Fugenelement (Arbeitsplatz, Geburtstag, Liebesbrief); bei anderen Wörtern lernt man es mit dem Wort. Komposita liest man von hinten nach vorn: Fachkräftemangel = Mangel an Fachkräften; Qualitätssicherungsmaßnahme = eine Maßnahme zur Sicherung der Qualität.",
        "exercise_prompt": "Täglich fünf Komposita aus der Zeitung von hinten nach vorn auflösen und fünf eigene aus dem Fachgebiet bilden.",
        "weeks": [7, 8],
        "lists_referenced": [],
    },
    "sutra_19": {
        "id": "sutra_19",
        "number": 19,
        "adhyaya": "VII",
        "title": "Liṅga: Genus nach der Endung",
        "rule": "Feminin sind fast alle Nomen auf -ung, -heit, -keit, -schaft, -ion, -tät, -ik, -ur, -enz, -anz; neutral die Nomen auf -chen, -lein, meist auch die auf -ment und lateinisches -um, dazu nominalisierte Infinitive; maskulin meist die Nomen auf -ling, -ismus, -or, Personen auf -ant, -ent, -ist und von Verben abgeleitete Personen und Geräte auf -er.",
        "examples_correct": [
            "feminin: die Entscheidung, die Möglichkeit, die Wissenschaft, die Information, die Qualität, die Statistik, die Struktur, die Konferenz",
            "neutral: das Experiment, das Studium, das Mädchen, das Lernen",
            "maskulin: der Lehrling, der Tourismus, der Faktor, der Praktikant, der Rechner",
        ],
        "examples_wrong": [
            {"wrong": "der Information (als Nominativ)", "correct": "die Information"},
            {"wrong": "die Experiment", "correct": "das Experiment"},
        ],
        "explanation": "Die Regeln gelten auch für jedes Kompositum, dessen Grundwort eine solche Endung trägt (die Datenverarbeitung). Ausnahmen gibt es (das Labor, der Konsum, das Abitur); Nomen ohne erkennbare Endung lernt man immer mit Artikel.",
        "exercise_prompt": "Aus einem Zeitungsartikel alle Nomen mit diesen Endungen sammeln, ihr Genus vorhersagen und dann prüfen.",
        "weeks": [7, 8],
        "lists_referenced": [],
    },
    "sutra_20": {
        "id": "sutra_20",
        "number": 20,
        "adhyaya": "VII",
        "title": "Nominalstil und Verbalstil",
        "rule": "Ein Nebensatz lässt sich in eine präpositionale Wortgruppe verwandeln: Das Verb wird zum Nomen; das Subjekt eines intransitiven Verbs und das Akkusativobjekt werden zum Genitiv; das Subjekt eines transitiven Verbs wird zu durch + A.",
        "examples_correct": [
            "„Nach eingehender Prüfung sämtlicher Unterlagen …“ ↔ „Nachdem man sämtliche Unterlagen eingehend geprüft hatte, …“ (Vorlage I.1)",
            "„Die Kommission prüft die Unterlagen.“ → die Prüfung der Unterlagen durch die Kommission",
            "„Die Preise steigen.“ → der Anstieg der Preise",
        ],
        "examples_wrong": [
            {"wrong": "wegen die Nachfrage steigt", "correct": "weil die Nachfrage steigt oder wegen der steigenden Nachfrage"},
            {"wrong": "die Prüfung von den Unterlagen von der Kommission", "correct": "die Prüfung der Unterlagen durch die Kommission"},
        ],
        "explanation": "Der Nominalstil ist kompakt und typisch für Berichte, Protokolle und Fachtexte. Der Verbalstil ist lebendiger und im Gespräch fast immer die bessere Wahl (Paribhāṣā 1). B2 heißt, in beide Richtungen umformen zu können.",
        "exercise_prompt": "Die Umformungsmatrix täglich mit einem neuen Satz aus den Nachrichten durchspielen, hin und zurück. In eigenen Texten Nominalisierungen gezielt einsetzen.",
        "weeks": [7, 8],
        "lists_referenced": ["list_4"],
    },

    # =========================================================================
    # ADHYĀYA VIII – Tumun: Infinitivsätze
    # =========================================================================
    "sutra_21": {
        "id": "sutra_21",
        "number": 21,
        "adhyaya": "VIII",
        "title": "Infinitivsätze",
        "rule": "Ein Infinitiv mit zu ersetzt einen Nebensatz, wenn sein gedachtes Subjekt im Hauptsatz schon genannt ist; um … zu, ohne … zu, (an)statt … zu verlangen dasselbe Subjekt, bei verschiedenen Subjekten stehen damit, ohne dass, (an)statt dass.",
        "examples_correct": [
            "„Anstatt bloße Kritik an den bestehenden Missständen zu üben, sollten alle Beteiligten konstruktive Alternativen zur Diskussion stellen.“ (Vorlage I.2)",
            "„Ich bewerbe mich, um meine Erfahrung in der Datenanalyse einzubringen.“",
            "„Wir schicken Ihnen die Unterlagen, damit Sie sich vorbereiten können.“",
        ],
        "examples_wrong": [
            {"wrong": "Ich lerne Deutsch, um meine Chancen verbessern.", "correct": "…, um meine Chancen zu verbessern."},
            {"wrong": "Ich schicke die Unterlagen, um Sie sich vorbereiten können.", "correct": "…, damit Sie sich vorbereiten können."},
            {"wrong": "zu ankommen", "correct": "anzukommen"},
        ],
        "explanation": "Die Formen:\n- Gegenwart: zu machen (Ich hoffe, die Prüfung zu bestehen.)\n- Vergangenheit: gemacht zu haben / gekommen zu sein (Ich bin froh, die Prüfung bestanden zu haben.)\n- Passiv: gemacht zu werden (Ich hoffe, zum Vorstellungsgespräch eingeladen zu werden.)\n- Passiv der Vergangenheit: gemacht worden zu sein (Sie freut sich, ausgewählt worden zu sein.)\n\nBei trennbaren Verben steht zu zwischen Verbzusatz und Stamm (einzureichen, anzukommen). Nach Modalverben und nach lassen, sehen, hören, bleiben, gehen steht der Infinitiv ohne zu. Brauchen steht verneint mit zu: Sie brauchen nicht zu warten.",
        "exercise_prompt": "Fünf Sätze eines Anschreibens mit Infinitivsätzen formulieren (Gegenwart, Vergangenheit, Passiv) und fünf Sätze zwischen um … zu und damit umformen.",
        "weeks": [7, 8],
        "lists_referenced": [],
    },

    # =========================================================================
    # ADHYĀYA IX – Vāk: die gesprochene Sprache
    # =========================================================================
    "sutra_22": {
        "id": "sutra_22",
        "number": 22,
        "adhyaya": "IX",
        "title": "Modalpartikeln",
        "rule": "Modalpartikeln (ja, doch, mal, eben, halt, wohl, eigentlich, denn) stehen unbetont im Mittelfeld; sie ändern nicht den Inhalt, sondern den Ton.",
        "examples_correct": [
            "ja (bekannt): „Das Projekt läuft ja schon seit März.“",
            "doch (Erinnerung, leiser Widerspruch): „Das habe ich Ihnen doch gestern geschickt.“",
            "mal (weichere Bitte): „Können Sie mir mal die Datei schicken?“",
            "eben und halt (nicht zu ändern): „Das ist eben so.“",
            "eigentlich (Nachfrage, Themenwechsel): „Was machen Sie eigentlich beruflich?“",
            "denn (interessierte Frage): „Wie funktioniert das denn?“",
            "wohl (Vermutung): „Sie ist wohl schon gegangen.“",
        ],
        "examples_wrong": [
            {"wrong": "Können Sie mir die Datei schicken mal?", "correct": "Können Sie mir mal die Datei schicken? (Partikeln stehen im Mittelfeld, nicht am Satzende)"},
        ],
        "explanation": "Am Satzanfang sind ja und doch keine Modalpartikeln mehr, sondern Antwortwörter oder Konnektoren. Im Vorstellungsgespräch setzt man Partikeln sparsam ein (mal, eigentlich, ja); in formellen Texten lässt man sie weg.",
        "exercise_prompt": "Beim Hören Modalpartikeln notieren, jeweils mit der Situation. Dann dieselben Sätze mit und ohne Partikel sprechen und den Unterschied im Ton beschreiben.",
        "weeks": [7, 8],
        "lists_referenced": [],
    },
}


# =============================================================================
# TEIL B – GAṆAPĀṬHA: 6 Lists
# =============================================================================

GANAPATHA: Dict[str, Dict[str, Any]] = {
    "list_1": {
        "id": "list_1",
        "title": "Dhātupāṭha: Verben, Adjektive und Nomen mit Präpositionen",
        "items": {
            "verben": {
                "an + A": ["denken an", "sich erinnern an", "glauben an", "sich gewöhnen an", "sich wenden an", "sich anpassen an"],
                "an + D": ["arbeiten an", "teilnehmen an", "sich beteiligen an", "zweifeln an", "leiden an (Krankheit)", "erkennen an", "liegen an", "es mangelt an", "jmdn. hindern an"],
                "auf + A": ["achten auf", "antworten auf", "sich beziehen auf", "sich freuen auf", "hinweisen auf", "sich konzentrieren auf", "reagieren auf", "sich verlassen auf", "sich vorbereiten auf", "warten auf", "verzichten auf", "eingehen auf", "hoffen auf", "sich einigen auf", "ankommen auf (es kommt darauf an)"],
                "auf + D": ["bestehen auf", "beruhen auf", "basieren auf"],
                "aus + D": ["bestehen aus", "entstehen aus", "folgen aus (daraus folgt)"],
                "bei + D": ["sich bedanken bei", "sich entschuldigen bei", "sich beschweren bei", "sich bewerben bei (Firma)", "helfen bei", "sich erkundigen bei (Person)"],
                "für + A": ["sich bedanken für", "sich entscheiden für", "sich entschuldigen für", "sich interessieren für", "sorgen für", "sich einsetzen für", "sich eignen für", "halten für", "ausgeben für"],
                "gegen + A": ["sich wehren gegen", "protestieren gegen", "verstoßen gegen", "kämpfen gegen"],
                "in + A": ["investieren in", "einwilligen in", "sich einarbeiten in", "sich verlieben in"],
                "in + D": ["bestehen in", "sich irren in", "sich täuschen in"],
                "mit + D": ["sich beschäftigen mit", "sich befassen mit", "sich auseinandersetzen mit", "anfangen mit", "aufhören mit", "rechnen mit", "übereinstimmen mit", "vergleichen mit", "zusammenarbeiten mit", "umgehen mit", "sich abfinden mit", "sich unterhalten mit"],
                "nach + D": ["fragen nach", "sich erkundigen nach (Sache)", "suchen nach", "sich richten nach", "streben nach", "sich sehnen nach"],
                "über + A": ["sprechen über", "diskutieren über", "nachdenken über", "sich ärgern über", "sich beschweren über", "sich freuen über", "(sich) informieren über", "berichten über", "sich wundern über", "verfügen über", "sich Gedanken machen über"],
                "um + A": ["sich bemühen um", "sich kümmern um", "bitten um", "sich bewerben um (Stelle)", "sich sorgen um", "es geht um", "es handelt sich um"],
                "unter + D": ["leiden unter", "verstehen unter"],
                "von + D": ["abhängen von", "ausgehen von", "halten von", "profitieren von", "überzeugen von", "sich unterscheiden von", "sich erholen von", "träumen von", "sich verabschieden von", "absehen von"],
                "vor + D": ["Angst haben vor", "sich fürchten vor", "warnen vor", "schützen vor", "fliehen vor"],
                "zu + D": ["beitragen zu", "führen zu", "gehören zu", "gratulieren zu", "neigen zu", "passen zu", "jmdn. auffordern zu", "sich entschließen zu", "einladen zu", "sich äußern zu", "jmdn. zwingen zu"],
            },
            "adjektive": {
                "von + D": ["abhängig", "begeistert", "überzeugt", "enttäuscht von"],
                "für + A": ["verantwortlich", "zuständig", "geeignet", "dankbar", "offen für"],
                "auf + A": ["stolz", "gespannt", "neugierig", "angewiesen auf"],
                "an + D": ["interessiert", "beteiligt", "reich an"],
                "mit + D": ["zufrieden", "einverstanden", "vertraut mit"],
                "weitere": ["erfahren in + D", "froh über + A", "bereit zu + D", "fähig zu + D"],
            },
            "nomen": [
                "die Angst vor + D", "das Interesse an + D", "die Kritik an + D", "der Zweifel an + D",
                "der Einfluss auf + A", "die Auswirkung auf + A", "die Antwort auf + A", "die Lust auf + A",
                "der Beitrag zu + D", "die Beziehung zu + D", "die Voraussetzung für + A", "der Grund für + A", "die Verantwortung für + A",
                "die Frage nach + D", "die Suche nach + D", "die Nachfrage nach + D", "die Erfahrung mit + D", "der Umgang mit + D",
                "die Diskussion über + A", "die Bitte um + A", "die Sorge um + A",
            ],
        },
    },
    "list_2": {
        "id": "list_2",
        "title": "Nomen-Verb-Verbindungen",
        "items": {
            "stellen / stehen": [
                "eine Frage stellen (fragen)", "einen Antrag stellen (beantragen)", "eine Forderung stellen (fordern)",
                "zur Verfügung stellen / stehen (bereitstellen / verfügbar sein)", "zur Diskussion stellen / stehen",
                "infrage stellen (bezweifeln)",
            ],
            "nehmen": [
                "Stellung nehmen zu (sich äußern)", "Rücksicht nehmen auf (berücksichtigen)",
                "Einfluss nehmen auf (beeinflussen)", "in Anspruch nehmen (nutzen)",
                "Bezug nehmen auf (sich beziehen)", "in Kauf nehmen (einen Nachteil akzeptieren)",
                "zur Kenntnis nehmen", "in Betrieb nehmen (starten)", "Kontakt aufnehmen mit (kontaktieren)",
            ],
            "bringen / kommen": [
                "zum Ausdruck bringen (ausdrücken)", "in Erfahrung bringen (herausfinden)",
                "zur Sprache bringen (ansprechen)", "zum Abschluss bringen (abschließen)",
                "zur Anwendung kommen (angewendet werden)", "zum Einsatz kommen (eingesetzt werden)",
                "zu einer Einigung kommen (sich einigen)", "zu dem Schluss kommen (folgern)",
                "infrage kommen (möglich sein)",
            ],
            "treffen / fassen / ergreifen": [
                "eine Entscheidung treffen (entscheiden)", "eine Vereinbarung treffen (vereinbaren)",
                "Vorbereitungen treffen (vorbereiten)", "einen Entschluss fassen (beschließen)",
                "Maßnahmen ergreifen (handeln)", "die Initiative ergreifen (aktiv werden)",
            ],
            "leisten / üben": [
                "einen Beitrag leisten zu (beitragen)", "Hilfe leisten (helfen)",
                "Widerstand leisten (sich widersetzen)", "Kritik üben an (kritisieren)",
            ],
            "machen": [
                "einen Vorschlag machen (vorschlagen)", "Fortschritte machen (vorankommen)",
                "sich Sorgen machen um (sich sorgen)", "sich Gedanken machen über (nachdenken)",
                "Gebrauch machen von (nutzen)",
            ],
            "ziehen": [
                "in Betracht ziehen (erwägen)", "Bilanz ziehen (ein Ergebnis zusammenfassen)",
                "Schlüsse ziehen aus (folgern)", "zur Verantwortung ziehen (verantwortlich machen)",
            ],
            "finden / stoßen": [
                "Anerkennung finden (anerkannt werden)", "Anwendung finden (angewendet werden)",
                "Beachtung finden (beachtet werden)", "auf Kritik stoßen (kritisiert werden)",
                "auf Interesse stoßen (Interesse wecken)",
            ],
            "haben / tragen": [
                "zur Folge haben (bewirken)", "Einfluss haben auf (beeinflussen)",
                "Anspruch haben auf (berechtigt sein)", "die Verantwortung tragen für (verantwortlich sein)",
                "Sorge tragen für (sorgen für)",
            ],
            "treten / setzen / spielen": [
                "in Kraft treten (gültig werden)", "in Verbindung treten mit (Kontakt aufnehmen)",
                "außer Betrieb setzen (stilllegen)", "in Gang setzen (starten)",
                "unter Druck setzen (drängen)", "eine Rolle spielen (wichtig sein)",
            ],
        },
    },
    "list_3": {
        "id": "list_3",
        "title": "Konnektoren nach Bedeutung und Klasse",
        "items": [
            {"bedeutung": "kausal", "subjunktion": "weil, da", "adverb": "deshalb, deswegen, daher, darum", "konjunktion": "denn", "praeposition": "wegen, aufgrund (+ G)"},
            {"bedeutung": "konsekutiv", "subjunktion": "sodass, so … dass", "adverb": "folglich, also, somit, infolgedessen", "konjunktion": "–", "praeposition": "infolge (+ G)"},
            {"bedeutung": "konzessiv", "subjunktion": "obwohl, obgleich, auch wenn", "adverb": "trotzdem, dennoch, dessen ungeachtet", "konjunktion": "–", "praeposition": "trotz (+ G)"},
            {"bedeutung": "konditional", "subjunktion": "wenn, falls, sofern, vorausgesetzt, dass", "adverb": "sonst, andernfalls", "konjunktion": "–", "praeposition": "bei (+ D), im Falle (+ G)"},
            {"bedeutung": "final", "subjunktion": "damit, um … zu", "adverb": "dazu, zu diesem Zweck", "konjunktion": "–", "praeposition": "zu (+ D), für (+ A)"},
            {"bedeutung": "adversativ", "subjunktion": "während, wohingegen", "adverb": "dagegen, hingegen, jedoch, stattdessen", "konjunktion": "aber, sondern", "praeposition": "statt (+ G)"},
            {"bedeutung": "temporal", "subjunktion": "als, wenn, während, nachdem, bevor, seit(dem), bis, sobald, solange", "adverb": "dann, danach, vorher, inzwischen, seitdem", "konjunktion": "–", "praeposition": "nach, vor, seit (+ D), während (+ G)"},
            {"bedeutung": "modal", "subjunktion": "indem, dadurch dass, ohne dass, ohne … zu", "adverb": "dadurch, so", "konjunktion": "–", "praeposition": "durch (+ A), ohne (+ A)"},
            {"bedeutung": "additiv", "subjunktion": "–", "adverb": "außerdem, zudem, darüber hinaus", "konjunktion": "und", "praeposition": "neben (+ D)"},
        ],
        "zweiteilig": [
            "je … desto/umso", "nicht nur … sondern auch", "sowohl … als auch",
            "weder … noch", "entweder … oder", "zwar … aber", "einerseits … andererseits",
        ],
    },
    "list_4": {
        "id": "list_4",
        "title": "Genitiv",
        "items": {
            "praepositionen": [
                "wegen", "trotz", "während", "aufgrund", "statt/anstatt", "anstelle",
                "innerhalb", "außerhalb", "oberhalb", "unterhalb", "infolge", "angesichts",
                "hinsichtlich", "bezüglich", "mithilfe", "anhand", "zugunsten", "einschließlich",
                "im Laufe", "im Rahmen", "im Falle",
            ],
            "praepositionen_dativ_oder_genitiv": ["laut", "dank"],
            "verben": [
                "bedürfen (Es bedarf einer Lösung.)",
                "sich bedienen (sich einer Methode bedienen)",
                "gedenken (der Opfer gedenken)",
                "sich vergewissern (sich der Fakten vergewissern)",
                "jmdn. einer Sache beschuldigen",
            ],
            "adjektive": [
                "sich einer Sache bewusst sein (Ich bin mir der Risiken bewusst.)",
                "sich einer Sache sicher sein",
            ],
        },
    },
    "list_5": {
        "id": "list_5",
        "title": "n-Deklination",
        "items": {
            "auf_e": ["der Kollege", "der Kunde", "der Experte", "der Junge", "der Zeuge", "der Bote", "der Erbe", "der Laie", "der Neffe", "der Biologe", "der Psychologe", "der Pädagoge"],
            "auf_ant_and": ["der Praktikant", "der Lieferant", "der Elefant", "der Doktorand"],
            "auf_ent": ["der Student", "der Präsident", "der Patient", "der Dozent", "der Konkurrent", "der Assistent"],
            "auf_ist": ["der Journalist", "der Spezialist", "der Tourist", "der Polizist"],
            "auf_at": ["der Kandidat", "der Soldat", "der Diplomat", "der Automat"],
            "einzeln": ["der Mensch", "der Herr (Herrn, Plural Herren)", "der Nachbar", "der Held", "der Bär", "der Prinz", "der Graf"],
            "genitiv_auf_ns": ["der Name", "der Gedanke", "der Glaube", "der Wille", "der Buchstabe", "das Herz (des Herzens, dem Herzen)"],
        },
    },
    "list_6": {
        "id": "list_6",
        "title": "Redemittel für Schreiben, Sprechen und Vorstellungsgespräch",
        "items": {
            "meinung_aeussern": [
                "Meiner Meinung nach …", "Ich bin der Auffassung, dass …",
                "Ich vertrete den Standpunkt, dass …", "Aus meiner Sicht …",
                "Ich halte es für sinnvoll, … zu …", "Es ist nicht zu bestreiten, dass …",
            ],
            "zustimmen": [
                "Da stimme ich Ihnen zu.", "Das sehe ich genauso.",
                "Da haben Sie völlig recht.", "Dem kann ich nur zustimmen.",
            ],
            "widersprechen": [
                "Da bin ich anderer Meinung.", "Das sehe ich etwas anders.",
                "Das mag sein, aber …", "Ich gebe zu bedenken, dass …", "Da muss ich widersprechen.",
            ],
            "vor_und_nachteile": [
                "Ein wichtiger Vorteil ist, dass …", "Dagegen spricht, dass …",
                "Ein Nachteil besteht darin, dass …", "Man darf nicht vergessen, dass …",
                "Wägt man die Argumente ab, so …",
            ],
            "vortrag_strukturieren": [
                "In meinem Vortrag geht es um …",
                "Zunächst möchte ich auf … eingehen, anschließend …, zum Schluss …",
                "Damit komme ich zum nächsten Punkt.", "Ein Beispiel dafür ist …",
                "Zusammenfassend lässt sich sagen, dass …", "Vielen Dank für Ihre Aufmerksamkeit.",
            ],
            "diskussion_fuehren": [
                "Darf ich kurz etwas ergänzen?",
                "Wenn ich Sie richtig verstanden habe, meinen Sie, dass …",
                "Was halten Sie davon, wenn …?",
                "Können wir uns darauf einigen, dass …?",
                "Lassen Sie uns zum eigentlichen Thema zurückkommen.",
            ],
            "nachfragen": [
                "Könnten Sie das bitte wiederholen?",
                "Was meinen Sie genau mit …?",
                "Habe ich Sie richtig verstanden, dass …?",
            ],
            "formelle_nachricht": [
                "Sehr geehrte Frau …, / Sehr geehrter Herr …,",
                "ich wende mich an Sie, weil …",
                "Ich beziehe mich auf Ihre E-Mail vom …",
                "Könnten Sie mir bitte mitteilen, ob …?",
                "Für eine kurze Rückmeldung wäre ich Ihnen dankbar.",
                "Mit freundlichen Grüßen",
            ],
            "vorstellungsgespraech": [
                "Nach meinem Studium der … habe ich …",
                "Zu meinen Aufgaben gehörte es, … zu …",
                "In meinem letzten Projekt war ich für … verantwortlich.",
                "Ich habe Erfahrung in … und mit …",
                "An dieser Stelle reizt mich besonders, dass …",
                "Meine Stärke liegt darin, … zu …",
                "Welche Aufgaben würden in den ersten Monaten auf mich zukommen?",
            ],
        },
    },
}


# =============================================================================
# TEIL C – PRAKRIYĀ: Exercises
# =============================================================================

# Übung 1 – Hin und zurück: 13 bidirectional transformations
TRANSFORMATIONS: List[Dict[str, Any]] = [
    {
        "id": "I.1", "number": 1,
        "schlicht": "Die Geschäftsleitung hat alle Unterlagen genau geprüft und dann beschlossen, die alten Produktionsanlagen sofort stillzulegen.",
        "gehoben": "Die Geschäftsleitung hat nach eingehender Prüfung sämtlicher Unterlagen den Entschluss gefasst, die veralteten Produktionsanlagen unverzüglich außer Betrieb zu setzen.",
        "sutras": ["sutra_03", "sutra_20"],
    },
    {
        "id": "I.2", "number": 2,
        "schlicht": "Alle Beteiligten sollten die Missstände nicht nur kritisieren, sondern bessere Alternativen vorschlagen.",
        "gehoben": "Anstatt bloße Kritik an den bestehenden Missständen zu üben, sollten alle Beteiligten konstruktive Alternativen zur Diskussion stellen.",
        "sutras": ["sutra_03", "sutra_21"],
    },
    {
        "id": "II.1", "number": 3,
        "schlicht": "Wenn sich die Fachkräfte intensiver mit den neuen Abläufen beschäftigen, kann man die Fehlerquote stärker senken.",
        "gehoben": "Je intensiver sich die Fachkräfte mit den neuen Arbeitsabläufen befassen, desto nachhaltiger lässt sich die Fehlerquote im laufenden Betrieb verringern.",
        "sutras": ["sutra_09", "sutra_12"],
    },
    {
        "id": "II.2", "number": 4,
        "schlicht": "Das Konzept stärkt das Verantwortungsbewusstsein der Abteilungen. Außerdem hilft es, den Standort zu sichern.",
        "gehoben": "Das Konzept stärkt nicht nur das Verantwortungsbewusstsein der Abteilungen, sondern es leistet zugleich einen wesentlichen Beitrag zur Standortsicherung.",
        "sutras": ["sutra_09", "sutra_03"],
    },
    {
        "id": "III.1", "number": 5,
        "schlicht": "Experten sagen deutlich: Der Erfolg eines Betriebs hängt vor allem davon ab, wie innovativ er ist.",
        "gehoben": "Wirtschaftsexperten weisen mit Nachdruck darauf hin, dass der künftige Erfolg eines Betriebs maßgeblich von dessen Innovationsbereitschaft abhängt.",
        "sutras": ["sutra_01", "sutra_02"],
    },
    {
        "id": "III.2", "number": 6,
        "schlicht": "Alle finden diese Schritte notwendig, wenn die Mitarbeiter nicht zu sehr unter den Sparmaßnahmen leiden.",
        "gehoben": "Niemand zweifelt an der Notwendigkeit dieser Schritte, sofern die Beschäftigten nicht unverhältnismäßig unter den Sparmaßnahmen leiden.",
        "sutras": ["sutra_01", "sutra_08"],
    },
    {
        "id": "IV.1", "number": 7,
        "schlicht": "Man muss die schweren Mängel im Brandschutzkonzept bis Ende des Monats alle beheben, sonst muss man mit hohen Bußgeldern rechnen.",
        "gehoben": "Die gravierenden Mängel im Brandschutzkonzept sind bis Ende des Monats ausnahmslos zu beheben, da andernfalls mit empfindlichen Bußgeldern zu rechnen ist.",
        "sutras": ["sutra_12"],
    },
    {
        "id": "IV.2", "number": 8,
        "schlicht": "Am Anfang gab es Bedenken, aber man kann die Methode ohne großen Aufwand durchführen.",
        "gehoben": "Trotz anfänglicher Bedenken erweist sich die Methode als eine ohne großen Aufwand durchführbare Lösung.",
        "sutras": ["sutra_12", "sutra_06"],
    },
    {
        "id": "V.1", "number": 9,
        "schlicht": "Die Fachkommission hat die Prüfberichte schon vor Monaten vorgelegt, aber die Behörden haben sie größtenteils ignoriert. Jetzt muss man sie sofort neu bewerten.",
        "gehoben": "Die von der Fachkommission bereits vor Monaten vorgelegten, von den Behörden jedoch weitgehend ignorierten Prüfberichte erfordern eine sofortige Neubewertung.",
        "sutras": ["sutra_13"],
    },
    {
        "id": "VI.1", "number": 10,
        "schlicht": "Die Projektleiterin hatte einen innovativen Ansatz, und diesem Ansatz verdankt das Team den Erfolg. Sie übernimmt bald die ganze Entwicklungsabteilung.",
        "gehoben": "Die Projektleiterin, deren innovativem Ansatz das Team diesen Erfolg verdankt, übernimmt künftig die gesamte Entwicklungsabteilung.",
        "sutras": ["sutra_14"],
    },
    {
        "id": "VI.2", "number": 11,
        "schlicht": "Es gibt eine Krise. Um sie dauerhaft zu überwinden, muss die Regierung tiefgreifende Reformen durchführen.",
        "gehoben": "Es handelt sich um eine Krise, zu deren nachhaltiger Überwindung die Regierung tiefgreifende Reformen einleiten muss.",
        "sutras": ["sutra_14"],
    },
    {
        "id": "VII.1", "number": 12,
        "schlicht": "Wenn die Verantwortlichen die Risiken rechtzeitig bedacht hätten, hätte man den großen Schaden sicher vermeiden können.",
        "gehoben": "Hätten die Verantwortlichen die Risiken rechtzeitig in Betracht gezogen, so wäre der verheerende Schaden mit Sicherheit vermieden worden.",
        "sutras": ["sutra_15", "sutra_03"],
    },
    {
        "id": "VII.2", "number": 13,
        "schlicht": "Der Vorstand sagte: „Die Umstrukturierung ist unvermeidbar und braucht die volle Unterstützung aller Mitarbeiter.“",
        "gehoben": "Der Vorstand erklärte, die Umstrukturierung sei unausweichlich und bedürfe der uneingeschränkten Unterstützung aller Mitarbeiter.",
        "sutras": ["sutra_16", "sutra_06"],
    },
]

# Übung 2 – Fehlerjagd: 10 sentences with one error each
ERROR_HUNT: List[Dict[str, Any]] = [
    {
        "id": "eh_1",
        "number": 1,
        "wrong": "Ich interessiere mich an dieser Stelle.",
        "sentence": "Ich interessiere mich an dieser Stelle.",
        "correct": "Ich interessiere mich für diese Stelle.",
        "correction": "für diese Stelle",
        "sutra": "sutra_01",
        "sutra_number": 1,
        "focus": "Präpositionalobjekt (interessieren für + A)",
        "explanation": "interessieren sich für + A (nicht an)",
    },
    {
        "id": "eh_2",
        "number": 2,
        "wrong": "Wir haben gestern eine Entscheidung gemacht.",
        "sentence": "Wir haben gestern eine Entscheidung gemacht.",
        "correct": "Wir haben gestern eine Entscheidung getroffen.",
        "correction": "getroffen",
        "sutra": "sutra_03",
        "sutra_number": 3,
        "focus": "Nomen-Verb-Verbindung (Entscheidung treffen)",
        "explanation": "eine Entscheidung treffen (nicht machen)",
    },
    {
        "id": "eh_3",
        "number": 3,
        "wrong": "Je länger ich in Deutschland lebe, desto ich verstehe mehr.",
        "sentence": "Je länger ich in Deutschland lebe, desto ich verstehe mehr.",
        "correct": "Je länger ich in Deutschland lebe, desto mehr verstehe ich.",
        "correction": "desto mehr verstehe ich",
        "sutra": "sutra_09",
        "sutra_number": 9,
        "focus": "Zweiteilige Konnektoren (je...desto + Inversion)",
        "explanation": "Komparativ direkt nach desto, dann finite Verbform (Inversion)",
    },
    {
        "id": "eh_4",
        "number": 4,
        "wrong": "Der Bericht ist gestern geschrieben geworden.",
        "sentence": "Der Bericht ist gestern geschrieben geworden.",
        "correct": "Der Bericht ist gestern geschrieben worden.",
        "correction": "geschrieben worden",
        "sutra": "sutra_10",
        "sutra_number": 10,
        "focus": "Vorgangspassiv Perfekt (worden)",
        "explanation": "Passiv-Perfekt: worden, nicht geworden",
    },
    {
        "id": "eh_5",
        "number": 5,
        "wrong": "Ich habe mit dem Kollege gesprochen.",
        "sentence": "Ich habe mit dem Kollege gesprochen.",
        "correct": "Ich habe mit dem Kollegen gesprochen.",
        "correction": "mit dem Kollegen",
        "sutra": "sutra_05",
        "sutra_number": 5,
        "focus": "n-Deklination (Kollege ➔ Kollegen)",
        "explanation": "n-Deklination: maskuline Nomen auf -e enden im Dativ auf -en",
    },
    {
        "id": "eh_6",
        "number": 6,
        "wrong": "Trotz dem schlechten Wetter fand die Konferenz statt.",
        "sentence": "Trotz dem schlechten Wetter fand die Konferenz statt.",
        "correct": "Trotz des schlechten Wetters fand die Konferenz statt.",
        "correction": "trotz des schlechten Wetters",
        "sutra": "sutra_06",
        "sutra_number": 6,
        "focus": "Genitiv-Präposition (trotz + Genitiv)",
        "explanation": "trotz verlangt im schriftlichen B2-Standard den Genitiv",
    },
    {
        "id": "eh_7",
        "number": 7,
        "wrong": "Die Firma, deren neue Produkt erfolgreich ist, sucht Mitarbeiter.",
        "sentence": "Die Firma, deren neue Produkt erfolgreich ist, sucht Mitarbeiter.",
        "correct": "Die Firma, deren neues Produkt erfolgreich ist, sucht Mitarbeiter.",
        "correction": "deren neues Produkt",
        "sutra": "sutra_04",
        "sutra_number": 4,
        "focus": "Adjektivendung nach Relativpronomen deren",
        "explanation": "Nach deren folgt starke Adjektivendung: neues Produkt (Nominativ Neutrum: -es)",
    },
    {
        "id": "eh_8",
        "number": 8,
        "wrong": "Er sagte, dass er hat keine Zeit.",
        "sentence": "Er sagte, dass er hat keine Zeit.",
        "correct": "Er sagte, dass er keine Zeit habe.",
        "correction": "dass er keine Zeit habe",
        "sutra": "sutra_17",
        "sutra_number": 17,
        "focus": "Indirekte Rede & Konjunktiv I",
        "explanation": "dass-Satz verlangt Verb am Satzende; indirekte Rede verlangt Konjunktiv I (habe)",
    },
    {
        "id": "eh_9",
        "number": 9,
        "wrong": "Wir hätten das früher merken gekonnt.",
        "sentence": "Wir hätten das früher merken gekonnt.",
        "correct": "Wir hätten das früher merken können.",
        "correction": "merken können",
        "sutra": "sutra_16",
        "sutra_number": 16,
        "focus": "Ersatzinfinitiv bei Modalverben im Konjunktiv II",
        "explanation": "Doppelter Infinitiv: Infinitiv statt Partizip II bei Modalverben",
    },
    {
        "id": "eh_10",
        "number": 10,
        "wrong": "Ich schicke Ihnen sie morgen.",
        "sentence": "Ich schicke Ihnen sie morgen.",
        "correct": "Ich schicke sie Ihnen morgen.",
        "correction": "sie Ihnen",
        "sutra": "sutra_07",
        "sutra_number": 7,
        "focus": "Pronomen-Reihenfolge im Mittelfeld",
        "explanation": "Bei zwei Pronomen steht das Akkusativpronomen immer vor dem Dativpronomen",
    },
]

# Übung 3 – Übersetzen mit dem Sūtra: 6 translation exercises
TRANSLATIONS: List[Dict[str, Any]] = [
    {
        "number": 1,
        "english": "The success depends on whether the data are reliable.",
        "sutra": "sutra_02",
        "german": "Der Erfolg hängt davon ab, ob die Daten zuverlässig sind.",
    },
    {
        "number": 2,
        "english": "The report must be submitted by Friday.",
        "sutra": "sutra_12",
        "hint": "mit sein + zu",
        "german": "Der Bericht ist bis Freitag einzureichen.",
    },
    {
        "number": 3,
        "english": "Had I known that, I would have applied earlier.",
        "sutra": "sutra_15",
        "hint": "ohne wenn",
        "german": "Hätte ich das gewusst, hätte ich mich früher beworben.",
    },
    {
        "number": 4,
        "english": "The more data we have, the more precise the model becomes.",
        "sutra": "sutra_09",
        "german": "Je mehr Daten wir haben, desto genauer wird das Modell.",
    },
    {
        "number": 5,
        "english": "The researcher, whose new method is widely used, is giving a talk tomorrow.",
        "sutra": "sutra_14",
        "german": "Die Forscherin, deren neue Methode weit verbreitet ist, hält morgen einen Vortrag.",
        "note": "bei einem Mann: Der Forscher, dessen neue Methode …",
    },
    {
        "number": 6,
        "english": "She said she had no time.",
        "sutra": "sutra_16",
        "german": "Sie sagte, sie habe keine Zeit.",
    },
]


# =============================================================================
# TEIL D – ABHYĀSA: Topics, Materials, and 12-Week Schedule
# =============================================================================

TOPICS: List[Dict[str, Any]] = [
    {"id": "t01", "title": "Arbeit und Beruf", "questions": ["Sollte Homeoffice ein Recht für alle Beschäftigten sein?", "Ist die Vier-Tage-Woche realistisch?"]},
    {"id": "t02", "title": "Bewerbung und Karriere", "questions": ["Worauf kommt es bei einer Bewerbung heute an?", "Konzern oder Start-up: Wo lernt man mehr?"]},
    {"id": "t03", "title": "Bildung und Weiterbildung", "questions": ["Ist lebenslanges Lernen Pflicht oder Chance?", "Sollten Hochschulen praxisnäher ausbilden?"]},
    {"id": "t04", "title": "Wissenschaft, Technik, KI", "questions": ["Welche Aufgaben sollte künstliche Intelligenz übernehmen und welche nicht?", "Wie viel Datenschutz brauchen wir?"]},
    {"id": "t05", "title": "Gesundheit", "questions": ["Sollten Krankenkassen einen gesunden Lebensstil belohnen?", "Wie wirkt sich Stress am Arbeitsplatz aus?"]},
    {"id": "t06", "title": "Umwelt und Klima", "questions": ["Was kann der Einzelne für den Klimaschutz tun?", "Sollte Fliegen teurer werden?"]},
    {"id": "t07", "title": "Medien und Kommunikation", "questions": ["Machen soziale Medien einsam?", "Wie erkennt man Falschmeldungen?"]},
    {"id": "t08", "title": "Wohnen und Stadt", "questions": ["Stadt oder Land: Wo lebt es sich besser?", "Wie lässt sich bezahlbarer Wohnraum schaffen?"]},
    {"id": "t09", "title": "Gesellschaft und Zusammenleben", "questions": ["Sollte ein soziales Pflichtjahr eingeführt werden?", "Was braucht gelungene Integration?"]},
    {"id": "t10", "title": "Konsum und Wirtschaft", "questions": ["Brauchen wir weniger Konsum?", "Online oder im Laden einkaufen?"]},
    {"id": "t11", "title": "Sprache und Kultur", "questions": ["Wie lernt man eine Sprache am besten?", "Sollten Kinder schon im Kindergarten Fremdsprachen lernen?"]},
]

MATERIALS = {
    "hoeren": [
        "Deutsche Welle (Langsam gesprochene Nachrichten und weitere Angebote von DW Deutsch lernen)",
        "Tagesschau (auch Tagesschau in 100 Sekunden)",
        "Deutschlandfunk",
        "Easy German auf YouTube",
    ],
    "lesen": [
        "Nachrichtenseiten großer Zeitungen",
        "Spektrum.de für Wissenschaft",
        "heise online für Technik",
        "Nachrichtenleicht (Deutschlandfunk) für den Einstieg",
    ],
    "grammatik_und_pruefung": [
        "ein Kursbuch der Stufe B2 (z. B. Aspekte neu B2 oder Sicher! B2)",
        "ein Prüfungstrainer für das Goethe-Zertifikat B2",
    ],
    "woerterbuecher": [
        "DWDS mit Wortprofil für typische Verbindungen",
        "Duden online für Genus, Plural und Rektion",
    ],
    "wiederholung": [
        "Karteikarten mit wachsenden Abständen, z. B. mit Anki",
    ],
    "korrektur": [
        "eine Lehrkraft, ein Tandempartner oder ein Kurs",
        "Erklärungen von KI-Werkzeugen gegen eine Grammatik oder das DWDS prüfen",
    ],
}

# 12-week schedule from Teil D
SCHEDULE: List[Dict[str, Any]] = [
    {"week": 0, "label": "Start", "sutras": [], "lists": [], "focus": "Diagnose: ein vollständiger Übungssatz unter Prüfungsbedingungen"},
    {"week": 1, "label": "Woche 1", "sutras": ["sutra_01", "sutra_02", "sutra_03"], "lists": ["list_1 (Verben an bis für)", "list_5"], "focus": "Rektion, Endungen"},
    {"week": 2, "label": "Woche 2", "sutras": ["sutra_04", "sutra_05", "sutra_06"], "lists": ["list_1 (Verben an bis für)", "list_5"], "focus": "Rektion, Endungen"},
    {"week": 3, "label": "Woche 3", "sutras": ["sutra_07", "sutra_08", "sutra_09"], "lists": ["list_1 (Rest)", "list_3"], "focus": "Satzbau, Passiv"},
    {"week": 4, "label": "Woche 4", "sutras": ["sutra_10", "sutra_11", "sutra_12"], "lists": ["list_1 (Rest)", "list_3"], "focus": "Satzbau, Passiv"},
    {"week": 5, "label": "Woche 5", "sutras": ["sutra_13", "sutra_14", "sutra_15"], "lists": ["list_2"], "focus": "Attribute, Konjunktiv"},
    {"week": 6, "label": "Woche 6", "sutras": ["sutra_16", "sutra_17"], "lists": ["list_2"], "focus": "Attribute, Konjunktiv"},
    {"week": 7, "label": "Woche 7", "sutras": ["sutra_18", "sutra_19", "sutra_20"], "lists": ["list_4", "list_6"], "focus": "Wortbildung, Nominalstil, gesprochene Sprache"},
    {"week": 8, "label": "Woche 8", "sutras": ["sutra_21", "sutra_22"], "lists": ["list_4", "list_6"], "focus": "Wortbildung, Nominalstil, gesprochene Sprache"},
    {"week": 9, "label": "Woche 9", "sutras": [], "lists": [], "focus": "Alle Sūtras im Wechsel, täglich fünf aufsagen; ein Übungssatz; Schreiben und Sprechen mit Korrektur"},
    {"week": 10, "label": "Woche 10", "sutras": [], "lists": [], "focus": "Alle Sūtras im Wechsel, täglich fünf aufsagen; ein Übungssatz; Schreiben und Sprechen mit Korrektur"},
    {"week": 11, "label": "Woche 11", "sutras": [], "lists": [], "focus": "Alle Sūtras im Wechsel, täglich fünf aufsagen; ein Übungssatz; Schreiben und Sprechen mit Korrektur"},
    {"week": 12, "label": "Woche 12", "sutras": [], "lists": [], "focus": "Alle Sūtras im Wechsel, täglich fünf aufsagen; ein Übungssatz; Schreiben und Sprechen mit Korrektur"},
]

DAILY_CHECKLIST = {
    "daily": [
        {"id": "sutras", "label": "20 Min: Sūtras lernen + Śākhā", "minutes": 20},
        {"id": "flashcards", "label": "15 Min: Karteikarten aus Teil B", "minutes": 15},
        {"id": "listening_reading", "label": "45–60 Min: Hören und Lesen", "minutes": 50},
        {"id": "speaking", "label": "30 Min: Sprechen (Vortrag oder Diskussion)", "minutes": 30},
        {"id": "recitation", "label": "5 Min: Sūtras vom Vortag aufsagen", "minutes": 5},
    ],
    "weekly": [
        {"id": "writing_1", "label": "Schreibaufgabe 1 (Forumsbeitrag)"},
        {"id": "writing_2", "label": "Schreibaufgabe 2 (formelle Nachricht)"},
        {"id": "prakriya", "label": "1 Übung aus Teil C"},
        {"id": "mock_exam", "label": "Ab Woche 9: vollständiger Übungssatz", "from_week": 9},
    ],
}

# Paribhāṣās (guiding principles from the document)
PARIBHASAS = [
    "Das Register folgt der Situation. Im Gespräch und im Vorstellungsgespräch bevorzugt man den Verbalstil. In formellen Texten passt ein maßvoller Nominalstil. B2 heißt, beides zu verstehen und zwischen beidem zu wechseln.",
    "Gelernt ist eine Regel erst, wenn man sie in eigenen Sätzen anwendet. Aufsagen allein genügt nicht.",
    "Wörter lernt man mit ihrer Umgebung: Nomen mit Artikel und Plural, Verben mit Präposition und Kasus, feste Verbindungen als Ganzes.",
]


# =============================================================================
# TRANSFORMATION MATRIX (Sūtra 20)
# =============================================================================

NOMINALSTIL_MATRIX: List[Dict[str, str]] = [
    {"bedeutung": "kausal", "verbalstil": "weil die Nachfrage steigt", "nominalstil": "wegen / aufgrund der steigenden Nachfrage"},
    {"bedeutung": "konzessiv", "verbalstil": "obwohl es Bedenken gab", "nominalstil": "trotz der Bedenken"},
    {"bedeutung": "konditional", "verbalstil": "wenn Probleme auftreten", "nominalstil": "bei Problemen / im Falle von Problemen"},
    {"bedeutung": "final", "verbalstil": "um die Qualität zu verbessern", "nominalstil": "zur Verbesserung der Qualität"},
    {"bedeutung": "temporal (danach)", "verbalstil": "nachdem wir die Daten geprüft hatten", "nominalstil": "nach der Prüfung der Daten"},
    {"bedeutung": "temporal (davor)", "verbalstil": "bevor das Projekt beginnt", "nominalstil": "vor Beginn des Projekts"},
    {"bedeutung": "temporal (gleichzeitig)", "verbalstil": "während wir die Daten erheben", "nominalstil": "während der Datenerhebung"},
    {"bedeutung": "modal", "verbalstil": "indem man die Kosten senkt", "nominalstil": "durch die Senkung der Kosten"},
]


# =============================================================================
# Helper Functions
# =============================================================================

def get_sutras_for_week(week: int) -> List[Dict[str, Any]]:
    """Returns all sūtras scheduled for a given week."""
    result = []
    for sutra_id, sutra in SUTRAS.items():
        if week in sutra.get("weeks", []):
            result.append(sutra)
    return sorted(result, key=lambda s: s["number"])


def get_sutra_by_id(sutra_id: str) -> Dict[str, Any]:
    """Returns a single sūtra by ID."""
    return SUTRAS.get(sutra_id, {})


def get_schedule_for_week(week: int) -> Dict[str, Any]:
    """Returns the schedule entry for a given week."""
    for entry in SCHEDULE:
        if entry["week"] == week:
            return entry
    return {}


def get_all_flashcard_items() -> List[Dict[str, str]]:
    """Flattens all Gaṇapāṭha list items into flashcard-ready format."""
    cards = []

    # List 1: Verben mit Präpositionen
    for prep_case, verbs in GANAPATHA["list_1"]["items"]["verben"].items():
        prep = prep_case.split(" ")[0]
        for verb in verbs:
            clean = verb.split("(")[0].strip()
            front_text = clean.replace(f" {prep}", " _____")
            if front_text == clean:
                front_text = f"{clean} (_____ + {prep_case.split(' ')[-1]})"
            cards.append({
                "list": "list_1",
                "front": front_text,
                "back": f"{verb} [{prep_case}]",
                "category": "Dhātupāṭha: Verb + Präposition",
            })

    # List 1: Adjektive mit Präpositionen
    for prep_case, adjs in GANAPATHA["list_1"]["items"]["adjektive"].items():
        for adj in adjs:
            clean = adj.split("(")[0].strip()
            cards.append({
                "list": "list_1",
                "front": f"{clean} + _____ ?",
                "back": f"{adj} [{prep_case}]",
                "category": "Dhātupāṭha: Adjektiv + Präposition",
            })

    # List 1: Nomen mit Präpositionen
    for nomen in GANAPATHA["list_1"]["items"]["nomen"]:
        parts = nomen.split("+")
        if len(parts) == 2:
            cards.append({
                "list": "list_1",
                "front": f"{parts[0].strip()} + _____ ?",
                "back": f"{nomen.strip()}",
                "category": "Dhātupāṭha: Nomen + Präposition",
            })

    # List 2: Nomen-Verb-Verbindungen
    for group, items in GANAPATHA["list_2"]["items"].items():
        for item in items:
            nvv = item.split("(")[0].strip()
            simple = item.split("(")[1].rstrip(")") if "(" in item else ""
            cards.append({
                "list": "list_2",
                "front": f"Schlicht: „{simple}“ ➔ NVV?",
                "back": f"{nvv} (Schlicht: {simple})",
                "category": f"Gaṇapāṭha: NVV ({group})",
            })

    # List 3: Konnektoren
    for conn in GANAPATHA["list_3"]["items"]:
        bedeutung = conn.get("bedeutung", "")
        cards.append({
            "list": "list_3",
            "front": f"Konnektor [{bedeutung.upper()}]: Subjunktion / Adverb / Präposition?",
            "back": f"Subjunktion (Verb am Ende): {conn.get('subjunktion')}\nAdverb (Inversion / Pos. 1): {conn.get('adverb')}\nPräposition: {conn.get('praeposition')}",
            "category": f"Gaṇapāṭha: Konnektoren ({bedeutung})",
        })
    for zweit in GANAPATHA["list_3"]["zweiteilig"]:
        cards.append({
            "list": "list_3",
            "front": f"Zweiteiliger Konnektor: Vervollständigen Sie: „{zweit.split(' … ')[0]} … _____“",
            "back": f"{zweit}",
            "category": "Gaṇapāṭha: Zweiteilige Konnektoren",
        })

    # List 4: Genitiv
    for prep in GANAPATHA["list_4"]["items"]["praepositionen"]:
        cards.append({
            "list": "list_4",
            "front": f"Genitiv-Präposition: „{prep}“ + Kasus?",
            "back": f"{prep} + GENITIV (z.B. {prep} des Berichts / der Lage)",
            "category": "Gaṇapāṭha: Genitiv-Präpositionen",
        })
    for verb_gen in GANAPATHA["list_4"]["items"]["verben"]:
        cards.append({
            "list": "list_4",
            "front": f"Verb mit Genitiv: Wie lautet das feste Muster für „{verb_gen.split('(')[0].strip()}“?",
            "back": f"{verb_gen}",
            "category": "Gaṇapāṭha: Verben mit Genitiv",
        })

    # List 5: n-Deklination
    for group, nouns in GANAPATHA["list_5"]["items"].items():
        for noun in nouns:
            cards.append({
                "list": "list_5",
                "front": f"n-Deklination: Deklinieren Sie „{noun}“ im Akkusativ, Dativ & Genitiv:",
                "back": f"{noun} ➔ Akk: {noun}n, Dat: {noun}n, Gen: {noun}n (Gruppe: {group})",
                "category": f"Gaṇapāṭha: n-Deklination ({group})",
            })

    # List 6: Redemittel
    for cat, phrases in GANAPATHA["list_6"]["items"].items():
        for phrase in phrases:
            cards.append({
                "list": "list_6",
                "front": f"Redemittel für [{cat.replace('_', ' ').title()}]:",
                "back": f"„{phrase}“",
                "category": f"Gaṇapāṭha: Redemittel ({cat})",
            })

    return cards


def get_total_counts() -> Dict[str, int]:
    """Returns counts of all content items."""
    total_verbs = sum(len(v) for v in GANAPATHA["list_1"]["items"]["verben"].values())
    total_adj = sum(len(v) for v in GANAPATHA["list_1"]["items"]["adjektive"].values())
    total_nomen = len(GANAPATHA["list_1"]["items"]["nomen"])
    total_nvv = sum(len(v) for v in GANAPATHA["list_2"]["items"].values())
    total_n_dekl = sum(len(v) for v in GANAPATHA["list_5"]["items"].values())
    total_redemittel = sum(len(v) for v in GANAPATHA["list_6"]["items"].values())

    return {
        "sutras": len(SUTRAS),
        "lists": len(GANAPATHA),
        "transformations": len(TRANSFORMATIONS),
        "error_hunt": len(ERROR_HUNT),
        "translations": len(TRANSLATIONS),
        "topics": len(TOPICS),
        "verben_mit_prep": total_verbs,
        "adjektive_mit_prep": total_adj,
        "nomen_mit_prep": total_nomen,
        "nvv": total_nvv,
        "n_deklination": total_n_dekl,
        "redemittel": total_redemittel,
        "konnektoren": len(GANAPATHA["list_3"]["items"]),
        "genitiv_praep": len(GANAPATHA["list_4"]["items"]["praepositionen"]),
    }

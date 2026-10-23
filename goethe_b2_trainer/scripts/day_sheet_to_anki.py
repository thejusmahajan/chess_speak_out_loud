"""Turn a B2 sprint day sheet into an Anki deck (.apkg).

Import the .apkg in AnkiDroid (or Anki desktop), then sync to AnkiWeb.
Notes get stable GUIDs, so re-importing a fixed sheet updates cards instead of
duplicating them, and a section repeated on a later day (the G1 table) merges.

Usage:
    python scripts/day_sheet_to_anki.py study_materials/b2_sprint/day_01_new.md
Needs: pip install genanki
"""
import hashlib
import html
import io
import os
import re
import sys

import genanki

CSS = """
.card { font-family: sans-serif; font-size: 20px; text-align: left; line-height: 1.45; }
.label { font-size: 13px; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.04em; }
.big { font-size: 26px; font-weight: bold; }
.hint, .gram, .ex, .note { margin-top: 10px; }
.gram { font-size: 16px; opacity: 0.8; }
.ex { font-style: italic; }
.note { font-size: 16px; opacity: 0.85; }
.g-m { color: #2f7fd8; } .g-f { color: #d64545; } .g-n { color: #2e9e4f; } .g-pl { color: #9a7ad6; }
.cloze { font-weight: bold; color: #d68a00; }
hr { opacity: 0.3; }
"""


def _id(name):
    return int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:8], 16)


VOCAB = genanki.Model(
    _id("goethe-b2-vocab-v1"), "Goethe B2 · Vocab (EN→DE)",
    fields=[{"name": n} for n in ("English", "German", "Gender", "Grammar", "Example", "Hint")],
    templates=[{
        "name": "EN→DE",
        "qfmt": '<div class="label">Deutsch?</div><div class="big">{{English}}</div>'
                '{{#Hint}}<div class="hint">{{Hint}}</div>{{/Hint}}',
        "afmt": '{{FrontSide}}<hr id="answer"><div class="big g-{{Gender}}">{{German}}</div>'
                '<div class="gram">{{Grammar}}</div><div class="ex">{{Example}}</div>'
                '{{tts de_DE:German}}',
    }], css=CSS)

PROMPT = genanki.Model(
    _id("goethe-b2-prompt-v1"), "Goethe B2 · Prompt",
    fields=[{"name": n} for n in ("Label", "Front", "Back", "Note")],
    templates=[{
        "name": "Prompt",
        "qfmt": '<div class="label">{{Label}}</div><div>{{Front}}</div>',
        "afmt": '{{FrontSide}}<hr id="answer"><div>{{Back}}</div>'
                '{{#Note}}<div class="note">{{Note}}</div>{{/Note}}',
    }], css=CSS)

CLOZE = genanki.Model(
    _id("goethe-b2-cloze-v1"), "Goethe B2 · Cloze",
    fields=[{"name": "Text"}, {"name": "Label"}, {"name": "Extra"}],
    templates=[{
        "name": "Cloze",
        "qfmt": '<div class="label">{{Label}}</div>{{cloze:Text}}',
        "afmt": '<div class="label">{{Label}}</div>{{cloze:Text}}'
                '{{#Extra}}<div class="note">{{Extra}}</div>{{/Extra}}',
    }], css=CSS, model_type=genanki.Model.CLOZE)


def inline(md):
    """Escape, then render the markdown the sheets use: **bold**, *italic*, `code`."""
    s = html.escape(md.strip(), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def sections(text):
    """{heading: body} for every ### heading."""
    out, head, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if head:
                out[head] = "\n".join(buf)
            head, buf = None, []
        elif line.startswith("### "):
            if head:
                out[head] = "\n".join(buf)
            head, buf = line[4:].strip(), []
        elif head:
            buf.append(line)
    if head:
        out[head] = "\n".join(buf)
    return out


def table(body):
    rows = [l for l in body.splitlines() if l.lstrip().startswith("|")]
    if len(rows) < 3:
        return []
    split = lambda l: [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", l.strip())[1:-1]]
    head = split(rows[0])
    return [dict(zip(head, split(r))) for r in rows[2:]]


def numbered(body):
    """(prompts before the first <details>, answers inside it), each {n: text}."""
    pre, _, post = body.partition("<details>")
    grab = lambda t: {int(m.group(1)): m.group(2) for m in re.finditer(r"^\s*(\d+)\.\s+(.+)$", t, re.M)}
    return grab(pre), grab(post.split("</details>")[0])


def gender(german, grammar):
    if "Pl." in grammar and "kein Pl." not in grammar:
        return "pl"
    return {"der": "m", "die": "f", "das": "n"}.get(german.split(" ", 1)[0], "")


def blank(example, german):
    """Hide the German word(s) in the example so the front disambiguates meaning."""
    out = example
    for alt in [a.strip() for a in german.split("/")]:
        out = re.sub(re.escape(alt), "____", out, flags=re.I)
    return out if out != example else ""


def build(path):
    text = io.open(path, encoding="utf-8").read()
    day = int(re.search(r"^# Day (\d+)", text, re.M).group(1))
    root = "Goethe B2::Day %02d" % day
    decks, counts = {}, {}

    def add(sub, model, fields, key):
        name = "%s::%s" % (root, sub)
        deck = decks.setdefault(name, genanki.Deck(_id(name), name))
        deck.add_note(genanki.Note(model=model, fields=fields, tags=["b2_day%02d" % day],
                                   guid=genanki.guid_for("goethe-b2", key)))
        counts[sub] = counts.get(sub, 0) + 1

    # Grammar point of the day, from "## Block 4 · Grammar: G2 Nebensätze I · ..."
    # (G1 keeps its old deck name, so "G1 drills" days merge into the same subdeck.)
    gm = re.search(r"^## Block 4 · Grammar: (G\d+)([^·\n]*)", text, re.M)
    grammar, title = (gm.group(1), gm.group(2).strip()) if gm else ("G1", "")
    grammar_deck = "G1 Wortstellung" if grammar == "G1" else ("%s %s" % (grammar, title)).strip()

    secs = sections(text)
    for head, body in secs.items():
        # Vocabulary: "B1-Check A: ..." and "W01 · ..."
        m = re.match(r"(B1-Check [A-Z]|W\d\d)\b", head)
        if m:
            code = m.group(1)
            for r in table(body):
                de, en = r.get("Deutsch", ""), r.get("English", "")
                if not de or not en:
                    continue
                gram, ex = r.get("Grammar", ""), r.get("Example", "")
                hint = blank(ex, de) if code.startswith("W") else ""
                add(code, VOCAB, [inline(en), inline(de), gender(de, gram), inline(gram),
                                  inline(ex), inline(hint)], "vocab|" + de)

        elif head == "The frames":
            filled = {}
            for fm in re.finditer(r"^- \*\*(\S+) · ([^:]+):\*\* (.+)$", secs.get(
                    "The frames filled in, from your own talks", ""), re.M):
                filled[fm.group(1)] = "<b>%s:</b> %s" % (fm.group(2), inline(fm.group(3)))
            for r in table(body):
                code = r["Code"].split(" ", 1)[0]
                front = "<div class='big'>%s</div><div class='hint'>Use it when: %s</div>" % (
                    inline(r["Code"]), inline(r["Use it when"]))
                back = "<div class='big'>%s</div><div class='gram'>%s</div>" % (
                    inline(r["Frame"]), inline(r["Grammar to watch"]))
                add("Frames", PROMPT, ["Frame · say it", front, back, filled.get(code, "")],
                    "frame|" + r["Code"])

        elif head.startswith("Say it with a new topic"):
            qs, ans = numbered(body)
            for n, q in qs.items():
                if n in ans:
                    add("Frames", PROMPT, ["Say it with a new topic", inline(q), inline(ans[n]), ""],
                        "say|%d|%s" % (day, q))

        elif head == "Cloze":
            qs, ans = numbered(body)
            for n, q in qs.items():
                if n not in ans:
                    continue
                label = re.match(r"\*\*(.+?):\*\*", q)
                label = label.group(1) if label else "Cloze"
                hints = re.findall(r"\*\((.+?)\)\*", q)
                if hints:
                    label += " · hint: " + ", ".join(hints)
                a, _, rule = ans[n].partition(" — ")
                cloze = re.sub(r"\*\*(.+?)\*\*", r"{{c1::\1}}", html.escape(a, quote=False))
                add("Frames", CLOZE, [cloze, html.escape(label), inline(rule)], "cloze|" + a)

        elif "Task point" in body and "<details>" in body:
            # "Five opinion paragraphs" -> "Opinion paragraph", "Two Gründe paragraphs" -> "Gründe paragraph"
            kind = re.search(r"(\w+) paragraphs?\b", head)
            kind = kind.group(1).capitalize() if kind else "Opinion"
            extra = " + one why-sentence with a connector" if kind == "Opinion" else ""
            models = {mm.group(1): (mm.group(2), mm.group(3)) for mm in re.finditer(
                r"^- \*\*(\S+) · (\S+):\*\* (.+)$", body, re.M)}
            for r in table(body):
                code = r["Task"].split(" ", 1)[0]
                if code not in models:
                    continue
                front = "<b>%s</b><div>%s</div><div class='hint'>Frame: <b>%s</b>%s</div>" % (
                    inline(r["Task"]), inline(r["Task point"]), inline(r["Your frame"]), extra)
                key = "opinion|" if kind == "Opinion" else kind.lower() + "|"
                add("Frames", PROMPT, [kind + " paragraph", front, inline(models[code][1]), ""],
                    key + r["Task"])

        elif head.startswith("G1 ·") and "Class" in body:
            for r in table(body):
                front = "Word order after:<div class='big'>%s</div>" % inline(r["Words"])
                back = "<div class='big'>%s</div><div>%s</div><div class='ex'>%s</div>" % (
                    inline(r["Class"]), inline(r["What happens"]), inline(r["Example"]))
                add("G1 Wortstellung", PROMPT, ["G1 · which class?", front, back, ""],
                    "g1class|" + r["Class"])

        elif "transformations" in head:
            qs, ans = numbered(body)
            for n, q in qs.items():
                if n not in ans:
                    continue
                a, _, rule = ans[n].partition(" — ")
                add(grammar_deck, PROMPT, ["%s · rewrite" % grammar, inline(q), inline(a), inline(rule)],
                    "%str|%d|%s" % (grammar.lower(), day, q))

    # Error lines anywhere: "✗ *wrong* → ✓ *right* explanation"
    for em in re.finditer(r"✗ \*(.+?)\* → ✓ \*(.+?)\*(.*)$", text, re.M):
        add("Fix the error", PROMPT, ["Find and fix the error", inline(em.group(1)),
                                      inline(em.group(2)), inline(em.group(3))],
            "fix|" + em.group(1))

    # Memory palace locus built today
    lm = re.search(r"\*\*Locus (\d+) — ([^.]+)\.\*\* Words the image holds: \*(.+?)\*\s*\n\s*\nImage: (.+)",
                   text)
    if lm:
        front = "Palace A · Locus %s — <b>%s</b><div class='hint'>Which phrases does the image hold?</div>" % (
            lm.group(1), html.escape(lm.group(2)))
        back = "<div>%s</div>" % "<br>".join(inline(p) for p in lm.group(3).rstrip(".").split(" · "))
        add("Frames", PROMPT, ["Memory palace", front, back, inline(lm.group(4))],
            "locus|A|" + lm.group(1))

    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "anki")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "day_%02d.apkg" % day)
    genanki.Package(list(decks.values())).write_to_file(out)
    for sub, n in counts.items():
        print("%-18s %3d" % (sub, n))
    print("total %d notes -> %s" % (sum(counts.values()), out))


if __name__ == "__main__":
    build(sys.argv[1])

"""Plan and check B2 sprint day sheets against the kit (goethe_b2_kit.zip).

    python scripts/verify_day_sheet.py plan 2026-10-26
        Which sheet belongs to that date, what it contains, which words and loci are due
        for review (learned 1, 3, 7, 14, 30 days earlier, counted on PLAN dates), whether it
        is a Sunday, and which earlier sheets do not exist yet.

    python scripts/verify_day_sheet.py check study_materials/b2_sprint/day_05.md [...]
        Copied German verbatim (word batches, grammar points, speeches, frames, worked
        examples, locus images, routines, model emails/posts), model posts in range with
        two sentences per paragraph, clock times contiguous, header and Tomorrow dates
        on the calendar. Exit 1 on any failure.

A check that passes proves nothing until it has failed once: after editing this file,
break one copied word in a sheet, watch `check` fail, and restore the sheet.
"""
import datetime as dt
import io
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIT = os.path.join(ROOT, "knowledge", "b2_kit_to_produce_daily_work_material", "goethe_b2_kit.zip")
SHEETS = os.path.join(ROOT, "study_materials", "b2_sprint")
YEAR = 2026
WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
REVIEW_GAPS = (1, 3, 7, 14, 30)


def load_kit():
    z = zipfile.ZipFile(KIT)
    read = lambda name: z.read("goethe_b2_kit/" + name).decode("utf-8")
    return read("01_generator_prompt.md"), read("02_toolkit.md"), read("03_speech_log.md")


GEN, TK, SPEECH = load_kit()


def cells(line):
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def rows(block):
    return [cells(l) for l in block.splitlines()
            if l.lstrip().startswith("|") and not re.match(r"^\s*\|\s*-{3}", l)]


def section(text, heading_re, stop_re=r"^#{1,3} "):
    """Body after the first line matching heading_re, up to the next heading matching stop_re."""
    m = re.search(heading_re, text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    end = re.search(stop_re, rest, re.M)
    return rest[:end.start()] if end else rest


def ddmm(s):
    m = re.search(r"(\d\d)\.(\d\d)\.", s)
    return dt.date(YEAR, int(m.group(2)), int(m.group(1)))


def label(d):
    return "%s %02d.%02d." % (WEEKDAYS[d.weekday()], d.day, d.month)


# ---------------------------------------------------------------- the calendar

def calendar():
    """[{label, file, date, memorise, grammar, words, produce, speech}] in order.
    Sheets 1-19 come from the generator's calendar (with merged sheets 13-14, 15-16, 17-18);
    20 onwards from toolkit §4, plus the batches the merges moved (W14 -> 28, W16 -> 38, W18 -> 39)."""
    out = []
    gen_cal = section(GEN, r"^\*\*Sheets 1 to 19\*\*", r"^\*\*Items moved")
    for r in rows(gen_cal)[1:]:
        m = re.match(r"\**Day (\d+)(?:–(\d+))?", r[0])
        if not m:
            continue
        a, b = m.group(1), m.group(2)
        name = a if not b else "%s-%s" % (a, b)
        out.append(dict(label="Day " + name.replace("-", "–"), file="day_%s.md" % (
            "%02d" % int(a) if not b else "%02d-%02d" % (int(a), int(b))), num=int(b or a),
            date=ddmm(r[1]), memorise=r[2], grammar=r[3], words=r[4], produce=r[5], speech=r[6]))
    moved = {int(d): w for w, d in re.findall(r"(W\d\d) → Day (\d+)", GEN)}
    plan = section(TK, r"^## 4\. The 58-day plan", r"^## 5\.")
    for r in rows(plan)[1:]:
        if not r[0].isdigit() or int(r[0]) <= 19:
            continue
        n = int(r[0])
        words = r[4] + (" + " + moved[n] if n in moved else "")
        out.append(dict(label="Day %d" % n, file="day_%02d.md" % n, num=n, date=ddmm(r[1]),
                        memorise=r[2], grammar=r[3], words=words, produce=r[5], speech="(plan)"))
    return out


def batches(words):
    return re.findall(r"B1-Check [AB]|W\d\d", words)


def plan(date_str):
    day = dt.date.fromisoformat(date_str)
    cal = calendar()
    today = [s for s in cal if s["date"] == day]
    print("%s %s" % (label(day), day.year))
    if not today:
        print("  No sheet on this date (before Day 1 or after the exam).")
        return 0
    s = today[0]
    exists = os.path.exists(os.path.join(SHEETS, s["file"]))
    print("  Sheet: %s -> %s%s" % (s["label"], s["file"], "  (exists)" if exists else ""))
    for k in ("memorise", "grammar", "words", "produce", "speech"):
        print("  %-9s %s" % (k.capitalize() + ":", s[k]))
    print("  Sunday:   %s" % ("yes: Block 6 adds the weekly error-type rewrite" if day.weekday() == 6 else "no"))
    print("Reviews due (counted on plan dates):")
    for gap in REVIEW_GAPS:
        for p in cal:
            if (day - p["date"]).days == gap:
                print("  +%-2d %s (%s): words %s · loci %s" % (
                    gap, p["label"], label(p["date"]), ", ".join(batches(p["words"])) or "none", p["memorise"]))
    missing = [p["file"] for p in cal if p["date"] < day
               and not os.path.exists(os.path.join(SHEETS, p["file"]))]
    print("Earlier sheets not built yet: %s" % (", ".join(missing) or "none"))
    return 0


# ---------------------------------------------------------------- the checks

class Report:
    def __init__(self, name):
        self.name, self.fails, self.oks = name, [], 0

    def ok(self, cond, what, detail=""):
        if cond:
            self.oks += 1
        else:
            self.fails.append(what + (": " + detail if detail else ""))


def lines_of(text):
    return {re.sub(r"^>\s?", "", l).strip() for l in text.splitlines()}


def check_vocab(sheet, rep):
    for m in re.finditer(r"^### (B1-Check [AB]|W\d\d)\b.*$", sheet, re.M):
        code = m.group(1)
        body = section(sheet[m.start():], r"^### .*$", r"^#{2,3} |^Rows copied")
        got = rows(body)
        src = rows(section(TK, r"^## %s\b.*$" % re.escape(code), r"^## "))
        if got and got[0] and got[0][0] in ("✓", ""):
            got = [r[1:] for r in got]
        exp = []
        for r in src[1:]:
            r = list(r)
            # nouns only: a phrase such as "die Initiative ergreifen" ends in a verb and keeps its –
            if r[0].split(" ", 1)[0] in ("der", "die", "das") and r[0].split()[-1][:1].isupper() and r[1] == "–":
                r[1] = "kein Pl."
            exp.append(r)
        bad = [(" | ".join(e), " | ".join(g)) for e, g in zip(exp, got[1:]) if e != g]
        rep.ok(len(got) - 1 == len(exp) and not bad, "%s rows verbatim (%d of %d)" % (code, len(got) - 1, len(exp)),
               str(bad[:2]))
        cnt = re.search(r"Rows copied:[^\n]*?%s (\d+) of (\d+)" % re.escape(code), sheet)
        rep.ok(cnt and int(cnt.group(1)) == int(cnt.group(2)) == len(exp), "%s 'Rows copied' line" % code)


def check_grammar(sheet, rep):
    have = lines_of(sheet)
    for g in re.findall(r"^### (G\d+) ·", sheet, re.M):
        src = section(TK, r"^### %s ·.*$" % g)
        missing = [l.strip() for l in src.splitlines() if l.strip() and l.strip() not in have]
        rep.ok(not missing, "%s copied in full" % g, str(missing[:2]))


def check_speeches(sheet, rep):
    have = lines_of(sheet)
    for m in re.finditer(r"^## (\d)\. (.+)$", SPEECH, re.M):
        german = section(SPEECH[m.start():], r"^### German version$", r"^#{2,3} ")
        src = [l.strip() for l in german.splitlines() if l.strip()]
        if any(l in have for l in src if len(l) > 40):  # any paragraph present: the whole speech must be
            missing = [l for l in src if l not in have]
            rep.ok(not missing, "speech %s German version verbatim" % m.group(1), str(missing[:1]))


def bank():
    bank8 = section(GEN, r"^## 8\. Style frame bank", r"^## 9\.")
    frames = {}
    for r in rows(bank8):
        if len(r) >= 4 and re.match(r"^(E-\d|H-[SV]|M-\d|G-\d|V-\d|A-\d|X-\d|S-\d)\b", r[0]):
            frames[r[0]] = r[2]
    examples = {(c, t): x for c, t, x in re.findall(r"^- \*\*([A-Z]-\d) · ([^:]+):\*\* (.+)$", bank8, re.M)}
    loci = [r for r in rows(section(bank8, r"^### Palace A ·.*$", r"^### ")) if len(r) == 4][1:]
    return frames, examples, loci


FRAMES, EXAMPLES, LOCI_A = bank()
LOCI_B = [r for r in rows(section(TK, r"^### Palace B — .*$", r"^### ")) if len(r) == 5][1:]
LOCI_C = [r for r in rows(section(TK, r"^### Palace C — .*$", r"^### ")) if len(r) == 5][1:]
# the generator's Palace C table: the link image to add at each locus ("—" = none)
LINKS_C = [r[3] for r in rows(section(GEN, r"^### Palace C · .*$", r"^### ")) if len(r) == 4][1:]
# toolkit §10: the Vortrag script and the three model talks (V1-V3); placeholders unescaped
VORTRAG = section(TK, r"^## 10\. .*$", r"^## ").replace("\\[", "[").replace("\\]", "]")


def check_frames(sheet, rep):
    for r in rows(sheet):
        if r and r[0] in FRAMES:
            frame = r[1] if len(r) == 2 else (r[2] if len(r) >= 4 else None)
            if frame is not None:
                rep.ok(frame == FRAMES[r[0]], "frame %s" % r[0], frame)
    for c, t, x in re.findall(r"^- \*\*([A-Z]-\d) · ([^:]+):\*\* (.+)$", sheet, re.M):
        if (c, t) in EXAMPLES:
            rep.ok(x == EXAMPLES[(c, t)], "worked example %s · %s" % (c, t), x)
    pat = r"\*\*(?:Palace ([A-D]) · )?Locus (\d+) — ([^.]+)\.\*\* Words the image holds: \*(.+?)\*\s*\n\s*\nImage: (.+)"
    for p, n, name, words, image in re.findall(pat, sheet):
        table = {"B": LOCI_B, "C": LOCI_C, "": LOCI_A, "A": LOCI_A}.get(p)
        if not table:
            continue
        src = table[int(n) - 1]
        rep.ok(words.rstrip(".") == src[-2].rstrip("."), "Palace %s locus %s words" % (p or "A", n), words)
        rep.ok(image.strip() == src[-1], "Palace %s locus %s image" % (p or "A", n), image[:60])
        if p == "C" and LINKS_C[int(n) - 1] != "—":
            rep.ok("Link image: " + LINKS_C[int(n) - 1] in lines_of(sheet), "Palace C locus %s link image" % n)
    # Palace C frames (C-Einleitung-1, C-Alternativen-2, ...) are pieces of the toolkit's Vortrag script,
    # and their worked examples are sentences from the model talks V1-V3
    c_frames = {}
    for r in rows(sheet):
        if r and re.match(r"^C-[A-Za-zä]+-\d", r[0]) and len(r) >= 4:
            c_frames[r[0]] = r[2]
            rep.ok(r[2] in VORTRAG, "Palace C frame %s is in the toolkit §10 script" % r[0], r[2])
    # a worked example is either a sentence of V1-V3, or it uses the frame's fixed opening words
    for c, t, x in re.findall(r"^- \*\*(C-\S+) · ([^:]+):\*\* (.+)$", sheet, re.M):
        lead = re.split(r"…|\[", c_frames.get(c, "\0"))[0].strip()
        rep.ok(x in VORTRAG or (lead and lead in x), "worked example %s · %s" % (c, t), x)
    if "| Time | Move | Frame |" in sheet:
        src = [l for l in section(TK, r"^### The script$").splitlines() if l.startswith("|")]
        rep.ok(all(l in sheet for l in src), "Vortrag script table verbatim")


def check_toolkit_pieces(sheet, rep):
    have, flat = lines_of(sheet), sheet
    if "### The 50-minute routine" in sheet:
        for h in ("### The 50-minute routine", "### The final check"):
            src = [re.sub(r"^\d+\.\s+", "", l).strip() for l in section(TK, r"^%s.*$" % re.escape(h)).splitlines() if l.strip()]
            missing = [l for l in src if l not in flat]
            rep.ok(not missing, h[4:], str(missing[:1]))
    if "Register traps" in sheet:
        src = [l for l in section(TK, r"^### Register traps$").splitlines() if l.startswith("- ")]
        rep.ok(all(l in have for l in src), "register traps verbatim")
    if "| Order | Function |" in sheet:
        src = [l for l in section(TK, r"^### Sorting the shuffled points$").splitlines() if l.startswith("|")]
        rep.ok(all(l in flat for l in src), "sorting table verbatim")
    for m in re.finditer(r"^### ((?:F|N)\d) · .*$", TK, re.M):
        body = [l.strip() for l in section(TK[m.start():], r"^### .*$").splitlines() if l.strip()]
        # any line unique to this model present (not a shared Gruß line): the whole model must be
        if any(l in have for l in body if len(l) > 40 and TK.count(l) == 1):
            missing = [l for l in body if l not in have]
            rep.ok(not missing, "model %s verbatim" % m.group(1), str(missing[:1]))
    # Mustervorträge V1-V3: any paragraph present, the whole talk must be
    for m in re.finditer(r"^\*\*(V\d) · [^*]+\*\* — .*$", VORTRAG, re.M):
        body = re.split(r"^\*\*V\d · |^### ", VORTRAG[m.end():], maxsplit=1, flags=re.M)[0]
        paras = [l.strip() for l in body.splitlines() if l.strip()]
        if any(l in have for l in paras if len(l) > 40):
            missing = [l for l in paras if l not in have]
            rep.ok(not missing, "Mustervortrag %s verbatim" % m.group(1), str(missing[:1])[:80])
    if "Thema + why you chose it" in sheet:
        src = [l.strip() for l in section(TK, r"^### Notes in the preparation room$").splitlines()
               if re.match(r"^\d\. ", l)]
        rep.ok(len(src) == 6 and all(l in have for l in src), "six keyword lines verbatim")


def words_of(t):
    return len(t.replace("*", "").replace("\\", "").replace("–", " ").split())


def check_models(sheet, rep):
    for lab, n, body in re.findall(r"<summary>Model: ([^<]*?)\((\d+) words\)</summary>(.+?)</details>", sheet, re.S):
        w = words_of(body)
        teil2 = re.search(r"\bN\d", lab)
        lo, hi = (110, 130) if teil2 else (170, 190)
        rep.ok(w == int(n), "model '%s' word count stated %s, counted %d" % (lab.strip(), n, w))
        rep.ok(lo <= w <= hi, "model '%s' within %d-%d words" % (lab.strip(), lo, hi), str(w))
        if not teil2:
            for para in [p.strip() for p in body.strip().split("\n\n") if p.strip()]:
                plain = para.replace("*", "")
                rep.ok(len(re.findall(r"[.!?](?:\s|$)", plain)) >= 2,
                       "model paragraph has two sentences (final check 1)", plain[:60])


def t2m(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def check_clock(sheet, rep):
    rng = r"(\d:\d\d)–(\d:\d\d)"
    blocks, cur = [], None
    for line in sheet.split("\n"):
        if line.startswith("```"):
            continue
        hm = re.match(r"^## .*?" + rng, line) or re.match(r"^\*\*Break · " + rng, line)
        if hm:
            cur = dict(s=t2m(hm.group(1)), e=t2m(hm.group(2)), l1=[], name=line[:40])
            blocks.append(cur)
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is None:
            continue
        h3 = re.match(r"^### .*?" + rng, line)
        if h3:
            cur["l1"].append(dict(s=t2m(h3.group(1)), e=t2m(h3.group(2)), l2=[]))
            continue
        b = re.match(r"^- \[ \] \*\*" + rng + r"\*\*", line)
        if b:
            item = (t2m(b.group(1)), t2m(b.group(2)))
            (cur["l1"][-1]["l2"] if cur["l1"] else cur.setdefault("l2", [])).append(item)

    def contiguous(items, s, e):
        return bool(items) and items[0][0] == s and items[-1][1] == e and all(
            a[1] == b[0] for a, b in zip(items, items[1:]))

    rep.ok(contiguous([(b["s"], b["e"]) for b in blocks], 0, 180), "blocks run 0:00-3:00 without gaps")
    for b in blocks:
        if b["l1"]:
            rep.ok(contiguous([(x["s"], x["e"]) for x in b["l1"]], b["s"], b["e"]), "sub-blocks of " + b["name"])
            for x in b["l1"]:
                if x["l2"]:
                    rep.ok(contiguous(x["l2"], x["s"], x["e"]), "steps inside %d-%d of %s" % (x["s"], x["e"], b["name"]))
        elif b.get("l2"):
            rep.ok(contiguous(b["l2"], b["s"], b["e"]), "steps of " + b["name"])


def check_dates(sheet, path, rep):
    cal = {c["label"]: c for c in calendar()}
    m = re.match(r"# (Day \d+(?:–\d+)?) · (\w\w) (\d\d\.\d\d\.)\d{4}", sheet)
    if not m or m.group(1) not in cal:
        rep.ok(False, "header names a calendar day", sheet[:60])
        return
    c = cal[m.group(1)]
    rep.ok(label(c["date"]) == "%s %s" % (m.group(2), m.group(3)), "header date is the plan date (%s)" % label(c["date"]))
    t = re.search(r"\*\*Tomorrow, (Day \d+(?:–\d+)?) \((\w\w \d\d\.\d\d\.)\)", sheet)
    if t and t.group(1) in cal:
        rep.ok(label(cal[t.group(1)]["date"]) == t.group(2), "Tomorrow line date (%s)" % label(cal[t.group(1)]["date"]))
    is_sunday = c["date"].weekday() == 6
    rep.ok(("Sunday" in sheet) == is_sunday, "Sunday task only on Sundays")


def check(paths):
    failed = 0
    for path in paths:
        sheet = io.open(path, encoding="utf-8").read()
        rep = Report(os.path.basename(path))
        for fn in (check_vocab, check_grammar, check_speeches, check_frames, check_toolkit_pieces,
                   check_models, check_clock):
            fn(sheet, rep)
        check_dates(sheet, path, rep)
        print("%s: %d ok, %d failed" % (rep.name, rep.oks, len(rep.fails)))
        for f in rep.fails:
            print("   FAIL " + f)
        failed += len(rep.fails)
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "plan":
        sys.exit(plan(sys.argv[2]))
    if len(sys.argv) >= 3 and sys.argv[1] == "check":
        sys.exit(check(sys.argv[2:]))
    print(__doc__)
    sys.exit(2)

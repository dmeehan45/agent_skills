#!/usr/bin/env python3
"""Measure how expensive a piece of writing is to read.

Every number here is a thermometer, not a target. The metrics catch the
mechanical causes of reading effort — long sentences, monotone rhythm, buried
points, walls of unbroken text, machine-sounding phrasing. None of them can
tell you whether the piece still means what the author meant. That judgement
stays with the person running the skill.

Standard library only. Python 3.8+.

    python3 load_report.py draft.md
    python3 load_report.py draft.md --profile blast
    python3 load_report.py after.md --baseline before.md
    python3 load_report.py after.md --json > report.json

Exit codes: 0 always, unless --strict is passed, in which case any FLAG exits 1.
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Reading-rate constants
# --------------------------------------------------------------------------
# Brysbaert (2019), meta-analysis of 190 studies: adult English silent reading
# of non-fiction averages 238 wpm; reading aloud averages 183 wpm.
WPM_SILENT_NONFICTION = 238
WPM_ALOUD = 183

PROFILES = {
    # name: (target minutes, max paragraph words, label)
    "blast": (2.0, 60, "email blast / note to users"),
    "brief": (5.0, 80, "quick write-up, read in one sitting"),
    "explainer": (10.0, 100, "longer explainer, still scannable"),
}

# --------------------------------------------------------------------------
# Phrase lists
# --------------------------------------------------------------------------
FILLER_PHRASES = [
    "it is important to note",
    "it's important to note",
    "it is worth noting",
    "it's worth noting",
    "it should be noted",
    "please note that",
    "in order to",
    "due to the fact that",
    "the fact that",
    "at this point in time",
    "in the event that",
    "for the purpose of",
    "with regard to",
    "with respect to",
    "in terms of",
    "as a matter of fact",
    "needless to say",
    "it goes without saying",
    "the vast majority of",
    "a wide range of",
    "a number of",
    "in the process of",
    "there is a need to",
    "we would like to",
    "this article will",
    "in this article",
    "in this post",
    "as mentioned above",
    "as previously stated",
    "first and foremost",
    "last but not least",
    "in conclusion",
    "to summarize",
    "moving forward",
]

AI_TELL_PHRASES = [
    "delve",
    "tapestry",
    "landscape of",
    "realm of",
    "navigate the complexities",
    "navigating the complexities",
    "in today's fast-paced",
    "in an era where",
    "ever-evolving",
    "game-changer",
    "game changing",
    "unlock the power",
    "unlock the potential",
    "harness the power",
    "leverage",
    "seamless",
    "seamlessly",
    "robust",
    "holistic",
    "multifaceted",
    "underscore",
    "underscores",
    "testament to",
    "at the end of the day",
    "the key takeaway",
    "let's dive in",
    "dive deep",
    "deep dive",
    "buckle up",
    "here's the thing",
    "that being said",
    "furthermore",
    "moreover",
    "additionally",
    "consequently",
    "crucial",
    "pivotal",
    "vital",
    "meticulous",
    "meticulously",
    "cornerstone",
    "paradigm shift",
    "elevate your",
    "supercharge",
    "transformative",
    "empower",
    "resonate",
    "curated",
    "bespoke",
    "myriad",
    "plethora",
    "utilize",
    "utilizing",
    "commence",
    "endeavor",
    "facilitate",
    "encompass",
    "encompasses",
]

AI_TELL_PATTERNS = [
    (r"\bnot (?:just|only|merely|simply)\b[^.!?]{2,80}?\bbut\b", "not just X but Y"),
    (r"\b(?:it|this|that)'?s not [^.!?]{2,60}?[,—-] (?:it|this|that)'?s\b", "it's not X, it's Y"),
    (r"\bisn'?t (?:about |just )?[^.!?]{2,60}?[,—-] (?:it'?s|they'?re)\b", "isn't X, it's Y"),
    (r"\b(?:more|less) than just an? \w+", "more than just a"),
    (r"\bwhether you'?re [^.!?]{2,60}? or\b", "whether you're X or Y"),
    (r"^\s*(?:In conclusion|To sum up|In summary|Overall)[,:]", "essay-closer opener"),
    (r"\bwe(?:'| a)re (?:excited|thrilled|delighted) to\b", "press-release enthusiasm"),
]

# Subordinators and empty openers that push the point away from the front of a
# sentence. Used only on the first sentence of each paragraph.
BURIED_OPENERS = [
    "while", "whilst", "although", "though", "if", "when", "as ", "because",
    "since", "given", "despite", "in order", "having", "after", "before",
    "in the context", "in an effort", "with the", "there is", "there are",
    "there's", "it is", "it's important", "one of the", "many of",
    "over the past", "for the past", "in recent", "as we", "as you",
]

BE_VERBS = {"is", "are", "was", "were", "be", "been", "being", "am"}

IRREGULAR_PARTICIPLES = {
    "made", "done", "seen", "given", "taken", "known", "shown", "written",
    "held", "built", "found", "sent", "kept", "left", "lost", "meant",
    "paid", "put", "read", "run", "said", "sold", "set", "spent", "told",
    "understood", "won", "brought", "bought", "caught", "chosen", "driven",
    "drawn", "eaten", "fallen", "felt", "forgotten", "hidden", "led", "let",
    "cut", "beaten", "broken", "begun", "dealt",
}

NOMINALIZATION_SUFFIXES = (
    "tion", "sion", "ment", "ness", "ity", "ance", "ence", "ancy", "ency",
    "ization", "isation", "ability", "ibility",
)

NOMINALIZATION_STOPLIST = {
    "moment", "element", "comment", "environment", "department", "equipment",
    "instrument", "document", "segment", "cement", "parent", "city", "quality",
    "community", "opportunity", "security", "ability", "activity", "identity",
    "reality", "priority", "majority", "minority", "authority", "company",
    "business", "finance", "advance", "distance", "balance", "chance",
    "audience", "experience", "evidence", "science", "difference", "reference",
    "sentence", "silence", "essence", "absence", "presence", "instance",
    "customer", "question", "session", "version", "vision", "mission",
}

ABBREVIATIONS = [
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "inc",
    "ltd", "co", "approx", "fig", "no", "eg", "ie", "am", "pm", "u.s", "u.k",
]


# --------------------------------------------------------------------------
# Markdown parsing
# --------------------------------------------------------------------------
def strip_front_matter(raw):
    """Drop a leading YAML block. It is metadata, not something anyone reads."""
    if not raw.startswith("---\n"):
        return raw
    end = raw.find("\n---", 3)
    if end == -1:
        return raw
    return raw[raw.find("\n", end + 1) + 1:]


class Document:
    """A very small markdown reader: enough to tell prose from structure."""

    def __init__(self, raw):
        self.raw = strip_front_matter(raw)
        self.headings = []       # (level, text)
        self.paragraphs = []     # str
        self.list_items = []     # str
        self.bold_spans = []     # str
        self.blocks = []         # ("heading"|"paragraph"|"list"|"break", text)
        self._parse()

    def _parse(self):
        lines = self.raw.split("\n")
        in_fence = False
        buffer = []

        def flush():
            if buffer:
                text = inline_clean(" ".join(buffer))
                if text:
                    self.paragraphs.append(text)
                    self.blocks.append(("paragraph", text))
                buffer.clear()

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```") or stripped.startswith("~~~"):
                flush()
                in_fence = not in_fence
                self.blocks.append(("break", ""))
                continue
            if in_fence:
                continue

            if not stripped:
                flush()
                continue

            heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading:
                flush()
                text = inline_clean(heading.group(2))
                self.headings.append((len(heading.group(1)), text))
                self.blocks.append(("heading", text))
                continue

            if re.match(r"^([-*+]|\d+[.)])\s+", stripped):
                flush()
                text = inline_clean(re.sub(r"^([-*+]|\d+[.)])\s+", "", stripped))
                self.list_items.append(text)
                self.blocks.append(("list", text))
                continue

            if stripped.startswith(">") or stripped.startswith("|"):
                flush()
                self.blocks.append(("break", ""))
                continue

            if re.match(r"^([-*_]\s*){3,}$", stripped):
                flush()
                self.blocks.append(("break", ""))
                continue

            buffer.append(stripped)

        flush()

        for span in re.findall(r"\*\*(.+?)\*\*|__(.+?)__", self.raw):
            text = span[0] or span[1]
            self.bold_spans.append(inline_clean(text))

    @property
    def prose_units(self):
        """Everything a reader actually reads as sentences."""
        return self.paragraphs + self.list_items


def inline_clean(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*|__|\*|_|~~", "", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# --------------------------------------------------------------------------
# Tokenising
# --------------------------------------------------------------------------
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")


def words(text):
    return WORD_RE.findall(text)


DOT = "\x00"


def split_sentences(text):
    guarded = text
    for abbr in ABBREVIATIONS:
        guarded = re.sub(
            r"\b" + re.escape(abbr) + r"\.", abbr + DOT, guarded, flags=re.I
        )
    guarded = re.sub(r"\b([A-Z])\.", r"\1" + DOT, guarded)
    parts = re.split(r"(?<=[.!?])[\"'”’)\]]*\s+", guarded)
    out = []
    for part in parts:
        part = part.replace(DOT, ".").strip()
        if words(part):
            out.append(part)
    return out


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|[^laeiouy]e|ed)$", "", w)
    w = re.sub(r"^y", "", w)
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------
def find_phrases(text, phrases):
    low = text.lower().replace("’", "'")
    hits = {}
    for phrase in phrases:
        pattern = r"\b" + r"\s+".join(re.escape(w) for w in phrase.split()) + r"\b"
        count = len(re.findall(pattern, low))
        if count:
            hits[phrase] = count
    return hits


def find_patterns(text, patterns):
    hits = {}
    for pattern, label in patterns:
        count = len(re.findall(pattern, text, flags=re.I | re.M))
        if count:
            hits[label] = hits.get(label, 0) + count
    return hits


def passive_hits(sentence):
    toks = [w.lower() for w in words(sentence)]
    count = 0
    for i, tok in enumerate(toks[:-1]):
        if tok not in BE_VERBS:
            continue
        j = i + 1
        while j < len(toks) and (toks[j].endswith("ly") or toks[j] in {"being", "been", "not", "also", "now", "then"}):
            j += 1
        if j >= len(toks):
            continue
        nxt = toks[j]
        if nxt in IRREGULAR_PARTICIPLES or (nxt.endswith("ed") and len(nxt) > 4):
            count += 1
    return count


def nominalizations(all_words):
    found = []
    for w in all_words:
        low = w.lower()
        if len(low) < 7 or low in NOMINALIZATION_STOPLIST:
            continue
        if low.endswith(NOMINALIZATION_SUFFIXES):
            found.append(low)
    return found


def analyse(raw, profile="brief"):
    doc = Document(raw)
    target_minutes, para_ceiling, profile_label = PROFILES[profile]

    prose = " ".join(doc.prose_units)
    all_words = words(prose)
    total_words = len(all_words)

    sentences = []
    for unit in doc.prose_units:
        sentences.extend(split_sentences(unit))
    lengths = [len(words(s)) for s in sentences if words(s)]

    heading_words = sum(len(words(h[1])) for h in doc.headings)
    body_words = total_words + heading_words

    # --- rhythm ---
    if lengths:
        mean_len = statistics.mean(lengths)
        median_len = statistics.median(lengths)
        stdev_len = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
        cv = stdev_len / mean_len if mean_len else 0.0
        ordered = sorted(lengths)
        p90 = ordered[min(len(ordered) - 1, int(round(0.9 * (len(ordered) - 1))))]
        max_len = max(lengths)
        over_25 = sum(1 for n in lengths if n > 25) / len(lengths)
        over_35 = sum(1 for n in lengths if n > 35) / len(lengths)
    else:
        mean_len = median_len = stdev_len = cv = p90 = max_len = 0
        over_25 = over_35 = 0.0

    longest_sentences = sorted(
        ((len(words(s)), s) for s in sentences), key=lambda x: -x[0]
    )[:5]

    # --- paragraphs and structure ---
    para_lengths = [len(words(p)) for p in doc.paragraphs] or [0]
    run, longest_run = 0, 0
    for kind, text in doc.blocks:
        if kind == "paragraph":
            run += len(words(text))
            longest_run = max(longest_run, run)
        elif kind in {"heading", "break"}:
            run = 0
        elif kind == "list":
            run = 0
    words_per_heading = body_words / len(doc.headings) if doc.headings else body_words

    # --- scan payload: what a 20%-reader actually gets ---
    payload_parts = [h[1] for h in doc.headings]
    payload_parts += [split_sentences(p)[0] for p in doc.paragraphs if split_sentences(p)]
    payload_parts += doc.bold_spans
    payload_words = sum(len(words(p)) for p in payload_parts)
    payload_share = payload_words / body_words if body_words else 0.0
    entry_points = len(doc.headings) + len(doc.list_items) + len(doc.bold_spans)
    entry_density = entry_points / body_words * 500 if body_words else 0.0

    # --- front-loading ---
    buried = []
    for p in doc.paragraphs:
        first = split_sentences(p)
        if not first:
            continue
        low = first[0].lower().lstrip("\"'“ ")
        if any(low.startswith(opener) for opener in BURIED_OPENERS):
            buried.append(first[0][:90])
    buried_share = len(buried) / len(doc.paragraphs) if doc.paragraphs else 0.0

    # --- word texture ---
    syl_counts = [syllables(w) for w in all_words]
    long_words = sum(1 for n in syl_counts if n >= 3)
    long_word_share = long_words / total_words if total_words else 0.0
    total_syllables = sum(syl_counts)
    noms = nominalizations(all_words)
    nom_rate = len(noms) / total_words * 1000 if total_words else 0.0

    passives = sum(1 for s in sentences if passive_hits(s))
    passive_share = passives / len(sentences) if sentences else 0.0

    if lengths and total_words:
        asl = total_words / len(lengths)
        asw = total_syllables / total_words
        flesch = 206.835 - 1.015 * asl - 84.6 * asw
        fk_grade = 0.39 * asl + 11.8 * asw - 15.59
    else:
        flesch = fk_grade = 0.0

    em_dashes = raw.count("—")
    em_dash_rate = em_dashes / body_words * 1000 if body_words else 0.0

    contractions = len(re.findall(r"\b\w+['’](?:s|t|re|ve|ll|d|m)\b", prose, re.I))
    contraction_rate = contractions / total_words * 1000 if total_words else 0.0

    list_words = sum(len(words(li)) for li in doc.list_items)

    return {
        "profile": profile,
        "profile_label": profile_label,
        "target_minutes": target_minutes,
        "paragraph_ceiling": para_ceiling,
        "words": body_words,
        "body_words": total_words,
        "heading_words": heading_words,
        "list_words": list_words,
        "list_share": list_words / total_words if total_words else 0.0,
        "read_minutes_silent": body_words / WPM_SILENT_NONFICTION,
        "read_minutes_aloud": body_words / WPM_ALOUD,
        "sentences": len(sentences),
        "sentence_mean": mean_len,
        "sentence_median": median_len,
        "sentence_stdev": stdev_len,
        "sentence_cv": cv,
        "sentence_p90": p90,
        "sentence_max": max_len,
        "share_over_25": over_25,
        "share_over_35": over_35,
        "longest_sentences": [{"words": n, "text": s} for n, s in longest_sentences],
        "paragraphs": len(doc.paragraphs),
        "paragraph_mean": statistics.mean(para_lengths),
        "paragraph_max": max(para_lengths),
        "longest_unbroken_run": longest_run,
        "headings": len(doc.headings),
        "heading_texts": [h[1] for h in doc.headings],
        "words_per_heading": words_per_heading,
        "list_items": len(doc.list_items),
        "bold_spans": len(doc.bold_spans),
        "scan_payload_words": payload_words,
        "scan_payload_share": payload_share,
        "entry_points": entry_points,
        "entry_density": entry_density,
        "buried_openers": buried,
        "buried_share": buried_share,
        "long_word_share": long_word_share,
        "nominalizations": sorted(set(noms)),
        "nominalization_rate": nom_rate,
        "passive_count": passives,
        "passive_share": passive_share,
        "flesch_reading_ease": flesch,
        "fk_grade": fk_grade,
        "em_dashes": em_dashes,
        "em_dash_rate": em_dash_rate,
        "contraction_rate": contraction_rate,
        "filler": find_phrases(prose, FILLER_PHRASES),
        "ai_phrases": find_phrases(prose, AI_TELL_PHRASES),
        "ai_patterns": find_patterns(prose, AI_TELL_PATTERNS),
    }


# --------------------------------------------------------------------------
# Verdicts
# --------------------------------------------------------------------------
def verdicts(m):
    """(label, value, status, note) where status is PASS / WATCH / FLAG / INFO."""
    out = []

    def add(label, value, status, note):
        out.append((label, value, status, note))

    minutes = m["read_minutes_silent"]
    target = m["target_minutes"]
    if minutes <= target:
        status = "PASS"
    elif minutes <= target * 1.25:
        status = "WATCH"
    else:
        status = "FLAG"
    add("read time (silent)", "%.1f min" % minutes, status,
        "target <= %.0f min for profile '%s' (%d wpm)" % (target, m["profile"], WPM_SILENT_NONFICTION))

    add("word count", m["words"], "INFO",
        "budget %d words at %d wpm" % (int(target * WPM_SILENT_NONFICTION), WPM_SILENT_NONFICTION))

    mean = m["sentence_mean"]
    if 11 <= mean <= 18:
        mean_status = "PASS"
    elif 9 <= mean <= 22:
        mean_status = "WATCH"
    else:
        mean_status = "FLAG"
    add("mean sentence", "%.1f words" % mean, mean_status,
        "spoken register is 12-18; under 11 means chopped, not rewritten")

    add("p90 sentence", "%d words" % m["sentence_p90"],
        "PASS" if m["sentence_p90"] <= 28 else "WATCH" if m["sentence_p90"] <= 34 else "FLAG",
        "one in ten sentences is at least this long")

    add("longest sentence", "%d words" % m["sentence_max"],
        "PASS" if m["sentence_max"] <= 34 else "WATCH" if m["sentence_max"] <= 44 else "FLAG",
        "over ~30 words is past a comfortable breath")

    add("over 25 words", "%.0f%%" % (m["share_over_25"] * 100),
        "PASS" if m["share_over_25"] <= 0.15 else "WATCH" if m["share_over_25"] <= 0.25 else "FLAG",
        "target <= 15% of sentences")

    cv = m["sentence_cv"]
    add("rhythm (length CV)", "%.2f" % cv,
        "PASS" if cv >= 0.45 else "WATCH" if cv >= 0.35 else "FLAG",
        "below 0.35 reads as machine-even; vary short and long")

    add("mean paragraph", "%.0f words" % m["paragraph_mean"],
        "PASS" if m["paragraph_mean"] <= m["paragraph_ceiling"] else "WATCH"
        if m["paragraph_mean"] <= m["paragraph_ceiling"] * 1.4 else "FLAG",
        "ceiling %d words for this profile" % m["paragraph_ceiling"])

    add("longest unbroken run", "%d words" % m["longest_unbroken_run"],
        "PASS" if m["longest_unbroken_run"] <= 200 else "WATCH"
        if m["longest_unbroken_run"] <= 300 else "FLAG",
        "words between structural breaks (heading, list, rule)")

    add("words per heading", "%.0f" % m["words_per_heading"],
        "PASS" if m["words_per_heading"] <= 200 else "WATCH"
        if m["words_per_heading"] <= 300 else "FLAG",
        "an unheaded stretch forces linear reading")

    add("scan payload", "%.0f%% of words" % (m["scan_payload_share"] * 100),
        "PASS" if m["scan_payload_share"] >= 0.20 else "WATCH"
        if m["scan_payload_share"] >= 0.14 else "FLAG",
        "headings + first sentences + bold; readers see ~20-28% of words")

    add("entry points", "%.1f per 500 words" % m["entry_density"],
        "PASS" if m["entry_density"] >= 4 else "WATCH"
        if m["entry_density"] >= 2.5 else "FLAG",
        "headings + list items + bold spans a scanner can land on")

    add("buried openers", "%.0f%% of paragraphs" % (m["buried_share"] * 100),
        "PASS" if m["buried_share"] <= 0.20 else "WATCH"
        if m["buried_share"] <= 0.35 else "FLAG",
        "paragraphs starting with a clause instead of the point")

    add("passive sentences", "%.0f%%" % (m["passive_share"] * 100),
        "PASS" if m["passive_share"] <= 0.15 else "WATCH"
        if m["passive_share"] <= 0.25 else "FLAG",
        "heuristic count; passive is fine when the actor is unknown")

    add("3+ syllable words", "%.0f%%" % (m["long_word_share"] * 100),
        "PASS" if m["long_word_share"] <= 0.18 else "WATCH"
        if m["long_word_share"] <= 0.24 else "FLAG",
        "keep necessary terms; cut latinate padding")

    add("nominalizations", "%.0f per 1k words" % m["nominalization_rate"],
        "PASS" if m["nominalization_rate"] <= 25 else "WATCH"
        if m["nominalization_rate"] <= 40 else "FLAG",
        "verbs turned into nouns; turn them back into verbs")

    add("em dashes", "%.1f per 1k words" % m["em_dash_rate"],
        "PASS" if m["em_dash_rate"] <= 4 else "WATCH"
        if m["em_dash_rate"] <= 8 else "FLAG",
        "you cannot hear an em dash; most should be a full stop")

    filler_total = sum(m["filler"].values())
    add("filler phrases", filler_total,
        "PASS" if filler_total == 0 else "WATCH" if filler_total <= 3 else "FLAG",
        "phrases that cost words and add nothing")

    ai_total = sum(m["ai_phrases"].values()) + sum(m["ai_patterns"].values())
    add("machine tells", ai_total,
        "PASS" if ai_total == 0 else "WATCH" if ai_total <= 2 else "FLAG",
        "target zero; each one costs the reader trust")

    add("Flesch reading ease", "%.0f" % m["flesch_reading_ease"], "INFO",
        "diagnostic only, never a target - surface features, easily gamed")
    add("FK grade", "%.1f" % m["fk_grade"], "INFO", "diagnostic only")
    add("contractions", "%.0f per 1k words" % m["contraction_rate"], "INFO",
        "near zero usually means the piece is not being spoken")

    return out


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
MARK = {"PASS": "ok  ", "WATCH": "watch", "FLAG": "FLAG", "INFO": "--  "}


def render(m, path, baseline=None, baseline_path=None):
    lines = []
    lines.append("cognitive load report: %s" % path)
    lines.append("profile: %s (%s)" % (m["profile"], m["profile_label"]))
    lines.append("=" * 72)
    lines.append("")

    rows = verdicts(m)
    base_rows = {r[0]: r[1] for r in verdicts(baseline)} if baseline else {}

    width = max(len(r[0]) for r in rows)
    for label, value, status, note in rows:
        line = "  %-5s %-*s  %-22s %s" % (MARK[status], width, label, value, note)
        lines.append(line)
        if baseline and label in base_rows and str(base_rows[label]) != str(value):
            lines.append("  %-5s %-*s  was %s" % ("", width, "", base_rows[label]))
    lines.append("")

    if m["longest_sentences"] and m["longest_sentences"][0]["words"] > 28:
        lines.append("longest sentences (read these out loud):")
        for item in m["longest_sentences"]:
            if item["words"] <= 28:
                continue
            text = item["text"]
            if len(text) > 150:
                text = text[:147] + "..."
            lines.append("  %3d w  %s" % (item["words"], text))
        lines.append("")

    if m["buried_openers"]:
        lines.append("paragraphs that do not open with their point:")
        for text in m["buried_openers"][:8]:
            lines.append("  - %s..." % text)
        lines.append("")

    if m["filler"]:
        lines.append("filler phrases:")
        for phrase, count in sorted(m["filler"].items(), key=lambda kv: -kv[1]):
            lines.append("  %2dx  %s" % (count, phrase))
        lines.append("")

    if m["ai_phrases"] or m["ai_patterns"]:
        lines.append("machine tells:")
        for phrase, count in sorted(m["ai_phrases"].items(), key=lambda kv: -kv[1]):
            lines.append("  %2dx  %s" % (count, phrase))
        for label, count in sorted(m["ai_patterns"].items(), key=lambda kv: -kv[1]):
            lines.append("  %2dx  %s  (construction)" % (count, label))
        lines.append("")

    if m["nominalizations"]:
        shown = ", ".join(m["nominalizations"][:20])
        lines.append("nominalizations: %s" % shown)
        lines.append("")

    if m["heading_texts"]:
        lines.append("heading-only read (does this alone carry the message?):")
        for text in m["heading_texts"]:
            lines.append("  - %s" % text)
        lines.append("")
    else:
        lines.append("no headings: a scanning reader has no entry points.")
        lines.append("")

    if baseline:
        lines.append("baseline: %s" % baseline_path)
        lines.append("  words        %5d -> %5d  (%+d)" % (
            baseline["words"], m["words"], m["words"] - baseline["words"]))
        lines.append("  read minutes %5.1f -> %5.1f" % (
            baseline["read_minutes_silent"], m["read_minutes_silent"]))
        lines.append("  rhythm CV    %5.2f -> %5.2f" % (
            baseline["sentence_cv"], m["sentence_cv"]))
        lines.append("  scan payload %4.0f%% -> %4.0f%%" % (
            baseline["scan_payload_share"] * 100, m["scan_payload_share"] * 100))
        lines.append("")

    flags = [r[0] for r in rows if r[2] == "FLAG"]
    watches = [r[0] for r in rows if r[2] == "WATCH"]
    if flags:
        lines.append("FLAGGED: %s" % ", ".join(flags))
    if watches:
        lines.append("watch:   %s" % ", ".join(watches))
    if not flags and not watches:
        lines.append("no flags. the numbers are clean - now check that it still")
        lines.append("means what the author meant.")
    lines.append("")
    lines.append("Numbers cannot see meaning. Run the fidelity check by hand.")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Measure how expensive a piece of writing is to read.")
    ap.add_argument("path", help="markdown or plain text file")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="brief",
                    help="target format (default: brief)")
    ap.add_argument("--minutes", type=float,
                    help="override the read-time target in minutes")
    ap.add_argument("--baseline", help="earlier draft to compare against")
    ap.add_argument("--json", action="store_true", help="emit raw metrics as JSON")
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything is FLAGged")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        sys.stderr.write("no such file: %s\n" % path)
        return 2

    metrics = analyse(path.read_text(encoding="utf-8"), args.profile)
    if args.minutes:
        metrics["target_minutes"] = args.minutes

    baseline = None
    if args.baseline:
        bpath = Path(args.baseline)
        if not bpath.exists():
            sys.stderr.write("no such baseline: %s\n" % bpath)
            return 2
        baseline = analyse(bpath.read_text(encoding="utf-8"), args.profile)
        if args.minutes:
            baseline["target_minutes"] = args.minutes

    if args.json:
        payload = {"file": str(path), "metrics": metrics}
        if baseline:
            payload["baseline"] = {"file": args.baseline, "metrics": baseline}
        print(json.dumps(payload, indent=2))
    else:
        print(render(metrics, str(path), baseline, args.baseline))

    if args.strict and any(r[2] == "FLAG" for r in verdicts(metrics)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

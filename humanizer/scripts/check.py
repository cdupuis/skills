#!/usr/bin/env python3
"""Flag AI-writing tells in a draft.

    python3 check.py draft.md                 # markdown venue (docs, PRs, issues)
    python3 check.py msg.txt --venue slack    # Slack message
    python3 check.py msg.txt --venue plain    # email or anything shown raw
    python3 check.py msg.txt --venue commit   # commit message
    echo "text" | python3 check.py -          # read stdin

Two levels:
  fix   a pattern on the list; rewrite the sentence
  look  often fine, sometimes a tell; decide in context

Exit code 0 when nothing is left to fix, 1 otherwise (--strict counts "look"
too). Code blocks, inline code, URLs and quoted lines ("> ...") are skipped,
so quoting someone else's text or showing a command is safe.

A clean run is a floor. The script cannot see inflated significance, a
formulaic structure or a paragraph that restates itself; read for those.
"""
import argparse
import json
import re
import statistics
import sys

FIX, LOOK = "fix", "look"
I = re.IGNORECASE

RULES = []


def rule(level, cat, pattern, advice, flags=I):
    RULES.append((level, cat, re.compile(pattern, flags), advice))


def words(level, cat, alternatives, advice):
    rule(level, cat, r"\b(?:" + "|".join(alternatives) + r")\b", advice)


# --- punctuation -----------------------------------------------------------
rule(FIX, "em dash", "—", "Use a comma, colon, parentheses, or two sentences.")
rule(FIX, "spaced en dash", r"\s–\s", "An en dash standing in for an em dash. Use a comma, colon or parentheses.")
rule(LOOK, "double hyphen", r"(?<=\w)\s--\s(?=\w)", "A typed em dash. Use a comma, colon or parentheses.")
rule(FIX, "curly quote", "[‘’“”]", "Type straight quotes and apostrophes.")

# --- vocabulary ------------------------------------------------------------
PLAIN = "Use the plain word, or cut the sentence if it only adds weight."
words(FIX, "AI vocabulary", [
    r"delv(?:e|es|ed|ing)", r"tapestr(?:y|ies)", "testament", "pivotal", r"crucial(?:ly)?",
    r"meticulous(?:ly)?", "intricate", "intricacies", "interplay", "vibrant",
    r"bolster(?:s|ed|ing)?", r"garner(?:s|ed|ing)?", r"showcas(?:e|es|ed|ing)",
    r"foster(?:s|ed|ing)?", r"underscor(?:es|ed|ing)", r"boast(?:s|ed|ing)?", "multifaceted",
    r"deep[- ]dives?", r"align(?:s|ed|ing)? with", "enduring", r"leverag(?:e|es|ed|ing)",
    r"seamless(?:ly)?", r"streamlin(?:e|es|ed|ing)", r"valuable insights?", r"key takeaways?",
    r"(?:digital|competitive|evolving|technological|regulatory|media|threat|security|ai|current|changing|broader|modern) landscape",
    r"ever[- ]evolving",
], PLAIN)
rule(FIX, "AI vocabulary", r"(?:^|(?<=[.!?]\s))Additionally,", "Drop it or join the sentences.", 0)
rule(FIX, "AI vocabulary",
     r"\bkey (?:role|moment|aspect|factor|component|element|insight|feature|driver|player|consideration|point|area|part)s?\b",
     'Say what it does. "Key" adds nothing.')
words(LOOK, "AI vocabulary", [
    "robust", "comprehensive", r"enhanc(?:e|es|ed|ing|ement|ements)", r"highlight(?:s|ed|ing)",
    r"emphasi[sz](?:e|es|ed|ing)", "landscape", "underscore", "quietly", "dependable", "steady",
    "clearer", "practical", r"prioriti[sz](?:e|es|ed|ing)", "universally", "echoed",
    r"profound(?:ly)?", "empirical", "causal", "valuable",
], "On the overused list. Fine if literal; otherwise use the plain word.")
rule(LOOK, "AI vocabulary", r"\bmatters\b(?! of\b)(?=[ .,;:]|$)",
     '"Why this matters" framing. Say the consequence.')
rule(LOOK, "transition", r"(?:^|(?<=[.!?]\s))(?:Moreover|Furthermore|Notably|Importantly|Consequently),",
     "Stock sentence opener. Usually deletable.", 0)
words(FIX, "stiff synonym", [
    r"utili[sz](?:e|es|ed|ing)", "authored", "relocated", "passed away",
], "Write used, wrote, moved, died.")
words(FIX, "promotional", [
    "nestled", "in the heart of", "breathtaking", "groundbreaking", "renowned", "diverse array",
    r"rich (?:tapestry|history|heritage|culture|cultural heritage)", "natural beauty",
    r"(?:unwavering |strong |deep )?commitment to (?:excellence|quality|innovation|sustainability)",
    r"cutting[- ]edge", r"state[- ]of[- ]the[- ]art", r"world[- ]class", r"game[- ]chang(?:er|ing)",
    r"(?:thrilled|excited|delighted|proud|pleased|happy) to (?:announce|share|introduce|unveil)",
    r"we(?:'re| are) (?:thrilled|excited|delighted|proud)", r"stay tuned", r"take (?:\w+ )?to the next level",
], "Brochure language. State the fact.")

# --- inflated significance -------------------------------------------------
words(FIX, "inflated significance", [
    r"(?:stands?|serves?|stood|served) as (?:a |an |the )?(?:testament|reminder|symbol|beacon|cornerstone|example)",
    r"is a testament", r"(?:pivotal|crucial|vital|significant|defining) (?:role|moment)",
    r"plays? (?:a|an) (?:\w+ )?role", r"turning point",
    r"(?:underscor|highlight)(?:es|s|ing|ed) (?:its|the|their) (?:importance|significance)",
    r"reflects? (?:a |the )?broader", r"setting the stage", r"sets the stage", r"indelible mark",
    r"deeply rooted", r"part of (?:a|the) (?:wider|broader|larger)", r"marks? a (?:\w+ )?shift",
    r"represents? a (?:\w+ )?(?:shift|milestone|step)", r"focal point", r"lasting (?:impact|legacy)",
    r"paves? the way", r"paving the way",
], "Says the thing is important without saying why. Give the fact or cut it.")
rule(FIX, "shaped discussions",
     r"\b(?:shaped|sparked|prompted|generated|fuel(?:l)?ed|contributed to) (?:\w+ )?(?:discussions?|debates?|conversations?|reflection)\b",
     "Name who said what, or cut it.")
words(FIX, "coverage instead of content", [
    r"(?:featured|profiled|highlighted|cited|covered) in (?:\w+ )?(?:outlets|publications|media)",
    "independent coverage", r"(?:extensively|widely) (?:documented|covered)",
    r"(?:active|strong) (?:social media|digital|online) presence", r"maintains? (?:a|an) [\w ]{0,20}presence",
], "Say what the coverage says.")
rule(LOOK, "source identifies",
     r"\b(?:identif(?:y|ies|ied)|list(?:s|ed)?|describ(?:es|ed)?|record(?:s|ed)?) (?:him|her|them|it|the \w+) as\b",
     "State it directly unless the attribution is the point.")

# --- tacked-on analysis ----------------------------------------------------
rule(FIX, "-ing tail",
     r",\s+(?:highlighting|underscoring|emphasi[sz]ing|reflecting|showcasing|fostering|symboli[sz]ing|"
     r"demonstrating|illustrating|enhancing|cementing|solidifying|reinforcing|contributing to|"
     r"ensuring (?:that )?(?:a|an|the|its|their)?)\b",
     "Analysis bolted onto the end of a sentence. End the sentence at the fact.")
rule(LOOK, "-ing tail", r",\s+(?:making (?:it|them)|allowing|enabling|providing|offering|creating|marking)\b",
     "Check the tail adds a fact and is not commentary.")
words(LOOK, "vague connection", [r"associated with", r"in (?:connection|association) with", r"connected (?:to|with)"],
      "Say what the relationship is.")
words(FIX, "weasel attribution", [
    r"experts (?:argue|say|believe|agree|note|suggest)", r"observers (?:have |)(?:noted|cited|argue|say)",
    r"industry (?:reports|experts|analysts|observers)", r"some (?:critics|experts|observers|analysts)",
    r"(?:studies|research) (?:show|shows|suggest|suggests|indicate|indicates)(?! that \w+ et al)",
    r"(?:it is|it's) widely (?:regarded|considered|believed|recognized)", r"many (?:believe|argue|consider)",
], "Name the source or drop the claim.")
words(FIX, "challenges formula", [
    r"despite (?:its|their|these|this|the) [\w ,'-]{0,60}?(?:challenges?|faces?|continues? to)",
    r"faces? (?:several|numerous|significant|many|new|a number of|its own)? ?challenges",
    r"future (?:outlook|prospects|directions)", r"challenges and (?:opportunities|future|legacy)",
    r"continues? to (?:thrive|evolve|grow)",
], "The despite/challenges/bright-future formula. Say the specific problem and its status.")

# --- sentence shapes -------------------------------------------------------
words(FIX, "copula dodge", [
    r"(?:serves?|served|stands?|stood|functions?|functioned|operates?) as (?:a|an|the)",
    r"holds? the distinction of", r"ventured into",
], 'Write "is" or "was".')
rule(LOOK, "copula dodge", r"\b(?:features|offers|boasts) (?:a|an|\d+|several|multiple|numerous)\b", 'Usually "has".')
rule(FIX, "negative parallelism", r"\bnot (?:just|only|merely|simply)\b[^.!?\n]{0,120}?\b(?:but|it'?s|they'?re|it is)\b",
     '"Not just X but Y". Say Y.')
rule(FIX, "negative parallelism",
     r"\b(?:isn'?t|aren'?t|wasn'?t|weren'?t|is not|are not|was not|it'?s not|this is not|that'?s not|doesn'?t just|don'?t just)"
     r"\b[^.!?\n]{1,80}?(?:[;:,]|\s-|\.)\s*(?:it'?s|it is|they'?re|they are|that'?s|this is|rather)\b",
     '"It\'s not X, it\'s Y". Say Y.')
rule(FIX, "negative parallelism", r"\bno \w+(?: \w+)?, no \w+(?: \w+)?,? (?:just|only)\b", '"No X, no Y, just Z". Say Z.')
rule(LOOK, "negative parallelism", r"\bnot [^.!?\n,]{1,50}, but\b", '"Not X, but Y". Say Y unless the contrast is real.')
rule(LOOK, "negative parallelism", r"\b(?:rather than|instead of)\b",
     "Common in recent AI text. Keep it only when the reader would expect the other thing.")
rule(FIX, "corrective disclaimer",
     r"\bshould (?:not )?be (?:treated|understood|viewed|read|seen|regarded) as\b|\bdoes not (?:by itself |in itself |on its own )?establish\b"
     r"|\bshould (?:not be confused with|be distinguished from)\b",
     "Telling the reader how to take a claim. State what is known.")
rule(LOOK, "definition lead", r"^[^.\n]{3,80}\brefers to\b", 'Defining the title as if it were a term. Write "X is".')

# --- chatbot residue -------------------------------------------------------
words(FIX, "chatbot voice", [
    r"certainly[!,]", r"of course[!,]", r"absolutely[!,]", r"you(?:'re| are) (?:absolutely |completely |totally )?right",
    r"great (?:question|point|idea)", r"(?:i )?hope this helps", r"let me know (?:if|how|what|whether)",
    r"feel free to", r"would you like(?: me)? to", r"is there anything else", r"(?:i'?d|i would|i am|i'?m|i will|i'?ll) (?:be )?happy to",
    r"happy to help", r"here(?:'s| is| are) (?:a|an|the|some|my) (?:\w+ )?(?:breakdown|rundown|overview|summary|draft|version|list)",
    r"more detailed breakdown", r"in this (?:section|article|post|guide),? we(?:'ll| will)", r"let'?s (?:dive|break|explore|unpack)",
    r"don'?t hesitate to", r"as an ai\b", r"(?:large )?language model", r"knowledge (?:cutoff|update)", r"training (?:data|update)",
    r"i (?:cannot|can'?t|am unable to) [^.\n]{0,40}, but i can",
], "Chat reply, not content. Delete it.")
words(FIX, "letter voice", [
    r"i hope this (?:(?:message|email|note) )?finds you well", r"i am writing to", r"i'?m writing to (?:let you know|inform)",
    r"thank you for your (?:time|consideration|understanding|patience)", r"dear (?:team|all|sir|madam|\w+ team)",
    r"(?:warm|best|kind) regards", r"please find (?:attached|below)",
], "Form-letter phrasing. Open with the point; close with your name or nothing.")
words(FIX, "customer-service voice", [
    r"i (?:have )?carefully reviewed", r"i (?:sincerely )?apologi[sz]e for any", r"any (?:inconvenience|confusion|disruption) (?:this|i|it|that) may have",
    r"i understand (?:your (?:concern|frustration)|the importance of|that)", r"i (?:would )?(?:appreciate|welcome) any (?:further |additional )?(?:feedback|guidance|input|suggestions)",
    r"if (?:there are|you have) any (?:specific |further |additional )?(?:concerns|issues|questions)", r"i am committed to", r"i remain committed",
    r"my (?:aim|goal|intent|intention) is to", r"i assure you", r"rest assured", r"i have taken the time to",
    r"(?:moving|going) forward,? (?:i|we) will", r"i respectfully", r"respectfully (?:request|disagree|contest)",
    r"concrete (?:evidence|examples|steps|feedback)", r"my intention is not to",
], "Help-desk phrasing. Say what happened and what you will do.")
rule(LOOK, "A, particularly B", r",\s+particularly\b", '"A, particularly B". Often just "B".')
words(FIX, "disclaimer", [
    r"it(?:'s| is) (?:important|worth|crucial|essential|vital) (?:to note|noting|to remember|to mention|mentioning|to understand|to differentiate|to recognize)",
    r"it should be noted", r"worth noting", r"while specific (?:details|information)", r"based on (?:the )?available (?:information|sources|data)",
    r"not (?:widely|extensively|publicly|well) (?:documented|available|disclosed|known)", r"in the (?:provided|available) (?:sources|search results)",
    r"keeps? (?:a|his|her|their) (?:low profile|personal (?:life|details) private)", r"maintains? a low profile",
], "Hedge that fills a gap. Say what you know, or say you don't know, once.")
rule(FIX, "summary closer",
     r"(?:^|(?<=[.!?]\s))(?:In summary|In conclusion|To summari[sz]e|To sum up|Overall|In essence|Ultimately|All in all),",
     "Restating what was just said. End on the last new point.", 0)
rule(FIX, "summary closer", r"^#{1,6}\s*(?:Conclusion|Summary|Final thoughts|Key takeaways|Wrapping up)\s*$",
     "A conclusion section for a short text. Cut it.")
rule(FIX, "placeholder",
     r"\[(?:your|insert|add|name|link|date|company|recipient|title|url|todo|placeholder|describe|reason)\b[^\]\n]{0,80}\]"
     r"|\(add [^)\n]{0,60} here\)|\b\d{4}-XX-XX\b|\b(?:INSERT|PASTE)_[A-Z_]+|\bXX-XX\b",
     "Unfilled placeholder.")
rule(FIX, "chat log", r"^(?:You said|ChatGPT said|Claude (?:said|responded)|Assistant):", "Pasted chat turn.")
rule(FIX, "explains Claude", r"\bClaude \((?:Anthropic|an AI|AI)[^)]*\)|Anthropic'?s AI assistant", "Nobody needs Claude explained.")
rule(FIX, "AI attribution", r"generated (?:with|by) (?:\[?claude|chatgpt|ai\b)|co-authored-by: claude", "No AI attribution lines or footers.")

# --- change summaries (commit messages, PR text) ---------------------------
words(FIX, "change-summary filler", [
    r"(?:improv|enhanc|refin)(?:e|es|ed|ing) (?:the )?(?:overall )?(?:clarity|readability|flow|consistency|tone|structure)",
    r"clarity,? (?:flow|readability|and)", r"for (?:better|improved) (?:clarity|readability|maintainability)",
    r"comprehensive (?:update|rewrite|refactor|overhaul|review|formatting|cleanup)",
    r"while (?:preserving|retaining|maintaining|keeping) (?:the )?(?:original|existing|current)?",
    r"ensur(?:e|es|ed|ing) (?:compliance|adherence|consistency|neutrality|accuracy|full compliance)",
    r"in (?:compliance|accordance) with", r"adheres? to (?:the )?(?:\w+ )?(?:guidelines|standards|best practices|style)",
    r"(?:follows?|following) best practices", r"various (?:improvements|fixes|changes|enhancements)",
    r"minor (?:improvements|tweaks) (?:and|for)",
], "Says the change is good, not what it is. Name what changed and why.")
rule(LOOK, "change-summary filler", r"\baddress(?:ed|es|ing)? (?:the )?(?:reviewer|review|pr) (?:feedback|comments)\b",
     "Say which point you addressed.")
rule(LOOK, "change-summary filler", r"\b(?:preserved|retained|left unchanged|untouched)\b",
     "Listing what you did not change reads like a prompt echo. Keep only if a reviewer would worry.")

# --- links and leaked markup (run on raw text) -----------------------------
RAW_RULES = [
    (FIX, "tracking parameter", re.compile(r"[?&](?:utm_[a-z]+|referrer)=[^\s)&>\]]*", I),
     "Strip tracking parameters from the URL."),
    (FIX, "placeholder URL", re.compile(r"https?://(?:www\.)?example\.com/\S+", I), "Placeholder URL."),
    (FIX, "leaked tool markup",
     re.compile(r"oaicite|contentReference|oai_citation|turn\d+(?:search|view|news)\d+|\[cite: ?\d+\]|grok_card|attached_file|ppl-ai-file-upload|↩", I),
     "Internal citation markup. Remove it and cite the real source."),
]

EMOJI = "(?:[\U0001F300-\U0001FAFF☀-➿⭐⬆⬇✅✨❌✔⬛⬜]|:[a-z][a-z0-9_+-]{1,30}:)"
TRIAD = re.compile(
    r"\b[\w'-]+(?: [\w'-]+){0,3}, [\w'-]+(?: [\w'-]+){0,3},? and [\w'-]+(?: [\w'-]+){0,2}\b", I)
SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "vs", "via", "with", "from", "into"}


def mask(text):
    """Blank out code, URLs and quoted lines, keeping line structure."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", blank, text, flags=re.S | re.M)
    text = re.sub(r"`[^`\n]+`", blank, text)
    text = re.sub(r"https?://\S+", blank, text)
    text = re.sub(r"^\s*>.*$", blank, text, flags=re.M)
    return text


def snippet(line, start, end, pad=28):
    a, b = max(0, start - pad), min(len(line), end + pad)
    return ("…" if a else "") + line[a:b].strip() + ("…" if b < len(line) else "")


def check(text, venue="markdown", allow_emoji=False):
    out = []

    def add(n, level, cat, shown, advice):
        out.append({"line": n, "level": level, "category": cat, "text": shown, "advice": advice})

    raw_lines = text.split("\n")
    masked_lines = mask(text).split("\n")

    for n, line in enumerate(masked_lines, 1):
        seen = []  # one finding per category per stretch of text
        for level, cat, rx, advice in RULES:
            for m in rx.finditer(line):
                if any(c == cat and m.start() < e and s < m.end() for c, s, e in seen):
                    continue
                seen.append((cat, m.start(), m.end()))
                add(n, level, cat, snippet(line, m.start(), m.end()), advice)
    for n, line in enumerate(raw_lines, 1):
        for level, cat, rx, advice in RAW_RULES:
            for m in rx.finditer(line):
                add(n, level, cat, snippet(line, m.start(), m.end()), advice)

    # --- formatting ---
    frontmatter = raw_lines[:1] == ["---"]
    in_front = frontmatter
    bold_spans = 0
    label_run = 0
    for n, line in enumerate(masked_lines, 1):
        if in_front:
            if n > 1 and line.strip() == "---":
                in_front = False
            continue
        s = line.strip()
        bold_spans += len(re.findall(r"\*\*[^*\n]+\*\*", line))
        if re.match(r"(?:[-*•–]|\d+[.)])\s+(?:\*\*|__)[^*_\n]{1,80}?(?:(?:\*\*|__)\s*[:—–-]|:(?:\*\*|__))", s):
            add(n, FIX, "bold-label bullet", s[:60], "Bullet that opens with a bold label and a colon. Write a sentence, or a plain list.")
        elif re.match(r"(?:\*\*|__)[^*_\n]{1,60}:(?:\*\*|__)|(?:\*\*|__)[^*_\n]{1,60}(?:\*\*|__):", s):
            add(n, LOOK, "bold label", s[:60], "Paragraph that opens with a bold label. Usually the sentence can carry it.")
        if re.match(r"[-*•]\s+[A-Z][\w /&-]{1,28}:\s+\S", s):
            label_run += 1
            if label_run == 3:
                add(n, LOOK, "label bullets", s[:60], 'Run of "Label: text" bullets. Prose or a plain list reads less templated.')
        elif s:
            label_run = 0
        if not allow_emoji and re.match(r"(?:#{1,6}\s+|[-*•]\s+|\d+[.)]\s+)?(?:\*\*)?" + EMOJI, s):
            add(n, FIX, "emoji as formatting", s[:60], "Emoji decorating a heading or bullet. Remove it.")
        elif not allow_emoji and re.search(EMOJI, line):
            add(n, LOOK, "emoji", s[:60], "Emoji in running text. Fine in a chat reply if that is how the channel talks; out of place elsewhere.")
        if re.search(r"(?:^|\s)(?:#[A-Za-z]\w+\s*){2,}$", s):
            add(n, LOOK, "hashtag block", s[-60:], "Row of hashtags. Keep one or two only if the venue really uses them.")
        if re.fullmatch(r"(?:-{3,}|\*{3,}|_{3,})", s):
            add(n, FIX, "rule between sections", s, "Horizontal rule as a section break. Remove it.")
        h = re.match(r"(#{1,6})\s+(.*)", s)
        heading = h.group(2) if h else None
        if heading is None:
            b = re.fullmatch(r"\*\*([^*]+)\*\*:?", s)
            heading = b.group(1) if b else None
        if heading:
            ws = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", heading)]
            rest = [w for w in ws[1:] if w.lower() not in SMALL and len(w) > 2]
            if len(rest) >= 2 and all(w[0].isupper() and w[1:].islower() for w in rest):
                add(n, LOOK, "title case heading", heading[:60], "Use sentence case unless these are proper nouns.")
            if re.search(r"\b\w+ (?:and|&) \w+\b", heading) and re.search(r"(?i)awards|recognition|challenges|legacy|outlook|impact", heading):
                add(n, FIX, "stock heading", heading[:60], 'The "X and Y" stock section. Name the section for what is in it.')
        if venue in ("plain", "commit"):
            if h or re.search(r"\*\*[^*\n]+\*\*|\[[^\]\n]+\]\([^)\n]+\)|^\s*\|.*\|\s*$", line) or raw_lines[n - 1].lstrip().startswith("```"):
                add(n, FIX, "markdown in plain text", s[:60], "This venue shows markup raw. Write plain text.")
        elif venue == "slack":
            if h or re.match(r"\s*\|.*\|\s*$", line):
                add(n, FIX, "markdown Slack won't render", s[:60], "Slack has no headings or tables. Use a short line or plain sentences.")

    prose_lines = [l for l in masked_lines
                   if l.strip() and not re.match(r"\s*(?:#{1,6}\s|[-*•]\s|\d+[.)]\s|\|)", l)]
    prose = " ".join(prose_lines)
    nwords = len(re.findall(r"[A-Za-z0-9'-]+", " ".join(masked_lines)))

    if bold_spans >= 4 and nwords and bold_spans / nwords > 1 / 70:
        add(0, LOOK, "bold density", f"{bold_spans} bold spans in {nwords} words", "Scattered bold reads as key-takeaways formatting. Keep bold for the one thing that must not be missed.")

    triads = [m.group(0) for m in TRIAD.finditer(" ".join(masked_lines))]
    if len(triads) >= 2:
        add(0, LOOK, "rule of three", "; ".join(t[:50] for t in triads[:4]),
            f"{len(triads)} three-item groups. Keep the ones that are real lists of three; cut padding to one or two items.")

    sents = [s for s in re.split(r"(?<=[.!?])\s+", prose) if len(s.split()) >= 2]
    lens = [len(s.split()) for s in sents]
    if len(lens) >= 6:
        if statistics.pstdev(lens) < 3.5 or all(7 <= x <= 21 for x in lens):
            add(0, LOOK, "uniform sentences", f"{len(lens)} sentences, {min(lens)} to {max(lens)} words",
                "Every sentence is about the same length. Let a short one and a long one in.")
    pw = len(prose.split())
    if pw >= 120 and not re.search(r"[:;()]", prose):
        add(0, LOOK, "flat punctuation", f"{pw} words of prose", "Only commas and full stops. A colon, semicolon or parenthesis where it fits.")

    if venue == "commit":
        first = next((l for l in raw_lines if l.strip()), "")
        if len(first) > 72:
            add(1, LOOK, "long subject", first[:60], "Subject line over 72 characters.")
        if re.match(r"\s*(?:I|We)\b", first):
            add(1, FIX, "first-person subject", first[:60], "Imperative subject: what the commit does.")

    out.sort(key=lambda f: (f["line"] == 0, f["line"], f["level"] != FIX))
    return out


def main():
    ap = argparse.ArgumentParser(description="Flag AI-writing tells in a draft.")
    ap.add_argument("paths", nargs="+", help="files to check, or - for stdin")
    ap.add_argument("--venue", choices=["markdown", "slack", "plain", "commit"], default="markdown")
    ap.add_argument("--allow-emoji", action="store_true", help="skip the emoji-as-formatting check (for a format the user set)")
    ap.add_argument("--strict", action="store_true", help='exit 1 on "look" findings too')
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    failed = False
    report = {}
    for p in a.paths:
        text = sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()
        found = check(text, a.venue, a.allow_emoji)
        report[p] = found
        fixes = sum(f["level"] == FIX for f in found)
        looks = len(found) - fixes
        failed |= bool(fixes) or (a.strict and bool(looks))
        if a.json:
            continue
        name = "stdin" if p == "-" else p
        if not found:
            print(f"{name}: clean")
            continue
        print(f"{name}: {fixes} to fix, {looks} to look at")
        for f in found:
            where = f"{f['line']:>4}" if f["line"] else "   -"
            print(f"{where} {f['level']:<4} {f['category']}: \"{f['text']}\"")
            print(f"          {f['advice']}")
    if a.json:
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        print()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

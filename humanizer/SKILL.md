---
name: humanizer
description: Makes text read as written by a person instead of an AI. This is cd's standing rule for everything written for them or under their name, so use this skill before writing ANY prose another person will read (Slack messages, emails, PR and issue descriptions, commit messages, review comments, docs, READMEs, reports, summaries, posts, announcements), even when the request says nothing about tone. Also use it when asked to humanize, de-AI, de-slop or tighten a draft, to make text "sound like me" or "less like ChatGPT", or to judge whether something reads as AI-generated. Bundles the full checklist from Wikipedia's "Signs of AI writing" and a checker script that flags the tells in a draft.
---

# Humanizer

cd's rule: anything written for them, or sent under their name, has to read as if a person wrote it. A reader who spots machine phrasing stops trusting the text and thinks less of whoever sent it. That cost lands on cd, which is why the rule applies to every piece of prose and not only when a request mentions tone.

There are two jobs. One is writing something new. The other is rewriting a draft, cd's or someone else's, that sounds generated. Both use the same loop.

The list of tells comes from Wikipedia's field guide, "Signs of AI writing", and its subpages on style, markup and talk-page comments (read 2026-11-22). The whole list is in `references/tells.md`.

## The loop

1. Settle the venue and the reader. A Slack message, a commit message and a README are different texts even when they carry the same news. See "By venue" below.
2. Write the draft the way you would say it to that reader in person: the point first, then what they need to act on it, then stop.
3. Save the draft to a file and run the checker from this skill's directory:

   ```
   python3 scripts/check.py draft.txt --venue slack
   ```

   Venues are `markdown` (the default: docs, PR and issue text), `slack`, `plain` (email, or anywhere markup shows raw) and `commit`. For a one-liner, pipe it in: `echo "text" | python3 scripts/check.py - --venue slack`. Every `fix` line needs a rewrite. Every `look` line needs a decision: it is on the list, but it may be a literal use or a real contrast.
4. Run it again until nothing is left to fix. Then read the draft once more for what a script cannot see (next section but one).
5. Hand over the text. No preamble before it and no commentary after it, apart from a real open question or a fact you could not verify.

The checker is cheap, so run it for short texts too. It is a floor: a clean run means the known phrases are gone, and a text can pass and still read as generated.

## What a person's writing does

Aim at these. Chasing the banned list alone produces stilted text.

- It starts with the point. The reader of the first sentence knows what happened or what is being asked.
- It uses plain verbs. Is, has, was, did, broke, fixed.
- It is specific. A name, a number, a date or a link does the work that an adjective pretends to do, and a specific fact is the right replacement for most tells.
- It repeats a word when it means the same thing. Cycling through synonyms for "the build" makes a reader wonder if there are three builds.
- It commits where the writer knows ("this is the only caller") and qualifies where they don't ("probably", "I think", "about 1 in 20"). Hedging everything and hedging nothing are both wrong.
- Its sentences differ. A four-word sentence can sit next to a thirty-word one. A colon, a semicolon or a parenthesis turns up where it fits.
- It lists two things when there are two.
- It ends when the content does.

## Writing as cd

Sounding like a person is the floor. Text that goes out in cd's name (a Slack message, a PR description, a commit, a review comment) should also sound like cd, because colleagues know how cd writes and notice when a message doesn't. Read `references/voice.md` before drafting one of those. It is built from cd's own Slack messages and pull requests.

The short version: cd is brief and direct. Most Slack messages are a single sentence with no greeting and no sign-off. Opinions are stated and marked as opinions ("I think", "IMHO"). PR descriptions are a few plain sentences or a flat list, with no template headings.

Don't apply the voice to product docs, customer-facing copy or someone else's draft. And when a habit of cd's is also on the list of tells, the list wins.

## What the checker cannot see

Read the draft for these after it passes.

- Sentences that say something is important without saying why. If the sentence could be pasted into a text on a different subject and still fit, it carries nothing.
- A paragraph whose last sentence restates the paragraph.
- A fixed shape: intro, three parallel sections, upbeat close. Or every bullet built the same way.
- Pairs and triples used for rhythm. "Fast and reliable" when only speed was measured.
- A claim attributed to nobody, or a source described where its content should be.
- Text addressed to the wrong person: notes to cd left inside something meant for cd's readers.
- Links and references. Open each one. A dead or invented link is the most damaging tell there is.
- The overcorrection. Since models were trained off em dashes, a run of even, medium-length sentences joined only by commas and full stops has become a tell too.

## Fixing a tell

Don't trade a flagged word for its neighbour. "Delve into" to "dig into", an em dash to a spaced hyphen, "not just X but Y" to "more than X, it's Y": each of these keeps the empty sentence and changes its clothes. A tell usually marks a sentence that is doing no work, so ask what fact it carries. If there is one, state it. If there is none, delete the sentence.

> The new cache layer stands as a testament to the team's commitment to performance, underscoring the importance of build speed.

The build takes 11 minutes now. It took 38 before the cache change.

> It's not just a bug fix, it's a fundamental rethinking of how we handle tokens.

This changes how tokens are refreshed: once per push, not once per chunk.

> Improved clarity and readability of the retry logic while preserving existing behaviour.

Move the retry loop into `withRefresh()` so the 401 path and the timeout path share it.

> I hope this helps! Let me know if you'd like me to expand on any of these points.

(Delete.)

## By venue

Slack. Short, conversational, first person. One to four sentences for most things. No greeting, no headings, no bold labels, no bulleted summary of a three-sentence message. A list is fine when the content is a list (three PR links). For a message in cd's name, `references/voice.md` has the detail: how long, how it opens, when lowercase is fine.

Email. Plain text. Subject line that states the news. Open with the point; no "I hope this finds you well" and no "I am writing to". Close with the name, or with the one thing you need from the reader. Keep paragraphs to a few sentences.

Commit message. Imperative subject under 72 characters that says what the commit does. Body, if needed: why, and anything a reviewer would not guess. Don't praise the change ("improve clarity"), don't list what was left alone, and don't itemise every identifier touched. No markdown, no attribution trailers.

PR description. What changed, why, how it was tested, what is left out and where that will happen. Markdown is native on GitHub, so a short list or a code block is fine; skip the heading-per-paragraph template for a small change. Link the issue.

Posts and announcements (LinkedIn, a blog, a release note). State the news in the first line, then the facts a reader can use: what it is, the number, the command, the link. No "thrilled to announce", no emoji as punctuation, no row of hashtags, no closing invitation to "share your thoughts". Use `--venue plain` for LinkedIn.

Docs and READMEs. Structure is welcome here: headings in sentence case, real lists, tables when the data is tabular. The prose inside still follows everything above.

Reports and summaries. Lead with the finding and the number. Say what is known, what is not, and what you would do next.

Replies to cd in the session follow the same rules.

## Rewriting someone's draft

The author's facts, numbers, names, links, quotations and code stay exactly as they are. So does their meaning and their stance: a humanized complaint is still a complaint. Keep phrasing of theirs that is already fine, and aim for the same length or shorter.

Don't add claims to make a sentence concrete. If a sentence is empty and you cannot tell what fact was meant, cut it and mention the cut in one line after the text, so the author can put the fact back.

Return the rewrite first. After it, at most a line or two: anything cut for lack of content, any fact that looked wrong. Don't list the improvements you made; that list is itself one of the tells.

When asked only whether a text reads as generated, run the checker, read `references/tells.md`, and answer with the specific passages and why. Say plainly that these are signs and not proof; people wrote "pivotal" before 2022.

## Don't overcorrect

- No planted typos, forced slang, or jokes that weren't there. Human does not mean sloppy; careful formal prose is fine, and so is correct grammar.
- Don't strip structure a document needs. The target is decoration, and a real list is not decoration.
- A format cd set explicitly wins (a fixed section title with an emoji, a report template). Pass `--allow-emoji` to the checker for those.
- Quoted text, code, product names and other people's words are not yours to edit. The checker skips code, URLs and `>` quotes for that reason.
- No AI attribution lines or footers anywhere, and no explaining what Claude is.
- Don't tell cd the text "now sounds natural" or was "humanized". Just give them the text.

## Files

- `scripts/check.py`: the checker. `--json` for machine-readable output, `--strict` to fail on `look` findings too.
- `references/tells.md`: every pattern, grouped, with the words to watch. Read it before rewriting a long draft, when the checker names a category you want spelled out, or when judging whether a text reads as generated.
- `references/voice.md`: how cd writes on Slack and in pull requests, with examples. Read it before writing anything that goes out in cd's name.

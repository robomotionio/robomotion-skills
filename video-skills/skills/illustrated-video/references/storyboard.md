# Storyboard

Write `STORYBOARD.md` before any scene code. It is the plan you build from
and the list you check the render against.

## Format

```markdown
# <title>

Idea: one sentence.
Spine: song | voiceover | music bed · <duration> s · <bpm or "speech">
Tier: drawn | stills | performance · fal budget $<n> (or none)
Inks: <set> · paper <hex> · arc: <how colour moves across the sections>
Clock: <the running device and where it sits>
Cast: <who, and each one's ink> (or none)
Hook: <what the first two seconds are>
Bookend: <how the last shot answers the first>

| # | Time | Words (from the spine) | Seen | Event | Type | Layers | Out |
|---|---|---|---|---|---|---|---|
| 01 | 0.00–2.35 | I see sparks of AGI | CU face right, sunburst | eyes flare on "sparks" | hero L, words slam | still (hero-cu), fg type | cut on bar |
| 02 | 2.35–4.50 | in your eyes | ECU eye | pupil reflects a tiny chart | mid, bottom-left | still, bg | push through the pupil |
| ... |
```

- **Time** snaps to the spine: a line start, a bar, a beat, or a word's own
  time. Write the real numbers.
- **Seen**: framing (ECU, CU, MS, WS), subject, set.
- **Event**: what changes between the first and last frame. Every shot has one.
- **Type**: which tier, which side, and on which word it lands.
- **Layers**: `bg` (drawn), `still (<name>)`, `perf (<slice name>)`, `fg`.
- **Out**: the transition, or "cut on <beat/bar>".

## Reads: timing for a first-time viewer

You know what happens; the viewer sees it once, at full speed. For each
shot, list what the viewer has to take in, in order, and give each thing
time to be found and understood before the next starts. A big central
thing reads in a few frames; a small, distant or subtle one needs half a
second or more. Two important things at once means one of them is missed.
Fast motion is fine when it is anticipated; the meaning after it needs a
hold. If a shot's reads do not fit its span, cut a read or merge two shots;
do not squeeze.

## Checks before you build

- Every shot has an event.
- No two important reads overlap.
- The first two seconds are the most designed frames.
- Hero type never sits on a busy background.
- Every seam has a transition or is a deliberate cut on the music.
- The chip band is clear in every shot with words.
- Every receipt is real, and you know where it came from.
- The last shot answers the first.
- Performance shots (tier 3) are the lines that matter most, not every line:
  budget and attention both run out.

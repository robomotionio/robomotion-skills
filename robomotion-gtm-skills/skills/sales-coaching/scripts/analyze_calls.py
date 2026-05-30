#!/usr/bin/env python3
"""analyze_calls.py — deterministic structural + discovery-quality metrics over sales call
transcripts.

NO LLM. Reads speaker-labelled transcripts and computes:
  - talk:listen ratio, rep talk %, longest monologue (the mechanical engagement metrics)
  - question count + open-vs-closed question ratio (discovery breadth)
  - MEDDIC/BANT coverage flags (pain / budget / authority / timeline / metrics / champion /
    decision-process / competition) via keyword detection across the rep's turns
  - a composite discovery-quality score (0-100) blending question volume, open ratio, and
    qualification-topic coverage
  - objection-handling detection: prospect objection cues + whether the rep responded with
    an acknowledge/clarify move vs. steamrolled
  - a won-vs-lost split on the headline metrics

The host agent still does the qualitative judgement (HOW well discovery/objection-handling/
demo were executed) from reading the transcript text; this script gives the deterministic
scaffold + score.

Transcript input: a JSON array of calls, each:
  {"call_id":"c1","rep":"Alex","outcome":"won",
   "turns":[{"speaker":"rep","text":"..."},{"speaker":"prospect","text":"..."}]}
Speaker normalized: anything matching --rep-name (or labelled "rep"/"me"/"sales") is the rep.

Example:
  analyze_calls.py --input calls.json --rep-name "Alex" --output call_metrics.json
"""
import argparse
import json
import re
import sys

FILLERS = ("um", "uh", "like", "you know", "kind of", "sort of", "basically", "actually",
           "literally", "i mean", "right")
# Open questions invite elaboration; closed questions get yes/no/one-word answers.
OPEN_STARTERS = ("what", "how", "why", "tell me", "describe", "walk me", "help me understand",
                 "talk me through", "what's", "how's")
CLOSED_STARTERS = ("is", "are", "do", "does", "did", "can", "could", "would", "will", "have",
                   "has", "was", "were", "should", "may", "might")
QUESTION_STARTERS = OPEN_STARTERS + CLOSED_STARTERS + ("when", "where", "who", "which")

# MEDDIC + BANT qualification-topic keyword maps (rep raised the topic if any cue fires).
QUAL_TOPICS = {
    "pain": ("problem", "challenge", "pain", "struggle", "frustrat", "bottleneck", "issue",
             "difficult", "hard to", "manual", "waste", "inefficien"),
    "budget": ("budget", "cost", "price", "pricing", "invest", "spend", "afford", "roi",
               "return on", "business case", "$"),
    "authority": ("decision", "who else", "sign off", "approve", "stakeholder", "owner",
                  "decision maker", "your boss", "the team", "who's involved", "buying group"),
    "timeline": ("timeline", "timeframe", "when do you", "go live", "deadline", "by when",
                 "quarter", "implement", "start date", "urgency", "how soon"),
    "metrics": ("metric", "kpi", "measure", "target", "goal", "quota", "number", "improve by",
                "reduce", "increase", "save"),
    "champion": ("champion", "advocate", "internally", "on your side", "help me sell",
                 "make the case"),
    "decision_process": ("process", "steps", "evaluation", "procurement", "legal", "security review",
                         "next step", "how do you", "criteria", "pilot", "trial"),
    "competition": ("competitor", "alternative", "currently using", "other option", "vendor",
                    "incumbent", "versus", "compared to", "evaluating"),
}

OBJECTION_CUES = ("too expensive", "no budget", "not interested", "already have", "already using",
                  "not a priority", "not right now", "not the right time", "need to think",
                  "talk to my", "not sure", "concern", "worried", "but ", "however",
                  "the problem is", "i don't", "we don't", "can't", "too much", "not convinced")
ACK_MOVES = ("understand", "makes sense", "hear you", "fair", "good question", "great question",
             "let me", "tell me more", "what i mean", "the way i", "other customers",
             "appreciate", "totally", "i get", "that's a", "help me understand", "can i ask")


def is_rep(speaker, rep_name):
    s = (speaker or "").strip().lower()
    if rep_name and rep_name.lower() in s:
        return True
    return s in ("rep", "me", "sales", "salesperson", "host", "seller")


def split_sentences(text):
    return [s.strip() for s in re.split(r"[.!?]\s+|\n+", text) if s.strip()]


def classify_questions(text):
    """Return (total_q, open_q, closed_q) over a turn's text."""
    total = open_q = closed_q = 0
    for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
        s = sent.strip()
        sl = s.lower()
        if not sl:
            continue
        is_q = s.endswith("?")
        first = sl.split()[0] if sl.split() else ""
        two = " ".join(sl.split()[:2])
        starts_q = (first in QUESTION_STARTERS or any(sl.startswith(o) for o in OPEN_STARTERS))
        if not (is_q or starts_q):
            continue
        total += 1
        if any(sl.startswith(o) for o in OPEN_STARTERS) or first in ("what", "how", "why"):
            open_q += 1
        elif first in CLOSED_STARTERS:
            closed_q += 1
        else:
            # who/when/where/which -> informational, count as open-ish (invites detail)
            open_q += 1
    return total, open_q, closed_q


def filler_count(text):
    tl = " " + text.lower() + " "
    return sum(tl.count(" " + f + " ") for f in FILLERS)


def words(text):
    return len(re.findall(r"\b\w+\b", text or ""))


def discovery_score(questions, open_ratio, topics_covered):
    """0-100 composite: question volume (40) + open ratio (25) + topic coverage (35)."""
    # volume: 12+ questions on a discovery call ~ full marks
    q_pts = min(questions / 12.0, 1.0) * 40
    o_pts = (open_ratio if open_ratio is not None else 0) * 25
    cov_pts = (topics_covered / len(QUAL_TOPICS)) * 35
    return round(q_pts + o_pts + cov_pts, 1)


def analyze_call(call, rep_name):
    rep_words = prospect_words = 0
    rep_fillers = 0
    longest_monologue = 0
    total_q = open_q = closed_q = 0
    rep_blob_parts = []
    objections = 0
    objections_handled = 0
    prev_prospect_objection = False

    for turn in call.get("turns", []):
        text = turn.get("text", "")
        w = words(text)
        if is_rep(turn.get("speaker"), rep_name):
            rep_words += w
            rep_fillers += filler_count(text)
            longest_monologue = max(longest_monologue, w)
            tq, oq, cq = classify_questions(text)
            total_q += tq
            open_q += oq
            closed_q += cq
            rep_blob_parts.append(text.lower())
            # rep turn right after a prospect objection: did they acknowledge/clarify?
            if prev_prospect_objection:
                tl = text.lower()
                if any(a in tl for a in ACK_MOVES) or "?" in text:
                    objections_handled += 1
            prev_prospect_objection = False
        else:
            prospect_words += w
            pl = text.lower()
            if any(cue in pl for cue in OBJECTION_CUES):
                objections += 1
                prev_prospect_objection = True
            else:
                prev_prospect_objection = False

    rep_blob = " ".join(rep_blob_parts)
    topics = {t: any(cue in rep_blob for cue in cues) for t, cues in QUAL_TOPICS.items()}
    topics_covered = sum(1 for v in topics.values() if v)
    total = rep_words + prospect_words
    open_ratio = round(open_q / total_q, 2) if total_q else None
    dscore = discovery_score(total_q, open_ratio, topics_covered)

    return {
        "call_id": call.get("call_id", ""),
        "rep": call.get("rep", rep_name),
        "outcome": call.get("outcome", ""),
        "rep_words": rep_words,
        "prospect_words": prospect_words,
        "talk_listen_ratio": round(rep_words / prospect_words, 2) if prospect_words else None,
        "rep_talk_pct": round(rep_words / total * 100, 1) if total else None,
        "longest_rep_monologue_words": longest_monologue,
        "rep_questions": total_q,
        "open_questions": open_q,
        "closed_questions": closed_q,
        "open_question_ratio": open_ratio,
        "rep_filler_count": rep_fillers,
        "rep_filler_per_100w": round(rep_fillers / rep_words * 100, 2) if rep_words else None,
        "meddic_bant_coverage": topics,
        "topics_covered": topics_covered,
        "topics_total": len(QUAL_TOPICS),
        "discovery_score": dscore,
        "objections_raised": objections,
        "objections_handled": objections_handled,
        "objection_handling_rate": round(objections_handled / objections, 2) if objections else None,
        "total_words": total,
    }


def main():
    ap = argparse.ArgumentParser(description="Deterministic structural + discovery-quality call metrics.")
    ap.add_argument("--input", required=True, help="calls JSON (array of {call_id,outcome,turns:[...]})")
    ap.add_argument("--rep-name", default="", help="rep's name/label to identify their turns")
    ap.add_argument("--output", default="-", help="output metrics JSON (default stdout)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        calls = json.load(f)
    if not isinstance(calls, list):
        sys.exit("ERROR: input must be a JSON array of calls.")

    per_call = [analyze_call(c, args.rep_name) for c in calls]

    def avg(key, subset):
        vals = [c[key] for c in subset if c.get(key) is not None]
        return round(sum(vals) / len(vals), 2) if vals else None

    won = [c for c in per_call if (c.get("outcome") or "").lower() in ("won", "win")]
    lost = [c for c in per_call if (c.get("outcome") or "").lower() in ("lost", "loss")]

    # aggregate topic coverage across all calls
    topic_coverage_pct = {}
    if per_call:
        for t in QUAL_TOPICS:
            hit = sum(1 for c in per_call if c["meddic_bant_coverage"].get(t))
            topic_coverage_pct[t] = round(hit / len(per_call), 2)

    summary = {
        "calls_analyzed": len(per_call),
        "avg_talk_listen_ratio": avg("talk_listen_ratio", per_call),
        "avg_rep_talk_pct": avg("rep_talk_pct", per_call),
        "avg_questions_per_call": avg("rep_questions", per_call),
        "avg_open_question_ratio": avg("open_question_ratio", per_call),
        "avg_filler_per_100w": avg("rep_filler_per_100w", per_call),
        "avg_discovery_score": avg("discovery_score", per_call),
        "avg_objection_handling_rate": avg("objection_handling_rate", per_call),
        "topic_coverage_rate": topic_coverage_pct,
        "won_vs_lost": {
            "won_avg_talk_pct": avg("rep_talk_pct", won),
            "lost_avg_talk_pct": avg("rep_talk_pct", lost),
            "won_avg_questions": avg("rep_questions", won),
            "lost_avg_questions": avg("rep_questions", lost),
            "won_avg_discovery_score": avg("discovery_score", won),
            "lost_avg_discovery_score": avg("discovery_score", lost),
            "won_avg_open_ratio": avg("open_question_ratio", won),
            "lost_avg_open_ratio": avg("open_question_ratio", lost),
        },
    }

    result = {"summary": summary, "calls": per_call}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"call metrics for {len(per_call)} calls -> {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()

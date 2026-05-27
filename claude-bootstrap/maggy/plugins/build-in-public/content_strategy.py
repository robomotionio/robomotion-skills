"""Content strategy engine — decides format, structure, timing per event.

Replaces simple one-post-per-event with intelligent scheduling:
- Classifies content complexity → format (single, thread, series)
- Thread splitting for rich X content with numbered posts
- Multi-day series for major features (teaser → deep dive → lessons)
- Queue-aware scheduling — never dumps, spaces out optimally
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

BEST_TIMES = {
    "linkedin": {
        "deep_dive": ["Tue 09:00", "Wed 09:00", "Thu 09:00"],
        "announcement": ["Tue 08:30", "Wed 08:30", "Thu 08:30"],
        "insight": ["Tue 10:00", "Wed 10:00", "Thu 10:00"],
    },
    "x": {
        "deep_dive": ["Tue 10:00", "Wed 10:00", "Thu 10:00"],
        "announcement": ["Tue 09:00", "Wed 09:00", "Thu 14:00"],
        "insight": ["Tue 11:00", "Wed 11:00", "Thu 11:00", "Fri 11:00"],
        "thread": ["Wed 10:30", "Thu 10:30"],
    },
}

SERIES_TEMPLATE = {
    "teaser": {"delay_days": 0, "tone": "curiosity, one-line hook"},
    "deep_dive": {"delay_days": 1, "tone": "technical, teaches something"},
    "lessons": {"delay_days": 3, "tone": "reflective, what surprised you"},
}


@dataclass
class ScheduledPost:
    channel: str
    text: str
    scheduled_at: str
    format: str  # single, thread_tweet, series_teaser, etc.
    thread_index: int = 0
    thread_total: int = 1
    media: list[str] = field(default_factory=list)


class ContentStrategy:
    """Decides what, where, when, and how to post."""

    def __init__(self, config: dict):
        self._config = config
        self._queue = self._load_queue()

    def plan(self, event_type: str, context: dict,
             narratives: dict) -> list[ScheduledPost]:
        """Plan the full posting schedule for an event. Returns ordered posts."""
        posts: list[ScheduledPost] = []
        channels = self._config.get("channels", {})

        for channel, base_text in narratives.items():
            cfg = channels.get(channel, {})
            content_type = self._classify(event_type, base_text, channel)
            format_type = self._best_format(base_text, channel, content_type)

            if format_type == "thread":
                posts.extend(self._build_thread(
                    channel, base_text, cfg, content_type, context,
                ))
            elif format_type == "series":
                posts.extend(self._build_series(
                    channel, context, cfg,
                ))
            else:
                posts.append(self._build_single(
                    channel, base_text, cfg, content_type,
                ))

        # Queue-aware scheduling — spread out, don't double-book
        return self._space_out(posts)

    def _classify(self, event_type: str, text: str, channel: str) -> str:
        """Classify content type: deep_dive, announcement, insight."""
        if event_type == "on_feature_shipped":
            return "announcement"
        if event_type == "on_review_passed":
            return "insight"
        if len(text) > 500 or channel == "linkedin":
            return "deep_dive"
        return "insight"

    def _best_format(self, text: str, channel: str,
                     content_type: str) -> str:
        """Decide format: single, thread, or series."""
        if channel != "x":
            return "single"

        max_chars = self._config.get("channels", {}).get("x", {}).get(
            "max_chars", 280,
        )

        # Thread decision: content >2x tweet length AND has multiple insights
        if len(text) > max_chars * 1.5:
            # Ask AI if this should be a thread
            decision = self._ai_decide_thread(text)
            if decision:
                return "thread"

        # Series decision: feature shipped + deep_dive → 3-post arc
        if content_type in ("announcement", "deep_dive") and len(text) > 400:
            return "series"

        return "single"

    def _ai_decide_thread(self, text: str) -> bool:
        """Ask DeepSeek if this content is thread-worthy."""
        prompt = (
            f"Does this content have multiple distinct, valuable insights "
            f"that each deserve their own tweet in a thread? "
            f"Reply YES or NO.\n\n{text[:500]}"
        )
        try:
            deepseek = os.path.expanduser("~/bin/deepseek")
            result = subprocess.run(
                [deepseek, "--flash", prompt],
                capture_output=True, text=True, timeout=15,
            )
            return "YES" in (result.stdout or "").upper()[:10]
        except Exception:
            return len(text) > 400  # Fallback heuristic

    def _build_single(self, channel: str, text: str, cfg: dict,
                      content_type: str) -> ScheduledPost:
        """Build a single post."""
        return ScheduledPost(
            channel=channel,
            text=text[:cfg.get("max_chars", 3000)],
            scheduled_at=self._best_time(channel, content_type, offset_days=0),
            format="single",
            media=[],
        )

    def _build_thread(self, channel: str, text: str, cfg: dict,
                      content_type: str, context: dict) -> list[ScheduledPost]:
        """Split rich content into a numbered X thread."""
        max_chars = cfg.get("max_chars", 280)
        tweets = self._split_into_tweets(text, max_chars)
        if len(tweets) <= 1:
            return [self._build_single(channel, text, cfg, content_type)]

        base_time = self._next_available_slot(channel, content_type)
        posts = []
        for i, tweet in enumerate(tweets):
            posts.append(ScheduledPost(
                channel=channel,
                text=f"{tweet} ({i+1}/{len(tweets)})" if len(tweets) > 1 else tweet,
                scheduled_at=base_time.isoformat(),
                format="thread_tweet",
                thread_index=i + 1,
                thread_total=len(tweets),
            ))
            base_time += timedelta(minutes=2)  # Thread spacing

        return posts

    def _split_into_tweets(self, text: str, max_chars: int) -> list[str]:
        """Split long text into tweet-sized chunks at sentence boundaries."""
        tweets = []
        sentences = text.replace("\n", " ").split(". ")
        current = ""

        for sentence in sentences:
            test = f"{current}. {sentence}" if current else sentence
            if len(test) > max_chars and current:
                tweets.append(current.strip())
                current = sentence
            else:
                current = test

        if current:
            tweets.append(current.strip()[:max_chars])
        return tweets

    def _build_series(self, channel: str, context: dict,
                      cfg: dict) -> list[ScheduledPost]:
        """Build a multi-day series arc for major features."""
        what = context.get("what", "a feature")
        body = context.get("context", "")[:500]
        posts = []

        for stage, template in SERIES_TEMPLATE.items():
            delay = template["delay_days"]
            tone = template["tone"]

            prompt = (
                f"Write a {stage} post ({tone}) for {channel.upper()} "
                f"about: {what}. Context: {body}. "
                f"Stage: {stage}. "
                f"Max {cfg.get('max_chars', 280)} chars. "
                f"Write ONLY the post text."
            )
            try:
                deepseek = os.path.expanduser("~/bin/deepseek")
                result = subprocess.run(
                    [deepseek, "--flash", prompt],
                    capture_output=True, text=True, timeout=30,
                )
                text = result.stdout.strip() if result.returncode == 0 else ""
            except Exception:
                text = ""

            if text:
                posts.append(ScheduledPost(
                    channel=channel,
                    text=text[:cfg.get("max_chars", 3000)],
                    scheduled_at=self._best_time(
                        channel, "deep_dive" if stage != "teaser" else "announcement",
                        offset_days=delay,
                    ),
                    format=f"series_{stage}",
                    media=[],
                ))

        return posts

    def _best_time(self, channel: str, content_type: str,
                   offset_days: int = 0) -> str:
        """Get best posting time for channel + content type."""
        times = BEST_TIMES.get(channel, {}).get(
            content_type, BEST_TIMES.get(channel, {}).get("insight", ["Tue 09:00"]),
        )

        now = datetime.now(timezone.utc)
        # Find next matching day
        for days_ahead in range(offset_days, offset_days + 14):
            target = now + timedelta(days=days_ahead)
            day_short = target.strftime("%a")
            for t in times:
                if t.startswith(day_short):
                    hour, minute = map(int, t.split(" ")[1].split(":"))
                    return target.replace(
                        hour=hour, minute=minute, second=0, microsecond=0,
                    ).isoformat()

        # Fallback
        target = now + timedelta(days=offset_days)
        return target.replace(hour=9, minute=0, second=0, microsecond=0).isoformat()

    def _next_available_slot(self, channel: str,
                             content_type: str) -> datetime:
        """Find next available slot, considering queue."""
        candidate = datetime.fromisoformat(
            self._best_time(channel, content_type, offset_days=0),
        )
        # Avoid double-booking: if a post exists within 2h, push forward
        for post in self._queue:
            existing = datetime.fromisoformat(post["scheduled_at"])
            if abs((candidate - existing).total_seconds()) < 7200:
                candidate += timedelta(hours=2)
        return candidate

    def _space_out(self, posts: list[ScheduledPost]) -> list[ScheduledPost]:
        """Ensure posts don't overlap — spread across available slots."""
        now = datetime.now(timezone.utc)
        used_slots: set[str] = set()

        for post in self._queue:
            used_slots.add(post["scheduled_at"][:13])  # Hour precision

        for post in posts:
            scheduled = datetime.fromisoformat(post.scheduled_at)
            # If slot taken, push to next available
            while scheduled.isoformat()[:13] in used_slots:
                scheduled += timedelta(hours=1)
            used_slots.add(scheduled.isoformat()[:13])
            post.scheduled_at = scheduled.isoformat()

        return sorted(posts, key=lambda p: p.scheduled_at)

    def commit(self, posts: list[ScheduledPost]):
        """Save scheduled posts to queue."""
        for post in posts:
            self._queue.append({
                "channel": post.channel,
                "text": post.text[:100],
                "scheduled_at": post.scheduled_at,
                "format": post.format,
            })
        self._save_queue()

    def _load_queue(self) -> list[dict]:
        qf = Path.home() / ".maggy" / "build-in-public" / "schedule.json"
        try:
            return json.loads(qf.read_text())
        except Exception:
            return []

    def _save_queue(self):
        qf = Path.home() / ".maggy" / "build-in-public" / "schedule.json"
        qf.parent.mkdir(parents=True, exist_ok=True)
        qf.write_text(json.dumps(self._queue[-50:], indent=2))  # Keep last 50

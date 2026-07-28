#!/usr/bin/env python3
"""Export public X audiences with Xquik X Follower Scraper on Apify."""

import argparse
import json
import math
import os
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apify_common  # noqa: E402


APIFY_ACTOR = "xquik~x-follower-scraper"
RELATIONS = (
    "followers",
    "following",
    "verified_followers",
    "list_members",
    "list_followers",
    "community_members",
)
X_HOSTS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}


def positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be at least 1")
    return parsed


def nonnegative_int(value):
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value cannot be negative")
    return parsed


def positive_amount(value):
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a finite positive number")
    return parsed


def x_handle(value):
    handle = value.strip().lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9_]{1,15}", handle):
        raise argparse.ArgumentTypeError(
            "handle must contain 1 to 15 letters, digits, or underscores"
        )
    return handle


def numeric_id(value):
    identifier = value.strip()
    if not identifier.isdigit():
        raise argparse.ArgumentTypeError("ID must contain only digits")
    return identifier


def x_url(value):
    target = value.strip()
    parsed = urlparse(target)
    if parsed.scheme != "https" or parsed.hostname not in X_HOSTS:
        raise argparse.ArgumentTypeError(
            "URL must be an HTTPS x.com or twitter.com URL"
        )
    return target


def build_input(args):
    run_input = {
        "maxItems": args.max_profiles,
        "outputMode": args.output_mode,
        "dedupeMode": args.dedupe_mode,
        "includeTargetMetadata": True,
    }
    if args.handle:
        run_input["twitterHandles"] = args.handle
    if args.user_id:
        run_input["userIds"] = args.user_id
    if args.list_id:
        run_input["listIds"] = args.list_id
    if args.community_id:
        run_input["communityIds"] = args.community_id
    if args.url:
        run_input["startUrls"] = [{"url": url} for url in args.url]

    relations = args.relation or ["followers"]
    if len(relations) == 1:
        run_input["relation"] = relations[0]
    else:
        run_input["relations"] = relations

    optional = {
        "maxItemsPerTarget": args.max_per_target,
        "minFollowers": args.min_followers,
        "bioContains": args.bio_contains,
        "locationContains": args.location_contains,
    }
    for field, value in optional.items():
        if value is not None:
            run_input[field] = value
    if args.verified_only:
        run_input["verifiedOnly"] = True
    return run_input


def partition_rows(items):
    profiles = []
    diagnostics = []
    reports = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        result_type = item.get("resultType")
        if result_type == "diagnostic":
            diagnostics.append(item)
        elif result_type == "run-report":
            reports.append(item)
        else:
            profiles.append(item)
    return profiles, diagnostics, reports


def integer_value(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def first_value(row, *keys):
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return ""


def profile_sort_key(profile):
    overlap = integer_value(
        first_value(profile, "overlapCount", "overlap_count")
    )
    followers = integer_value(
        first_value(
            profile,
            "followersCount",
            "followers_count",
            "followers",
        )
    )
    return overlap, followers


def print_summary(profiles):
    print(
        f"{'#':<4} {'Followers':<11} {'Overlap':<9} "
        f"{'Username':<18} {'Relation':<20} Source"
    )
    print("-" * 108)
    for index, profile in enumerate(profiles, 1):
        followers = integer_value(
            first_value(
                profile,
                "followersCount",
                "followers_count",
                "followers",
            )
        )
        overlap = integer_value(
            first_value(profile, "overlapCount", "overlap_count")
        )
        username = first_value(
            profile,
            "userName",
            "username",
            "screenName",
            "screen_name",
        )
        relation = first_value(
            profile,
            "sourceRelation",
            "source_relation",
        )
        source = first_value(
            profile,
            "sourceTarget",
            "source_target",
        )
        print(
            f"{index:<4} {followers:<11} {overlap:<9} "
            f"{str(username)[:16]:<18} {str(relation)[:18]:<20} "
            f"{str(source)[:30]}"
        )


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Export public X audiences with Xquik X Follower Scraper on Apify."
        )
    )
    parser.add_argument(
        "--handle",
        action="append",
        type=x_handle,
        help="X handle. Repeat for several targets.",
    )
    parser.add_argument(
        "--user-id",
        action="append",
        type=numeric_id,
        help="Numeric X user ID. Repeat as needed.",
    )
    parser.add_argument(
        "--list-id",
        action="append",
        type=numeric_id,
        help="Numeric X list ID. Repeat as needed.",
    )
    parser.add_argument(
        "--community-id",
        action="append",
        type=numeric_id,
        help="Numeric community ID. Repeat as needed.",
    )
    parser.add_argument(
        "--url",
        action="append",
        type=x_url,
        help="Public X target URL. Repeat as needed.",
    )
    parser.add_argument(
        "--relation",
        action="append",
        choices=RELATIONS,
        help="Relation. Repeat for a multi-relation run.",
    )
    parser.add_argument(
        "--max-profiles",
        type=positive_int,
        default=100,
        help="Run-wide result cap. Default: 100.",
    )
    parser.add_argument(
        "--max-per-target",
        type=positive_int,
        help="Optional result cap for each target.",
    )
    parser.add_argument(
        "--output-mode",
        choices=["compact", "full", "raw"],
        default="compact",
        help="Actor output depth. Default: compact.",
    )
    parser.add_argument(
        "--dedupe-mode",
        choices=["none", "first", "merge"],
        default="first",
        help="Duplicate handling. Use merge for overlap analysis.",
    )
    parser.add_argument(
        "--min-followers",
        type=nonnegative_int,
        help="Minimum follower count filter.",
    )
    parser.add_argument(
        "--verified-only",
        action="store_true",
        help="Keep verified profiles only.",
    )
    parser.add_argument(
        "--bio-contains",
        help="Case-insensitive biography filter.",
    )
    parser.add_argument(
        "--location-contains",
        help="Case-insensitive location filter.",
    )
    parser.add_argument(
        "--estimate-only",
        action="store_true",
        help="Preview run limits without spending.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm a paid Apify run.",
    )
    parser.add_argument(
        "--max-cost-usd",
        type=positive_amount,
        default=1.0,
        help="Hard maximum charge. Default: 1.00.",
    )
    parser.add_argument(
        "--apify-timeout",
        type=positive_int,
        default=600,
        help="Abort after this many seconds. Default: 600.",
    )
    parser.add_argument(
        "--output",
        choices=["json", "summary"],
        default="json",
        help="Output format. Default: json.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not any(
        [
            args.handle,
            args.user_id,
            args.list_id,
            args.community_id,
            args.url,
        ]
    ):
        parser.error(
            "add at least one handle, user ID, list ID, community ID, or URL"
        )

    run_input = build_input(args)
    if args.estimate_only:
        estimate = apify_common.estimate(
            APIFY_ACTOR,
            run_input,
            max_cost_usd=args.max_cost_usd,
            timeout_s=args.apify_timeout,
            items_hint=args.max_profiles,
            label="x-follower-scraper",
        )
        json.dump(estimate, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not token:
        sys.exit("ERROR: APIFY_API_TOKEN is required for a paid Actor run.")
    if not args.yes:
        sys.exit(
            "ERROR: this Apify Actor spends credits. Re-run with --yes, "
            "or use --estimate-only to preview limits."
        )

    try:
        items = apify_common.run_actor(
            APIFY_ACTOR,
            run_input,
            max_cost_usd=args.max_cost_usd,
            timeout_s=args.apify_timeout,
            tok=token,
        )
    except apify_common.CostGateError as error:
        sys.exit(f"ERROR: cost gate: {error}")
    except apify_common.ApifyError as error:
        sys.exit(f"ERROR: Apify: {error}")

    profiles, diagnostics, reports = partition_rows(items)
    for diagnostic in diagnostics:
        status = diagnostic.get("status", "unknown")
        message = diagnostic.get("message", "No diagnostic message returned.")
        print(f"Actor diagnostic ({status}): {message}", file=sys.stderr)
    for report in reports:
        status = report.get("status", "completed")
        print(f"Actor run report: {status}", file=sys.stderr)

    profiles.sort(key=profile_sort_key, reverse=True)
    if args.output == "summary":
        print_summary(profiles)
    else:
        json.dump(profiles, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()

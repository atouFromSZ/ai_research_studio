from __future__ import annotations

import argparse

from ai_research_studio.workflows.daily_brief.orchestrator import (
    generate_daily_brief,
    summarize_latest_daily_brief,
    view_latest_daily_brief,
)


def run_daily_brief_command() -> None:
    result = generate_daily_brief()
    if result.source_refs:
        print(f"Daily brief generated: {result.source_refs[0]}")
    else:
        print(result.headline)


def view_latest_daily_brief_command() -> None:
    result = view_latest_daily_brief()
    print(result.headline)
    print()
    for item in result.key_points:
        print(item)


def summarize_latest_daily_brief_command() -> None:
    result = summarize_latest_daily_brief()
    print(result.headline)
    print()
    for item in result.key_points:
        print(item)
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-research-studio")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("daily-brief", help="Generate daily brief")
    subparsers.add_parser("daily-brief-view", help="View latest daily brief")
    subparsers.add_parser("daily-brief-summary", help="Summarize latest daily brief")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "daily-brief":
        run_daily_brief_command()
        return

    if args.command == "daily-brief-view":
        view_latest_daily_brief_command()
        return

    if args.command == "daily-brief-summary":
        summarize_latest_daily_brief_command()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
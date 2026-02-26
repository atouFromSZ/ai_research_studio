import argparse
from rich import print

from ai_research_studio.pipelines.daily_brief import run_daily_brief


def run_daily_brief_command() -> None:
    report_path = run_daily_brief()
    print(f"[green]Daily brief generated:[/green] {report_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-research-studio",
        description="AI Research Studio task runner",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "daily-brief",
        help="Generate the daily brief markdown report",
    )

    subparsers.add_parser(
        "healthcheck",
        help="Run a simple project health check",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "daily-brief":
        run_daily_brief_command()
    elif args.command == "healthcheck":
        print("[green]AI Research Studio is healthy.[/green]")
    else:
        parser.print_help()
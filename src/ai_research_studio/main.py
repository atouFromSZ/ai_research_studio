from rich import print

from ai_research_studio.pipelines.daily_brief import run_daily_brief


def main() -> None:
    report_path = run_daily_brief()
    print(f"[green]Daily brief generated:[/green] {report_path}")


if __name__ == "__main__":
    main()
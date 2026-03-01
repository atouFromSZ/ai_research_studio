## cli.py 会用 argparse 解析命令参数
## 如果命令是 daily-brief，则调用 run_daily_brief_command()
## 如果命令是 healthcheck，则打印健康检查结果
## 如果命令是其他，则打印帮助信息

import argparse
from rich import print

from ai_research_studio.pipelines.daily_brief import run_daily_brief


def run_daily_brief_command() -> None:
    """CLI 封装：运行 daily brief 流程，并在终端中回显生成路径。"""
    report_path = run_daily_brief()
    print(f"[green]Daily brief generated:[/green] {report_path}")


def build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器，注册所有支持的子命令。"""
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
    """入口函数：解析命令并分发到对应子命令实现。"""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "daily-brief":
        run_daily_brief_command()
    elif args.command == "healthcheck":
        print("[green]AI Research Studio is healthy.[/green]")
    else:
        parser.print_help()
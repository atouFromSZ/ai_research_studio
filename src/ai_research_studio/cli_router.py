from __future__ import annotations

import sys

from ai_research_studio.workflows.telegram_commands.router import route_telegram_command


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python -m ai_research_studio.cli_router '<命令>'")
        return 1

    text = " ".join(sys.argv[1:]).strip()
    result = route_telegram_command(text)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
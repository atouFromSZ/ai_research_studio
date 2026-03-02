from __future__ import annotations

from pathlib import Path


def write_markdown(file_path: Path, content: str) -> Path:
    """确保目标目录存在后，把 Markdown 内容写入磁盘并返回路径。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path


def get_latest_markdown_file(directory: Path) -> Path | None:
    files = sorted(
        directory.glob("*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def read_markdown(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")
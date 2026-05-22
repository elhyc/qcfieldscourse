"""Normalize nbconvert Markdown math so mdBook's MathJax renderer can read it."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


INLINE_DOLLAR = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)")
SINGLE_LINE_DISPLAY = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$")
MARKDOWN_ESCAPE_IN_MATH = re.compile(r"(?<!\\)([_*|])")


def normalize_macros(text: str) -> str:
    """Use TeX definitions that can be safely repeated across notebook cells."""
    return (
        text.replace(r"\renewcommand{\ket}[1]{|#1\rangle}", r"\def\ket#1{|#1\rangle}")
        .replace(r"\renewcommand{\bra}[1]{\langle#1|}", r"\def\bra#1{\langle#1|}")
        .replace(r"\newcommand{\ket}[1]{|#1\rangle}", r"\def\ket#1{|#1\rangle}")
        .replace(r"\newcommand{\bra}[1]{\langle#1|}", r"\def\bra#1{\langle#1|}")
    )


def escape_display_linebreaks(text: str) -> str:
    """mdBook needs TeX linebreaks doubled inside display math blocks."""
    return text.replace(r"\\", r"\\\\")


def escape_markdown_in_math(text: str) -> str:
    """Hide Markdown punctuation that should reach MathJax unchanged."""
    return MARKDOWN_ESCAPE_IN_MATH.sub(r"\\\1", text)


def normalize_inline_math(text: str) -> str:
    """Convert Jupyter-style inline dollars outside inline code spans."""
    parts = re.split(r"(`+[^`]*`+)", text)

    def replace_inline(match: re.Match[str]) -> str:
        content = escape_markdown_in_math(match.group(1))
        return rf"\\({content}\\)"

    for index, part in enumerate(parts):
        if index % 2 == 0:
            parts[index] = INLINE_DOLLAR.sub(replace_inline, part)
    return "".join(parts)


def normalize_markdown(text: str) -> str:
    text = normalize_macros(text)
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    in_fence = False
    in_display = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            output.append(line)
            continue

        if in_fence:
            output.append(line)
            continue

        if in_display:
            if stripped.startswith("$$"):
                output.append(line.replace("$$", r"\\]", 1))
                in_display = False
            else:
                line = escape_display_linebreaks(line)
                output.append(escape_markdown_in_math(line))
            continue

        if stripped == "$$":
            output.append(line.replace("$$", r"\\[" if not in_display else r"\\]"))
            in_display = not in_display
            continue

        if stripped.startswith("$$") and not stripped.endswith("$$"):
            output.append(line.replace("$$", r"\\[", 1))
            in_display = True
            continue

        def replace_display(match: re.Match[str]) -> str:
            content = escape_display_linebreaks(match.group(1))
            content = escape_markdown_in_math(content)
            return rf"\\[{content}\\]"

        line = SINGLE_LINE_DISPLAY.sub(replace_display, line)
        line = normalize_inline_math(line)
        output.append(line)

    return "".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    source = args.path.read_text(encoding="utf-8")
    args.path.write_text(normalize_markdown(source), encoding="utf-8")


if __name__ == "__main__":
    main()

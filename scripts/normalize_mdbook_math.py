"""Normalize nbconvert Markdown math so mdBook's MathJax renderer can read it."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


INLINE_DOLLAR = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)")
SINGLE_LINE_DISPLAY = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$")
MARKDOWN_ESCAPE_IN_MATH = re.compile(r"(?<!\\)([_*])")
LOCAL_BRAKET_MACRO = re.compile(
    r"(?m)^\$\$\\(?:re)?newcommand\{\\(?:ket|bra)\}\[1\]\{[^$\n]+\}\$\$\s*\n?"
)
DISPLAY_ENV_START = re.compile(r"^\\begin\{(equation\*?|align\*?)\}\s*$")
DISPLAY_ENV_END = re.compile(r"^\\end\{(equation\*?|align\*?)\}\s*$")
TRAILING_WHITESPACE = re.compile(r"[ \t]+(?=\r?\n|$)")
BRAKET_DEFINITIONS = (
    r"\\(\def\ket#1{\left|#1\right\rangle}"
    r"\def\bra#1{\left\langle#1\right|}\\)"
)


def strip_repeated_braket_macros(text: str) -> str:
    """Remove notebook-local braket macro cells; one page-level definition is inserted later."""
    return LOCAL_BRAKET_MACRO.sub("", text)


def needs_braket_macros(text: str) -> bool:
    return r"\ket" in text or r"\bra" in text


def escape_display_linebreaks(text: str) -> str:
    """mdBook needs TeX linebreaks doubled inside display math blocks."""
    return text.replace(r"\\", r"\\\\")


def line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


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
    inject_braket_macros = needs_braket_macros(text)
    text = strip_repeated_braket_macros(text)
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    in_fence = False
    in_html_comment = False
    in_display = False
    in_display_env: str | None = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            output.append(line)
            continue

        if in_fence:
            output.append(line)
            continue

        if in_html_comment:
            output.append(line)
            if "-->" in stripped:
                in_html_comment = False
            continue

        if stripped.startswith("<!--"):
            output.append(line)
            if "-->" not in stripped:
                in_html_comment = True
            continue

        if in_display_env is not None:
            end_match = DISPLAY_ENV_END.match(stripped)
            if end_match and end_match.group(1) == in_display_env:
                if in_display_env.startswith("align"):
                    output.append(r"\end{aligned}" + line_ending(line))
                output.append(r"\\]" + line_ending(line))
                in_display_env = None
            else:
                line = escape_display_linebreaks(line)
                output.append(escape_markdown_in_math(line))
            continue

        start_match = DISPLAY_ENV_START.match(stripped)
        if start_match:
            in_display_env = start_match.group(1)
            output.append(r"\\[" + line_ending(line))
            if in_display_env.startswith("align"):
                output.append(r"\begin{aligned}" + line_ending(line))
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

    normalized = TRAILING_WHITESPACE.sub("", "".join(output))
    if inject_braket_macros and not normalized.startswith(BRAKET_DEFINITIONS):
        return f"{BRAKET_DEFINITIONS}\n\n{normalized}"

    return normalized


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    source = args.path.read_text(encoding="utf-8")
    args.path.write_text(normalize_markdown(source), encoding="utf-8")


if __name__ == "__main__":
    main()

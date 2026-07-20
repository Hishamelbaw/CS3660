import re
from html import escape

_LINE_RE = re.compile(r"^\s*([^:]+):\s*(\d+(?:\.\d+)?)\s*/\s*10\s*-?\s*(.*)$")

_WIDTH = 640
_BAR_MAX_WIDTH = 360
_ROW_HEIGHT = 70
_LEFT_MARGIN = 20
_LABEL_WIDTH = 160


def _parse_fit_analysis(fit_analysis_text: str) -> list[tuple[str, float, str]]:
    rows = []
    for line in fit_analysis_text.splitlines():
        match = _LINE_RE.match(line)
        if not match:
            continue
        label, score, reason = match.groups()
        rows.append((label.strip(), float(score), reason.strip()))
    return rows


def _score_color(score: float) -> str:
    if score >= 7:
        return "#16a34a"
    if score >= 4:
        return "#d97706"
    return "#dc2626"


def render_infographic_svg(fit_analysis_text: str) -> str:
    rows = _parse_fit_analysis(fit_analysis_text)
    if not rows:
        rows = [("Overall Fit", 0.0, "No analysis available")]

    height = _ROW_HEIGHT * len(rows) + 40
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{height}" '
        f'viewBox="0 0 {_WIDTH} {height}" font-family="Helvetica, Arial, sans-serif">',
        f'<rect x="0" y="0" width="{_WIDTH}" height="{height}" fill="#ffffff"/>',
        f'<text x="{_LEFT_MARGIN}" y="28" font-size="18" font-weight="bold" fill="#111111">'
        f"Company Fit</text>",
    ]

    for i, (label, score, reason) in enumerate(rows):
        y = 50 + i * _ROW_HEIGHT
        bar_width = max(0.0, min(score, 10.0)) / 10 * _BAR_MAX_WIDTH
        color = _score_color(score)
        parts.append(
            f'<text x="{_LEFT_MARGIN}" y="{y + 14}" font-size="13" fill="#111111">'
            f"{escape(label)}</text>"
        )
        parts.append(
            f'<rect x="{_LEFT_MARGIN + _LABEL_WIDTH}" y="{y}" width="{_BAR_MAX_WIDTH}" '
            f'height="18" fill="#e5e7eb" rx="4"/>'
        )
        parts.append(
            f'<rect x="{_LEFT_MARGIN + _LABEL_WIDTH}" y="{y}" width="{bar_width:.1f}" '
            f'height="18" fill="{color}" rx="4"/>'
        )
        parts.append(
            f'<text x="{_LEFT_MARGIN + _LABEL_WIDTH + _BAR_MAX_WIDTH + 8}" y="{y + 14}" '
            f'font-size="12" fill="#111111">{score:g}/10</text>'
        )
        parts.append(
            f'<text x="{_LEFT_MARGIN + _LABEL_WIDTH}" y="{y + 34}" font-size="11" '
            f'fill="#4b5563">{escape(reason)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)

"""横向柱状图SVG生成。"""


def horizontal_bar(value: float, max_val: float, color: str = '#2a9d8f',
                   width: int = 400, height: int = 22) -> str:
    """单条横向柱。"""
    bar_w = abs(value) / max_val * width if max_val > 0 else 0
    bar_w = min(bar_w, width)
    return f'<rect x="0" y="0" width="{bar_w:.0f}" height="{height}" rx="3" fill="{color}" opacity="0.75"/>'


def sparkbar_html(value: float, max_val: float, css_class: str = 'sh') -> str:
    """表格内迷你柱状图HTML。"""
    pct = value / max_val * 100 if max_val > 0 else 0
    pct = min(pct, 100)
    return (f'<td class="sb"><div class="sb-b {css_class}" style="width:{pct:.0f}%"></div>'
            f'<span class="sb-v"><b>{value:.1f}</b></span></td>')

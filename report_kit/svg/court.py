"""半场SVG模板 + 投篮坐标转换。"""


def court_small():
    """480×380散点图用半场 (viewBox="0 0 480 380")。"""
    return '''<g transform="translate(29,10)"><rect x="27.5" y="9.4" width="367.0" height="254.2" rx="2" fill="#eef0f3" stroke="#b0b6be" stroke-width="1.2"/>
<rect x="142.2" y="160.0" width="137.6" height="113.0" rx="1" fill="#e2e5ea" stroke="#b0b6be" stroke-width="0.8"/>
<line x1="142.2" y1="160.0" x2="279.8" y2="160.0" stroke="#b0b6be" stroke-width="0.8"/>
<circle cx="211.0" cy="160.0" r="27.5" fill="none" stroke="#b0b6be" stroke-width="0.6" stroke-dasharray="3,3"/>
<path d="M 64.2 273.0 Q 64.2 35.8, 211.0 35.8 Q 357.8 35.8, 357.8 273.0" fill="none" stroke="#b0b6be" stroke-width="1"/>
<circle cx="211.0" cy="258.9" r="5.5" fill="none" stroke="#b0b6be" stroke-width="1.2"/>
<line x1="197.2" y1="265.5" x2="224.8" y2="265.5" stroke="#b0b6be" stroke-width="1.5"/>
<path d="M 183.5 273.0 A 27.5 28.2 0 0 1 238.5 273.0" fill="none" stroke="#b0b6be" stroke-width="0.6"/></g>'''


def court_large():
    """660×410威胁图用半场。"""
    return '''<g transform="translate(44,10)">
<rect x="41.3" y="13.1" width="550.4" height="353.8" rx="2" fill="#eef0f3" stroke="#b0b6be" stroke-width="1.2"/>
<rect x="213.3" y="222.8" width="206.4" height="157.2" rx="1" fill="#e2e5ea" stroke="#b0b6be" stroke-width="0.8"/>
<line x1="213.3" y1="222.8" x2="419.7" y2="222.8" stroke="#b0b6be" stroke-width="0.8"/>
<circle cx="316.5" cy="222.8" r="41.3" fill="none" stroke="#b0b6be" stroke-width="0.6" stroke-dasharray="3,3"/>
<path d="M 96.3 380.0 Q 96.3 49.8, 316.5 49.8 Q 536.7 49.8, 536.7 380.0" fill="none" stroke="#b0b6be" stroke-width="1"/>
<circle cx="316.5" cy="360.3" r="8.3" fill="none" stroke="#b0b6be" stroke-width="1.2"/>
<line x1="295.9" y1="369.5" x2="337.1" y2="369.5" stroke="#b0b6be" stroke-width="1.5"/>
<path d="M 275.2 380.0 A 41.3 39.3 0 0 1 357.8 380.0" fill="none" stroke="#b0b6be" stroke-width="0.6"/>
</g>'''


# 威胁图球员位置坐标 (SVG absolute coords on court_large)
POSITION_COORDS = {
    'PG': (360, 120),
    'SG': (530, 160),
    'SF': (140, 160),
    'PF': (450, 280),
    'C':  (260, 300),
}


def shot_to_svg(shot: dict) -> str:
    """将K8投篮记录转换为SVG元素。

    shot: {shotX: 0-1, shotY: 0-1, pbpType: '2PM'|'2Pm'|'3PM'|'3Pm'}
    大写M = 命中, 小写m = 未中
    返回: SVG circle(命中) 或 双line X(未中)
    """
    sx = float(shot.get('shotX', 0.5))
    sy = float(shot.get('shotY', 0.5))
    ptype = shot.get('pbpType', '')

    # 归一化坐标 → SVG坐标 (court_small viewBox)
    x = 56.5 + sx * 367.0
    y = 19.4 + sy * 254.2

    is_made = ptype.endswith('M')
    if is_made:
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2a9d8f" opacity="0.75"/>'
    else:
        x1, y1 = x - 3.5, y - 3.5
        x2, y2 = x + 3.5, y + 3.5
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="#e63946" stroke-width="1.8" opacity="0.65"/>'
                f'<line x1="{x2:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y2:.1f}" '
                f'stroke="#e63946" stroke-width="1.8" opacity="0.65"/>')

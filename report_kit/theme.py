"""Color palette, PPP heat colors, threat classification."""


# Default color palette (shared across all reports)
COLORS = {
    'red': '#e63946',
    'green': '#2a9d8f',
    'blue': '#457b9d',
    'gray': '#95a0ab',
    'light_gray': '#b0b8c1',
    'bg_gray': '#f7f8fa',
    'border': '#e2e6ea',
    'text': '#1a1a2e',
    'text_light': '#5a6270',
    'yellow': '#e9a820',
}


def ppp_class(ppp: float) -> str:
    """PPP heat color CSS class.

    Returns: 'pp pp-h hg' (very good ≥1.3), 'pp pp-h hw' (good ≥1.0),
             'pp pp-l hr' (bad <0.75), 'pp pp-l' (neutral)
    """
    if ppp >= 1.3:
        return 'pp pp-h hg'
    elif ppp >= 1.0:
        return 'pp pp-h hw'
    elif ppp < 0.75:
        return 'pp pp-l hr'
    else:
        return 'pp pp-l'


def bar_size_class(pct: float, max_pct: float) -> str:
    """Mini bar CSS class based on percentage magnitude."""
    if pct >= 20:
        return 'sb-b sh'
    elif pct >= 8:
        return 'sb-b sw'
    else:
        return 'sb-b sc'


def threat_level(three_pct: float, three_att_per_game: float) -> tuple:
    """三分投射威胁分级。

    注意：此分级仅评估三分投射威胁，不代表该球员可以在所有区域被放空。
    绿色球员仍可能具备篮下终结、中距离、空切等其他进攻威胁。
    "三分可收缩"意味着防守端可在外线适度收缩，将资源配置到更高威胁的射手，
    但仍需根据该球员的其他进攻能力做综合判断。

    Returns: (emoji, label, color_hex)
        🔴 三分威胁高（命中率≥33% + 场均出手≥2），建议外线优先关注
        🟡 三分威胁中等，外线需兼顾回位
        🟢 三分威胁较低，外线可适度收缩
    """
    if three_pct >= 0.33 and three_att_per_game >= 2.0:
        return ('🔴', '三分威胁高，建议外线优先关注', COLORS['red'])
    elif three_pct >= 0.25 or (three_att_per_game >= 2.0 and three_pct >= 0.20):
        return ('🟡', '三分威胁中等，外线需兼顾回位', COLORS['yellow'])
    else:
        return ('🟢', '三分威胁较低，外线可适度收缩', COLORS['green'])


def efficiency_color(value: float, low: float, high: float) -> str:
    """Return CSS class for efficiency value coloring.

    Below low → pp-l (red text), above high → pp-h (green), else neutral.
    """
    if value <= low:
        return 'pp-l'
    elif value >= high:
        return 'pp-h'
    return ''

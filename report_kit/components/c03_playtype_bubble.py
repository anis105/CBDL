"""❸ 进攻方式分布 — 气泡图。"""
import math
from ..loader.game_data import GameData, PlayTypeData


def _build_bubble_chart(play_types: list[PlayTypeData], title: str, dot_color: str = '#e63946') -> str:
    if not play_types:
        return ''
    max_pct = max(pt.pct for pt in play_types)
    n = len(play_types)
    spacing = min(92, 1032 // max(n, 1))
    start_x = 106
    vb_w = max(1040, start_x + (n - 1) * spacing + 60)

    svg = (f'<div class="ct" style="margin-bottom:12px"><div class="ct-h">'
           f'<span class="dot" style="background:{dot_color}"></span>{title}</div>'
           f'<div class="ct-b"><svg viewBox="0 0 {vb_w} 180">'
           f'<rect x="4" y="4" width="{vb_w - 8}" height="152" rx="6" fill="#f7f8fa" stroke="#e2e6ea" stroke-width="0.8"/>')

    for i, pt in enumerate(play_types):
        cx = start_x + i * spacing
        r = max(12, min(50, 12 + math.sqrt(pt.pct / max_pct) * 38)) if max_pct > 0 else 12
        if pt.ppp >= 1.0:
            fill, stroke = 'rgba(230,126,34,0.5)', 'rgba(230,126,34,0.9)'
        elif pt.ppp >= 0.80:
            fill, stroke = 'rgba(52,152,219,0.5)', 'rgba(52,152,219,0.9)'
        else:
            fill, stroke = 'rgba(149,165,166,0.5)', 'rgba(149,165,166,0.9)'
        label_y = 70 + r + 14
        svg += f'\n<circle cx="{cx}" cy="70" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        svg += f'\n<text x="{cx}" y="67" text-anchor="middle" fill="#1a1a2e" font-size="13" font-weight="700">{pt.name}</text>'
        svg += f'\n<text x="{cx}" y="80" text-anchor="middle" fill="#1a1a2e" font-size="13" font-weight="800">{pt.ppp:.2f}</text>'
        svg += f'\n<text x="{cx}" y="{label_y:.0f}" text-anchor="middle" fill="#5a6270" font-size="12">{pt.pct*100:.1f}%</text>'

    svg += '\n</svg></div></div>'
    return svg


def render(data: GameData, config=None) -> str:
    cfg = data.config
    primary = cfg.primary_event
    baseline = cfg.baseline_event

    analysis_text = cfg.player_overrides.get('_section3_text', '')
    if not analysis_text:
        analysis_text = f'{cfg.team_name}进攻方式分析待填写。'

    wcq_bubble = _build_bubble_chart(data.playtypes_primary,
                                      f'{primary.label} 按占比排序', cfg.accent_color)
    euro_bubble = ''
    if baseline and data.playtypes_baseline:
        euro_bubble = _build_bubble_chart(data.playtypes_baseline,
                                          f'{baseline.label} 按占比排序', '#457b9d')

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">3</span>进攻方式分布</div>
  <div class="nb">{analysis_text}</div>
  <div class="sec-sub">气泡面积 = 占比 · 颜色 = 每回合得分效率（暖色≥1.0 · 蓝色≥0.8 · 灰色&lt;0.8）</div>
{wcq_bubble}
{euro_bubble}
</div>'''

"""❺ 球员威胁图 — 球场SVG + 圆形头像。"""
from collections import Counter
from ..loader.game_data import GameData, PlayerData
from ..svg.court import court_large, POSITION_COORDS
from ..svg.headshot_clip import headshot_circle
from ..theme import threat_level


def _pos_short(position: str) -> str:
    """位置缩写。"""
    mapping = {'控球后卫': 'PG', '得分后卫': 'SG', '小前锋': 'SF', '大前锋': 'PF', '中锋': 'C',
               'PG': 'PG', 'SG': 'SG', 'SF': 'SF', 'PF': 'PF', 'C': 'C'}
    return mapping.get(position, position[:2] if position else '??')


def _fg_color(pct: float) -> str:
    if pct >= 0.50: return '#2a9d8f'
    if pct >= 0.40: return '#e67e22'
    return '#e63946'


def _build_threat_chart(players: list[PlayerData], title: str,
                        headshots: dict, chart_id: str = 'wcq') -> str:
    svg_parts = [f'<svg viewBox="0 0 660 410">{court_large()}']

    pos_count = Counter(_pos_short(p.position) for p in players)
    used_positions = {}

    for p in players:
        position = _pos_short(p.position)
        base_pos = POSITION_COORDS.get(position, (316, 200))

        # 同位置多人时错开
        total_at_pos = pos_count[position]
        if position in used_positions:
            count = used_positions[position]
            if total_at_pos == 2:
                offsets = [(-40, -15), (40, 15)]
            elif total_at_pos == 3:
                offsets = [(-70, -20), (0, 0), (70, -20)]
            else:
                offsets = [(i * 65, i * 10) for i in range(total_at_pos)]
            idx = count
            dx, dy = offsets[idx] if idx < len(offsets) else (idx * 65, idx * 10)
            base_pos = (base_pos[0] + dx, base_pos[1] + dy)
            used_positions[position] = count + 1
        else:
            if total_at_pos > 1:
                if total_at_pos == 2:
                    offsets = [(-40, -15), (40, 15)]
                elif total_at_pos == 3:
                    offsets = [(-70, -20), (0, 0), (70, -20)]
                else:
                    offsets = [(i * 65, i * 10) for i in range(total_at_pos)]
                dx, dy = offsets[0]
                base_pos = (base_pos[0] + dx, base_pos[1] + dy)
            used_positions[position] = 1

        cx, cy = base_pos
        r = max(18, min(30, p.shots_per_game * 2.5))
        color = _fg_color(p.fg_pct)
        threat = threat_level(p.three_pct, p.three_att)
        threat_color = threat[2]

        # 头像圈
        hs_svg = headshot_circle(p.number, cx, cy, r, headshots,
                                  clip_prefix=f'tc-{chart_id}', stroke_color=color)
        svg_parts.append(hs_svg)

        # 威胁色点
        svg_parts.append(f'<circle cx="{cx+r*0.7:.0f}" cy="{cy-r*0.7:.0f}" r="5" '
                         f'fill="{threat_color}" stroke="white" stroke-width="1.5"/>')

        # 名字标签
        short_name = p.name.split()[-1] if ' ' in p.name else p.name
        svg_parts.append(f'<text x="{cx}" y="{cy+r+14:.0f}" text-anchor="middle" '
                         f'fill="#1a1a2e" font-size="10" font-weight="700">#{p.number} {short_name}</text>')
        svg_parts.append(f'<text x="{cx}" y="{cy+r+26:.0f}" text-anchor="middle" '
                         f'fill="#5a6270" font-size="9">{p.ppg:.1f}分 {p.fg_pct*100:.0f}%命中</text>')

    svg_parts.append('</svg>')
    svg_str = '\n'.join(svg_parts)

    return (f'<div class="ct" style="margin-bottom:12px">'
            f'<div class="ct-h"><span class="dot" style="background:#e63946"></span>{title}</div>'
            f'<div class="ct-b" style="max-width:860px;margin:0 auto">{svg_str}</div></div>')


def render(data: GameData, config=None) -> str:
    cfg = data.config
    primary = cfg.primary_event
    baseline = cfg.baseline_event

    analysis_text = cfg.player_overrides.get('_section5_text', '')
    if not analysis_text:
        analysis_text = f'{cfg.team_name}球员威胁分析待填写。'

    # 主赛事威胁图（取得分前8-9人）
    players_primary = [p for p in data.players_primary if p.mpg >= 8][:9]
    chart_wcq = _build_threat_chart(players_primary,
                                     f'{primary.label}（{len(players_primary)}人）',
                                     data.headshots)

    # 基线赛事威胁图
    chart_baseline = ''
    if baseline and data.players_baseline:
        players_bl = [p for p in data.players_baseline if p.mpg >= 8][:9]
        hs_bl = data.headshots_baseline or data.headshots
        chart_baseline = _build_threat_chart(players_bl,
                                              f'{baseline.label}（主要轮换）',
                                              hs_bl, chart_id='bl')

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">5</span>球员威胁图</div>
  <div class="nb">{analysis_text}</div>
  <div class="sec-sub">环圈颜色=整体命中率 · 右上色点=三分威胁 · 环圈大小=出手量</div>
<div style="text-align:center;font-size:10px;color:#5a6270;margin:-12px 0 16px"><span style="margin:0 8px"><span style="color:#e63946">●</span> 🔴 外线风险高(3P≥33%+2次)</span><span style="margin:0 8px"><span style="color:#e9a820">●</span> 🟡 风险可控需兼顾(3P≥25%)</span><span style="margin:0 8px"><span style="color:#2a9d8f">●</span> 🟢 外线风险较低</span></div>
{chart_wcq}
{chart_baseline}
</div>'''

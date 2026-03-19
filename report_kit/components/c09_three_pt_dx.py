"""❾ 三分火力诊断。"""
from ..loader.game_data import GameData, PlayerData
from ..theme import threat_level


def _pos_short(p):
    m = {'控球后卫': 'PG', '得分后卫': 'SG', '小前锋': 'SF', '大前锋': 'PF', '中锋': 'C',
         'PG': 'PG', 'SG': 'SG', 'SF': 'SF', 'PF': 'PF', 'C': 'C'}
    return m.get(p, p[:2] if p else '??')


def _build_3pt_chart(players: list[PlayerData], headshots: dict) -> str:
    players = sorted(players, key=lambda x: x.three_att, reverse=True)
    players = [p for p in players if p.three_att > 0]

    row_h = 45
    chart_h = 60 + len(players) * row_h + 20

    svg = [f'<svg viewBox="0 0 1040 {chart_h}">']
    svg.append(f'<text x="520.0" y="22" text-anchor="middle" fill="#1a1a2e" font-size="14" font-weight="700">'
               f'三分火力诊断：谁能拉开空间？</text>')
    svg.append(f'<text x="520.0" y="40" text-anchor="middle" fill="#95a0ab" font-size="10">'
               f'条形长度=三分命中率 · 右侧=每36分钟三分出手次数 · 颜色=威胁等级</text>')

    max_pct = max((p.three_pct for p in players), default=0.5) or 0.5
    bar_max_w = 400

    for i, p in enumerate(players):
        y = 55 + i * row_h
        hs_key = f"{int(p.number):02d}" if p.number.isdigit() else p.number
        hs_b64 = headshots.get(hs_key, '')
        threat = threat_level(p.three_pct, p.three_att)
        color = threat[2]

        if hs_b64:
            img_cy = y + 15
            clip_id = f"hs-3pt-{p.number}"
            svg.append(f'<defs><clipPath id="{clip_id}"><circle cx="40" cy="{img_cy}" r="14"/></clipPath></defs>')
            svg.append(f'<image href="data:image/png;base64,{hs_b64}" x="26" y="{img_cy-14}" '
                       f'width="28" height="28" clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMin slice"/>')

        short_name = p.name.split()[-1] if ' ' in p.name else p.name
        svg.append(f'<text x="70" y="{y+12}" fill="#1a1a2e" font-size="12" font-weight="700">'
                   f'#{p.number} {short_name}</text>')
        svg.append(f'<text x="70" y="{y+26}" fill="#95a0ab" font-size="10">{_pos_short(p.position)}</text>')

        bar_x = 200
        svg.append(f'<rect x="{bar_x}" y="{y+4}" width="{bar_max_w}" height="22" rx="3" fill="#eef0f2"/>')

        bar_w = max((p.three_pct / max_pct) * bar_max_w, 2)
        svg.append(f'<rect x="{bar_x}" y="{y+4}" width="{bar_w:.0f}" height="22" rx="3" '
                   f'fill="{color}" opacity="0.75"/>')

        svg.append(f'<text x="{bar_x + bar_w + 8:.0f}" y="{y+20}" fill="{color}" '
                   f'font-size="13" font-weight="800">{p.three_pct*100:.1f}%</text>')

        per36 = p.three_att_per36
        svg.append(f'<text x="700" y="{y+20}" fill="#5a6270" font-size="11" font-weight="600">{per36:.1f}次/36分</text>')
        svg.append(f'<text x="800" y="{y+20}" fill="{color}" font-size="11" font-weight="700">{threat[0]} {threat[1]}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


def render(data: GameData, config=None) -> str:
    cfg = data.config

    analysis_text = cfg.player_overrides.get('_section9_text', '')
    if not analysis_text:
        analysis_text = f'{cfg.team_name}三分火力诊断分析待填写。'

    players = data.core_players if data.core_players else [p for p in data.players_primary if p.mpg >= 10][:8]
    diag_svg = _build_3pt_chart(players, data.headshots)

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">9</span>三分火力诊断</div>
  <div class="nb">{analysis_text}</div>
  <div class="sec-sub">条形长度=三分命中率 · 右侧=每36分钟三分出手 · 颜色=威胁等级</div>
<div class="ct" style="margin-bottom:12px">
  <div class="ct-h"><span class="dot" style="background:#e63946"></span>三分火力诊断</div>
  <div class="ct-b">{diag_svg}</div>
</div>
</div>'''

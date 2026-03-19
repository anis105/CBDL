"""❿ 防守策略与取舍分析 — DFG%可视化。"""
from ..loader.game_data import GameData
from ..loader.csv_loader import safe_float, safe_int
from ..coach_safe import rewrite_all

MIN_DEF_ATTEMPTS = 3


def _pos_short(p):
    m = {'控球后卫': 'PG', '得分后卫': 'SG', '小前锋': 'SF', '大前锋': 'PF', '中锋': 'C',
         'PG': 'PG', 'SG': 'SG', 'SF': 'SF', 'PF': 'PF', 'C': 'C'}
    return m.get(p, p[:2] if p else '??')


def _dfg_color(pct: float) -> str:
    """DFG% color: green=good defender (<35%), yellow=mid, red=poor (>45%)."""
    if pct < 35:
        return '#2d936c'
    elif pct <= 45:
        return '#e9c46a'
    else:
        return '#e63946'


def _pctile_label(pctile: float) -> str:
    """Percentile badge text (coach-safe: neutral descriptors)."""
    if pctile >= 80:
        return '前20%'
    elif pctile >= 60:
        return '中上'
    elif pctile >= 40:
        return '中等'
    elif pctile >= 20:
        return '中下'
    else:
        return '后20%'


def _filter_defense_rows(rows: list[dict], team_name: str, league_name: str) -> list[dict]:
    """Filter defense CSV rows by team and league (same logic as _parse_players)."""
    league_map = {'世预赛': '世界杯资格赛', '世界杯资格赛': '世界杯资格赛',
                  '欧洲杯': '欧洲杯', '非洲杯': '非洲杯'}
    result = []
    for row in rows:
        if row.get('teamName') != team_name:
            continue
        rln = row.get('_leagueName', '') or row.get('leagueEvent', '')
        if league_name and rln and league_name not in rln and rln not in league_name:
            mapped = league_map.get(league_name, league_name)
            if mapped not in rln:
                continue
        result.append(row)
    return result


def _build_defense_chart(rows: list[dict], headshots: dict) -> str:
    """Build SVG bar chart for DFG% data."""
    # Parse and filter
    parsed = []
    for row in rows:
        attempts = safe_int(row.get('防守投篮出手总数', 0))
        if attempts < MIN_DEF_ATTEMPTS:
            continue
        parsed.append({
            'name': row.get('playerEnName', ''),
            'number': row.get('number', '').strip(),
            'position': row.get('position', ''),
            'dfg_pct': safe_float(row.get('防守投篮命中率', 0)) * 100,  # to percentage
            'def_attempts': attempts,
            'dfg_pctile': safe_float(row.get('防守投篮命中率百分位排名', 50)),
            'stl_rate': safe_float(row.get('抢断率', 0)) * 100,
            'stl_pctile': safe_float(row.get('抢断率百分位排名', 50)),
            'blk_rate': safe_float(row.get('盖帽率', 0)) * 100,
            'blk_pctile': safe_float(row.get('盖帽率百分位排名', 50)),
        })

    if not parsed:
        return ''

    # If all values are ≤1, treat as decimals and multiply by 100
    if all(p['dfg_pct'] <= 1.0 for p in parsed):
        for p in parsed:
            p['dfg_pct'] = p['dfg_pct'] * 100
    # If values seem too large (like 4000+), the source was already in percentage
    if any(p['dfg_pct'] > 100 for p in parsed):
        for p in parsed:
            p['dfg_pct'] /= 100
            p['stl_rate'] /= 100
            p['blk_rate'] /= 100

    # Sort by DFG% ascending (best defenders first)
    parsed.sort(key=lambda x: x['dfg_pct'])

    row_h = 45
    chart_h = 60 + len(parsed) * row_h + 20

    svg = [f'<svg viewBox="0 0 1040 {chart_h}">']
    svg.append(f'<text x="520" y="22" text-anchor="middle" fill="#1a1a2e" font-size="14" font-weight="700">'
               f'防守投篮命中率 (DFG%) — 越低越好</text>')
    svg.append(f'<text x="520" y="40" text-anchor="middle" fill="#95a0ab" font-size="10">'
               f'条形长度=DFG% · 右侧=抢断率/盖帽率 · 颜色：绿&lt;35% · 黄35-45% · 红&gt;45%</text>')

    bar_max_w = 350
    max_pct = max((p['dfg_pct'] for p in parsed), default=60) or 60
    # Cap scale at 70% for visual clarity
    scale = min(max_pct * 1.15, 70)

    for i, p in enumerate(parsed):
        y = 55 + i * row_h
        color = _dfg_color(p['dfg_pct'])

        # Headshot
        hs_key = f"{int(p['number']):02d}" if p['number'].isdigit() else p['number']
        hs_b64 = headshots.get(hs_key, '')
        if hs_b64:
            img_cy = y + 15
            clip_id = f"hs-def-{p['number']}"
            svg.append(f'<defs><clipPath id="{clip_id}"><circle cx="40" cy="{img_cy}" r="14"/></clipPath></defs>')
            svg.append(f'<image href="data:image/png;base64,{hs_b64}" x="26" y="{img_cy-14}" '
                       f'width="28" height="28" clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMin slice"/>')

        # Name and position
        short_name = p['name'].split()[-1] if ' ' in p['name'] else p['name']
        svg.append(f'<text x="70" y="{y+12}" fill="#1a1a2e" font-size="12" font-weight="700">'
                   f'#{p["number"]} {short_name}</text>')
        svg.append(f'<text x="70" y="{y+26}" fill="#95a0ab" font-size="10">'
                   f'{_pos_short(p["position"])} · {p["def_attempts"]}次防守</text>')

        # Bar background
        bar_x = 200
        svg.append(f'<rect x="{bar_x}" y="{y+4}" width="{bar_max_w}" height="22" rx="3" fill="#eef0f2"/>')

        # Bar fill
        bar_w = max((p['dfg_pct'] / scale) * bar_max_w, 2)
        svg.append(f'<rect x="{bar_x}" y="{y+4}" width="{bar_w:.0f}" height="22" rx="3" '
                   f'fill="{color}" opacity="0.75"/>')

        # DFG% label
        svg.append(f'<text x="{bar_x + bar_w + 8:.0f}" y="{y+20}" fill="{color}" '
                   f'font-size="13" font-weight="800">{p["dfg_pct"]:.1f}%</text>')

        # Percentile badge
        pctile_label = _pctile_label(p['dfg_pctile'])
        svg.append(f'<text x="640" y="{y+15}" fill="#5a6270" font-size="10">'
                   f'P{p["dfg_pctile"]:.0f} {pctile_label}</text>')

        # Steal rate & block rate
        svg.append(f'<text x="740" y="{y+12}" fill="#5a6270" font-size="10">抢断率 {p["stl_rate"]:.1f}%</text>')
        svg.append(f'<text x="740" y="{y+26}" fill="#95a0ab" font-size="9">P{p["stl_pctile"]:.0f}</text>')
        svg.append(f'<text x="860" y="{y+12}" fill="#5a6270" font-size="10">盖帽率 {p["blk_rate"]:.1f}%</text>')
        svg.append(f'<text x="860" y="{y+26}" fill="#95a0ab" font-size="9">P{p["blk_pctile"]:.0f}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


def render(data: GameData, config=None) -> str:
    cfg = data.config

    analysis_text = cfg.player_overrides.get('_section10_text', '')
    if not analysis_text:
        analysis_text = f'基于{cfg.team_name}的进攻特点和数据分析，防守策略待分析师填写。'

    # Apply coach-safe language rewriting
    analysis_text = rewrite_all(analysis_text)

    # Build DFG% chart from defense_data
    defense_svg = ''
    if data.defense_data:
        league_name = cfg.primary_event.label_short if cfg.primary_event else ''
        filtered = _filter_defense_rows(data.defense_data, cfg.team_name, league_name)
        defense_svg = _build_defense_chart(filtered, data.headshots)

    defense_block = ''
    if defense_svg:
        defense_block = f'''
<div class="ct" style="margin-bottom:12px">
  <div class="ct-h"><span class="dot" style="background:#2d936c"></span>防守投篮命中率 (DFG%)</div>
  <div class="ct-b">{defense_svg}</div>
</div>'''

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">10</span>防守策略与取舍分析</div>
  <div class="nb">{analysis_text}</div>
{defense_block}
</div>'''

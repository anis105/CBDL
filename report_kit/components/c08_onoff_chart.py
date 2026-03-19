"""❽ 在/不在场净效率差值。"""
from ..loader.game_data import GameData
from ..loader.csv_loader import safe_float
from ..svg.headshot_clip import headshot_img_tag


def _build_onoff_chart(onoff_data: list[dict], title: str, headshots: dict,
                       year: int = 2026, league_name: str = '',
                       player_name_map: dict = None) -> str:
    """横向柱状图SVG。"""
    # Build name→number map from primary players for headshot lookup
    name_to_num = player_name_map or {}

    diffs = []
    for row in onoff_data:
        if row.get('onOff') != '差值':
            continue
        # Filter by year
        if str(row.get('season', '')).strip() != str(year):
            continue
        # Filter by league if provided
        rln = row.get('_leagueName', '')
        league_map = {'世预赛': '世界杯资格赛', '世界杯资格赛': '世界杯资格赛', '欧洲杯': '欧洲杯'}
        if league_name:
            mapped = league_map.get(league_name, league_name)
            if mapped not in rln and rln not in mapped and league_name not in rln:
                continue

        name = row.get('playerEnName', '').strip() or row.get('playerName', '')
        num = row.get('number', '').strip()
        # Try to find number from player map
        if not num and name in name_to_num:
            num = name_to_num[name]
        efg_diff = safe_float(row.get('有效投篮命中率', 0))
        diffs.append({'number': num, 'name': name, 'diff': efg_diff})

    diffs.sort(key=lambda x: x['diff'], reverse=True)

    if not diffs:
        return '<div class="nb">在/不在场数据暂无</div>'

    row_h = 30
    chart_h = 15 + len(diffs) * row_h + 20
    center_x = 580
    scale = 800

    svg = [f'<svg viewBox="0 0 1040 {chart_h}">']
    svg.append(f'<line x1="{center_x}" y1="15" x2="{center_x}" y2="{chart_h-20}" '
               f'stroke="#e2e6ea" stroke-width="1" stroke-dasharray="3,3"/>')
    svg.append(f'<text x="{center_x}" y="11" text-anchor="middle" fill="#95a0ab" font-size="9">0</text>')

    for i, d in enumerate(diffs):
        y = 17 + i * row_h
        num = d['number']
        hs_key = f"{int(num):02d}" if num.isdigit() else num
        hs_b64 = headshots.get(hs_key, '')

        svg.append(f'<rect x="180" y="{y}" width="800" height="{row_h-4}" rx="3" '
                   f'fill="#f7f8fa" opacity="0.6"/>')

        if hs_b64:
            img_y = y + (row_h-4)/2
            clip_id = f"hs-onoff-{num}"
            svg.append(f'<defs><clipPath id="{clip_id}"><circle cx="30" cy="{img_y:.0f}" r="10"/></clipPath></defs>')
            svg.append(f'<image href="data:image/png;base64,{hs_b64}" x="20" y="{img_y-10:.0f}" '
                       f'width="20" height="20" clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMin slice"/>')

        short_name = d['name'].split()[-1] if ' ' in d['name'] else d['name']
        svg.append(f'<text x="50" y="{y+row_h/2+4:.0f}" fill="#1a1a2e" font-size="11" font-weight="600">'
                   f'#{num} {short_name}</text>')

        diff_val = d['diff']
        bar_w = min(abs(diff_val) * scale, 350)
        if diff_val >= 0:
            color = '#2a9d8f'
            bar_x = center_x
        else:
            color = '#e63946'
            bar_x = center_x - bar_w

        svg.append(f'<rect x="{bar_x:.0f}" y="{y+4}" width="{bar_w:.0f}" height="{row_h-12}" '
                   f'rx="2" fill="{color}" opacity="0.7"/>')

        label_x = center_x + (bar_w + 8 if diff_val >= 0 else -(bar_w + 8))
        anchor = "start" if diff_val >= 0 else "end"
        svg.append(f'<text x="{label_x:.0f}" y="{y+row_h/2+4:.0f}" text-anchor="{anchor}" '
                   f'fill="{color}" font-size="11" font-weight="700">{diff_val:+.3f}</text>')

    svg.append('</svg>')
    return (f'<div class="ct" style="margin-bottom:12px">\n'
            f'  <div class="ct-h"><span class="dot" style="background:#b0b8c1"></span>{title}</div>\n'
            f'  <div class="ct-b">{"".join(svg)}</div></div>')


def render(data: GameData, config=None) -> str:
    cfg = data.config
    primary = cfg.primary_event

    analysis_text = cfg.player_overrides.get('_section8_text', '')
    if not analysis_text:
        analysis_text = ('在/不在场数据反映球员对球队效率的实际影响。<b>正值越大</b>说明球队在该球员在场时效率显著提升，'
                         '球队对其依赖度越高。正值突出的球员可作为防守端重点关注对象。')

    # Build playerName→number map from primary players for headshot lookup
    name_map = {}
    for p in data.players_primary:
        name_map[p.name] = p.number

    chart = _build_onoff_chart(data.onoff_rows,
                                f'{primary.label}在/不在场净效率差值（eFG%）',
                                data.headshots,
                                year=primary.year,
                                league_name=primary.label_short,
                                player_name_map=name_map)

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">8</span>在/不在场净效率差值</div>
  <div class="nb">{analysis_text}</div>
  <div class="sec-sub">球员在场与不在场的球队eFG%变化 · 向右=球队更依赖该球员</div>
{chart}
</div>'''

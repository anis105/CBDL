"""❻ 全队个人数据一览。"""
from ..loader.game_data import GameData, PlayerData
from ..svg.headshot_clip import headshot_img_tag
from ..theme import threat_level


def _pos_short(position: str) -> str:
    mapping = {'控球后卫': 'PG', '得分后卫': 'SG', '小前锋': 'SF', '大前锋': 'PF', '中锋': 'C',
               'PG': 'PG', 'SG': 'SG', 'SF': 'SF', 'PF': 'PF', 'C': 'C'}
    return mapping.get(position, position[:2] if position else '??')


def _player_row(p: PlayerData, is_starter: bool, headshots: dict, max_ppg: float) -> str:
    hs_img = headshot_img_tag(p.number, headshots)
    threat = threat_level(p.three_pct, p.three_att)
    starter_mark = '★ ' if is_starter else ''

    fg_pct = f"{p.fg_pct*100:.0f}%"
    rim_pct = f"{p.rim_pct:.0f}%"
    mid_pct = f"{p.mid_pct:.0f}%"
    three_pct = f"{p.three_pct*100:.0f}%"

    fg_class = 'pp-h' if p.fg_pct >= 0.45 else ('pp-l' if p.fg_pct < 0.30 else '')
    rim_class = 'pp-h' if p.rim_pct >= 60 else ('pp-l' if p.rim_pct < 40 else '')
    three_class = 'pp-h' if p.three_pct >= 0.33 else ('pp-l' if p.three_pct < 0.15 else '')

    row_class = ' class="hg"' if is_starter or p.ppg >= 9 else ''
    bar_w = p.ppg / max_ppg * 100 if max_ppg > 0 else 0

    short_name = p.name.split()[-1] if ' ' in p.name else p.name

    return (f'<tr{row_class}><td>{hs_img}{starter_mark}#{p.number} {short_name}</td>'
            f'<td>{_pos_short(p.position)}</td>'
            f'<td class="sb"><div class="sb-b sh" style="width:{bar_w:.0f}%"></div>'
            f'<span class="sb-v"><b>{p.ppg:.1f}</b></span></td>'
            f'<td>{p.shots_per_game:.1f}</td>'
            f'<td><span class="pp {fg_class}">{fg_pct}</span></td>'
            f'<td><span class="pp {rim_class}">{rim_pct}</span></td>'
            f'<td>{mid_pct}</td>'
            f'<td><span class="pp {three_class}">{three_pct}</span></td>'
            f'<td>{p.three_att:.1f}</td>'
            f'<td>{p.rpg:.1f}</td><td>{p.apg:.1f}</td><td>{p.spg:.1f}</td>'
            f'<td>{p.topg:.1f}</td><td>{threat[0]}</td></tr>')


def render(data: GameData, config=None) -> str:
    cfg = data.config
    primary = cfg.primary_event
    players = data.players_primary
    if not players:
        return ''

    max_ppg = max(p.ppg for p in players) if players else 14

    rows = '\n'.join(
        _player_row(p, p.number in data.starter_numbers, data.headshots, max_ppg)
        for p in players
    )

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">6</span>{primary.label}全队个人数据一览（场均）</div>
  <div class="sec-sub">按得分排序 · ★ = 曾首发 · 投射风险：🔴外线风险高 🟡风险可控需兼顾 🟢外线风险较低</div>
  <div class="tw"><div class="th">{primary.label} 球员数据（{len(players)}人）</div>
  <table>
    <thead><tr><th>球员</th><th>位置</th><th>得分</th><th>出手</th><th>命中率</th><th>篮下%</th><th>中距离%</th><th>三分%</th><th>三分出手</th><th>篮板</th><th>助攻</th><th>抢断</th><th>失误</th><th>威胁</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table></div>
</div>'''

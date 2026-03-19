"""❹ 进攻方式效率表。"""
from ..loader.game_data import GameData, PlayTypeData


def _build_table(play_types: list[PlayTypeData], title: str) -> str:
    if not play_types:
        return ''
    max_pct = max(pt.pct for pt in play_types) if play_types else 1
    rows_html = ''
    for pt in play_types:
        bar_w = pt.pct / max_pct * 90 if max_pct > 0 else 0
        ppp_cls = 'pp-h' if pt.ppp >= 0.95 else ('pp-l' if pt.ppp < 0.70 else '')
        rows_html += (f'<tr><td>{pt.name}</td>'
                      f'<td class="sb"><div class="sb-b sh" style="width:{bar_w:.0f}%"></div>'
                      f'<span class="sb-v">{pt.pct*100:.1f}%</span></td>'
                      f'<td>{pt.rounds}</td>'
                      f'<td><span class="pp {ppp_cls}">{pt.ppp:.2f}</span></td>'
                      f'<td>{pt.efg*100:.1f}%</td>'
                      f'<td>{pt.tov_pct*100:.1f}%</td>'
                      f'<td>{pt.rim_pct}</td><td>{pt.mid_pct}</td><td>{pt.three_pct}</td></tr>\n')

    return f'''<div class="tw"><div class="th">{title}</div>
  <table>
    <thead><tr><th>打法</th><th>占比</th><th>回合数</th><th>PPP</th><th>eFG%</th><th>失误%</th><th>篮下</th><th>中距离</th><th>三分</th></tr></thead>
    <tbody>
{rows_html}    </tbody>
  </table></div>'''


def render(data: GameData, config=None) -> str:
    cfg = data.config
    primary = cfg.primary_event
    baseline = cfg.baseline_event

    wcq_table = _build_table(data.playtypes_primary, f'{primary.label} 进攻方式效率一览')
    euro_table = ''
    if baseline and data.playtypes_baseline:
        euro_table = _build_table(data.playtypes_baseline, f'{baseline.label} 进攻方式效率一览')

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">4</span>进攻方式效率表</div>
  <div class="sec-sub">迷你柱图 = 占比 · PPP热力色 = 每回合得分效率</div>
  {wcq_table}
  {euro_table}
</div>'''

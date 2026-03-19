"""❼ 球员个人档案卡。"""
from ..loader.game_data import GameData, PlayerData
from ..theme import threat_level


def _pos_short(p):
    m = {'控球后卫': 'PG', '得分后卫': 'SG', '小前锋': 'SF', '大前锋': 'PF', '中锋': 'C',
         'PG': 'PG', 'SG': 'SG', 'SF': 'SF', 'PF': 'PF', 'C': 'C'}
    return m.get(p, p[:2] if p else '??')


def _zone_class(pct):
    if pct >= 50: return 'zh'
    if pct >= 35: return 'zw'
    if pct >= 20: return 'zc'
    return 'zn'


def _bar_class(pct):
    if pct >= 50: return 'h'
    if pct >= 30: return 'w'
    return 'c'


def _build_card(p: PlayerData, is_starter: bool, headshots: dict, shotcharts: dict) -> str:
    hs_key = f"{int(p.number):02d}" if p.number.isdigit() else p.number
    hs_b64 = headshots.get(hs_key, '')
    st_class = ' st' if is_starter else ''

    hs_img = ''
    if hs_b64:
        hs_img = (f'<img src="data:image/png;base64,{hs_b64}" '
                  f'style="width:36px;height:36px;border-radius:50%;object-fit:cover;margin-right:8px">')

    three_pct_val = p.three_pct * 100
    threat = threat_level(p.three_pct, p.three_att)
    threat_style = f'border-color:{threat[2]};color:{threat[2]}'

    max_att = max(p.rim_att, p.mid_att, p.three_att, 1)

    # 投篮图PNG
    shot_charts_html = ''
    sc_keys = [f"{hs_key}_欧洲杯", f"{hs_key}_世界杯资格赛"]
    found = [(k.split('_', 1)[1], shotcharts[k]) for k in sc_keys if k in shotcharts]
    if found:
        shot_charts_html = '<div style="margin-top:8px;border-top:1px solid #e2e6ea;padding-top:8px">'
        shot_charts_html += '<div style="font-size:10px;color:#95a0ab;margin-bottom:4px">中国篮协技战术服务平台 · 投篮点图</div>'
        cols = ' '.join(['1fr'] * len(found))
        shot_charts_html += f'<div style="display:grid;grid-template-columns:{cols};gap:6px">'
        for label, b64 in found:
            shot_charts_html += (f'<div><div style="font-size:9px;color:#95a0ab;text-align:center;margin-bottom:2px">{label}</div>'
                                 f'<img src="data:image/png;base64,{b64}" style="width:100%;border-radius:4px;border:1px solid #e2e6ea"></div>')
        shot_charts_html += '</div></div>'

    return f'''<div class="pc{st_class}">
    <div class="pc-h" style="display:flex;align-items:center">
      {hs_img}<div style="flex:1"><div class="pc-nm">#{p.number} {p.name}</div><div class="pc-mt">{_pos_short(p.position)} · {p.height}cm · {p.age}岁</div></div>
      <div style="text-align:right"><div class="pc-pt">{p.ppg:.1f}</div><div class="pc-ps">分/场</div></div>
    </div>
    <div class="pc-bd">
      <div class="zr">
        <div class="zb {_zone_class(p.rim_pct)}"><div class="zl">篮下</div><div class="zv">{p.rim_pct:.0f}%</div><div class="zd">{p.rim_att:.1f}次</div></div>
        <div class="zb {_zone_class(p.mid_pct)}"><div class="zl">中距离</div><div class="zv">{p.mid_pct:.0f}%</div><div class="zd">{p.mid_att:.1f}次</div></div>
        <div class="zb {_zone_class(three_pct_val)}"><div class="zl">三分</div><div class="zv">{three_pct_val:.0f}%</div><div class="zd">{p.three_att:.1f}次</div></div>
      </div>
      <div class="bars">
        <div class="br"><div class="br-l">篮下</div><div class="br-t"><div class="br-f {_bar_class(p.rim_pct)}" style="width:{p.rim_att/max_att*100:.0f}%"></div></div><div class="br-v {_bar_class(p.rim_pct)}">{p.rim_pct:.0f}%</div><div class="br-s">{p.rim_att:.1f}</div></div>
        <div class="br"><div class="br-l">中距</div><div class="br-t"><div class="br-f {_bar_class(p.mid_pct)}" style="width:{p.mid_att/max_att*100:.0f}%"></div></div><div class="br-v {_bar_class(p.mid_pct)}">{p.mid_pct:.0f}%</div><div class="br-s">{p.mid_att:.1f}</div></div>
        <div class="br"><div class="br-l">三分</div><div class="br-t"><div class="br-f {_bar_class(three_pct_val)}" style="width:{p.three_att/max_att*100:.0f}%"></div></div><div class="br-v {_bar_class(three_pct_val)}">{three_pct_val:.0f}%</div><div class="br-s">{p.three_att:.1f}</div></div>
      </div>
      <div class="ss"><div class="s"><b>{p.fg_pct*100:.0f}%</b> 命中率</div><span class="s" style="{threat_style}">{threat[0]} {threat[1]}</span></div>
      <div class="pn">{p.scouting_note}</div>
      {shot_charts_html}
    </div>
  </div>'''


def render(data: GameData, config=None) -> str:
    cfg = data.config
    primary = cfg.primary_event

    # 使用core_players如果有，否则用主赛事球员取前8
    players = data.core_players if data.core_players else [p for p in data.players_primary if p.mpg >= 10][:8]

    starters = [p for p in players if p.number in data.starter_numbers]
    bench = [p for p in players if p.number not in data.starter_numbers]

    starters_html = '\n'.join(_build_card(p, True, data.headshots, data.shotcharts) for p in starters)
    bench_html = '\n'.join(_build_card(p, False, data.headshots, data.shotcharts) for p in bench)

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">7</span>球员个人档案（每36分钟频次）</div>
  <div class="sec-sub">分区命中率条形图 · 核心数据芯片 · 三分威胁标签 · {primary.label}</div>
  <div class="pg">
{starters_html}
{bench_html}
  </div>
</div>'''

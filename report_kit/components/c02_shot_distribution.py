"""❷ 投篮分布与分区效率 — SVG散点图。"""
from ..loader.game_data import GameData
from ..svg.court import court_small, shot_to_svg

# 每场比赛的标记颜色轮换
_MATCH_COLORS = ['#2a9d8f', '#457b9d', '#e63946', '#e67e22', '#8e44ad']


def _build_shot_scatter(shots: list, title: str, dot_color: str) -> str:
    """生成单场投篮散点SVG卡片。"""
    total = len(shots)
    made = sum(1 for s in shots if s.get('pbpType', '').endswith('M'))
    pct = f"{made/total*100:.0f}%" if total else "0%"

    three_total = sum(1 for s in shots if '3P' in s.get('pbpType', ''))
    three_made = sum(1 for s in shots if s.get('pbpType') == '3PM')
    three_pct = f"{three_made/three_total*100:.0f}%" if three_total else "0%"
    three_freq = f"{three_total/total*100:.0f}%" if total else "0%"

    shot_elements = '\n'.join(shot_to_svg(s) for s in shots)
    summary = f"{made}/{total}投 ({pct}) · 三分{three_made}/{three_total} ({three_pct}) · 三分频率{three_freq}"

    return f'''<div class="ct"><div class="ct-h"><span class="dot" style="background:{dot_color}"></span>{title}</div><div class="ct-b"><svg viewBox="0 0 480 380">{court_small()}
{shot_elements}
<text x="240.0" y="365" text-anchor="middle" fill="#5a6270" font-size="10">{summary}</text>
<circle cx="380" cy="18" r="4" fill="#2a9d8f" opacity="0.75"/><text x="388" y="22" fill="#95a0ab" font-size="9">命中</text><text x="420" y="22" fill="#e63946" font-size="11" font-weight="700">x</text><text x="428" y="22" fill="#95a0ab" font-size="9">不中</text></svg></div></div>'''


def render(data: GameData, config=None) -> str:
    cfg = data.config

    analysis_text = cfg.player_overrides.get('_section2_text', '')
    if not analysis_text:
        analysis_text = f'{cfg.team_name}投篮分布分析待填写。'

    # 生成每场比赛的散点图
    scatter_cards = []
    for i, match in enumerate(data.matches):
        if not match.shots:
            continue
        color = _MATCH_COLORS[i % len(_MATCH_COLORS)]
        title = f'对{match.opponent} 投篮散点'
        scatter_cards.append(_build_shot_scatter(match.shots, title, color))

    # 两列布局
    scatter_html = ''
    for i in range(0, len(scatter_cards), 2):
        pair = scatter_cards[i:i+2]
        if len(pair) == 2:
            scatter_html += f'<div class="courts">{pair[0]}{pair[1]}</div>'
        else:
            scatter_html += f'<div class="courts">{pair[0]}<div></div></div>'

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">2</span>投篮分布与分区效率</div>
  <div class="nb">{analysis_text}</div>
  <div class="sec-sub">绿圆=命中 · 红X=不中 · 数据来源：中国篮协技战术服务平台</div>
{scatter_html}
</div>'''

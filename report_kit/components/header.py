"""报告头部。"""
from ..loader.game_data import GameData


def render_header(data: GameData) -> str:
    cfg = data.config
    primary = cfg.primary_event

    # Match score chips
    score_chips = []
    for m in data.matches:
        color = '#2a9d8f' if m.result == 'win' else '#e63946'
        score_chips.append(f'<span style="font-size:14px;color:{color}">vs{m.opponent} {m.score}</span>')

    baseline = cfg.baseline_event
    baseline_text = f'{baseline.label}' if baseline else ''

    return f'''<div class="hdr">
  <div class="hdr-top">
    <div class="hdr-badge">FIBA 世界杯预选赛 · {cfg.team_name}球探报告</div>
    <div class="hdr-date">{cfg.report_date}<br>{baseline_text + ' + ' if baseline_text else ''}{primary.label}</div>
  </div>
  <div class="score-row">
    <span class="tm" style="color:{cfg.accent_color}">{cfg.flag_emoji} {cfg.team_name}</span>
    {" ".join(score_chips)}
  </div>
  <div class="hdr-line"></div>
</div>'''

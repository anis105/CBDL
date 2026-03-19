"""报告页脚。"""
from ..loader.game_data import GameData


def render_footer(data: GameData) -> str:
    cfg = data.config
    primary = cfg.primary_event
    baseline = cfg.baseline_event
    events_text = f'{baseline.label_short} + {primary.label_short}' if baseline else primary.label_short

    return f'''<div class="ftr">
  {cfg.team_name}{primary.label_short}球探报告 · {cfg.attribution} · {events_text}
</div>'''

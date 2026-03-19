"""❿ 防守策略与取舍分析。"""
from ..loader.game_data import GameData
from ..coach_safe import rewrite_all


def render(data: GameData, config=None) -> str:
    cfg = data.config

    analysis_text = cfg.player_overrides.get('_section10_text', '')
    if not analysis_text:
        analysis_text = f'基于{cfg.team_name}的进攻特点和数据分析，防守策略待分析师填写。'

    # Apply coach-safe language rewriting
    analysis_text = rewrite_all(analysis_text)

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">10</span>防守策略与取舍分析</div>
  <div class="nb">{analysis_text}</div>
</div>'''

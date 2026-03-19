"""❶ 四要素总览。

注意：四要素分析文本是报告中最需要分析师判断的部分。
config.player_overrides 中可以放 section_text 覆盖自动生成的文本。
当前实现：显示框架，分析文本由 config 提供。
"""
from ..loader.game_data import GameData


def render(data: GameData, config=None) -> str:
    cfg = data.config
    # 分析文本从config获取，或留空由分析师填写
    analysis_text = cfg.player_overrides.get('_section1_text', '')
    if not analysis_text:
        analysis_text = f'{cfg.team_name}四要素分析待填写。'

    primary = cfg.primary_event
    baseline = cfg.baseline_event
    sub_text = f'{baseline.label} vs {primary.label}' if baseline else primary.label

    return f'''<div class="sec">
  <div class="sec-t"><span class="n">1</span>四要素总览</div>
  <div class="nb">{analysis_text}</div>
  <div class="sec-sub">{sub_text} · 高亮色 = 效率优势</div>
</div>'''

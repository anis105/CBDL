"""JSON数据加载 — 比赛数据、球队数据、名单。"""
import json


def load_json(path) -> dict:
    """读取JSON文件。"""
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def extract_shots(match_json: dict, team_side: str) -> list[dict]:
    """从比赛JSON提取投篮坐标数据。

    team_side: 'home' → homeShoots, 'away' → awayShoots
    每条记录: {shotX: 0-1, shotY: 0-1, pbpType: '2PM'|'2Pm'|'3PM'|'3Pm', quarter, ...}
    pbpType大写M=命中，小写m=未中
    """
    key = 'homeShoots' if team_side == 'home' else 'awayShoots'
    # v2 format: teamData.gameShotPlot.full.{key}
    try:
        return match_json['teamData']['gameShotPlot']['full'][key]
    except (KeyError, TypeError):
        pass
    # v1 format: top-level {key}
    return match_json.get(key, [])


def extract_quarter_scores(match_json: dict, focus_team: str, opponent_team: str) -> list[tuple]:
    """提取四节比分 → [(focus_q1, opp_q1), (focus_q2, opp_q2), ...]"""
    ff = match_json.get('teamData', {}).get('fourFactors', {})
    quarters = []
    for qk in ['q1', 'q2', 'q3', 'q4']:
        q_data = ff.get(qk, [])
        focus_pts, opp_pts = 0, 0
        for team in q_data:
            if team.get('teamName') == focus_team:
                focus_pts = team.get('points', 0)
            elif team.get('teamName') == opponent_team:
                opp_pts = team.get('points', 0)
        quarters.append((focus_pts, opp_pts))
    return quarters

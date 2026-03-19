"""文件扫描器 — 按命名规则分类data_dir下的CSV/JSON文件。"""
import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class FileManifest:
    """分类后的文件清单。"""
    # 球队级别聚合数据 (event-level)
    four_factors: dict[str, str] = field(default_factory=dict)       # event_label → path
    four_factors_onoff: dict[str, str] = field(default_factory=dict)
    team_playtype: dict[str, str] = field(default_factory=dict)
    team_shots: dict[str, str] = field(default_factory=dict)
    team_offdef: dict[str, str] = field(default_factory=dict)
    player_basic: dict[str, str] = field(default_factory=dict)       # event → path
    player_shooting: dict[str, str] = field(default_factory=dict)
    player_impact: dict[str, str] = field(default_factory=dict)
    player_onoff: dict[str, str] = field(default_factory=dict)
    player_defense: dict[str, str] = field(default_factory=dict)
    playtype_detail: dict[str, str] = field(default_factory=dict)

    # 比赛级别数据
    match_jsons: dict[str, str] = field(default_factory=dict)        # opponent → path
    match_csvs: dict[str, dict] = field(default_factory=dict)        # opponent → {type: path}

    # 资产
    headshot_json: str = ''
    shotchart_json: str = ''

    # 球队比赛统计
    match_base_data: dict[str, str] = field(default_factory=dict)
    match_log_base_data: dict[str, str] = field(default_factory=dict)
    team_shot_onoff: dict[str, str] = field(default_factory=dict)

    # 其他JSON
    roster_json: dict[str, str] = field(default_factory=dict)        # event → path
    team_json: dict[str, str] = field(default_factory=dict)


def scan_data_dir(data_dir: str, team_name: str) -> FileManifest:
    """扫描目录，按命名规则分类文件。"""
    m = FileManifest()
    p = Path(data_dir)

    for f in sorted(p.iterdir()):
        name = f.name

        # Skip hidden files
        if name.startswith('.') or name.startswith('_build'):
            continue

        # Asset JSONs (prefixed with _)
        if name == '_headshots_b64.json':
            m.headshot_json = str(f)
            continue
        if name == '_headshots_euro_b64.json':
            # Store as secondary headshot source
            continue
        if name == '_shotcharts_b64.json':
            m.shotchart_json = str(f)
            continue
        if name.startswith('_'):
            continue

        # Match-level data: two patterns from K8 extension v7.3:
        #   JSON: {A}vs{B}_比赛数据_*.json  (has 比赛数据)
        #   CSV:  {A}vs{B}_四要素_*.csv      (no 比赛数据 prefix)
        #   CSV:  比赛数据_{A}vs{B}_四要素_*.csv  (manually prefixed)
        if 'vs' in name and (name.endswith('.json') or name.endswith('.csv')):
            # Skip team-level CSVs that happen to have 'vs' in team name
            # Match files always have the pattern {TeamA}vs{TeamB}
            parts = name.split('_')
            vs_part = next((part for part in parts if 'vs' in part), '')
            if not vs_part:
                pass  # not a match file
            else:
                teams = vs_part.split('vs')
                opponent = teams[1] if teams[0] == team_name else teams[0] if len(teams) > 1 else ''

                if name.endswith('.json') and '比赛数据' in name:
                    m.match_jsons[opponent] = str(f)
                elif name.endswith('.csv'):
                    if opponent not in m.match_csvs:
                        m.match_csvs[opponent] = {}
                    if '四要素' in name:
                        m.match_csvs[opponent]['four_factors'] = str(f)
                    elif '投篮分布' in name:
                        m.match_csvs[opponent]['shots'] = str(f)
                    elif '热区图' in name:
                        m.match_csvs[opponent]['heatmap'] = str(f)
                    elif '球员打法' in name:
                        m.match_csvs[opponent]['player_playtype'] = str(f)
                    elif '球员名单' in name:
                        m.match_csvs[opponent]['roster'] = str(f)
                continue

        # Team-level aggregate CSVs
        # Match both patterns:
        #   欧洲杯_捷克_捷克_球员数据_基础统计_*.csv (team name in filename)
        #   世界杯资格赛_欧洲杯_欧洲杯_球员数据_基础统计_*.csv (no team name, combined events)
        if name.endswith('.csv'):
            if team_name in name:
                # Pattern A: {赛事}_{球队}_{球队}_{数据类型}_*.csv  → event = 赛事
                # Pattern B: {球队}_{apiKey}_{日期}.csv             → event = 球队 (no event prefix)
                if name.startswith(team_name + '_'):
                    # Pattern B: team name at start, no event prefix
                    # Use apiKey heuristic to extract event_label = team_name
                    event_label = team_name
                    for kw in ['球员数据', 'fourFactors', 'teamPlaytype', 'teamShots',
                                'teamOffDef', 'teamShotOnOff', '在场', '防守数据', '打法类型',
                                'matchBaseData', 'matchLogBaseData', 'playersMatchInfo',
                                'fourFactorsOnOff']:
                        if kw in name:
                            event_label = team_name
                            break
                else:
                    # Pattern A: event prefix before team name
                    event_label = name.split(f'_{team_name}')[0]
                    if not event_label:
                        event_label = name.split('_')[0]
            elif '比赛数据' not in name and 'vs' not in name:
                # Combined event files without team name — use first part as label
                parts = name.split('_')
                event_label = parts[0] if parts else name
                # For combined like "世界杯资格赛_欧洲杯_欧洲杯_..." use full event prefix
                # Heuristic: find the data type keyword position
                for kw in ['球员数据', 'fourFactors', 'teamPlaytype', 'teamShots',
                            'teamOffDef', 'teamShotOnOff', '在场', '防守数据', '打法类型',
                            'matchBaseData', 'matchLogBaseData', 'playersMatchInfo']:
                    if kw in name:
                        idx = name.index(kw)
                        event_label = name[:idx].rstrip('_')
                        break
            else:
                continue  # skip match CSVs already handled above

            # K8 extension v7.3 team-level API keys:
            #   fourFactors, fourFactorsOnOff, teamPlaytype, teamShots, teamOffDef,
            #   playersMatchInfo, matchBaseData, matchLogBaseData, teamShotOnOff
            # Player-level API keys (tab_name):
            #   球员数据_基础统计, 球员数据_投篮分布, 球员数据_综合影响力,
            #   在场_不在场_在场影响, 防守数据_防守总览, 打法类型_打法总览
            if 'fourFactorsOnOff' in name:
                m.four_factors_onoff[event_label] = str(f)
            elif 'fourFactors' in name:
                m.four_factors[event_label] = str(f)
            elif 'teamPlaytype' in name:
                m.team_playtype[event_label] = str(f)
            elif 'teamShotOnOff' in name:
                m.team_shot_onoff[event_label] = str(f)
            elif 'teamShots' in name:
                m.team_shots[event_label] = str(f)
            elif 'teamOffDef' in name:
                m.team_offdef[event_label] = str(f)
            elif 'matchLogBaseData' in name:
                m.match_log_base_data[event_label] = str(f)
            elif 'matchBaseData' in name:
                m.match_base_data[event_label] = str(f)
            elif '球员数据_基础统计' in name or 'playersMatchInfo' in name:
                m.player_basic[event_label] = str(f)
            elif '球员数据_投篮分布' in name:
                m.player_shooting[event_label] = str(f)
            elif '球员数据_综合影响力' in name:
                m.player_impact[event_label] = str(f)
            elif '在场_不在场_在场影响' in name:
                m.player_onoff[event_label] = str(f)
            elif '防守数据_防守总览' in name:
                m.player_defense[event_label] = str(f)
            elif '打法类型_打法总览' in name:
                m.playtype_detail[event_label] = str(f)

        # Team-level aggregate JSON
        # K8 extension: {球队}_球队数据_{date}.json, {球队}_{N}人_{date}.json
        if name.endswith('.json') and team_name in name and 'vs' not in name:
            event_label = name.split(f'_{team_name}')[0]
            if not event_label:
                event_label = team_name
            if '人_' in name:
                # {球队}_{N}人_{date}.json → roster
                m.roster_json[event_label] = str(f)
            elif '球队数据' in name:
                m.team_json[event_label] = str(f)

    return m

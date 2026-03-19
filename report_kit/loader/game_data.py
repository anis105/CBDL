"""数据汇总入口 — config → GameData。"""
import os
from dataclasses import dataclass, field

from ..schema import TeamConfig, MatchConfig
from .scanner import scan_data_dir, FileManifest
from .csv_loader import load_csv, safe_float, safe_int, filter_rows, filter_by_year
from .json_loader import load_json, extract_shots
from .headshot import load_headshots_json, load_shotcharts_json
from ..i18n import PLAYTYPE_CN


# Shared league name mapping — single source of truth
LEAGUE_MAP = {
    '世预赛': '世界杯资格赛', '世界杯资格赛': '世界杯资格赛',
    '欧洲杯': '欧洲杯', '非洲杯': '非洲杯',
    '亚洲杯': '亚洲杯', '美洲杯': '美洲杯', '奥运会': '奥运会',
}


def _league_match(league_name: str, row_league: str) -> bool:
    """Check if config league_name matches CSV row league value."""
    if not league_name or not row_league:
        return True  # no filter
    if league_name in row_league or row_league in league_name:
        return True
    mapped = LEAGUE_MAP.get(league_name, league_name)
    return mapped in row_league


@dataclass
class MatchData:
    """单场比赛数据。"""
    opponent: str
    score: str
    result: str
    shots: list[dict] = field(default_factory=list)
    json_raw: dict = field(default_factory=dict)


@dataclass
class PlayerData:
    """球员数据（从CSV汇总）。"""
    number: str
    name: str
    position: str
    height: str = ''
    age: str = ''
    ppg: float = 0
    fg_pct: float = 0
    rim_pct: float = 0       # 0-100
    mid_pct: float = 0       # 0-100
    three_pct: float = 0     # 0-1
    three_att: float = 0
    rim_att: float = 0
    mid_att: float = 0
    shots_per_game: float = 0
    rpg: float = 0
    apg: float = 0
    spg: float = 0
    topg: float = 0
    mpg: float = 0
    games: int = 0
    is_starter: bool = False
    scouting_note: str = ''

    @property
    def three_att_per36(self) -> float:
        return self.three_att * 36.0 / self.mpg if self.mpg > 0 else 0


@dataclass
class PlayTypeData:
    """进攻方式数据。"""
    name: str           # 中文名
    en_name: str        # 英文原名
    pct: float          # 占比 0-1
    ppp: float          # 每回合得分
    efg: float          # 有效命中率 0-1
    tov_pct: float = 0  # 失误占比 0-1
    ft_pct: float = 0   # 造罚球占比 0-1
    rounds: int = 0     # 回合数
    rim_pct: str = '0%'
    mid_pct: str = '0%'
    three_pct: str = '0%'


@dataclass
class GameData:
    """完整报告数据包。"""
    config: TeamConfig = None

    # 比赛数据
    matches: list[MatchData] = field(default_factory=list)

    # 球员数据（按赛事分组）
    players_primary: list[PlayerData] = field(default_factory=list)    # 主赛事球员
    players_baseline: list[PlayerData] = field(default_factory=list)   # 基线赛事球员

    # 进攻方式数据（按赛事）
    playtypes_primary: list[PlayTypeData] = field(default_factory=list)
    playtypes_baseline: list[PlayTypeData] = field(default_factory=list)

    # On/Off数据
    onoff_rows: list[dict] = field(default_factory=list)

    # 资产
    headshots: dict[str, str] = field(default_factory=dict)
    headshots_baseline: dict[str, str] = field(default_factory=dict)
    shotcharts: dict[str, str] = field(default_factory=dict)

    # 防守数据（原始dict列表，从player_defense CSV加载）
    defense_data: list[dict] = field(default_factory=list)

    # 文件清单
    manifest: FileManifest = None

    # 首发名单
    starter_numbers: set = field(default_factory=set)

    # 核心球员（带scouting_note的重点球员）
    core_players: list[PlayerData] = field(default_factory=list)


def load_game_data(config: TeamConfig) -> GameData:
    """主入口：配置 → GameData。"""
    data = GameData(config=config)

    # 1. 扫描文件
    manifest = scan_data_dir(config.data_dir, config.team_name)
    data.manifest = manifest

    # 2. 加载头像
    if manifest.headshot_json:
        data.headshots = load_headshots_json(manifest.headshot_json)
    elif config.headshot_source:
        hs_path = os.path.join(config.data_dir, config.headshot_source)
        if os.path.exists(hs_path):
            data.headshots = load_headshots_json(hs_path)

    # 加载备用头像（baseline event）
    baseline = config.baseline_event
    if baseline:
        for suffix in [f'_headshots_{baseline.label_short}_b64.json',
                       f'_headshots_euro_b64.json', '_headshots_baseline_b64.json']:
            bl_path = os.path.join(config.data_dir, suffix)
            if os.path.exists(bl_path):
                data.headshots_baseline = load_headshots_json(bl_path)
                break

    # 加载投篮图
    if manifest.shotchart_json:
        data.shotcharts = load_shotcharts_json(manifest.shotchart_json)

    # 3. 加载比赛数据
    for match_cfg in config.matches:
        md = MatchData(
            opponent=match_cfg.opponent,
            score=match_cfg.score,
            result=match_cfg.result,
        )
        json_path = os.path.join(config.data_dir, match_cfg.json_file)
        if os.path.exists(json_path):
            md.json_raw = load_json(json_path)
            md.shots = extract_shots(md.json_raw, match_cfg.team_side)
        data.matches.append(md)

    # 4. 加载球员数据（主赛事）
    primary_event = config.primary_event
    # 尝试找组合赛事的球员数据（如"世界杯资格赛_欧洲杯"）
    basic_path = _find_best_csv(manifest.player_basic, primary_event.label_short)
    if basic_path:
        rows = load_csv(basic_path)
        data.players_primary = _parse_players(rows, config.team_name,
                                               primary_event.label_short, primary_event.year)
        data.starter_numbers = _find_starters(rows, config.team_name,
                                               primary_event.label_short)

    # 基线赛事球员
    baseline_event = config.baseline_event
    if baseline_event:
        bl_path = _find_best_csv(manifest.player_basic, baseline_event.label_short)
        if not bl_path:
            # Try event-specific files
            for key, path in manifest.player_basic.items():
                if baseline_event.label_short in key:
                    bl_path = path
                    break
        if bl_path:
            rows = load_csv(bl_path)
            data.players_baseline = _parse_players(rows, config.team_name,
                                                    baseline_event.label_short, baseline_event.year)

    # 5. 加载进攻方式
    pt_path = _find_best_csv(manifest.team_playtype, primary_event.label_short)
    if pt_path:
        rows = load_csv(pt_path)
        data.playtypes_primary = _parse_playtypes(rows, primary_event.year)

    if baseline_event:
        bl_pt_path = _find_best_csv(manifest.team_playtype, baseline_event.label_short)
        if not bl_pt_path:
            for key, path in manifest.team_playtype.items():
                if baseline_event.label_short in key:
                    bl_pt_path = path
                    break
        if bl_pt_path:
            rows = load_csv(bl_pt_path)
            data.playtypes_baseline = _parse_playtypes(rows, baseline_event.year)

    # 6. 加载On/Off数据
    onoff_path = _find_best_csv(manifest.player_onoff, primary_event.label_short)
    if onoff_path:
        data.onoff_rows = load_csv(onoff_path)

    # 7. 加载防守数据
    def_path = _find_best_csv(manifest.player_defense, primary_event.label_short)
    if def_path:
        data.defense_data = load_csv(def_path)

    # 8. 从config的player_overrides填充scouting_note
    for p in data.players_primary:
        if p.number in config.player_overrides:
            override = config.player_overrides[p.number]
            if isinstance(override, dict):
                p.scouting_note = override.get('scouting_note', '')
            elif isinstance(override, str):
                p.scouting_note = override

    return data


def _find_best_csv(path_dict: dict, label_short: str) -> str:
    """从path_dict中找最匹配的文件路径。"""
    # 优先找包含多赛事合并的（如"世界杯资格赛_欧洲杯"）
    for key, path in path_dict.items():
        if label_short in key and '_' in key:
            return path
    # 再找单赛事的
    for key, path in path_dict.items():
        if label_short in key:
            return path
    # 都没有就返回第一个
    if path_dict:
        return next(iter(path_dict.values()))
    return ''


def _parse_players(rows: list[dict], team_name: str, league_name: str, year: int) -> list[PlayerData]:
    """从基础统计CSV解析球员列表。"""
    players = []
    for row in rows:
        if row.get('teamName') != team_name:
            continue
        rln = row.get('_leagueName', '') or row.get('leagueEvent', '')
        if not _league_match(league_name, rln):
            continue

        num = row.get('number', '').strip()
        if not num:
            continue

        players.append(PlayerData(
            number=num,
            name=row.get('playerEnName', row.get('playerName', '')),
            position=row.get('position', row.get('positionCn', '')),
            height=str(row.get('height', '')),
            age=str(row.get('age', '')),
            ppg=safe_float(row.get('得分', 0)),
            fg_pct=safe_float(row.get('投篮命中率', 0)),
            rim_pct=safe_float(row.get('篮下命中率', 0)) * 100,
            mid_pct=safe_float(row.get('中距离命中率', 0)) * 100,
            three_pct=safe_float(row.get('三分命中率', 0)),
            three_att=safe_float(row.get('三分出手数', 0)),
            rim_att=safe_float(row.get('篮下出手数', 0)),
            mid_att=safe_float(row.get('中距离出手数', 0)),
            shots_per_game=safe_float(row.get('投篮出手数', 0)),
            rpg=safe_float(row.get('篮板(总)', 0)),
            apg=safe_float(row.get('助攻', 0)),
            spg=safe_float(row.get('抢断', 0)),
            topg=safe_float(row.get('失误', 0)),
            mpg=safe_float(row.get('上场时间(分钟)', 0)),
            games=safe_int(row.get('出场次数', 0)),
        ))

    players.sort(key=lambda p: p.ppg, reverse=True)
    return players


def _find_starters(rows: list[dict], team_name: str, league_name: str) -> set:
    """从CSV找首发球员号码。"""
    starters = set()
    for row in rows:
        if row.get('teamName') != team_name:
            continue
        rln = row.get('_leagueName', '') or row.get('leagueEvent', '')
        if not _league_match(league_name, rln):
            continue
        if safe_int(row.get('首发次数', 0)) > 0:
            starters.add(row.get('number', '').strip())
    return starters


def _parse_playtypes(rows: list[dict], year: int) -> list[PlayTypeData]:
    """从teamPlaytype CSV解析进攻方式。"""
    result = []
    for row in rows:
        if str(row.get('year', '')).strip() != str(year):
            continue
        en_name = row.get('打法类型', '')
        cn_name = PLAYTYPE_CN.get(en_name, en_name)
        if cn_name in ('其他', '混乱球'):
            continue

        pct = safe_float(row.get('该打法占比', 0))
        ppp = safe_float(row.get('每回合得分', 0))
        efg = safe_float(row.get('有效投篮命中率', 0))
        tov_pct = safe_float(row.get('失误占比', 0))
        ft_pct = safe_float(row.get('造罚球占比', 0))
        rounds = safe_int(row.get('打法类型回合数', 0))
        rim_att = safe_int(row.get('篮下出手数', 0))
        mid_att = safe_int(row.get('中距离出手数', 0))
        three_att = safe_int(row.get('三分出手数', 0))
        total_att = rim_att + mid_att + three_att

        result.append(PlayTypeData(
            name=cn_name,
            en_name=en_name,
            pct=pct,
            ppp=ppp,
            efg=efg,
            tov_pct=tov_pct,
            ft_pct=ft_pct,
            rounds=rounds,
            rim_pct=f"{rim_att/total_att*100:.0f}%" if total_att else "0%",
            mid_pct=f"{mid_att/total_att*100:.0f}%" if total_att else "0%",
            three_pct=f"{three_att/total_att*100:.0f}%" if total_att else "0%",
        ))

    result.sort(key=lambda x: x.pct, reverse=True)
    return result

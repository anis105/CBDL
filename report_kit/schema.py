"""Team config schema and data classes."""
from dataclasses import dataclass, field
from typing import Optional
import os
import yaml


@dataclass
class EventConfig:
    """A competition event (e.g., 欧洲杯, 世预赛, 非洲杯)."""
    label: str              # "欧洲杯6场"
    label_short: str         # "欧洲杯"
    year: int               # 2025
    league_event_id: int = 0  # K8 platform leagueEventId (0 = unknown)
    is_primary: bool = True   # True = report主体, False = 对比基线


@dataclass
class MatchConfig:
    """A specific game within the event."""
    opponent: str           # "南苏丹"
    score: str              # "89-52"
    result: str             # "win" / "loss"
    json_file: str          # 比赛数据JSON文件名(相对于data_dir)
    team_side: str          # "home" or "away" → 决定用homeShoots还是awayShoots


@dataclass
class TeamConfig:
    """Complete team scouting report configuration."""
    # Identity
    team_name: str          # "捷克"
    team_name_en: str       # "Czech Republic"
    team_id: str            # K8 platform teamId
    flag_emoji: str         # "🇨🇿"
    accent_color: str       # "#457b9d"

    # Data sources
    data_dir: str           # 数据文件目录绝对路径

    # Events (ordered: primary first)
    events: list[EventConfig]

    # Matches
    matches: list[MatchConfig]

    # Report metadata
    report_date: str        # "2026-03-14"

    # Optional fields (must come after required fields)
    headshot_source: str = ''  # 头像JSON文件名(相对于data_dir)，可选
    report_title: str = ""  # 自动生成: "{team_name} 世预赛球探报告"
    attribution: str = "数据来源：中国篮协技战术服务平台 cbastats.com"

    # Section selection
    sections: list[int] = field(default_factory=lambda: list(range(1, 11)))

    # Player overrides (number → scouting note)
    player_overrides: dict = field(default_factory=dict)
    excluded_players: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.events:
            raise ValueError("TeamConfig: events 列表不能为空")
        if not self.report_title:
            primary = next((e for e in self.events if e.is_primary), self.events[0])
            self.report_title = f"{self.team_name} {primary.label_short}球探报告"
        self.data_dir = os.path.expanduser(self.data_dir)

    @property
    def primary_event(self) -> EventConfig:
        return next((e for e in self.events if e.is_primary), self.events[0])

    @property
    def baseline_event(self) -> Optional[EventConfig]:
        return next((e for e in self.events if not e.is_primary), None)

    @property
    def headshot_path(self) -> str:
        return os.path.join(self.data_dir, self.headshot_source)


def load_config(yaml_path: str) -> TeamConfig:
    """Load a TeamConfig from a YAML file."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f)

    events = [EventConfig(**e) for e in raw.pop('events', [])]
    matches = [MatchConfig(**m) for m in raw.pop('matches', [])]

    return TeamConfig(events=events, matches=matches, **raw)

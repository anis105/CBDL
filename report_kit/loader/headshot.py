"""头像加载 — 支持JSON和目录两种源。"""
import json
from pathlib import Path


def load_headshots_json(json_path: str) -> dict[str, str]:
    """从JSON文件加载base64头像。返回 {jersey_number: base64_string}。"""
    if not json_path or not Path(json_path).exists():
        return {}
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)


def load_shotcharts_json(json_path: str) -> dict[str, str]:
    """从JSON文件加载base64投篮图。返回 {key: base64_string}。"""
    if not json_path or not Path(json_path).exists():
        return {}
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)


def fiba_headshot_url(person_id: int, competition_id: int = 208973,
                      w: int = 300, h: int = 300) -> str:
    """生成FIBA Cloudinary头像URL。"""
    return (f"https://assets.fiba.basketball/image/upload/"
            f"w_{w},h_{h},c_fill,g_face/q_auto/f_auto/"
            f".headshot--person_{person_id}--competition_{competition_id}")

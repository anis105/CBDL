"""头像加载 — 支持JSON和PNG目录两种源。"""
import base64
import json
import re
from pathlib import Path


def load_headshots_json(json_path: str) -> dict[str, str]:
    """从JSON文件加载base64头像。返回 {jersey_number: base64_string}。"""
    if not json_path or not Path(json_path).exists():
        return {}
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)


def load_headshots_dir(dir_path: str) -> dict[str, str]:
    """从PNG目录加载头像。文件名格式: {号码}_{名字}.png
    返回 {jersey_number_2digit: base64_string}。"""
    d = Path(dir_path)
    if not d.is_dir():
        return {}
    result = {}
    for f in sorted(d.glob('*.png')):
        m = re.match(r'^(\d+)_', f.name)
        if m:
            num = f"{int(m.group(1)):02d}"
            b64 = base64.b64encode(f.read_bytes()).decode('ascii')
            result[num] = b64
    return result


def load_shotcharts_json(json_path: str) -> dict[str, str]:
    """从JSON文件加载base64投篮图。返回 {key: base64_string}。"""
    if not json_path or not Path(json_path).exists():
        return {}
    with open(json_path, encoding='utf-8') as f:
        return json.load(f)


def load_shotcharts_dir(dir_path: str) -> dict[str, str]:
    """从PNG目录加载投篮图。文件名格式: {号码}_{名字}_投篮图_{赛事}.png
    返回 {num_event: base64_string}，与JSON格式的key一致。"""
    d = Path(dir_path)
    if not d.is_dir():
        return {}
    result = {}
    for f in sorted(d.glob('*.png')):
        m = re.match(r'^(\d+)_.*_投篮图_(.+)\.png$', f.name)
        if m:
            num = f"{int(m.group(1)):02d}"
            event = m.group(2)
            key = f"{num}_{event}"
            b64 = base64.b64encode(f.read_bytes()).decode('ascii')
            result[key] = b64
    return result


def fiba_headshot_url(person_id: int, competition_id: int = 208973,
                      w: int = 300, h: int = 300) -> str:
    """生成FIBA Cloudinary头像URL。"""
    return (f"https://assets.fiba.basketball/image/upload/"
            f"w_{w},h_{h},c_fill,g_face/q_auto/f_auto/"
            f".headshot--person_{person_id}--competition_{competition_id}")

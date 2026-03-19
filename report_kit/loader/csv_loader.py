"""CSV读取 — utf-8-sig编码 + 安全类型转换。"""
import csv


def load_csv(path, encoding='utf-8-sig') -> list[dict]:
    """读取CSV为dict列表。"""
    with open(path, encoding=encoding) as f:
        return list(csv.DictReader(f))


def safe_float(val, default=0.0) -> float:
    """安全转换为float，处理NaN/空值/None。"""
    if val is None:
        return default
    try:
        v = float(val)
        if v != v:  # NaN check
            return default
        return v
    except (ValueError, TypeError):
        return default


def safe_int(val, default=0) -> int:
    return int(safe_float(val, default))


def filter_rows(rows: list[dict], **kwargs) -> list[dict]:
    """按字段值筛选行。
    filter_rows(rows, teamName='捷克', _leagueName='世界杯资格赛')
    """
    result = []
    for row in rows:
        if all(str(row.get(k, '')).strip() == str(v) for k, v in kwargs.items()):
            result.append(row)
    return result


def filter_by_year(rows: list[dict], year: int) -> list[dict]:
    """筛选指定年份的行。"""
    return [r for r in rows if str(r.get('year', '')).strip() == str(year)]

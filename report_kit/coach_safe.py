"""Coach-safe defense language rewriter.

Converts directive/commanding expressions into neutral, data-driven
analysis language suitable for coaching staff communications.

核心原则：
1. 不做绝对判断，只量化代价，让教练决策
2. "放空"必须限定区域——"三分可收缩"≠"可以不防"
3. 绿色球员仍可能具备篮下/中距离/空切威胁，只是三分威胁较低
4. 分析语言参照 Dean Oliver 风格：数据先行、平和克制、因果推理

Rules from: coach-safe-defense-language.txt + 方法论文档 1.4 协防轮转精确性原则
"""

# Fixed substitution rules (ordered: longer matches first to avoid partial replacements)
_RULES = [
    # Multi-word phrases first
    ('不给任何接球三分机会', '建议优先控制其外线接球出手空间'),
    ('不给任何', '尽量限制'),
    ('不可放空', '三分威胁高，建议外线优先关注'),
    ('不完全放空', '外线需兼顾回位'),
    ('可大胆放空', '三分威胁较低，外线可适度收缩'),
    ('谨慎放空', '三分威胁中等，外线需兼顾回位'),
    ('必须坚决阻止', '建议重点限制'),
    ('必须执行', '建议优先考虑'),
    ('必须', '建议'),
    ('坚决', '重点'),
    ('紧贴', '优先关注'),
    ('包夹', '重点协防'),
    ('极其恐怖', '终结效率突出'),
    ('务必', '需要'),
    ('一定要', '建议'),
    # "放空"单独出现时 → "收缩"，但要注意上下文
    # 三分放空 → 外线收缩；笼统放空 → 收缩
    ('三分放空', '外线收缩'),
    ('放空', '收缩'),
]

# Table header replacements
_HEADER_RULES = [
    ('策略', '防守对象'),
    ('代价（对手空位得分预期）', '三分投射风险'),
    ('代价', '三分投射风险'),
    ('收益', '协防价值'),
    ('净收益评估', '参考建议'),
]

# Threat label replacements
_THREAT_LABELS = {
    '三分不可放空': '三分威胁高，建议外线优先关注',
    '三分谨慎放空': '三分威胁中等，外线需兼顾回位',
    '三分可放空': '三分威胁较低，外线可适度收缩',
    '可放空': '三分威胁较低，外线可适度收缩',  # 兜底：补全区域限定
}


def rewrite(text: str) -> str:
    """Apply all coach-safe language substitutions to text."""
    for old, new in _RULES:
        text = text.replace(old, new)
    return text


def rewrite_headers(text: str) -> str:
    """Apply table header substitutions."""
    for old, new in _HEADER_RULES:
        text = text.replace(old, new)
    return text


def rewrite_threat_labels(text: str) -> str:
    """Apply threat level label substitutions."""
    for old, new in _THREAT_LABELS.items():
        text = text.replace(old, new)
    return text


def rewrite_all(text: str) -> str:
    """Apply all rewrite rules (general + headers + threat labels)."""
    text = rewrite_threat_labels(text)
    text = rewrite_headers(text)
    text = rewrite(text)
    return text

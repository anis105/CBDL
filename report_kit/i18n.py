"""Internationalization: play type translations, position mappings."""

# K8 platform English play type → Chinese
PLAYTYPE_CN = {
    'Cut': '空切',
    'Hand-Off': '手递手',
    'Isolation': '单打',
    'Miscellaneous': '其他',
    'Off-Screen': '绕掩护',
    'P&R-Ball-Handler': '挡拆持球',
    'P&R-Roll-Man': '挡拆顺下',
    'Post-Up': '低位',
    'Put-Backs': '补篮',
    'Spot-Up': '定点',
    'Transition': '快攻',
}

# Position English → Chinese short
POS_CN = {
    'PG': '控卫', 'SG': '得分后卫', 'SF': '小前锋',
    'PF': '大前锋', 'C': '中锋',
    'G': '后卫', 'F': '前锋', 'F-C': '前锋/中锋',
    'G-F': '后卫/前锋',
}

# Position Chinese → English short
POS_EN = {v: k for k, v in POS_CN.items()}
POS_EN.update({
    '控球后卫': 'PG', '得分后卫': 'SG', '小前锋': 'SF',
    '大前锋': 'PF', '中锋': 'C', '后卫': 'G', '前锋': 'F',
})

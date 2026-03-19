"""AI 分析师模块 — 从 GameData 自动生成专业分析文本。

分析风格参照：
  - Dean Oliver "Basketball on Paper" — 数据先行、四要素骨架
  - 策略分析与战术决策框架（方法论文档）— 取舍量化、反面思维、精确分档
  - 语气：平和、克制、基于证据，不做绝对判断

核心原则：
  1. 每个观点必须锚定具体数据（"43.5%（7.7次出手）"）
  2. 有基线就对比，没基线就描述现状
  3. "三分可收缩"≠"可以不防"——收缩仅限外线三分区域
  4. 不做判断，只量化代价，让教练决策
  5. 中文语境适配：简洁、信息密度高、适合手机阅读
"""

from .loader.game_data import GameData, PlayerData, PlayTypeData
from .theme import threat_level


def _pname(p: PlayerData) -> str:
    """球员显示名：优先中文名，无则取英文姓。"""
    if p.cn_name:
        return p.cn_name
    return p.name.split()[-1] if ' ' in p.name else p.name


# ── 评价词库 ──────────────────────────────────────────

def _trend_word(delta: float) -> str:
    """根据变化幅度选择评价词。"""
    if delta >= 5:
        return '显著提升'
    elif delta >= 2:
        return '有所提升'
    elif delta >= -2:
        return '基本持平'
    elif delta >= -5:
        return '有所下降'
    else:
        return '显著下降'


def _efficiency_word(pct: float) -> str:
    """根据命中率选择评价词。"""
    if pct >= 50:
        return '效率突出'
    elif pct >= 45:
        return '效率较好'
    elif pct >= 40:
        return '效率中等'
    elif pct >= 35:
        return '效率偏低'
    else:
        return '效率低下'


def _volume_word(att: float) -> str:
    """根据场均出手量选择评价词。"""
    if att >= 5:
        return '出手量大'
    elif att >= 3:
        return '出手量中等'
    else:
        return '出手量较少'


# ── Section 1：四要素总览 ─────────────────────────────

def _analyze_section1(data: GameData) -> str:
    """四要素分析：球队画像 + 四维拆解 + 趋势。"""
    cfg = data.config
    players = data.players_primary
    if not players:
        return f'{cfg.team_name}四要素数据暂不可用。'

    # 基础统计
    n_matches = len(data.matches)
    wins = sum(1 for m in data.matches if m.result == 'win')
    losses = n_matches - wins
    total_ppg = sum(p.ppg for p in players)

    # 球队投篮结构判定
    total_3att = sum(p.three_att for p in players)
    total_rim = sum(p.rim_att for p in players)
    total_mid = sum(p.mid_att for p in players)
    total_att = max(total_3att + total_rim + total_mid, 1)

    pct_3 = total_3att / total_att * 100
    pct_rim = total_rim / total_att * 100

    # 球队类型判定
    team_type = _classify_team_type(pct_3, pct_rim, data.playtypes_primary)

    # 平均三分命中率
    avg_3pct = (sum(p.three_pct * p.three_att for p in players) /
                max(total_3att, 1)) * 100

    parts = []
    record = f'{n_matches}场（{wins}胜{losses}负）' if n_matches > 0 else ''
    parts.append(f'{cfg.team_name}是{team_type}。{cfg.primary_event.label_short}{record}。')

    # 投篮结构
    parts.append(
        f'投篮结构上，三分出手占比{pct_3:.0f}%，篮下占比{pct_rim:.0f}%，中距离占比{100-pct_3-pct_rim:.0f}%。'
        f'三分整体命中率{avg_3pct:.1f}%。'
    )

    # 进攻效率最高/最低的球员
    scorers = sorted([p for p in players if p.mpg >= 10], key=lambda x: x.ppg, reverse=True)
    if scorers:
        top = scorers[0]
        parts.append(
            f'进攻端#{top.number} {_pname(top)}场均{top.ppg:.1f}分领跑全队。'
        )

    return ''.join(parts)


def _classify_team_type(pct_3: float, pct_rim: float,
                         playtypes: list[PlayTypeData]) -> str:
    """根据投篮分布和打法数据判断球队类型。"""
    tags = []

    if pct_3 >= 38:
        tags.append('外线投射')
    elif pct_3 >= 30:
        tags.append('内外均衡')

    if pct_rim >= 35:
        tags.append('内线终结')

    # 检查快攻占比
    for pt in playtypes:
        if pt.en_name in ('Transition', 'transition') and pt.pct >= 0.15:
            tags.append('快攻')
            break

    # 检查挡拆占比
    for pt in playtypes:
        if 'P&R' in pt.en_name and 'Ball' in pt.en_name and pt.pct >= 0.15:
            tags.append('挡拆体系')
            break

    if not tags:
        tags.append('均衡进攻')

    return '以<b>' + '+'.join(tags) + '</b>为特点的球队'


# ── Section 2：投篮分布 ──────────────────────────────

def _analyze_section2(data: GameData) -> str:
    """投篮分布分析：三区效率 + 单场差异。"""
    cfg = data.config
    players = data.players_primary
    if not players:
        return f'{cfg.team_name}投篮分布数据暂不可用。'

    total_3att = sum(p.three_att for p in players)
    total_rim = sum(p.rim_att for p in players)
    total_mid = sum(p.mid_att for p in players)
    total = max(total_3att + total_rim + total_mid, 1)

    # 加权命中率
    avg_rim = sum(p.rim_pct * p.rim_att for p in players) / max(sum(p.rim_att for p in players), 1)
    avg_mid = sum(p.mid_pct * p.mid_att for p in players) / max(sum(p.mid_att for p in players), 1)
    avg_3 = sum(p.three_pct * p.three_att for p in players) / max(total_3att, 1) * 100

    parts = []
    parts.append(
        f'{cfg.team_name}三分出手占比{total_3att/total*100:.0f}%，'
        f'命中率{avg_3:.1f}%。'
        f'篮下命中率{avg_rim:.0f}%，{_efficiency_word(avg_rim)}。'
        f'中距离命中率{avg_mid:.0f}%。'
    )

    # 找篮下效率最高的球员
    rim_stars = sorted([p for p in players if p.rim_att >= 2],
                       key=lambda x: x.rim_pct, reverse=True)
    if rim_stars:
        top = rim_stars[0]
        parts.append(
            f'篮下终结效率最高的是#{top.number} {_pname(top)}'
            f'（{top.rim_pct:.0f}%，场均{top.rim_att:.1f}次出手）。'
        )

    # 识别效率短板
    if avg_mid < 35:
        parts.append(f'中距离命中率偏低（{avg_mid:.0f}%），是进攻效率的薄弱环节。')
    if avg_3 < 30:
        parts.append(f'三分整体命中率偏低（{avg_3:.1f}%），外线效率有提升空间。')

    return ''.join(parts)


# ── Section 3：进攻方式 ──────────────────────────────

def _analyze_section3(data: GameData) -> str:
    """进攻方式分析：核心打法 + 效率排序 + 趋势变化 + 防守优先级。"""
    cfg = data.config
    pts = data.playtypes_primary
    if not pts:
        return f'{cfg.team_name}进攻方式数据暂不可用。'

    # 按占比排序
    by_pct = sorted(pts, key=lambda x: x.pct, reverse=True)
    # 按效率排序
    by_ppp = sorted(pts, key=lambda x: x.ppp, reverse=True)

    top2 = by_pct[:2]
    best_eff = by_ppp[0]
    worst_eff = by_ppp[-1] if len(by_ppp) > 1 else None

    parts = []
    top_names = '和'.join(f'<b>{t.name}（{t.pct*100:.1f}%）</b>' for t in top2)
    parts.append(f'{cfg.team_name}最核心的进攻方式是{top_names}。')

    parts.append(
        f'效率最高的是{best_eff.name}（PPP {best_eff.ppp:.2f}）。'
    )
    if worst_eff and worst_eff.ppp < 0.8:
        parts.append(
            f'{worst_eff.name}效率偏低（PPP {worst_eff.ppp:.2f}），'
            f'是进攻端的低效方式。'
        )

    # 基线对比
    if data.playtypes_baseline:
        base_map = {pt.en_name: pt for pt in data.playtypes_baseline}
        changes = []
        for pt in by_pct[:3]:
            base = base_map.get(pt.en_name)
            if base:
                delta_pct = (pt.pct - base.pct) * 100
                delta_ppp = pt.ppp - base.ppp
                if abs(delta_pct) >= 2 or abs(delta_ppp) >= 0.1:
                    direction = '增加' if delta_pct > 0 else '减少'
                    changes.append(
                        f'{pt.name}占比{direction}{abs(delta_pct):.1f}个百分点'
                        f'（PPP {base.ppp:.2f}→{pt.ppp:.2f}）'
                    )
        if changes:
            baseline_label = cfg.baseline_event.label_short if cfg.baseline_event else '基线赛事'
            parts.append(f'<br><br>对比{baseline_label}，' + '，'.join(changes) + '。')

    # 防守资源配置（想反面 — 6.1）
    if best_eff.ppp >= 0.95:
        parts.append(
            f'<br><br>防守资源配置参考：<b>{best_eff.name}</b>'
            f'效率最高（PPP {best_eff.ppp:.2f}），建议优先限制。'
        )

    return ''.join(parts)


# ── Section 5：球员威胁图 ─────────────────────────────

def _analyze_section5(data: GameData) -> str:
    """球员三分威胁分析：分三档 + 收缩参考。"""
    cfg = data.config
    players = data.players_primary
    if not players:
        return f'{cfg.team_name}球员威胁数据暂不可用。'

    red, yellow, green = [], [], []
    for p in players:
        if p.mpg < 5:
            continue
        level = threat_level(p.three_pct, p.three_att)
        if level[0] == '🔴':
            red.append(p)
        elif level[0] == '🟡':
            yellow.append(p)
        else:
            green.append(p)

    parts = []

    if red:
        names = '、'.join(f'#{p.number} {p.name.split()[-1] if " " in p.name else p.name}'
                          f'（{p.three_pct*100:.1f}%，场均{p.three_att:.1f}次）'
                          for p in red)
        parts.append(f'<b>三分威胁高</b>的球员：{names}。建议外线优先关注其接球与出手机会。')

    if green:
        names = '、'.join(f'#{p.number}' for p in green)
        parts.append(
            f'<br><br><b>三分威胁较低</b>的球员：{names}。'
            f'外线可适度收缩，将防守资源配置到高威胁射手。'
            f'<b>注意</b>：三分威胁低不代表可以不防——'
        )
        # 检查绿色球员是否有篮下/中距离威胁
        rim_threats = [p for p in green if p.rim_pct >= 50 and p.rim_att >= 2]
        if rim_threats:
            rim_names = '、'.join(f'#{p.number}（篮下{p.rim_pct:.0f}%）' for p in rim_threats)
            parts.append(f'{rim_names}仍具备篮下终结威胁，收缩仅限外线三分区域。')
        else:
            parts.append('仍需根据其篮下/中距离能力综合判断。')

    return ''.join(parts)


# ── Section 8：在/不在场 ──────────────────────────────

def _analyze_section8(data: GameData) -> str:
    """在/不在场分析（通用说明 + 数据驱动的依赖度判断）。"""
    return (
        '在/不在场数据反映球员对球队效率的实际影响。'
        '<b>正值越大</b>说明球队在该球员在场时效率显著提升，球队对其依赖度越高。'
        '正值突出的球员可作为防守端重点关注对象，通过限制其发挥降低对手整体效率。'
        '负值球员在场时球队效率反而下降，可视为对手阵容轮换中相对薄弱的环节。'
        '<br><br>'
        '<b>战略参考</b>：球队依赖度最高的球员，'
        '如能通过造犯规迫使其下场，对手整体效率可能显著下降'
        '（参考首发-替补降级分析框架）。'
    )


# ── Section 9：三分火力诊断 ───────────────────────────

def _analyze_section9(data: GameData) -> str:
    """三分火力诊断：射手分档 + 外线收缩参考点 + 预期代价。"""
    cfg = data.config
    players = data.players_primary
    if not players:
        return f'{cfg.team_name}三分火力诊断数据暂不可用。'

    shooters = sorted([p for p in players if p.three_att > 0 and p.mpg >= 8],
                      key=lambda x: x.three_att, reverse=True)

    red, green = [], []
    for p in shooters:
        level = threat_level(p.three_pct, p.three_att)
        if level[0] == '🔴':
            red.append(p)
        elif level[0] == '🟢':
            green.append(p)

    parts = []
    parts.append('三分投射能力直接影响防守端外线资源配置。')

    if red:
        for p in red:
            short = _pname(p)
            per36 = p.three_att_per36
            parts.append(
                f'<b>#{p.number} {short}</b>（{p.three_pct*100:.1f}%，每36分钟{per36:.1f}次出手）'
                f'三分威胁高，建议列为外线优先关注对象。'
            )

    if green:
        green_names = '、'.join(
            f'<b>#{p.number}</b>（{p.three_pct*100:.1f}%）'
            for p in green
        )
        # 预期代价量化（方法论5.2）
        total_cost = sum(p.three_pct * p.three_att * 3 for p in green)
        parts.append(
            f'<br><br>{green_names}三分威胁较低，外线可适度收缩，'
            f'将防守资源更多配置到高威胁射手。'
            f'预计因外线收缩增加的三分预期失分约{total_cost:.1f}分/场，'
            f'风险可控。'
        )

    return ''.join(parts)


# ── Section 10：防守策略 ──────────────────────────────

def _analyze_section10(data: GameData) -> str:
    """防守策略综合分析：取舍量化 + 优先级排序。"""
    cfg = data.config
    players = data.players_primary
    pts = data.playtypes_primary
    if not players:
        return f'基于{cfg.team_name}的进攻特点和数据分析，防守策略待分析师填写。'

    parts = [f'基于{cfg.team_name}的进攻特点和数据分析，以下为防守端资源配置参考：<br><br>']

    priority = 1

    # 1. 快攻防守（方法论1.1 取舍 + 6.1 想反面）
    trans = next((pt for pt in pts if pt.en_name in ('Transition', 'transition')), None)
    if trans and trans.ppp >= 0.95:
        parts.append(
            f'<b>{priority}. 转换防守（建议优先关注）</b>：'
            f'快攻PPP {trans.ppp:.2f}，占比{trans.pct*100:.1f}%，'
            f'是效率最高的进攻方式之一。'
            f'建议优先控制攻守转换节奏，减少推快攻机会。<br><br>'
        )
        priority += 1

    # 2. 红色射手逐个列出
    red_shooters = sorted(
        [p for p in players if p.mpg >= 10
         and threat_level(p.three_pct, p.three_att)[0] == '🔴'],
        key=lambda x: x.three_att, reverse=True
    )
    for p in red_shooters:
        short = _pname(p)
        parts.append(
            f'<b>{priority}. #{p.number} {short}｜外线优先关注对象</b>：'
            f'场均{p.ppg:.1f}分，三分{p.three_pct*100:.1f}%'
            f'（场均{p.three_att:.1f}次出手）。'
            f'建议优先控制其外线接球与出手空间。<br><br>'
        )
        priority += 1

    # 3. 绿色球员 = 外线收缩参考点
    green_players = [
        p for p in players if p.mpg >= 10
        and threat_level(p.three_pct, p.three_att)[0] == '🟢'
    ]
    if green_players:
        names = '、'.join(
            f'#{p.number}（三分{p.three_pct*100:.1f}%）'
            for p in green_players
        )
        parts.append(
            f'<b>{priority}. 外线可收缩参考点</b>：{names}三分威胁较低，'
            f'外线防守可适度收缩，将资源更多配置到高威胁射手。'
        )
        # 篮下威胁提醒（严谨性）
        rim_threats = [p for p in green_players if p.rim_pct >= 50 and p.rim_att >= 2]
        if rim_threats:
            rim_names = '、'.join(
                f'#{p.number}（篮下{p.rim_pct:.0f}%，场均{p.rim_att:.1f}次出手）'
                for p in rim_threats
            )
            parts.append(
                f'<br>注意：{rim_names}篮下终结效率突出，'
                f'收缩仅限外线三分区域，篮下仍需重点关注。'
            )
        parts.append('<br><br>')
        priority += 1

    # 4. 挡拆防守参考
    pnr = next((pt for pt in pts if 'P&R' in pt.en_name and 'Ball' in pt.en_name), None)
    if pnr:
        parts.append(
            f'<b>{priority}. 挡拆防守参考</b>：'
            f'挡拆持球占比{pnr.pct*100:.1f}%，PPP {pnr.ppp:.2f}。'
        )
        if pnr.ppp < 0.85:
            parts.append('效率偏低，大延误或换防策略可作为参考方案。')
        elif pnr.ppp >= 1.0:
            parts.append('效率较高，建议在上线施加更大压力，同时注意底线补位配套。')
        else:
            parts.append('效率中等，可根据场上对位情况灵活选择延误或换防。')

    return ''.join(parts)


# ── 主入口 ────────────────────────────────────────────

_ANALYZERS = {
    '_section1_text': _analyze_section1,
    '_section2_text': _analyze_section2,
    '_section3_text': _analyze_section3,
    '_section5_text': _analyze_section5,
    '_section8_text': _analyze_section8,
    '_section9_text': _analyze_section9,
    '_section10_text': _analyze_section10,
}


def _scout_tag(p: PlayerData) -> str:
    """为单个球员生成一句话球探标签。

    参考NBA官方球探报告风格：定性角色定位 + 关键数据锚点。
    语气平和、专业，避免绝对判断。
    """
    tags = []
    role = ''

    # ── 角色定位 ──
    ppg = p.ppg
    games = p.games if hasattr(p, 'games') else 0
    minutes = p.minutes if hasattr(p, 'minutes') else 0

    # 得分角色
    if ppg >= 15:
        role = '核心得分手'
    elif ppg >= 10:
        role = '重要轮换得分点'
    elif ppg >= 5:
        role = '角色球员'
    else:
        role = '功能型球员'

    # ── 进攻特点 ──
    # 投篮结构
    total_att = p.rim_att + p.mid_att + p.three_att
    if total_att > 0:
        rim_ratio = p.rim_att / total_att
        three_ratio = p.three_att / total_att

        if rim_ratio >= 0.5 and p.rim_pct >= 50:
            tags.append(f'篮下终结突出（{p.rim_pct:.0f}%）')
        elif rim_ratio >= 0.4:
            tags.append('偏内线进攻')

        if three_ratio >= 0.4:
            if p.three_pct >= 0.35:
                tags.append(f'外线投射稳定（三分{p.three_pct*100:.0f}%，{p.three_att:.1f}次）')
            elif p.three_pct >= 0.25:
                tags.append(f'有三分射程但效率一般（{p.three_pct*100:.0f}%，{p.three_att:.1f}次）')
            else:
                tags.append(f'三分出手多但效率偏低（{p.three_pct*100:.0f}%，{p.three_att:.1f}次）')
        elif p.three_att >= 2 and p.three_pct >= 0.35:
            tags.append(f'三分威胁需关注（{p.three_pct*100:.0f}%）')

        if p.mid_att >= 3 and p.mid_pct >= 40:
            tags.append(f'中距离稳定（{p.mid_pct:.0f}%）')

    # 组织能力 (通过助攻判断)
    apg = p.apg if hasattr(p, 'apg') else 0
    if apg >= 4:
        tags.append(f'组织能力突出（{apg:.1f}助攻）')
    elif apg >= 2.5:
        tags.append('兼具一定组织能力')

    # 篮板
    rpg = p.rpg if hasattr(p, 'rpg') else 0
    if rpg >= 8:
        tags.append(f'篮板控制力强（{rpg:.1f}篮板）')
    elif rpg >= 5:
        tags.append(f'篮板贡献稳定（{rpg:.1f}）')

    # ── 三分威胁分级 ──
    tl = threat_level(p.three_pct, p.three_att)
    if tl[0] == '🔴':
        tags.append('外线不可放空')
    elif tl[0] == '🟢' and p.three_att >= 1:
        tags.append('外线可适度收缩')

    # ── 组装 ──
    if not tags:
        return f'{role}，数据样本有限，需进一步观察。'

    return f'{role}，{"，".join(tags)}。'


def generate_all_analysis(data: GameData) -> dict[str, str]:
    """为所有模块生成分析文本。

    Returns: {'_section1_text': '...', '_section3_text': '...', ...}
    同时为每个球员生成球探标签（key: 球衣号码）
    """
    results = {}
    for key, analyzer in _ANALYZERS.items():
        try:
            results[key] = analyzer(data)
        except Exception as e:
            results[key] = f'（分析文本自动生成失败：{e}）'

    # 球员球探标签
    for p in data.players_primary:
        num_key = p.number
        if num_key not in results and num_key not in (data.config.player_overrides or {}):
            try:
                tag = _scout_tag(p)
                results[num_key] = {'scouting_note': tag}
            except Exception:
                pass

    return results

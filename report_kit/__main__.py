"""CLI入口: python -m report_kit configs/czech.yaml"""
import argparse
import sys
from pathlib import Path

from .schema import load_config
from .loader.game_data import load_game_data
from .assembler import assemble
from .components.css import render_css
from .components.header import render_header
from .components.footer import render_footer
from .components import (
    c01_four_factors,
    c02_shot_distribution,
    c03_playtype_bubble,
    c04_playtype_table,
    c05_threat_map,
    c06_player_table,
    c07_player_profiles,
    c08_onoff_chart,
    c09_three_pt_dx,
    c10_defense,
)

SECTION_RENDERERS = {
    1: c01_four_factors.render,
    2: c02_shot_distribution.render,
    3: c03_playtype_bubble.render,
    4: c04_playtype_table.render,
    5: c05_threat_map.render,
    6: c06_player_table.render,
    7: c07_player_profiles.render,
    8: c08_onoff_chart.render,
    9: c09_three_pt_dx.render,
    10: c10_defense.render,
}


def main():
    parser = argparse.ArgumentParser(description='篮球球探报告生成器')
    parser.add_argument('config', nargs='?', help='YAML配置文件路径')
    parser.add_argument('-o', '--output', help='输出HTML路径')
    parser.add_argument('--sections', help='要渲染的模块编号(逗号分隔)', default='')
    parser.add_argument('--png', action='store_true', help='导出手机版PNG长图(390px/3x)')
    parser.add_argument('--pdf', action='store_true', help='导出手机版PDF(105mm x 187mm)')
    parser.add_argument('--png-desktop', action='store_true', help='导出电脑版PNG长图(1280px/2x)')
    parser.add_argument('--pdf-desktop', action='store_true', help='导出电脑版PDF(A4横向)')
    parser.add_argument('--all-formats', action='store_true', help='导出全部格式(手机PNG/PDF + 电脑PNG/PDF)')
    parser.add_argument('--card', type=int, help='单卡片模式：只渲染指定模块为独立HTML卡片')
    parser.add_argument('--init', metavar='DATA_DIR', help='扫描数据目录，自动生成YAML配置草稿')
    args = parser.parse_args()

    # --init 模式：自动生成配置
    if args.init:
        _auto_init(args.init, args.output)
        return

    if not args.config:
        parser.error('请指定YAML配置文件，或使用 --init DATA_DIR 自动生成配置')

    # 加载配置
    config = load_config(args.config)

    # 加载数据
    print(f"📂 加载数据: {config.data_dir}")
    data = load_game_data(config)
    print(f"   球员: {len(data.players_primary)}人")
    print(f"   比赛: {len(data.matches)}场")
    print(f"   头像: {len(data.headshots)}张")
    print(f"   投篮图: {len(data.shotcharts)}张")
    print(f"   进攻方式(主): {len(data.playtypes_primary)}种")

    # AI分析师：自动生成分析文本（不覆盖手写文本）
    from .analyst import generate_all_analysis
    auto_texts = generate_all_analysis(data)
    filled = 0
    for key, text in auto_texts.items():
        if not config.player_overrides.get(key):
            config.player_overrides[key] = text
            filled += 1
    if filled:
        print(f"   AI分析: 自动生成{filled}段分析文本")

    # 单卡片模式
    if args.card:
        _render_card(args, config, data)
        return

    # 确定渲染哪些模块
    if args.sections:
        section_nums = [int(s.strip()) for s in args.sections.split(',')]
    else:
        section_nums = config.sections

    # 渲染各模块
    section_htmls = []
    for sec_num in section_nums:
        renderer = SECTION_RENDERERS.get(sec_num)
        if renderer:
            print(f"   渲染模块 {sec_num}...")
            section_htmls.append(renderer(data))

    # 组装HTML
    css = render_css(config.accent_color)
    header = render_header(data)
    footer = render_footer(data)
    html = assemble(config.report_title, css, header, section_htmls, footer)

    # 写入文件
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(config.data_dir) / f"{config.team_name}_球探报告.html"
    out_path.write_text(html, encoding='utf-8')
    print(f"\n✅ 报告生成: {out_path}")
    print(f"   大小: {len(html):,} bytes")

    # 导出
    do_all = args.all_formats
    if args.png or do_all:
        from .export import to_png
        to_png(str(out_path))
    if args.pdf or do_all:
        from .export import to_pdf
        to_pdf(str(out_path))
    if args.png_desktop or do_all:
        from .export import to_png_desktop
        to_png_desktop(str(out_path))
    if args.pdf_desktop or do_all:
        from .export import to_pdf_desktop
        to_pdf_desktop(str(out_path))


def _render_card(args, config, data):
    """单卡片模式：渲染一个模块为独立的自包含HTML。"""
    sec_num = args.card
    renderer = SECTION_RENDERERS.get(sec_num)
    if not renderer:
        print(f"❌ 模块 {sec_num} 不存在（可用: 1-10）")
        sys.exit(1)

    from .components.css import render_css
    css = render_css(config.accent_color)
    section_html = renderer(data)

    # 包装为独立HTML
    SECTION_NAMES = {
        1: '四要素总览', 2: '投篮分布', 3: '进攻方式气泡图',
        4: '进攻方式效率表', 5: '球员威胁图', 6: '球员数据表',
        7: '球员档案卡', 8: '在场效率差值', 9: '三分火力诊断',
        10: '防守策略',
    }
    title = f"{config.team_name} — {SECTION_NAMES.get(sec_num, f'模块{sec_num}')}"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="rpt" style="max-width:420px;margin:0 auto;padding:16px">
{section_html}
</div>
</body>
</html>"""

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(config.data_dir) / f"{config.team_name}_card_{sec_num}.html"
    out_path.write_text(html, encoding='utf-8')
    print(f"\n🃏 卡片生成: {out_path}")
    print(f"   模块: {sec_num} — {SECTION_NAMES.get(sec_num, '')}")
    print(f"   大小: {len(html):,} bytes")


def _auto_init(data_dir: str, output: str = None):
    """扫描数据目录，自动生成YAML配置草稿。"""
    import re
    data_dir = str(Path(data_dir).resolve())

    # 1. 找出球队名：优先从比赛JSON的_meta提取
    p = Path(data_dir)
    team_candidates = {}
    team_id_map = {}   # name → id
    match_info = []

    for f in sorted(p.iterdir()):
        name = f.name
        if name.startswith('.') or name.startswith('_'):
            continue

        # 从比赛JSON提取球队名和比分（最可靠来源）
        if name.endswith('.json') and 'vs' in name and '比赛数据' in name:
            try:
                from .loader.json_loader import load_json
                j = load_json(str(f))
                meta = j.get('_meta', {})
                home = meta.get('homeTeam', '')
                away = meta.get('awayTeam', '')
                score = meta.get('finalScore', '')
                if home:
                    team_candidates[home] = team_candidates.get(home, 0) + 1
                    if meta.get('homeTeamId'):
                        team_id_map[home] = str(meta['homeTeamId'])
                if away:
                    team_candidates[away] = team_candidates.get(away, 0) + 1
                    if meta.get('awayTeamId'):
                        team_id_map[away] = str(meta['awayTeamId'])
                match_info.append({
                    'home': home or '主队', 'away': away or '客队',
                    'score': score, 'json_file': name,
                })
            except Exception:
                # fallback: 从文件名提取
                parts = name.split('_')
                vs_part = next((x for x in parts if 'vs' in x), '')
                if vs_part:
                    teams = vs_part.split('vs')
                    for t in teams:
                        team_candidates[t] = team_candidates.get(t, 0) + 1
                    match_info.append({
                        'home': teams[0], 'away': teams[1] if len(teams) > 1 else '',
                        'score': '', 'json_file': name,
                    })

        # 从球队级CSV补充（只用不含赛事关键词的第一段）
        if name.endswith('.csv') and 'vs' not in name:
            first_part = name.split('_')[0]
            # 排除赛事名、英文API key
            skip_words = ['fourFactors', 'team', 'match', 'players', 'playtype',
                          '世界杯', '欧洲杯', '非洲杯', '亚洲杯', '奥运', '友谊赛', '资格赛']
            if first_part and not any(kw in first_part for kw in skip_words):
                team_candidates[first_part] = team_candidates.get(first_part, 0) + 1

    if not team_candidates:
        print("❌ 未在目录中找到可识别的球队数据文件")
        sys.exit(1)

    # 最频繁出现的名字就是目标球队
    team_name = max(team_candidates, key=team_candidates.get)
    team_id = team_id_map.get(team_name, 'TODO')

    # 2. 扫描文件分类
    from .loader.scanner import scan_data_dir
    manifest = scan_data_dir(data_dir, team_name)

    # 3. 从playtype CSV猜year
    years = set()
    if manifest.team_playtype:
        from .loader.csv_loader import load_csv
        for pt_path in manifest.team_playtype.values():
            rows = load_csv(pt_path)
            for r in rows:
                y = r.get('year', '')
                if y:
                    years.add(str(y))

    # 4. 检测赛事
    events_found = set()
    for d in [manifest.player_basic, manifest.team_playtype, manifest.four_factors, manifest.player_onoff]:
        events_found.update(d.keys())

    # 5. 生成matches配置
    matches_yaml = []
    for mi in match_info:
        opponent = mi['away'] if mi['home'] == team_name else mi['home']
        side = 'home' if mi['home'] == team_name else 'away'
        score = mi['score'] or 'TODO'
        # 猜result
        if score != 'TODO' and '-' in score:
            parts = score.split('-')
            try:
                h, a = int(parts[0]), int(parts[1])
                if side == 'home':
                    result = 'win' if h > a else 'loss'
                else:
                    result = 'win' if a > h else 'loss'
                # 客队视角反转比分显示
                if side == 'away':
                    score = f"{a}-{h}"
            except ValueError:
                result = 'TODO'
        else:
            result = 'TODO'
        matches_yaml.append(f"""  - opponent: {opponent}
    score: "{score}"
    result: {result}
    json_file: {mi['json_file']}
    team_side: {side}""")

    # 6. 检测headshot
    has_headshots = '_headshots_b64.json' in [f.name for f in p.iterdir()]
    hs_line = 'headshot_source: _headshots_b64.json' if has_headshots else '# headshot_source: _headshots_b64.json  # TODO: 准备头像文件'

    # 7. 生成YAML
    primary_year = max(years) if years else '2026'
    events_list = sorted(events_found)
    primary_event = events_list[0] if events_list else 'TODO'

    events_yaml = ""
    for i, evt in enumerate(events_list[:2]):
        is_primary = 'true' if i == 0 else 'false'
        evt_year = primary_year if i == 0 else (min(years) if len(years) > 1 else primary_year)
        events_yaml += f"""  - label: {evt}
    label_short: {evt}
    year: {evt_year}
    is_primary: {is_primary}
"""

    if not events_yaml:
        events_yaml = """  - label: TODO
    label_short: TODO
    year: 2026
    is_primary: true
"""

    yaml_content = f"""# 自动生成的球探报告配置 — 请检查并补充
team_name: {team_name}
team_name_en: TODO              # 英文队名
team_id: "{team_id}"            # K8平台球队ID
flag_emoji: "TODO"              # 国旗emoji
accent_color: "#457b9d"         # 报告主色调

data_dir: {data_dir}
{hs_line}

events:
{events_yaml}
matches:
{chr(10).join(matches_yaml) if matches_yaml else '  # TODO: 添加比赛数据'}

report_date: "{__import__('datetime').date.today().isoformat()}"
attribution: "数据来源：中国篮协技战术服务平台 cbastats.com"
sections: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ====== 扫描结果 ======
# 球队: {team_name}
# 比赛JSON: {len(manifest.match_jsons)}场
# 球员基础统计: {list(manifest.player_basic.keys())}
# 球队进攻方式: {list(manifest.team_playtype.keys())}
# 球员在场/不在场: {list(manifest.player_onoff.keys())}
# 防守数据: {list(manifest.player_defense.keys())}
# 头像JSON: {'有' if manifest.headshot_json else '无'}
# 投篮图JSON: {'有' if manifest.shotchart_json else '无'}
"""

    if output:
        out_path = Path(output)
    else:
        out_path = Path(data_dir) / f"{team_name}_config.yaml"

    out_path.write_text(yaml_content, encoding='utf-8')
    print(f"✅ 配置草稿生成: {out_path}")
    print(f"   球队: {team_name}")
    print(f"   比赛: {len(match_info)}场")
    print(f"   赛事: {', '.join(events_list) or 'TODO'}")
    print(f"   年份: {', '.join(sorted(years)) or 'TODO'}")
    print()
    print("   📝 请检查YAML中标记为 TODO 的字段")
    print(f"   然后运行: python -m report_kit {out_path}")


if __name__ == '__main__':
    main()

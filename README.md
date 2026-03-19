# 球探报告生成器

输入：K8平台导出的CSV/JSON文件 + 本工具
输出：HTML球探报告（可转PNG/PDF）

## 快速开始

用户会上传两样东西：
1. 本工具的zip包（含report_kit代码）
2. 一个数据文件夹（或多个CSV/JSON文件）

### 第1步：环境准备

```bash
pip install pyyaml
# 如需导出PNG/PDF：
pip install playwright && playwright install chromium
```

### 第2步：找到数据文件

用户上传的数据文件可能在：
- 上传目录下的某个文件夹
- 散落的多个CSV/JSON文件

先确认数据位置：
```bash
find /上传目录 -name "*.csv" -o -name "*.json" | head -20
```

如果文件散落，建议先归拢到一个文件夹：
```bash
mkdir -p /tmp/data && cp /上传目录/*.csv /上传目录/*.json /tmp/data/
```

### 第3步：自动生成配置

```bash
cd /解压后的report_kit所在目录
python -m report_kit --init /数据文件夹路径 --team 球队中文名
```

这会扫描数据文件夹，自动生成 `configs/球队名.yaml`。

**重要**：`--team` 后的名字必须和CSV文件里的 `teamName` 列完全一致（如"捷克"、"南苏丹"）。

### 第4步：生成报告

```bash
python -m report_kit configs/球队名.yaml
```

输出 HTML 文件。用浏览器打开即可查看。

### 第5步（可选）：导出图片

```bash
python -m report_kit configs/球队名.yaml --png          # 手机版PNG
python -m report_kit configs/球队名.yaml --png-desktop   # 电脑版PNG
python -m report_kit configs/球队名.yaml --all-formats   # 全格式
```

## 单独生成某个模块（卡片）

```bash
python -m report_kit configs/球队名.yaml --card 5        # 只生成模块5
python -m report_kit configs/球队名.yaml --sections 1,5  # 生成模块1和5
```

10个模块：1四要素 2投篮分布 3进攻方式气泡 4进攻效率表 5威胁图 6球员表 7球员卡 8轮换影响 9三分诊断 10防守策略

## 常见问题

**Q: 生成报告显示"0人"**
A: `--team` 名字和CSV里不一致，或者 `events.label_short` 和CSV里的赛事名不匹配。用这个命令检查CSV里的实际值：
```bash
head -2 数据文件.csv
```

**Q: 配置文件里的 team_side 怎么填？**
A: 看比赛JSON文件名。"捷克vs南苏丹"中捷克在前=home，南苏丹=away。

**Q: 没有头像/投篮图怎么办？**
A: 正常生成，只是对应位置空白。头像和投篮图是可选的。

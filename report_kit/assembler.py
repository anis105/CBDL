"""HTML组装器 — sections + css + header + footer → 完整HTML。"""


def assemble(title: str, css: str, header: str,
             sections: list[str], footer: str) -> str:
    """组装完整HTML文档。"""
    sections_html = '\n\n'.join(sections)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>

{header}

{sections_html}

{footer}

</body>
</html>'''

"""SVG圆形裁切头像元素。"""


def headshot_circle(number: str, cx: float, cy: float, r: float,
                    headshots: dict, clip_prefix: str = 'hs',
                    stroke_color: str = '#2a9d8f') -> str:
    """生成SVG圆形头像 + clipPath。

    返回: SVG元素字符串 (circle背景 + clipPath定义 + image)
    """
    hs_key = f"{int(number):02d}" if number.isdigit() else number
    hs_b64 = headshots.get(hs_key, '')

    clip_id = f"{clip_prefix}-{number}"
    base = f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" fill="white" stroke="{stroke_color}" stroke-width="3" opacity="0.95"/>'

    if hs_b64:
        return (f'{base}\n'
                f'<defs><clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="{r-2:.0f}"/></clipPath></defs>\n'
                f'<image href="data:image/png;base64,{hs_b64}" '
                f'x="{cx-r+2:.0f}" y="{cy-r+2:.0f}" width="{(r-2)*2:.0f}" height="{(r-2)*2:.0f}" '
                f'clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMin slice"/>')
    return base


def headshot_img_tag(number: str, headshots: dict, size: int = 22) -> str:
    """生成HTML img标签（表格内联用）。"""
    hs_key = f"{int(number):02d}" if number.isdigit() else number
    hs_b64 = headshots.get(hs_key, '')
    if not hs_b64:
        return ''
    return (f'<img src="data:image/png;base64,{hs_b64}" '
            f'style="width:{size}px;height:{size}px;border-radius:50%;'
            f'object-fit:cover;margin-right:6px;vertical-align:middle">')

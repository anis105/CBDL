"""HTML → PNG/PDF 导出 (Playwright)。

支持两种尺寸：
  - 手机版: 390px viewport, 105mm×187mm PDF
  - 电脑版: 1280px viewport, A4 landscape PDF
"""
from pathlib import Path


# 手机优化CSS
MOBILE_CSS = """
body { max-width: 100% !important; padding: 0 !important; margin: 0 !important; background: #fff !important; }
.report { max-width: 100% !important; padding: 0 !important; }
.chart-svg, svg { width: 100% !important; height: auto !important; max-width: 100% !important; }
.module { padding: 12px 16px !important; margin-bottom: 2px !important; }
.module-half { width: 100% !important; display: block !important; padding: 10px 16px !important; }
.module-row { display: block !important; }
.module-row .module-half { width: 100% !important; float: none !important; display: block !important; }
table { font-size: 10px !important; width: 100% !important; }
td { padding: 5px 4px !important; }
div[style*="grid-template-columns:repeat(3"] { grid-template-columns: 1fr !important; gap: 6px !important; }
"""


# ── 手机版 ──────────────────────────────────────────

def to_png(html_path: str, png_path: str = None,
           viewport_width: int = 390, scale: int = 3):
    """HTML → 手机版高清长图PNG (390px / 3x)。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("导出PNG需要playwright: pip install playwright && playwright install chromium")

    html_path = Path(html_path)
    if png_path is None:
        png_path = html_path.with_name(html_path.stem + '_手机长图.png')
    png_path = Path(png_path)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": viewport_width, "height": 800},
            device_scale_factor=scale,
        )
        page.goto(html_path.as_uri())
        page.add_style_tag(content=MOBILE_CSS)
        page.wait_for_timeout(800)
        page.screenshot(path=str(png_path), full_page=True, type="png")

        dims = page.evaluate("() => ({ w: document.body.scrollWidth, h: document.body.scrollHeight })")
        browser.close()

    phys_w = dims['w'] * scale
    phys_h = dims['h'] * scale
    print(f"  手机长图: {png_path}")
    print(f"  逻辑: {dims['w']}x{dims['h']}px  物理: {phys_w}x{phys_h}px ({scale}x)")
    print(f"  大小: {png_path.stat().st_size / 1024 / 1024:.1f} MB")


def to_pdf(html_path: str, pdf_path: str = None,
           page_width: str = "105mm", page_height: str = "187mm"):
    """HTML → 手机版PDF (105mm x 187mm)。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("导出PDF需要playwright: pip install playwright && playwright install chromium")

    html_path = Path(html_path)
    if pdf_path is None:
        pdf_path = html_path.with_name(html_path.stem + '_手机版.pdf')
    pdf_path = Path(pdf_path)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 420, "height": 800})
        page.goto(html_path.as_uri())
        page.add_style_tag(content=MOBILE_CSS)
        page.wait_for_timeout(500)
        page.pdf(
            path=str(pdf_path),
            width=page_width,
            height=page_height,
            print_background=True,
            margin={"top": "4mm", "bottom": "4mm", "left": "3mm", "right": "3mm"},
        )
        browser.close()

    print(f"  手机PDF: {pdf_path}")
    print(f"  页面: {page_width} x {page_height}")


# ── 电脑版 ──────────────────────────────────────────

def to_png_desktop(html_path: str, png_path: str = None,
                   viewport_width: int = 1280, scale: int = 2):
    """HTML → 电脑版高清长图PNG (1280px / 2x)。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("导出PNG需要playwright: pip install playwright && playwright install chromium")

    html_path = Path(html_path)
    if png_path is None:
        png_path = html_path.with_name(html_path.stem + '_电脑版.png')
    png_path = Path(png_path)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": viewport_width, "height": 900},
            device_scale_factor=scale,
        )
        page.goto(html_path.as_uri())
        page.wait_for_timeout(800)
        page.screenshot(path=str(png_path), full_page=True, type="png")

        dims = page.evaluate("() => ({ w: document.body.scrollWidth, h: document.body.scrollHeight })")
        browser.close()

    phys_w = dims['w'] * scale
    phys_h = dims['h'] * scale
    print(f"  电脑长图: {png_path}")
    print(f"  逻辑: {dims['w']}x{dims['h']}px  物理: {phys_w}x{phys_h}px ({scale}x)")
    print(f"  大小: {png_path.stat().st_size / 1024 / 1024:.1f} MB")


def to_pdf_desktop(html_path: str, pdf_path: str = None):
    """HTML → 电脑版PDF (A4横向)。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("导出PDF需要playwright: pip install playwright && playwright install chromium")

    html_path = Path(html_path)
    if pdf_path is None:
        pdf_path = html_path.with_name(html_path.stem + '_电脑版.pdf')
    pdf_path = Path(pdf_path)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(html_path.as_uri())
        page.wait_for_timeout(500)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            landscape=True,
            print_background=True,
            margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"},
        )
        browser.close()

    print(f"  电脑PDF: {pdf_path}")
    print(f"  页面: A4 横向")

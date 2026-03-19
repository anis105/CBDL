"""共享CSS — 从两份报告提取的100%通用样式。"""


def render_css(accent_color: str = '#e63946') -> str:
    return f'''*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  background:#ffffff;color:#1a1a2e;line-height:1.5;-webkit-font-smoothing:antialiased;
  max-width:1120px;margin:0 auto;padding:0 0 40px}}
.hdr{{background:#f7f8fa;padding:28px 32px 22px;border-bottom:1px solid #e2e6ea}}
.hdr-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px}}
.hdr-badge{{font-size:12px;letter-spacing:1.5px;color:#95a0ab}}
.hdr-date{{font-size:13px;color:#5a6270;text-align:right}}
.score-row{{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap}}
.tm{{font-size:24px;font-weight:700;letter-spacing:-0.5px}}
.qtr{{display:flex;gap:12px;margin-top:10px;font-size:13px;color:#95a0ab}}
.qtr span{{color:#5a6270;font-weight:600}}
.hdr-line{{height:2px;background:linear-gradient(90deg,{accent_color} 50%,#95a0ab 50%);margin-top:14px}}
.sec{{padding:0 32px}}
.sec-t{{font-size:15px;font-weight:700;margin:32px 0 6px;padding:8px 0;border-bottom:1px solid #e2e6ea;
  color:#1a1a2e;display:flex;align-items:center;gap:8px}}
.sec-t .n{{background:{accent_color};color:#fff;width:18px;height:18px;border-radius:50%;
  display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}}
.sec-sub{{font-size:13px;color:#95a0ab;margin-bottom:16px}}
.ff{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:24px}}
.ff-b{{border:1px solid #e2e6ea;padding:12px 10px;text-align:center;background:#f7f8fa;border-radius:4px}}
.ff-b .l{{font-size:12px;color:#95a0ab;margin-bottom:5px;font-weight:500}}
.ff-b .vs{{display:flex;justify-content:center;align-items:baseline;gap:6px}}
.ff-b .v{{font-size:22px;font-weight:800}}
.ff-b .v.r{{color:#e63946}}.ff-b .v.g{{color:#2a9d8f}}.ff-b .v.b{{color:#2a9d8f}}.ff-b .v.c{{color:#457b9d}}
.ff-b .d{{font-size:11px;color:#95a0ab}}.ff-b .nt{{font-size:11px;color:#95a0ab;margin-top:4px}}
.courts{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px}}
.ct{{background:#f7f8fa;border:1px solid #e2e6ea;overflow:hidden;border-radius:6px}}
.ct-h{{padding:8px 12px;font-size:13px;font-weight:700;border-bottom:1px solid #e2e6ea;
  display:flex;align-items:center;gap:6px;color:#1a1a2e}}
.ct-h .dot{{width:6px;height:6px;border-radius:50%}}
.ct-b{{padding:10px}}.ct-b svg{{width:100%;height:auto}}
.pg{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:24px}}
.pc{{background:#f7f8fa;border:1px solid #e2e6ea;overflow:hidden;border-radius:4px}}
.pc.st{{border-left:3px solid {accent_color}}}
.pc-h{{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid #e2e6ea}}
.pc-nm{{font-size:15px;font-weight:700;color:#1a1a2e}}
.pc-mt{{font-size:12px;color:#95a0ab;margin-top:1px}}
.pc-pt{{font-size:28px;font-weight:800;color:#1a1a2e}}
.pc-ps{{font-size:10px;color:#95a0ab;letter-spacing:1px}}
.pc-bd{{padding:10px 14px}}
.zr{{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;margin-bottom:8px}}
.zb{{text-align:center;padding:5px 3px;border:1px solid #e2e6ea;border-radius:3px}}
.zl{{font-size:9px;color:#95a0ab;letter-spacing:0.5px;margin-bottom:2px}}
.zv{{font-size:16px;font-weight:800;line-height:1}}
.zd{{font-size:10px;color:#95a0ab;margin-top:2px}}
.zh{{background:rgba(230,57,70,0.08);border-color:rgba(230,57,70,0.2)}}.zh .zv{{color:#e63946}}
.zw{{background:rgba(233,168,32,0.08);border-color:rgba(233,168,32,0.2)}}.zw .zv{{color:#c08820}}
.zc{{background:rgba(42,157,143,0.06);border-color:rgba(42,157,143,0.15)}}.zc .zv{{color:#2a9d8f}}
.zn{{background:#f7f8fa;border-color:#e2e6ea}}.zn .zv{{color:#95a0ab}}
.bars{{margin-bottom:6px}}
.br{{display:flex;align-items:center;gap:6px;padding:4px 0}}
.br+.br{{border-top:1px solid #e2e6ea}}
.br-l{{font-size:10px;color:#95a0ab;width:32px;flex-shrink:0;letter-spacing:0.5px}}
.br-t{{flex:1;height:10px;background:#eef0f2;border-radius:2px;overflow:hidden}}
.br-f{{height:100%;border-radius:2px}}
.br-f.h{{background:linear-gradient(90deg,#c04545,#e06060)}}
.br-f.w{{background:linear-gradient(90deg,#c09030,#d0a840)}}
.br-f.c{{background:linear-gradient(90deg,#3a8a7d,#50a898)}}
.br-v{{font-size:13px;font-weight:700;width:46px;text-align:right;flex-shrink:0}}
.br-v.h{{color:#e63946}}.br-v.w{{color:#c09030}}.br-v.c{{color:#2a9d8f}}.br-v.n{{color:#95a0ab}}
.br-s{{font-size:10px;color:#95a0ab;width:24px;text-align:center;flex-shrink:0}}
.ss{{display:flex;gap:3px;flex-wrap:wrap;margin-bottom:6px}}
.s{{font-size:11px;padding:2px 5px;background:#eef0f2;border:1px solid #e2e6ea;color:#5a6270;border-radius:2px}}
.s b{{font-weight:700;color:#1a1a2e}}
.pn{{font-size:12px;color:#5a6270;line-height:1.6;padding:6px 8px;background:#f0f2f4;border-left:2px solid #e2e6ea;border-radius:2px}}
.sb{{position:relative;overflow:hidden}}
.sb-b{{position:absolute;left:0;top:0;bottom:0;border-radius:2px;pointer-events:none}}
.sb-b.sh{{background:rgba(230,57,70,0.12)}}
.sb-b.sw{{background:rgba(233,168,32,0.10)}}
.sb-b.sc{{background:rgba(42,157,143,0.08)}}
.sb-v{{position:relative;z-index:1}}
.hg{{background:rgba(42,157,143,0.10)!important}}
.hh{{background:rgba(230,57,70,0.08)!important}}
.hw{{background:rgba(233,168,32,0.08)!important}}
.hc{{background:rgba(69,123,157,0.08)!important}}
.hr{{background:rgba(230,57,70,0.12)!important}}
.hg{{color:#2a9d8f}}.hr td,.hr{{color:#e06060}}
.tw{{background:#f7f8fa;border:1px solid #e2e6ea;margin-bottom:18px;overflow-x:auto;border-radius:4px}}
.th{{padding:10px 14px;font-size:13px;font-weight:700;border-bottom:1px solid #e2e6ea;color:#1a1a2e}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
thead th{{padding:7px 8px;text-align:center;font-weight:600;font-size:10px;letter-spacing:0.5px;color:#95a0ab;border-bottom:1px solid #e2e6ea;background:#f0f2f4;white-space:nowrap}}
thead th:first-child{{text-align:left}}
td{{padding:6px 8px;text-align:center;border-bottom:1px solid #f0f2f4;color:#5a6270}}
td:first-child{{text-align:left;font-weight:600;color:#1a1a2e;white-space:nowrap}}
tr:hover{{background:#f5f6f8}}
.pp{{font-weight:800;font-size:13px}}.pp-h{{color:#2a9d8f}}.pp-l{{color:#e63946}}
.du{{color:#2a9d8f;font-weight:600}}.dd{{color:#e63946;font-weight:600}}.dn{{color:#95a0ab}}
.nb{{border:1px solid #e2e6ea;border-left:3px solid {accent_color};padding:14px 18px;
  margin-bottom:16px;background:#f7f8fa;font-size:13px;line-height:1.8;color:#5a6270;border-radius:4px}}
.nb b{{font-weight:700;color:#1a1a2e}}.nb.grn{{border-left-color:#2a9d8f}}
.ftr{{text-align:center;padding:24px 32px;font-size:11px;color:#95a0ab;
  border-top:1px solid #e2e6ea;margin-top:20px}}
@media(max-width:800px){{.pg,.courts,.ff{{grid-template-columns:1fr}}.sec{{padding:0 16px}}}}
@media print{{body{{max-width:none;background:#fff}}.pc,.tw,.nb{{break-inside:avoid}}.hdr{{background:#f7f8fa}}}}
.pn{{font-size:17px !important;line-height:1.75 !important}}
.pc-nm{{font-size:19px !important}}.pc-mt{{font-size:15px !important}}
.pc-pt{{font-size:32px !important}}.pc-ps{{font-size:13px !important}}
.s{{font-size:14px !important;padding:3px 6px !important}}
.br-l{{font-size:14px !important;width:38px !important}}.br-v{{font-size:16px !important}}.br-s{{font-size:13px !important}}
.zl{{font-size:12px !important}}.zv{{font-size:19px !important}}.zd{{font-size:13px !important}}
.sec-t{{font-size:20px !important}}.sec-sub{{font-size:16px !important}}
.nb{{font-size:16px !important;line-height:1.85 !important}}
table{{font-size:15px !important}}thead th{{font-size:13px !important}}.th{{font-size:16px !important}}
.hdr-badge{{font-size:15px !important}}.hdr-date{{font-size:16px !important}}.ftr{{font-size:14px !important}}
.ff-b .l{{font-size:14px !important}}.ff-b .v{{font-size:26px !important}}
.ff-b .d{{font-size:13px !important}}.ff-b .nt{{font-size:13px !important}}
.ct-h{{font-size:16px !important}}.pp{{font-size:16px !important}}.qtr{{font-size:15px !important}}
.tm{{font-size:26px !important}}
.role-chip{{font-size:13px;padding:3px 6px;border-radius:2px;color:#457b9d;border:1px solid #457b9d;white-space:nowrap}}'''

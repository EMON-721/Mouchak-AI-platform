"""Bengali shaping through MuPDF's HTML story engine, with embedded OFL font."""

from html import escape
import io, json
from .store import ROOT


def report(data):
    import fitz

    font = ROOT / "public/fonts"

    def value(v):
        if isinstance(v, dict):
            return (
                "<dl>"
                + "".join(
                    "<dt>"
                    + escape(str(k).replace("_", " "))
                    + "</dt><dd>"
                    + value(x)
                    + "</dd>"
                    for k, x in v.items()
                )
                + "</dl>"
            )
        if isinstance(v, list):
            return "<ul>" + "".join("<li>" + value(x) + "</li>" for x in v) + "</ul>"
        return escape(str(v)).replace("\n", "<br>")

    html = (
        "<html><head><style>@font-face {font-family: Bengali;src:url(NotoSansBengali.ttf)} body{font-family:Bengali,sans-serif;font-size:11pt;line-height:1.7;color:#142c32}h1{font-size:23pt;color:#116f6e}dt{font-size:9pt;color:#53666b;margin-top:10pt}dd{margin-left:0} .note{background:#f6f4ed;padding:10pt}li{margin-bottom:7pt}</style></head><body><h1>মৌচাক এআই · Mouchak AI</h1><h2>"
        + escape(data["module"])
        + "</h2><p>"
        + escape(data["created_at"])
        + '</p><p class="note">ব্যক্তিগত সহায়ক রিপোর্ট। পূর্ণ AI মূল্যায়ন সম্পন্ন নয়।<br>Private support report. Full AI production validation is pending.</p>'
        + value(data["output"]["facts"])
        + "<h2>সীমাবদ্ধতা / Limitations</h2>"
        + value(data["output"]["uncertainties"])
        + "<h2>উৎস / Sources</h2>"
        + value(data["output"]["references"])
        + "</body></html>"
    )
    out = io.BytesIO()
    writer = fitz.DocumentWriter(out)
    story = fitz.Story(html=html, archive=fitz.Archive(str(font)))

    def rectfn(rect_num, filled):
        return (fitz.Rect(0, 0, 595, 842), fitz.Rect(42, 42, 553, 800), None)

    story.write(writer, rectfn)
    writer.close()
    return out.getvalue()

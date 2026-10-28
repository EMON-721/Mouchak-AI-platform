from services.model_worker.pdf_report import report
from services.model_worker.domain import process
import fitz


def test_bengali_pdf_is_a_real_readable_document():
    data = {
        "module": "landledger-bd",
        "created_at": "2026-10-27",
        "output": process("land", {"value": "০.৪৫১৪", "unit": "acre"}),
    }
    content = report(data)
    assert content.startswith(b"%PDF-")
    document = fitz.open(stream=content, filetype="pdf")
    assert len(document) >= 1
    assert "45.1400" in "".join(p.get_text() for p in document)
    assert document[0].get_pixmap().width > 0


def test_no_false_source_license_state():
    from services.model_worker.main import MODULES
    from services.model_worker.store import ROOT
    import json

    x = json.loads(
        (ROOT / "packages/module-registry/source-candidates.json").read_text()
    )
    assert len(x["sources"]) == 244
    assert all(s["ingested"] is False for s in x["sources"])
    assert all(m["full_module_complete"] is False for m in MODULES.values())

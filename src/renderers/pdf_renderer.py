import os
import sys
from pathlib import Path


def render_pdf(docx_path: str | Path, output_path: str | Path) -> Path:
    """
    Converts a generated .docx file to a high-quality .pdf document.
    Attempts docx2pdf (MS Word engine on Windows), falling back gracefully
    to HTML+Weasyprint or direct PDF renderer.
    """
    in_docx = Path(docx_path).resolve()
    out_pdf = Path(output_path).resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    # 1. Primary: docx2pdf (Direct Windows MS Word Automation)
    try:
        from docx2pdf import convert
        convert(str(in_docx), str(out_pdf))
        if out_pdf.exists() and out_pdf.stat().st_size > 0:
            return out_pdf
    except Exception:
        pass

    # 2. Secondary: Direct comtypes Word automation if docx2pdf had transient issue
    if sys.platform == "win32":
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(str(in_docx))
            # 17 = wdFormatPDF
            doc.SaveAs(str(out_pdf), FileFormat=17)
            doc.Close()
            word.Quit()
            if out_pdf.exists() and out_pdf.stat().st_size > 0:
                return out_pdf
        except Exception:
            pass

    # 3. Tertiary: Weasyprint fallback
    try:
        from weasyprint import HTML
        # Extract text from docx and render HTML template to PDF
        from docx import Document
        doc = Document(str(in_docx))
        html_lines = ["<html><head><style>body{font-family: Arial, sans-serif; font-size: 10pt; margin: 0.5in;}</style></head><body>"]
        for p in doc.paragraphs:
            if p.text.strip():
                html_lines.append(f"<p>{p.text}</p>")
        html_lines.append("</body></html>")
        HTML(string="".join(html_lines)).write_pdf(str(out_pdf))
        if out_pdf.exists() and out_pdf.stat().st_size > 0:
            return out_pdf
    except Exception:
        pass

    # 4. If all converters fail, raise clear actionable error
    raise RuntimeError(
        f"PDF conversion failed for {in_docx}. "
        "Ensure Microsoft Word is installed (Windows) or install weasyprint."
    )

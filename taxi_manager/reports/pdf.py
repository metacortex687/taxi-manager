from fpdf import FPDF


def renderReportToPDF(report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(40, 10, "Hello World!")
    return pdf.output()

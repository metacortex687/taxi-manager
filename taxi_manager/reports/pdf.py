from fpdf import FPDF


FONT_NAME = "DejaVuSans"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TITLE_FONT_SIZE = 16
BODY_FONT_SIZE = 11
ROW_HEIGHT = 8
TABLE_WIDTHS = (60, 40, 30)


def renderReportToPDF(report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_font(FONT_NAME, "", FONT_PATH_REGULAR)
    pdf.add_font(FONT_NAME, "B", FONT_PATH_BOLD)

    def set_font(style="", size=BODY_FONT_SIZE):
        pdf.set_font(FONT_NAME, style=style, size=size)

    def write_line(text):
        pdf.cell(0, ROW_HEIGHT, str(text), new_x="LMARGIN", new_y="NEXT")

    def write_table_row(values, style=""):
        set_font(style=style)
        last_index = len(values) - 1

        for index, (width, value) in enumerate(zip(TABLE_WIDTHS, values)):
            kwargs = {}
            if index == last_index:
                kwargs = {"new_x": "LMARGIN", "new_y": "NEXT"}

            pdf.cell(width, ROW_HEIGHT, str(value), border=1, **kwargs)

    def format_date(value):
        return value.strftime("%Y-%m-%d")

    period_from, period_to = report.get_period_dates_in_report_time_zone()
    headers = report.get_result_model().get_table_headers()

    set_font(style="B", size=TITLE_FONT_SIZE)
    pdf.cell(0, 10, str(report._meta.verbose_name), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    set_font()
    write_line(f"Автомобиль: {report.vehicle.display_name}")
    write_line(f"Предприятие: {report.enterprise.name}")
    write_line(f"Часовой пояс: {report.time_zone.code}")
    write_line(f"Период: {period_from} - {period_to}")
    write_line(f"Периодичность: {report.get_frequency_display()}")
    pdf.ln(4)

    write_table_row([header["verbose_name"] for header in headers], style="B")

    total_mileage = 0.0
    total_trips = 0

    for row in report.get_results():
        mileage = round(row.mileage or 0, 1)
        count_trip = row.count_trip or 0

        total_mileage += mileage
        total_trips += count_trip

        write_table_row([format_date(row.date), f"{mileage:.1f}", count_trip])

    write_table_row(["Итого", f"{total_mileage:.1f}", total_trips], style="B")

    return pdf.output()
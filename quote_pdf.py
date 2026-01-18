from dataclasses import dataclass
from typing import List, Union, IO
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -------------------------
# Fonts (Bundled)
# -------------------------
# These files must exist:
# static/fonts/Calibri.ttf
# static/fonts/Calibri-Bold.ttf
pdfmetrics.registerFont(TTFont("Calibri", "static/fonts/Calibri.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Bold", "static/fonts/Calibri-Bold.ttf"))

UNIT_PRICE = 120.00  # adjust if needed

def money(x: float) -> str:
    return f"${x:,.2f}"

@dataclass
class QuoteItem:
    description: str
    estimated_hours: float

    @property
    def unit_price(self) -> float:
        return UNIT_PRICE

    @property
    def total_price(self) -> float:
        return self.estimated_hours * self.unit_price


def render_quote_pdf(
    output: Union[str, Path, IO[bytes]],
    *,
    quote_no_text: str,
    submitted_on: str,
    work_order: str,
    due_date: str,
    items: List[QuoteItem],
    logo_path: str = "static/logo.png",
) -> None:
    c = canvas.Canvas(output, pagesize=LETTER)
    w, h = LETTER

    L = 0.85 * inch
    R = w - 0.85 * inch
    TOP = h - 0.65 * inch

    BRAND_BLUE = colors.HexColor("#2F5BEA")
    LABEL_GREY = colors.HexColor("#8E8E8E")
    LINE_GREY = colors.HexColor("#D9D9D9")
    TABLE_HEAD_BG = colors.HexColor("#F2F2F2")
    TABLE_HEAD_TEXT = colors.HexColor("#2339A7")

    # Top bar
    c.setFillColor(BRAND_BLUE)
    c.rect(L, TOP + 0.18 * inch, R - L, 0.18 * inch, stroke=0, fill=1)

    y = TOP - 0.10 * inch

    # Logo
    lp = Path(logo_path)
    if lp.exists():
        logo_width = 2.2 * inch
        logo_height = 0.6 * inch
        c.drawImage(str(lp), L, y - logo_height, width=logo_width, height=logo_height, mask="auto")
        y -= logo_height + 10
    else:
        y -= 10

    c.setFillColor(colors.black)
    c.setFont("Calibri", 10)
    y -= 14
    c.drawString(L, y, "Monclus Vending Services")
    y -= 14
    c.drawString(L, y, "184-10 Jamaica Ave.")
    y -= 14
    c.drawString(L, y, "Hollis, NY 11423")
    y -= 14
    c.drawString(L, y, "(347) 757-7939")

    title_y = y - 0.55 * inch
    c.setFont("Calibri-Bold", 28)
    c.drawString(L, title_y, "Quote")

    sub_y = title_y - 0.35 * inch
    c.setFont("Calibri-Bold", 11)
    c.setFillColor(LABEL_GREY)
    c.drawString(L, sub_y, "Submitted on:")
    c.setFillColor(colors.HexColor("#4A4A4A"))
    c.setFont("Calibri", 11)
    c.drawString(L + 1.05 * inch, sub_y, submitted_on)

    blocks_top = sub_y - 0.40 * inch
    col1_x = L
    col2_x = L + 3.25 * inch
    col3_x = L + 5.90 * inch

    c.setFillColor(colors.black)
    c.setFont("Calibri-Bold", 11)
    c.drawString(col1_x, blocks_top, "Quote for")
    c.setFont("Calibri", 10)
    yy = blocks_top - 18
    c.drawString(col1_x, yy, "Newco Services"); yy -= 14
    c.drawString(col1_x, yy, "Dispatch@newcoservices.com"); yy -= 14
    c.drawString(col1_x, yy, "1200 S. Federal Hwy, Suite 304"); yy -= 14
    c.drawString(col1_x, yy, "Boynton Beach, FL 33435"); yy -= 14
    c.drawString(col1_x, yy, "(866) 549-6146"); yy -= 14

    c.setFont("Calibri-Bold", 11)
    c.drawString(col2_x, blocks_top, "Payable to")
    c.setFont("Calibri", 10)
    c.drawString(col2_x, blocks_top - 18, "Monclus Vending Services LLC")

    c.setFont("Calibri-Bold", 11)
    c.drawString(col3_x, blocks_top, "Quote")
    c.drawString(col3_x, blocks_top - 16, quote_no_text)

    info_y = blocks_top - 40
    c.setFont("Calibri-Bold", 11)
    c.drawString(col2_x, info_y, "Work Order")
    c.drawString(col3_x, info_y, "Due date")
    c.setFont("Calibri", 10)
    c.drawString(col2_x, info_y - 16, work_order)
    c.drawString(col3_x, info_y - 16, due_date)

    div_y = info_y - 0.55 * inch
    c.setStrokeColor(LINE_GREY)
    c.setLineWidth(1)
    c.line(L, div_y, R, div_y)

    table_top = div_y - 0.35 * inch
    header_h = 0.34 * inch
    c.setFillColor(TABLE_HEAD_BG)
    c.rect(L, table_top - header_h + 2, R - L, header_h, stroke=0, fill=1)

    desc_x = L + 0.12 * inch
    hours_x = L + 4.75 * inch
    unit_x = L + 5.75 * inch
    total_x = R - 0.12 * inch

    c.setFillColor(TABLE_HEAD_TEXT)
    c.setFont("Calibri-Bold", 11)
    c.drawString(desc_x, table_top - 0.23 * inch, "Description")
    c.drawRightString(hours_x, table_top - 0.23 * inch, "Estimated Hours")
    c.drawRightString(unit_x, table_top - 0.23 * inch, "Unit price")
    c.drawRightString(total_x, table_top - 0.23 * inch, "Total price")

    c.setFillColor(colors.black)
    c.setFont("Calibri", 10)
    yrow = table_top - header_h - 0.10 * inch
    row_h = 0.28 * inch

    subtotal = 0.0
    for it in items:
        subtotal += it.total_price
        c.setStrokeColor(colors.HexColor("#E6E6E6"))
        c.setLineWidth(0.8)
        c.line(L, yrow - 6, R, yrow - 6)

        c.drawString(desc_x, yrow, it.description)
        c.drawRightString(hours_x, yrow, f"{it.estimated_hours:g}")
        c.drawRightString(unit_x, yrow, money(it.unit_price))
        c.drawRightString(total_x, yrow, money(it.total_price))
        yrow -= row_h

    ytot = yrow - 0.25 * inch
    c.setStrokeColor(LINE_GREY)
    c.line(L, ytot + 14, R, ytot + 14)

    c.setFillColor(colors.black)
    c.setFont("Calibri", 10)
    c.drawRightString(unit_x, ytot, "Subtotal")
    c.drawRightString(total_x, ytot, money(subtotal))

    c.setFont("Calibri-Bold", 15)
    c.drawRightString(unit_x, ytot - 44, "Total")
    c.drawRightString(total_x, ytot - 44, money(subtotal))

    ysig = ytot - 0.55 * inch
    c.setFont("Calibri", 10)
    c.drawString(L, ysig, "PO # ________________________________")
    c.drawString(L, ysig - 18, "Approved By ____________________________")

    c.setFont("Calibri-Bold", 11)
    c.setFillColor(colors.HexColor("#C2185B"))
    c.drawString(L, ysig - 126, "Thank you for your business!")

    c.save()









from django.http import HttpResponse
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime
from rest_framework.views import APIView
from rest_framework import serializers





QUERY_MAP = {
    "user": "D_FETCH_ALL_USER_DATA",
    "leads": "D_FETCH_ALL_LEADS_DATA",
    "payment":"D_FETCH_ALL_PENDING_PAYMENTS",
    "daily_report":"D_FETCH_DAILY_REPORT_PDF"
    
}


class DynamicPdfGenrate(APIView):
    # class InputSerializer(serializers.Serializer):
    #     id=serializers.IntegerField(required=False)

    def get(self, request, table_name,id):
        print(request)
        # 🔹 validate table
        query_key = QUERY_MAP.get(table_name)
        if not query_key:
            return HttpResponse("Invalid table", status=400)

        # 🔹 fetch data
        # id = id
        print("id",id)

        data = exec_raw_sql(query_key, {"id": id}) or []

        # 🔹 response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{table_name}_report.pdf"'

        # 🔹 use landscape (important for many columns)
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=20 * mm,
            bottomMargin=15 * mm,
        )

        elements = []

        # =========================================================
        # 🎨 COLORS
        # =========================================================
        PRIMARY = colors.HexColor('#4CAF50')
        PRIMARY_LIGHT = colors.HexColor('#E8F5E9')
        BORDER = colors.HexColor('#E0E0E0')
        WHITE = colors.white

        # =========================================================
        # ✍️ STYLES
        # =========================================================
        title_style = ParagraphStyle(
            'title', fontSize=16, textColor=PRIMARY, spaceAfter=10
        )

        header_style = ParagraphStyle(
            'header', fontSize=9, textColor=WHITE, alignment=1
        )

        cell_style = ParagraphStyle(
            'cell', fontSize=8
        )
        cell_style.wordWrap = 'CJK'   # 🔥 long text wrap

        # =========================================================
        # 📊 STATS SECTION (SAFE)
        # =========================================================
        total = len(data)

        stats = {
            "Total Records": total,
        }

        # optional stats (safe check)
        if data and isinstance(data[0], dict):
            if 'payment_amount' in data[0]:
                stats["With Payment"] = sum(1 for d in data if d.get('payment_amount'))
                stats["No Payment"] = sum(1 for d in data if not d.get('payment_amount'))

        stats_table_data = [
            [Paragraph(str(k), cell_style), Paragraph(str(v), header_style)]
            for k, v in stats.items()
        ]

        stats_table = Table(stats_table_data, colWidths=[400, 80])

        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, -1), PRIMARY),
            ('TEXTCOLOR', (1, 0), (1, -1), WHITE),
            ('BOX', (0, 0), (-1, -1), 1, PRIMARY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('BACKGROUND', (0, 0), (0, -1), PRIMARY_LIGHT),
        ]))

        elements.append(Paragraph("Summary", title_style))
        elements.append(stats_table)

        # =========================================================
        # 📋 TABLE SECTION
        # =========================================================
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"{table_name.title()} Data", title_style))

        if data and isinstance(data[0], dict):

            headers = list(data[0].keys())

            # 🔥 TABLE DATA
            table_data = []

            # header row
            table_data.append([
                Paragraph(h.replace('_', ' ').title(), header_style)
                for h in headers
            ])

            # rows
            for row in data:
                table_data.append([
                    Paragraph(str(row.get(col) or ""), cell_style)
                    for col in headers
                ])

            # =====================================================
            # 🔥 COLUMN WIDTH FIX (MAIN BUG FIX)
            # =====================================================
            page_width = landscape(A4)[0] - 10 * mm
            num_cols = len(headers)

            if num_cols <= 6:
                col_widths = [page_width / num_cols] * num_cols
            else:
                col_widths = [80] * num_cols   # fixed width for many cols

            table = Table(
                table_data,
                colWidths=col_widths,
                repeatRows=1
            )

            table.setStyle(TableStyle([
                # header
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),

                # grid
                ('GRID', (0, 0), (-1, -1), 0.5, BORDER),

                # padding fix
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),

                # zebra rows
                *[
                    ('BACKGROUND', (0, i), (-1, i),
                     PRIMARY_LIGHT if i % 2 == 0 else WHITE)
                    for i in range(1, len(table_data))
                ]
            ]))

            elements.append(table)

        else:
            elements.append(Paragraph("No Data Available", cell_style))

        # =========================================================
        # 📄 BUILD PDF
        # =========================================================
        doc.build(elements)

        return response



































from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ..services.query_services import *
#pip install reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)

from datetime import datetime


# ─────────────────────────────────────────────
#  COLOR PALETTE  (ஒரே இடத்துல மாத்தினா போதும்)
# ─────────────────────────────────────────────
PRIMARY       = colors.HexColor('#4CAF50')   # green  – badge, header line
PRIMARY_DARK  = colors.HexColor('#388E3C')   # dark green – heading text
PRIMARY_LIGHT = colors.HexColor('#E8F5E9')   # very light green – row bg
BADGE_TEXT    = colors.white                 # number text inside badge
ROW_ALT       = colors.HexColor('#F9F9F9')   # alternate row bg
BORDER_COLOR  = colors.HexColor('#E0E0E0')   # table border / divider
TEXT_DARK     = colors.HexColor('#212121')   # main text
TEXT_GREY     = colors.HexColor('#757575')   # subtitle / meta text
TEXT_BROWN    = colors.HexColor('#5D4037')   # date label
MANUAL_BG     = colors.HexColor('#F1F8E9')   # manual entry section bg
MSG_BG        = colors.HexColor('#FAFAFA')   # message box bg
WHITE         = colors.white


# ─────────────────────────────────────────────
#  HELPER – hex string → reportlab Color
# ─────────────────────────────────────────────
def hc(hex_str: str, alpha: float = 1.0) -> colors.Color:
    h = hex_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    return colors.Color(r, g, b, alpha)


# ─────────────────────────────────────────────
#  PAGE HEADER + FOOTER  (every page)
# ─────────────────────────────────────────────
def _on_page(canvas, doc):
    canvas.saveState()
    page_w, page_h = A4

    # ── Top green bar ──────────────────────────
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, page_h - 10 * mm, page_w, 10 * mm, fill=1, stroke=0)

    # Company name in bar
    canvas.setFont('Helvetica-Bold', 11)
    canvas.setFillColor(WHITE)
    canvas.drawString(15 * mm, page_h - 7 * mm, 'CRM System')

    # Date right side of bar
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(
        page_w - 15 * mm,
        page_h - 7 * mm,
        datetime.now().strftime('%d %b %Y')
    )

    # ── Bottom footer line ─────────────────────
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, 12 * mm, page_w - 15 * mm, 12 * mm)

    # Generated timestamp (left)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(TEXT_GREY)
    canvas.drawString(
        15 * mm, 8 * mm,
        f'Generated: {datetime.now().strftime("%d %b %Y, %H:%M")}'
    )

    # Page number (right)
    canvas.drawRightString(
        page_w - 15 * mm, 8 * mm,
        f'Page {doc.page}'
    )

    canvas.restoreState()


# ─────────────────────────────────────────────
#  MAIN VIEW
# ─────────────────────────────────────────────
@csrf_exempt
def download_crm_report(request,**data):

    # ── 1. Response setup ──────────────────────
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Daily_Report.pdf"'

    # ── 2. Document setup ──────────────────────
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=22 * mm,   # space below green bar
        bottomMargin=18 * mm,
    )

    elements = []

    # ─────────────────────────────────────────
    #  STYLES
    # ─────────────────────────────────────────
    title_style = ParagraphStyle(
        'TitleStyle',
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=PRIMARY_DARK,
        alignment=TA_LEFT,
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        'SubStyle',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_GREY,
        alignment=TA_LEFT,
        spaceAfter=10,
    )

    date_style = ParagraphStyle(
        'DateStyle',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=TEXT_BROWN,
        spaceAfter=14,
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=PRIMARY_DARK,
        spaceBefore=14,
        spaceAfter=8,
    )

    label_style = ParagraphStyle(
        'LabelStyle',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
    )

    badge_style = ParagraphStyle(
        'BadgeStyle',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=BADGE_TEXT,
        alignment=TA_CENTER,
    )

    manual_label_style = ParagraphStyle(
        'ManualLabel',
        fontName='Helvetica',
        fontSize=11,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
    )

    manual_value_style = ParagraphStyle(
        'ManualValue',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
    )

    msg_style = ParagraphStyle(
        'MsgStyle',
        fontName='Helvetica',
        fontSize=10,
        textColor=TEXT_GREY,
        leading=16,
        alignment=TA_LEFT,
    )

    # ─────────────────────────────────────────
    #  HEADER SECTION
    # ─────────────────────────────────────────
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Daily Report", title_style))
    # elements.append(Paragraph("Auto-synced from today's activity", subtitle_style))

    # Thin green divider under header text
    elements.append(Spacer(1, 16))
    elements.append(HRFlowable(
        width='100%',
        thickness=2,
        color=PRIMARY,
        spaceAfter=10,
    ))
    elements.append(Spacer(1, 14))
    elements.append(Paragraph("Date :  12/06/2025", date_style))

    # ─────────────────────────────────────────
    #  STATS TABLE
    #  Left col  = label (light green bg)
    #  Right col = green badge with white number
    # ─────────────────────────────────────────

    # ── உங்கள் backend data ──────────────────
    # data_rows = [
    #     ('Total No of Leads',  '55'),
    #     ('Call Spoked',        '65'),
    #     ('Not Respond',        '65'),
    #     ('Follow Up',          '65'),
    #     ('Joined',             '65'),
    #     ('Pending Follow Up',  '65'),
    #     ('Partial Payment',    '65'),
    #     ('Full Payment',       '65'),
    # ]
    # data = exec_raw_sql('D_FETCH_ALL_LEADS_DATA', {})
    datas=data
    result = datas[0] if datas else {}

    data_rows = [
        (key.replace('_', ' ').title(), str(value))
        for key, value in result.items()
    ]

    # Paragraph objects ஆக மாத்துவோம்
    table_data = [
        [
            Paragraph(label, label_style),
            Paragraph(value, badge_style),
        ]
        for label, value in data_rows
    ]

    # colWidths: label wide, badge narrow
    page_usable = A4[0] - 30 * mm          # total usable width
    label_w = page_usable * 0.80
    badge_w = page_usable * 0.20

    report_table = Table(
        table_data,
        colWidths=[label_w, badge_w],
        spaceBefore=0,
        spaceAfter=0,
    )

    report_table.setStyle(TableStyle([
        # ── Alignment ────────────────────────
        ('ALIGN',   (0, 0), (0, -1), 'LEFT'),
        ('ALIGN',   (1, 0), (1, -1), 'CENTER'),
        ('VALIGN',  (0, 0), (-1, -1), 'MIDDLE'),

        # ── Font ─────────────────────────────
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),

        # ── Padding ──────────────────────────
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),

        # ── Zebra rows (alternate bg) ─────────
        *[
            ('BACKGROUND', (0, i), (0, i),
             PRIMARY_LIGHT if i % 2 == 0 else ROW_ALT)
            for i in range(len(table_data))
        ],

        # ── Badge column always green ─────────
        ('BACKGROUND', (1, 0), (1, -1), PRIMARY),

        # ── Row separator lines ───────────────
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER_COLOR),

        # ── Outer border ─────────────────────
        ('BOX', (0, 0), (-1, -1), 1, PRIMARY),

        # ── Rounded corners ──────────────────
        ('ROUNDEDCORNERS', [6]),
    ]))

    elements.append(report_table)

    # ─────────────────────────────────────────
    #  MANUAL ENTRY SECTION
    # ─────────────────────────────────────────
    elements.append(Paragraph("Manual Entry", section_style))

    manual_data = [
        [
            Paragraph('Tomorrow Expected Conversion', manual_label_style),
            Paragraph('0', manual_value_style),
        ],
        [
            Paragraph('Leads For Tomorrow', manual_label_style),
            Paragraph('0', manual_value_style),
        ],
    ]

    manual_table = Table(
        manual_data,
        colWidths=[label_w, badge_w],
    )
    manual_table.setStyle(TableStyle([
        # ── Background ───────────────────────
        ('BACKGROUND', (0, 0), (-1, -1), MANUAL_BG),

        # ── Alignment ────────────────────────
        ('ALIGN',  (0, 0), (0, -1), 'LEFT'),
        ('ALIGN',  (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # ── Font ─────────────────────────────
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (1, 0), (1, -1), PRIMARY_DARK),

        # ── Padding ──────────────────────────
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),

        # ── Row separator ─────────────────────
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, BORDER_COLOR),

        # ── Outer border ─────────────────────
        ('BOX', (0, 0), (-1, -1), 1, PRIMARY),

        ('ROUNDEDCORNERS', [6]),
    ]))
    elements.append(manual_table)

    # ─────────────────────────────────────────
    #  MESSAGE BOX SECTION
    # ─────────────────────────────────────────
    elements.append(Paragraph("Write Your Own Message", section_style))

    # உங்கள் backend-இல் இருந்து message வரும்
    user_message = "User message here..."    # ← DB-இல் இருந்து replace பண்ணுங்க

    msg_box = Table(
        [[Paragraph(user_message, msg_style)]],
        colWidths=[page_usable],
    )
    msg_box.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), MSG_BG),
        ('BOX',           (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('TOPPADDING',    (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 40),   # min height feel
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('ROUNDEDCORNERS', [6]),
    ]))
    elements.append(msg_box)

    # ─────────────────────────────────────────
    #  BUILD PDF
    # ─────────────────────────────────────────
    doc.build(
        elements,
        onFirstPage=_on_page,
        onLaterPages=_on_page,
    )

    return response



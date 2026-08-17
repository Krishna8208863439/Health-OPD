import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

DISCLAIMER_TEXT = (
    "HealthPredict AI provides machine-learning-based risk estimates for educational "
    "and decision-support purposes only. It does not diagnose, treat, cure, or prevent "
    "any disease. Always consult a qualified healthcare professional for medical advice."
)

def generate_prediction_pdf(prediction_record: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0e7490'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#334155'),
        leading=13
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        leading=11,
        alignment=1 # Center
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("HealthPredict AI — Clinical Risk Evaluation Report", title_style))
    elements.append(Paragraph(f"Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Record Reference: #{prediction_record['id']}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0e7490'), spaceAfter=14))

    # 2. Risk Assessment Summary Table
    risk_level = prediction_record.get('risk_level', 'Low')
    risk_color = '#10b981' if risk_level == 'Low' else ('#f59e0b' if risk_level == 'Moderate' else '#ef4444')
    
    summary_data = [
        [
            Paragraph("<b>Target Disease:</b>", body_style),
            Paragraph(f"<b>{prediction_record['disease'].upper()}</b>", body_style),
            Paragraph("<b>Assessment Date:</b>", body_style),
            Paragraph(prediction_record['created_at'][:19].replace('T', ' '), body_style),
        ],
        [
            Paragraph("<b>Risk Probability:</b>", body_style),
            Paragraph(f"<b>{prediction_record['risk_percentage']}%</b>", body_style),
            Paragraph("<b>Stratification:</b>", body_style),
            Paragraph(f"<font color='{risk_color}'><b>{risk_level.upper()} RISK</b></font>", body_style),
        ],
        [
            Paragraph("<b>Classifier Model:</b>", body_style),
            Paragraph(prediction_record.get('model_name', 'Supervised Ensemble'), body_style),
            Paragraph("<b>Clinical Finding:</b>", body_style),
            Paragraph("High Risk Indicator Present" if prediction_record['prediction'] == 1 else "Low Risk / Within Expected Range", body_style),
        ]
    ]

    summary_table = Table(summary_data, colWidths=[110, 150, 110, 160])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 14))

    # 3. Patient Clinical Inputs Table
    elements.append(Paragraph("Patient Clinical Measurements & Biometric Inputs", section_heading))
    input_data = prediction_record.get('input_data', {})
    
    def format_input_val(k, v):
        if str(k).strip().lower() == 'sex':
            s = str(v).strip().lower()
            if s in ('1', '1.0', 'male', 'm'):
                return 'Male'
            elif s in ('0', '0.0', 'female', 'f'):
                return 'Female'
        return str(v)

    input_rows = []
    keys = list(input_data.keys())
    for i in range(0, len(keys), 2):
        k1 = keys[i]
        v1 = format_input_val(k1, input_data[k1])
        if i + 1 < len(keys):
            k2 = keys[i+1]
            v2 = format_input_val(k2, input_data[k2])
            input_rows.append([
                Paragraph(f"<b>{k1}:</b>", body_style), Paragraph(str(v1), body_style),
                Paragraph(f"<b>{k2}:</b>", body_style), Paragraph(str(v2), body_style)
            ])
        else:
            input_rows.append([
                Paragraph(f"<b>{k1}:</b>", body_style), Paragraph(str(v1), body_style),
                "", ""
            ])

    input_table = Table(input_rows, colWidths=[130, 135, 130, 135])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 14))

    # 4. Model Feature Importance Breakdown
    elements.append(Paragraph("Machine Learning Factor Importance (Key Risk Drivers)", section_heading))
    fi_list = prediction_record.get('feature_importance', [])[:6] # Top 6 features
    fi_rows = [
        [
            Paragraph("<b>Clinical Feature</b>", body_style),
            Paragraph("<b>Relative Weight (%)</b>", body_style),
            Paragraph("<b>Clinical Relevance</b>", body_style)
        ]
    ]
    for item in fi_list:
        fi_rows.append([
            Paragraph(item.get('feature', ''), body_style),
            Paragraph(f"{item.get('percentage', 0.0):.2f}%", body_style),
            Paragraph(item.get('description', ''), body_style)
        ])

    if len(fi_rows) > 1:
        fi_table = Table(fi_rows, colWidths=[120, 100, 310])
        fi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0f2fe')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
            ('PADDING', (0, 0), (-1, -1), 4.5),
        ]))
        elements.append(fi_table)

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#cbd5e1'), spaceAfter=10))

    # 5. Mandatory Verbatim Medical Disclaimer (Phase 10 / Global Rule 7)
    elements.append(Paragraph(f"<b>IMPORTANT NOTICE & MEDICAL DISCLAIMER:</b> {DISCLAIMER_TEXT}", disclaimer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

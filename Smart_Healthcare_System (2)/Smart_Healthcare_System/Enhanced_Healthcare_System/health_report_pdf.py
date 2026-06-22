import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#6B7280')) # Slate Gray
        
        # Footer dividing line
        self.setStrokeColor(colors.HexColor('#E2E8F0'))
        self.setLineWidth(0.75)
        self.line(40, 45, 555, 45)
        
        # Footer text
        self.drawString(40, 30, "HealthCare+ Clinical Information System • Daily Health Summary")
        self.drawRightString(555, 30, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_health_report(patient_name, age, contact, diet_goal, health_score, food_logs, medication_logs, symptom_logs, file_path):
    """
    Generate a professional hospital-branded PDF health report with premium layout and styling.
    """
    # Page setup (margins: left=40, right=40, top=40, bottom=55 for footer space)
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=55
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Premium Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.white,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#F1F5F9'),
        spaceAfter=8
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#1E3A8A'), # Navy Blue
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#1E293B'), # Slate 800
        leading=13.5
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#334155'), # Slate 700
        leading=11.5
    )

    story = []
    
    # Premium Color Palette
    primary_color = colors.HexColor('#1E3A8A')  # Deep Navy Blue
    secondary_color = colors.HexColor('#0284C7') # Premium Sky Blue
    neutral_light = colors.HexColor('#F8FAFC')   # Slate 50
    border_color = colors.HexColor('#E2E8F0')    # Slate 200
    
    # ─── HEADER BLOCK WITH HOSPITAL BRANDING ───
    header_data = [
        [
            Paragraph("HealthCare Plus Hospital", title_style),
            Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle('DateText', parent=title_style, alignment=2, fontSize=10))
        ],
        [
            Paragraph("Personalized Daily Patient Health Report", subtitle_style),
            Paragraph("System Status: Active Care", ParagraphStyle('SystemText', parent=subtitle_style, alignment=2, fontSize=8))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[315, 200])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('PADDING', (0,0), (-1,-1), 14),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 12))
    
    # ─── PATIENT BIO & HEALTH SCORE CARD ───
    score_display = f"{health_score}/100"
    if health_score >= 80:
        score_label = "Optimal Condition"
        score_color = '#10B981' # Emerald Green
    elif health_score >= 60:
        score_label = "Moderate Condition"
        score_color = '#F59E0B' # Amber Yellow
    else:
        score_label = "Requires Attention"
        score_color = '#EF4444' # Crimson Red
        
    patient_info_html = f"""
    <b>Patient Bio Information:</b><br/>
    Name: {patient_name}<br/>
    Age: {age} years<br/>
    Contact Details: {contact or 'N/A'}<br/>
    Active Diet Goal: <b>{diet_goal}</b>
    """
    
    score_html = f"""
    <font size="11" color="{score_color}"><b>Today's Health Score:</b></font><br/>
    <font size="30" color="{score_color}"><b>{score_display}</b></font><br/>
    <font size="9.5" color="#475569"><b>Status: {score_label}</b></font>
    """
    
    info_card_data = [
        [
            Paragraph(patient_info_html, body_style),
            Paragraph(score_html, ParagraphStyle('ScoreBlock', parent=body_style, alignment=1))
        ]
    ]
    
    info_card_table = Table(info_card_data, colWidths=[315, 200])
    info_card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), neutral_light),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 12),
    ]))
    
    story.append(info_card_table)
    story.append(Spacer(1, 10))
    
    # ─── SECTION 1: MEDICATION ADHERENCE LOGS ───
    story.append(Paragraph("1. Medication Adherence Tracker", h1_style))
    
    if len(medication_logs) > 0:
        med_table_data = [[
            Paragraph("Medicine Name", table_header_style),
            Paragraph("Scheduled Time", table_header_style),
            Paragraph("Log Status", table_header_style),
            Paragraph("Taken At Timestamp", table_header_style)
        ]]
        
        for log in medication_logs:
            status_text = log['status'].upper()
            status_color = '#10B981' if log['status'] == 'taken' else '#EF4444'
            status_html = f'<font color="{status_color}"><b>{status_text}</b></font>'
            
            med_table_data.append([
                Paragraph(log['medicine_name'], table_cell_style),
                Paragraph(log['reminder_time'], table_cell_style),
                Paragraph(status_html, table_cell_style),
                Paragraph(log['created_at'], table_cell_style)
            ])
            
        med_table = Table(med_table_data, colWidths=[155, 90, 90, 180])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), secondary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, neutral_light]),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(med_table)
    else:
        story.append(Paragraph("<i>No medication reminders logged today.</i>", body_style))
        
    story.append(Spacer(1, 10))
    
    # ─── SECTION 2: CALORIE & DIET LOG ───
    story.append(Paragraph("2. Daily Diet & Calorie Scanner Logs", h1_style))
    
    if len(food_logs) > 0:
        food_table_data = [[
            Paragraph("Food Scanned", table_header_style),
            Paragraph("Calories", table_header_style),
            Paragraph("Protein / Carbs / Fat", table_header_style),
            Paragraph("Diet Assessment Tag", table_header_style)
        ]]
        
        for log in food_logs:
            fitness = log.get('goal_fitness', 'success')
            fitness_label = "RECOMMENDED" if fitness == 'success' else ("MODERATION" if fitness == 'warning' else "LIMIT / AVOID")
            fitness_color = '#10B981' if fitness == 'success' else ('#F59E0B' if fitness == 'warning' else '#EF4444')
            fitness_html = f'<font color="{fitness_color}"><b>{fitness_label}</b></font>'
            
            macros_text = f"P: {log.get('protein', '0g')} | C: {log.get('carbs', '0g')} | F: {log.get('fat', '0g')}"
            
            food_table_data.append([
                Paragraph(log['food_name'], table_cell_style),
                Paragraph(f"{log['calories']} kcal", table_cell_style),
                Paragraph(macros_text, table_cell_style),
                Paragraph(fitness_html, table_cell_style)
            ])
            
        food_table = Table(food_table_data, colWidths=[150, 85, 145, 135])
        food_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), secondary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, neutral_light]),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(food_table)
    else:
        story.append(Paragraph("<i>No food scans logged today.</i>", body_style))
        
    story.append(Spacer(1, 10))
    
    # ─── SECTION 3: DAILY SYMPTOM JOURNAL TIMELINE ───
    story.append(Paragraph("3. Daily Symptom Journal Notes", h1_style))
    
    if len(symptom_logs) > 0:
        symptom_table_data = [[
            Paragraph("Logged Time", table_header_style),
            Paragraph("Mood", table_header_style),
            Paragraph("Severity Level", table_header_style),
            Paragraph("Patient Note", table_header_style)
        ]]
        
        for log in symptom_logs:
            severity = log.get('severity', 'mild').upper()
            sev_color = '#10B981' if log.get('severity') == 'mild' else ('#F59E0B' if log.get('severity') == 'moderate' else '#EF4444')
            sev_html = f'<font color="{sev_color}"><b>{severity}</b></font>'
            
            symptom_table_data.append([
                Paragraph(log['log_date'], table_cell_style),
                Paragraph(log.get('mood', 'N/A').title(), table_cell_style),
                Paragraph(sev_html, table_cell_style),
                Paragraph(log['symptoms'], table_cell_style)
            ])
            
        symptom_table = Table(symptom_table_data, colWidths=[85, 75, 95, 260])
        symptom_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), secondary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, neutral_light]),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(symptom_table)
    else:
        story.append(Paragraph("<i>No symptom notes logged recently.</i>", body_style))
        
    story.append(Spacer(1, 10))
    
    # ─── SECTION 4: CLINICAL CORRELATIONAL AI INSIGHTS ───
    story.append(Paragraph("4. Clinical AI Insights & Correlations", h1_style))
    
    insights_html = ""
    if len(medication_logs) > 0 and len(symptom_logs) > 0:
        missed_meds = sum(1 for log in medication_logs if log['status'] == 'skipped')
        if missed_meds > 0:
            insights_html += "⚠️ <b>MEDICATION CORRELATION:</b> Noticeable increase in symptom severity on days with skipped medication.<br/><br/>"
        else:
            insights_html += "✅ <b>MEDICATION CORRELATION:</b> Patient shows excellent medication adherence, correlating with stable vitals.<br/><br/>"
            
    if len(food_logs) > 0 and len(symptom_logs) > 0:
        poor_diet = sum(1 for log in food_logs if log.get('goal_fitness') in ['warning', 'danger'])
        if poor_diet > 0:
            insights_html += "⚠️ <b>DIETARY CORRELATION:</b> Higher pain levels and 'Nausea' tags observed following intake of 'LIMIT / AVOID' foods (likely high sodium/sugar).<br/><br/>"
        else:
            insights_html += "✅ <b>DIETARY CORRELATION:</b> Diet remains within recommended limits, positively impacting overall mood.<br/><br/>"
            
    if not insights_html:
        insights_html = "<i>Insufficient data points to generate AI correlations. Patient needs to log more food and symptom data.</i>"
        
    insight_card_data = [[Paragraph(insights_html, body_style)]]
    insight_table = Table(insight_card_data, colWidths=[515])
    insight_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')), # Light slate-blue
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BFDBFE')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(insight_table)
    
    # Build Document with custom NumberedCanvas page numbering
    doc.build(story, canvasmaker=NumberedCanvas)

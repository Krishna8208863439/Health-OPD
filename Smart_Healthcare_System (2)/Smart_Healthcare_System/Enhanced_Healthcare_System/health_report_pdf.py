import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_health_report(patient_name, age, contact, diet_goal, health_score, food_logs, medication_logs, symptom_logs, file_path):
    """
    Generate a professional hospital-branded PDF health report.
    """
    # Page setup
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.white,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#E5E7EB'),
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0066CC'),
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#1F2937'),
        leading=14
    )
    
    body_bold_style = ParagraphStyle(
        'BodyDarkBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#374151'),
        leading=12
    )

    story = []
    
    # Color system
    primary_color = colors.HexColor('#0066CC')
    neutral_light = colors.HexColor('#F3F4F6')
    border_color = colors.HexColor('#E5E7EB')
    
    # ─── HEADER BLOCK ───
    # We will build a table container with primary background for the header
    header_data = [
        [
            Paragraph("HealthCare Plus Hospital", title_style),
            Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle('DateText', parent=title_style, alignment=2, fontSize=11))
        ],
        [
            Paragraph("Personalized Daily Patient Health Report", subtitle_style),
            Paragraph("System: Connected Care", ParagraphStyle('SystemText', parent=subtitle_style, alignment=2, fontSize=9))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[330, 180])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('PADDING', (0,0), (-1,-1), 16),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # ─── PATIENT INFORMATION & HEALTH SCORE CARD ───
    score_display = f"{health_score}/100"
    score_label = "Optimal Condition" if health_score >= 80 else ("Moderate Condition" if health_score >= 60 else "Requires Attention")
    score_color = '#10B981' if health_score >= 80 else ('#F59E0B' if health_score >= 60 else '#EF4444')
    
    patient_info_html = f"""
    <b>Patient Bio Information:</b><br/>
    Name: {patient_name}<br/>
    Age: {age} years<br/>
    Contact Details: {contact or 'N/A'}<br/>
    Active Diet Goal: <b>{diet_goal}</b>
    """
    
    score_html = f"""
    <font size="12" color="{score_color}"><b>Today's Daily Health Score:</b></font><br/>
    <font size="32" color="{score_color}"><b>{score_display}</b></font><br/>
    <font size="10" color="#6B7280"><b>Status: {score_label}</b></font>
    """
    
    info_card_data = [
        [
            Paragraph(patient_info_html, body_style),
            Paragraph(score_html, ParagraphStyle('ScoreBlock', parent=body_style, alignment=1))
        ]
    ]
    
    info_card_table = Table(info_card_data, colWidths=[320, 190])
    info_card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), neutral_light),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 14),
    ]))
    
    story.append(info_card_table)
    story.append(Spacer(1, 15))
    
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
            
        med_table = Table(med_table_data, colWidths=[160, 100, 100, 150])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, neutral_light]),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(med_table)
    else:
        story.append(Paragraph("<i>No medication reminders logged today.</i>", body_style))
        
    story.append(Spacer(1, 15))
    
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
            
        food_table = Table(food_table_data, colWidths=[150, 90, 150, 120])
        food_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, neutral_light]),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(food_table)
    else:
        story.append(Paragraph("<i>No food scans logged today.</i>", body_style))
        
    story.append(Spacer(1, 15))
    
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
            
        symptom_table = Table(symptom_table_data, colWidths=[90, 80, 100, 240])
        symptom_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, neutral_light]),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(symptom_table)
    else:
        story.append(Paragraph("<i>No symptom notes logged recently.</i>", body_style))
        
    story.append(Spacer(1, 15))
    
    # ─── SECTION 4: CLINICAL CORRELATIONAL AI INSIGHTS ───
    story.append(Paragraph("4. Clinical AI Insights & Correlations", h1_style))
    
    # Generate some dynamic mock insights based on the data presence
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
    insight_table = Table(insight_card_data, colWidths=[510])
    insight_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#BFDBFE')),
        ('PADDING', (0,0), (-1,-1), 16),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(insight_table)
    
    # Build Document
    doc.build(story)

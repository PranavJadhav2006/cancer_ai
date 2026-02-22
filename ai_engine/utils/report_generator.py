from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os

def generate_cancer_report(output_filename, patient_data):
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    doc = SimpleDocTemplate(output_filename, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # --- CUSTOM STYLES ---
    main_title_style = ParagraphStyle('MainTitle', parent=styles['Heading1'], alignment=1, fontSize=16, textColor=colors.navy, spaceAfter=20)
    section_header_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, textColor=colors.white, backColor=colors.navy, borderPadding=5, spaceBefore=12, spaceAfter=8)
    sub_header_style = ParagraphStyle('SubHeader', parent=styles['Heading3'], fontSize=10, textColor=colors.darkblue, spaceBefore=8, spaceAfter=5)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=9, leftIndent=20, spaceAfter=4)

    # Helper function to clean values (Remove N/A)
    def clean(val):
        if val is None or str(val).strip().upper() in ["N/A", "NONE", "UNDEFINED", "NAN", "___"]:
            return ""
        return str(val)

    def lbl_val(label, value):
        val = clean(value)
        return Paragraph(f"<b>{label}:</b> {val}", styles['Normal'])

    # 1. MAIN TITLE
    story.append(Paragraph("AI-DRIVEN PERSONALIZED CANCER TREATMENT SUMMARY", main_title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.navy, spaceAfter=10))

    # 2. PATIENT PROFILE
    story.append(Paragraph("PATIENT PROFILE", section_header_style))
    p_info = [
        [lbl_val("Name", patient_data.get('name')), lbl_val("MRN", patient_data.get('mrn'))],
        [lbl_val("Gender", patient_data.get('gender')), lbl_val("DOB", patient_data.get('dob'))],
        [lbl_val("Age", patient_data.get('age')), lbl_val("DOD", patient_data.get('dod'))]
    ]
    story.append(Table(p_info, colWidths=[260, 260]))

    # 3. DISEASE CHARACTERIZATION & PATHOLOGY
    story.append(Paragraph("DISEASE CHARACTERIZATION & PATHOLOGY", section_header_style))
    pathology = patient_data.get('pathology', {})
    char_data = [
        [lbl_val("Primary Diagnosis", pathology.get('diagnosis')), lbl_val("Histological Subtype", pathology.get('subtype'))],
        [lbl_val("Clinical Stage", pathology.get('stage')), lbl_val("WHO Grade", pathology.get('grade'))]
    ]
    story.append(Table(char_data, colWidths=[260, 260]))

    # 4. GENOMIC & VCF SUMMARY
    story.append(Paragraph("GENOMIC & VCF SUMMARY", section_header_style))
    vcf = patient_data.get('vcf_metrics', {})
    vcf_info = [[lbl_val("Total Variants", vcf.get('total')), lbl_val("Actionable", vcf.get('actionable')), lbl_val("VUS", vcf.get('vus'))]]
    story.append(Table(vcf_info, colWidths=[173, 173, 173]))
    
    # Genomic Table
    gen_data = [["Gene", "Mutation Status", "Clinical Impact", "AI Weight"]]
    genomics = patient_data.get('genomics', [])
    if genomics:
        gen_data.extend(genomics)
    else:
        gen_data.append(["", "", "", ""])
    
    t_gen = Table(gen_data, colWidths=[80, 120, 240, 80])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 5))
    story.append(t_gen)

    # 5. FUNCTIONAL STATUS, SYMPTOMS & COMORBIDITIES
    story.append(Paragraph("FUNCTIONAL & PERFORMANCE STATUS", section_header_style))
    func = [
        [lbl_val("KPS Score", patient_data.get('kps')), lbl_val("ECOG Score", patient_data.get('ecog'))],
        [lbl_val("Functional Category", patient_data.get('functional_category')), ""]
    ]
    story.append(Table(func, colWidths=[260, 260]))

    story.append(Paragraph("SYMPTOMS & COMORBIDITIES", sub_header_style))
    symp_val = ", ".join(patient_data.get('symptoms', [])) if patient_data.get('symptoms') else ""
    comorb_val = ", ".join(patient_data.get('comorbidities', [])) if patient_data.get('comorbidities') else ""
    symp_data = [
        [Paragraph(f"<b>Presenting Symptoms:</b> {symp_val}", styles['Normal']), Paragraph(f"<b>Comorbidities:</b> {comorb_val}", styles['Normal'])]
    ]
    story.append(Table(symp_data, colWidths=[260, 260]))

    # 6. VOLUMETRIC ANALYSIS (Imaging removed as requested)
    story.append(Paragraph("VOLUMETRIC ANALYSIS", section_header_style))
    metrics = patient_data.get('imaging_metrics', {})
    m_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Tumor Volume", f"{clean(metrics.get('tumor_vol'))} cm³" if clean(metrics.get('tumor_vol')) else "", "Active Core Volume", f"{clean(metrics.get('core_vol'))} cm³" if clean(metrics.get('core_vol')) else ""],
        ["Edema Volume", f"{clean(metrics.get('edema_vol'))} cm³" if clean(metrics.get('edema_vol')) else "", "Necrotic Fraction", f"{clean(metrics.get('necrotic_pct'))} %" if clean(metrics.get('necrotic_pct')) else ""],
        ["Tumor Location", clean(metrics.get('location')), "Sphericity Index", clean(metrics.get('sphericity'))]
    ]
    t_metrics = Table(m_data, colWidths=[130, 130, 130, 130])
    t_metrics.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTSIZE', (0,0), (-1,-1), 8), ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke)]))
    story.append(t_metrics)

    # 7. BIOMARKER STATUS
    story.append(Paragraph("BIOMARKER ANALYSIS", section_header_style))
    bio_data = [["Biomarker", "Status", "Clinical Meaning"]]
    biomarkers = patient_data.get('biomarkers', [])
    if biomarkers:
        bio_data.extend(biomarkers)
    else:
        bio_data.append(["", "", ""])
    t_bio = Table(bio_data, colWidths=[100, 120, 300])
    t_bio.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('FONTSIZE', (0,0), (-1,-1), 8)]))
    story.append(t_bio)

    # 8. AI RECOMMENDED TREATMENT PLAN
    story.append(Paragraph("AI-RECOMMENDED TREATMENT PLAN", section_header_style))
    story.append(Paragraph(patient_data.get('treatment_plan', ''), styles['Normal']))
    story.append(Paragraph("Rationale:", sub_header_style))
    for r in patient_data.get('rationale', []):
        story.append(Paragraph(f"• {r}", bullet_style))

    # 9. OUTCOME PROJECTIONS
    story.append(Paragraph("OUTCOME PROJECTIONS", section_header_style))
    outcomes = patient_data.get('outcomes', {})
    out_data = [
        [lbl_val("Overall Survival (Median)", outcomes.get('os')), lbl_val("Progression-Free Survival", outcomes.get('pfs'))],
        [lbl_val("Quality of Life Score", outcomes.get('qol')), lbl_val("Primary Toxicity Risk", outcomes.get('toxicity'))]
    ]
    story.append(Table(out_data, colWidths=[260, 260]))

    doc.build(story)

if __name__ == "__main__":
    pass

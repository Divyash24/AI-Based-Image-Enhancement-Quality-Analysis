from pathlib import Path
from datetime import datetime

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as ReportImage,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


REPORTS_DIR = Path("outputs/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TEMP_REPORT_IMG_DIR = Path("temp/report_images")
TEMP_REPORT_IMG_DIR.mkdir(parents=True, exist_ok=True)


def save_temp_image(image: Image.Image, filename: str) -> Path:
    path = TEMP_REPORT_IMG_DIR / filename
    image.convert("RGB").save(path, format="PNG")
    return path


def metrics_to_table_data(title: str, metrics: dict) -> list:
    return [
        [title, ""],
        ["Resolution", metrics.get("resolution", "-")],
        ["Blur Score", metrics.get("blur_score", "-")],
        ["Sharpness Score", metrics.get("sharpness_score", "-")],
        ["Noise Level", metrics.get("noise_level", "-")],
        ["Brightness", metrics.get("brightness", "-")],
        ["Contrast", metrics.get("contrast", "-")],
        ["Overall Quality Score", f'{metrics.get("overall_quality_score", "-")} %'],
    ]


def create_metrics_table(data: list) -> Table:
    table = Table(data, colWidths=[2.2 * inch, 2.2 * inch])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("SPAN", (0, 0), (-1, 0)),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table


def generate_pdf_report(
    input_image: Image.Image,
    output_image: Image.Image,
    input_metrics: dict,
    output_metrics: dict,
    method_used: str,
    issues: list[str],
    backend_used: str | None = None,
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"image_enhancement_report_{timestamp}.pdf"

    doc = SimpleDocTemplate(
        str(report_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = styles["BodyText"]

    story = []

    story.append(Paragraph("AI-Based Image Enhancement and Quality Analysis Report", title_style))
    story.append(Paragraph(f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Enhancement Summary", heading_style))
    story.append(Paragraph(f"<b>Method Used:</b> {method_used}", normal_style))

    if backend_used:
        story.append(Paragraph(f"<b>Backend Used:</b> {backend_used}", normal_style))

    input_score = input_metrics.get("overall_quality_score", 0)
    output_score = output_metrics.get("overall_quality_score", 0)
    improvement = round(output_score - input_score, 2)

    story.append(Paragraph(f"<b>Quality Improvement:</b> {improvement} %", normal_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Detected Issues", heading_style))

    if issues:
        issue_text = "<br/>".join([f"• {issue}" for issue in issues])
    else:
        issue_text = "No major quality issue detected."

    story.append(Paragraph(issue_text, normal_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Before / After Image Preview", heading_style))

    input_img_path = save_temp_image(input_image, f"input_{timestamp}.png")
    output_img_path = save_temp_image(output_image, f"output_{timestamp}.png")

    input_report_img = ReportImage(str(input_img_path), width=2.4 * inch, height=2.0 * inch)
    output_report_img = ReportImage(str(output_img_path), width=2.4 * inch, height=2.0 * inch)

    image_table = Table(
        [
            ["Input Image", "Enhanced Output"],
            [input_report_img, output_report_img],
        ],
        colWidths=[2.8 * inch, 2.8 * inch],
    )

    image_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(image_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Input Image Metrics", heading_style))
    story.append(create_metrics_table(metrics_to_table_data("Input Metrics", input_metrics)))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Enhanced Image Metrics", heading_style))
    story.append(create_metrics_table(metrics_to_table_data("Output Metrics", output_metrics)))

    doc.build(story)

    return report_path
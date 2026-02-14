from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

SITE_URL = "https://dentalhygienistsmatter.com"
QR_PATH = "design/flyer/qr-dhm.png"
OUT_PATH = "design/flyer/dentalhygienistsmatter-flyer-letter.pdf"


def wrap_text(c, text, x, y, max_width, leading=14, font_name="Helvetica", font_size=11):
    c.setFont(font_name, font_size)
    words = text.split()
    line = ""
    lines = []
    for w in words:
        trial = (line + " " + w).strip()
        if c.stringWidth(trial, font_name, font_size) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    return y


def main():
    W, H = letter
    c = canvas.Canvas(OUT_PATH, pagesize=letter)

    # BACKGROUND_STYLE: subtle pink geometric lines (to match reference)
    # Light blush wash
    c.setFillColor(colors.Color(0.98, 0.86, 0.88, alpha=0.20))
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Large curved arcs (circle outlines)
    c.setStrokeColor(colors.Color(0.95, 0.55, 0.62, alpha=0.30))
    c.setLineWidth(2)
    # Big circle partially off-page (bottom-left)
    c.circle(W * 0.05, H * 0.10, 8.5 * inch, stroke=1, fill=0)
    # Secondary circle partially off-page (top-right)
    c.setStrokeColor(colors.Color(0.95, 0.55, 0.62, alpha=0.22))
    c.setLineWidth(1.6)
    c.circle(W * 0.92, H * 0.95, 6.2 * inch, stroke=1, fill=0)

    # Thin guide lines (vertical/horizontal) + a couple diagonals
    c.setStrokeColor(colors.Color(0.95, 0.55, 0.62, alpha=0.22))
    c.setLineWidth(1)
    c.line(W * 0.70, 0, W * 0.70, H)
    c.line(0, H * 0.18, W, H * 0.18)

    c.setStrokeColor(colors.Color(0.95, 0.55, 0.62, alpha=0.18))
    c.setLineWidth(1)
    c.line(W * 0.52, 0, W * 0.86, H)
    c.line(W * 0.40, 0, W * 0.78, H)

    margin = 0.6 * inch
    inner_w = W - 2 * margin

    # Header background
    header_h = 1.65 * inch
    x0 = margin
    y0 = H - margin - header_h

    c.setFillColorRGB(0.17, 0.04, 0.35)  # deep purple-ish
    c.roundRect(x0, y0, inner_w, header_h, 14, fill=1, stroke=0)

    # Header text
    c.setFillColor(colors.whitesmoke)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(x0 + 0.28 * inch, y0 + header_h - 0.65 * inch, "Dental Hygienists Matter")

    c.setFont("Helvetica", 12.5)
    tagline = (
        "Protect standards of care in preventive dentistry. Learn what Virginia’s proposed “Route B” workforce bills "
        "would change—and how to take action."
    )
    # simple wrap
    ty = y0 + header_h - 0.98 * inch
    c.setFillColor(colors.Color(0.93, 0.95, 1.0, alpha=0.92))
    ty = wrap_text(c, tagline, x0 + 0.28 * inch, ty, inner_w - 0.56 * inch, leading=16, font_name="Helvetica", font_size=12.5)

    # Main cards area
    gap = 0.25 * inch
    card_y_top = y0 - gap

    left_w = inner_w * 0.60
    right_w = inner_w - left_w - gap

    card_h = 6.6 * inch

    # Left card
    lx = x0
    ly = card_y_top - card_h
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.Color(0.05, 0.06, 0.12, alpha=0.18))
    c.setLineWidth(1)
    c.roundRect(lx, ly, left_w, card_h, 14, fill=1, stroke=1)

    c.setFillColor(colors.Color(0.17, 0.04, 0.35))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(lx + 0.22 * inch, card_y_top - 0.45 * inch, "WHY THIS MATTERS")

    c.setFillColor(colors.Color(0.05, 0.06, 0.12))
    c.setFont("Helvetica", 11)

    bullet_x = lx + 0.25 * inch
    text_x = bullet_x + 0.18 * inch
    y = card_y_top - 0.75 * inch

    bullets = [
        "SB 178 / HB 970 are described as “Route B” workforce expansion.",
        "They create/expand a “preventive dental assistant” role authorized for limited scaling/polishing (often framed as “above-the-gumline” cleanings) under supervision.",
        "Concerns include incomplete care, patient confusion, and inconsistent training/competency verification.",
    ]

    for b in bullets:
        c.setFillColor(colors.Color(0.05, 0.06, 0.12))
        c.setFont("Helvetica", 11)
        c.drawString(bullet_x, y, "•")
        y = wrap_text(c, b, text_x, y, left_w - 0.5 * inch, leading=15, font_name="Helvetica", font_size=11) - 6

    # Pull quote box
    pq_h = 1.15 * inch
    pq_y = y - pq_h - 10
    c.setFillColor(colors.Color(0.65, 0.70, 0.99, alpha=0.22))
    c.setStrokeColor(colors.Color(0.65, 0.70, 0.99, alpha=0.5))
    c.roundRect(lx + 0.22 * inch, pq_y, left_w - 0.44 * inch, pq_h, 12, fill=1, stroke=1)

    c.setFillColor(colors.Color(0.05, 0.06, 0.12))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(lx + 0.35 * inch, pq_y + pq_h - 0.40 * inch, "Patients deserve clarity.")
    c.setFont("Helvetica", 11)
    wrap_text(
        c,
        "If roles expand, people must know who provided care, what was done, and what follow-up is recommended.",
        lx + 0.35 * inch,
        pq_y + pq_h - 0.65 * inch,
        left_w - 0.70 * inch,
        leading=14,
        font_name="Helvetica",
        font_size=11,
    )

    # CTA box (increase bottom padding)
    cta_h = 1.32 * inch
    cta_y = pq_y - cta_h - 14
    c.setFillColor(colors.Color(0.13, 0.77, 0.37, alpha=0.12))
    c.setStrokeColor(colors.Color(0.13, 0.77, 0.37, alpha=0.35))
    c.roundRect(lx + 0.22 * inch, cta_y, left_w - 0.44 * inch, cta_h, 12, fill=1, stroke=1)

    c.setFillColor(colors.Color(0.05, 0.06, 0.12))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(lx + 0.35 * inch, cta_y + cta_h - 0.38 * inch, "Take 60 seconds:")
    c.setFont("Helvetica", 11)
    wrap_text(
        c,
        "Scan the QR code to get a simple script and a pre-filled email you can send to the decision-makers who can still affect the outcome.",
        lx + 0.35 * inch,
        cta_y + cta_h - 0.62 * inch,
        left_w - 0.70 * inch,
        leading=14,
        font_name="Helvetica",
        font_size=11,
    )

    # Accent line
    ax = lx + 0.22 * inch
    ay = ly + 0.35 * inch
    aw = left_w - 0.44 * inch
    c.setStrokeColor(colors.Color(0.13, 0.77, 0.37))
    c.setLineWidth(6)
    c.line(ax, ay, ax + aw * 0.35, ay)
    c.setStrokeColor(colors.Color(0.65, 0.70, 0.99))
    c.line(ax + aw * 0.35, ay, ax + aw * 0.70, ay)
    c.setStrokeColor(colors.Color(0.98, 0.44, 0.52))
    c.line(ax + aw * 0.70, ay, ax + aw, ay)

    # Right card (QR)
    rx = lx + left_w + gap
    ry = ly
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.Color(0.05, 0.06, 0.12, alpha=0.18))
    c.setLineWidth(1)
    c.roundRect(rx, ry, right_w, card_h, 14, fill=1, stroke=1)

    # QR image
    qr_size = 2.55 * inch
    qr_x = rx + (right_w - qr_size) / 2
    qr_y = card_y_top - qr_size - 0.55 * inch
    img = ImageReader(QR_PATH)
    c.drawImage(img, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')

    c.setFillColor(colors.Color(0.05, 0.06, 0.12))
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(rx + right_w / 2, qr_y - 0.35 * inch, "Scan to learn & act")

    c.setFont("Helvetica", 9.5)
    c.setFillColor(colors.Color(0.05, 0.06, 0.12, alpha=0.75))
    c.drawCentredString(rx + right_w / 2, qr_y - 0.55 * inch, SITE_URL)

    # Footer line
    footer_y = margin - 0.10 * inch
    c.setFillColor(colors.Color(0.05, 0.06, 0.12, alpha=0.70))
    c.setFont("Helvetica", 9)

    c.showPage()
    c.save()
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

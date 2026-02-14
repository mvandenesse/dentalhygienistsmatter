from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

SITE_URL = "https://dentalhygienistsmatter.com"
QR_PATH = "design/flyer/qr-dhm.png"
OUT_HALF = "design/flyer/dentalhygienistsmatter-flyer-half-letter.pdf"  # 5.5x8.5
OUT_TWOUP = "design/flyer/dentalhygienistsmatter-flyer-two-up-letter.pdf"  # 2 per letter sheet


def wrap_text(c, text, x, y, max_width, leading=12, font_name="Helvetica", font_size=10):
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


def draw_flyer(c, x0, y0, w, h):
    """Draw a compact flyer into the rectangle x0,y0 with size w,h."""
    margin = 0.28 * inch

    # Header
    header_h = 1.10 * inch
    c.setFillColorRGB(0.17, 0.04, 0.35)
    c.roundRect(x0 + margin, y0 + h - margin - header_h, w - 2 * margin, header_h, 12, fill=1, stroke=0)

    c.setFillColor(colors.whitesmoke)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(x0 + margin + 0.20 * inch, y0 + h - margin - 0.55 * inch, "Dental Hygienists Matter")

    c.setFont("Helvetica", 10.5)
    c.setFillColor(colors.Color(0.93, 0.95, 1.0, alpha=0.92))
    tagline = "Protect standards of care in preventive dentistry. Learn what Virginia’s ‘Route B’ bills would change—and take action."
    wrap_text(c, tagline, x0 + margin + 0.20 * inch, y0 + h - margin - 0.82 * inch, w - 2 * margin - 0.40 * inch, leading=13, font_size=10.5)

    # Body cards
    gap = 0.18 * inch
    body_top = y0 + h - margin - header_h - gap
    body_h = h - (2 * margin + header_h + gap + 0.55 * inch)

    left_w = (w - 2 * margin) * 0.62
    right_w = (w - 2 * margin) - left_w - gap

    lx = x0 + margin
    ly = body_top - body_h
    rx = lx + left_w + gap
    ry = ly

    # Left card
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.Color(0.05, 0.06, 0.12, alpha=0.18))
    c.setLineWidth(1)
    c.roundRect(lx, ly, left_w, body_h, 12, fill=1, stroke=1)

    c.setFillColor(colors.Color(0.17, 0.04, 0.35))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(lx + 0.16 * inch, body_top - 0.30 * inch, "WHY THIS MATTERS")

    bullets = [
        "SB 178 / HB 970 expand ‘Route B’ workforce scope.",
        "Creates/expands a ‘preventive dental assistant’ role for limited scaling/polishing.",
        "Concerns: incomplete care, patient confusion, inconsistent competency safeguards.",
    ]

    y = body_top - 0.52 * inch
    bullet_x = lx + 0.18 * inch
    text_x = bullet_x + 0.16 * inch

    c.setFillColor(colors.Color(0.05, 0.06, 0.12))
    for b in bullets:
        c.setFont("Helvetica", 10)
        c.drawString(bullet_x, y, "•")
        y = wrap_text(c, b, text_x, y, left_w - 0.36 * inch, leading=12.5, font_size=10) - 3

    # CTA
    cta_h = 0.80 * inch
    cta_y = ly + 0.26 * inch
    c.setFillColor(colors.Color(0.13, 0.77, 0.37, alpha=0.12))
    c.setStrokeColor(colors.Color(0.13, 0.77, 0.37, alpha=0.35))
    c.roundRect(lx + 0.12 * inch, cta_y, left_w - 0.24 * inch, cta_h, 10, fill=1, stroke=1)
    c.setFillColor(colors.Color(0.05, 0.06, 0.12))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(lx + 0.22 * inch, cta_y + cta_h - 0.30 * inch, "Take 60 seconds: scan")
    c.setFont("Helvetica", 9.8)
    wrap_text(c, "Review how these bills can affect your health—then send a pre-filled message (edit name + ZIP).", lx + 0.22 * inch, cta_y + cta_h - 0.50 * inch, left_w - 0.44 * inch, leading=12, font_size=9.8)

    # Right card (QR)
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.Color(0.05, 0.06, 0.12, alpha=0.18))
    c.setLineWidth(1)
    c.roundRect(rx, ry, right_w, body_h, 12, fill=1, stroke=1)

    qr_size = min(2.05 * inch, right_w - 0.40 * inch)
    qr_x = rx + (right_w - qr_size) / 2
    qr_y = body_top - qr_size - 0.45 * inch
    img = ImageReader(QR_PATH)
    c.drawImage(img, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')

    c.setFillColor(colors.Color(0.05, 0.06, 0.12))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(rx + right_w / 2, qr_y - 0.25 * inch, "Scan")
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.Color(0.05, 0.06, 0.12, alpha=0.75))
    c.drawCentredString(rx + right_w / 2, qr_y - 0.42 * inch, SITE_URL)

    # Footer
    c.setFillColor(colors.Color(0.05, 0.06, 0.12, alpha=0.65))
    c.setFont("Helvetica", 7.8)
    c.drawString(x0 + margin, y0 + 0.18 * inch, "Informational/advocacy; not medical or legal advice. Please be respectful—no harassment or threats.")


def make_half_letter():
    W = 5.5 * inch
    H = 8.5 * inch
    c = canvas.Canvas(OUT_HALF, pagesize=(W, H))
    draw_flyer(c, 0, 0, W, H)
    c.showPage()
    c.save()


def make_two_up_letter():
    # Letter portrait 8.5x11 with two half-letter flyers stacked
    W = 8.5 * inch
    H = 11 * inch
    c = canvas.Canvas(OUT_TWOUP, pagesize=(W, H))

    half_h = H / 2
    draw_flyer(c, 0, half_h, W, half_h)  # top
    draw_flyer(c, 0, 0, W, half_h)       # bottom

    # cut line
    c.setStrokeColor(colors.Color(0, 0, 0, alpha=0.25))
    c.setLineWidth(1)
    c.setDash(3, 3)
    c.line(0.5 * inch, half_h, W - 0.5 * inch, half_h)

    c.showPage()
    c.save()


if __name__ == "__main__":
    make_half_letter()
    make_two_up_letter()
    print("Wrote:", OUT_HALF)
    print("Wrote:", OUT_TWOUP)

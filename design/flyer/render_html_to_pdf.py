from pathlib import Path
from weasyprint import HTML

IN_HTML = Path('design/flyer/flyer-letter.html')
OUT_PDF = Path('design/flyer/flyer-letter-from-html.pdf')


def main():
    html = IN_HTML.read_text('utf-8')
    # Ensure relative assets resolve from the HTML file location
    HTML(string=html, base_url=str(IN_HTML.parent.resolve())).write_pdf(str(OUT_PDF))
    print('Wrote', OUT_PDF)


if __name__ == '__main__':
    main()

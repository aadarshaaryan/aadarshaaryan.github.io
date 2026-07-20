from flask import Blueprint, render_template, request, Response, redirect, url_for
from app.models import EventResult, db
import qrcode
import io
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import os
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

# Register the fonts
pdfmetrics.registerFont(TTFont('Cinzel', os.path.join(FONT_DIR, 'Cinzel-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Afacad-SemiBold', os.path.join(FONT_DIR, 'AfacadFlux-SemiBold.ttf')))
pdfmetrics.registerFont(TTFont('Afacad-Bold', os.path.join(FONT_DIR, 'AfacadFlux-Bold.ttf')))

certificates_bp = Blueprint("certificates", __name__)

@certificates_bp.route('/verify', methods=['GET', 'POST'])
@certificates_bp.route('/verify/', methods=['GET', 'POST'])
@certificates_bp.route('/verify/<string:cert_code>', methods=['GET', 'POST'])
def verify_certificate(cert_code=None):
    if request.method == 'POST':
        form_code = request.form.get('cert_code')
        if form_code:
            return redirect(url_for('certificates.verify_certificate', cert_code=form_code.strip().upper()))
        return redirect(url_for('certificates.verify_certificate'))

    search_code = cert_code.strip() if cert_code else None
    result = EventResult.query.filter_by(certificate_code=search_code.upper()).first() if search_code else None

    return render_template('certificates/verification.html', result=result, cert_code=search_code or "")

def generate_certificate_pdf(result):
    # Setup Canvas
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(842, 595))
    
    # 1. QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(f"http://10.47.216.205:5000/verify/{result.certificate_code}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_bytes = io.BytesIO()
    qr_img.save(qr_bytes, format='PNG')
    qr_bytes.seek(0)
    can.drawImage(ImageReader(qr_bytes), 620.13, 115.71, width=80, height=80)
    
    # 2. Name (Centered with Dynamic Scaling)
    name_text = str(result.participant_name)
    name_font, max_size, min_size, max_width = "Cinzel", 46, 20, 700
    current_size = max_size
    can.setFont(name_font, current_size)
    
    # Loop to shrink font if text exceeds max_width
    while can.stringWidth(name_text, name_font, current_size) > max_width and current_size > min_size:
        current_size -= 1
        can.setFont(name_font, current_size)
        
    text_width = can.stringWidth(name_text, name_font, current_size)
    can.drawString(420.5 - (text_width / 2), 297.27, name_text) 

    # 3. Dynamic Recognition Sentence
    can.setFont("Afacad-SemiBold", 14.43)
    if result.position and 1 <= result.position <= 3:
        rank_map = {1: "1st", 2: "2nd", 3: "3rd"}
        rank_text = f"{rank_map.get(result.position)} Position"
        prefix, suffix = "In recognition of securing ", " in"
        
        p_w = can.stringWidth(prefix, "Afacad-SemiBold", 14.43)
        r_w = can.stringWidth(rank_text, "Afacad-Bold", 14.43)
        s_w = can.stringWidth(suffix, "Afacad-SemiBold", 14.43)
        start_x = 421 - ((p_w + r_w + s_w) / 2)
        
        can.drawString(start_x, 252.04, prefix)
        can.saveState()
        can.setFillColor(HexColor('#E19E4F'))
        can.setFont("Afacad-Bold", 14.43)
        can.drawString(start_x + p_w, 252.04, rank_text)
        can.restoreState()
        can.drawString(start_x + p_w + r_w, 252.04, suffix)
    else:
        text = "In recognition of your participation in"
        can.drawString(421 - (can.stringWidth(text, "Afacad-SemiBold", 14.43) / 2), 252.04, text)

    # 4. Event Name
    can.setFont("Afacad-SemiBold", 26)
    can.setFillColor(HexColor('#000000'))
    event_text = str(result.event.title)
    # Using 8% line spacing as requested (26 * 1.08)
    can.drawString(420.5 - (can.stringWidth(event_text, "Afacad-SemiBold", 26) / 2), 252.04 - (26 * 1.08), event_text) 

    # 5. Footer Metadata
    can.setFont("Afacad-Bold", 11.54)
    can.setFillColor(HexColor('#FFFFFF'))
    # Spacing metadata at 10% (11.54 * 1.10)
    can.drawString(224, 32, result.submitted_at.strftime('%Y-%m-%d') if hasattr(result, 'submitted_at') else "N/A")
    can.drawString(363.48, 32, str(result.event.category))
    can.drawString(542.92, 32, str(result.certificate_code))
    
    can.save()
    packet.seek(0)
    
    # 6. Merge with Template
    template_path = os.path.join(BASE_DIR, 'static', 'certificate_template.pdf')
    with open(template_path, "rb") as f:
        output = PdfWriter()
        page = PdfReader(f).pages[0]
        page.merge_page(PdfReader(packet).pages[0])
        output.add_page(page)
        final_pdf = io.BytesIO()
        output.write(final_pdf)
        return final_pdf.getvalue()

@certificates_bp.route('/download-my-certificate/<string:cert_code>')
def download_my_certificate(cert_code):
    result = EventResult.query.filter_by(certificate_code=cert_code).first_or_404()
    return Response(generate_certificate_pdf(result), mimetype="application/pdf", 
                    headers={"Content-Disposition": f"attachment;filename=Certificate_{result.participant_name}.pdf"})
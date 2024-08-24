from flask import Flask, render_template, request, send_file
import fitz  
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import base64
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file:
        
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")

        # novo PDF em memória usando ReportLab
        output_pdf = io.BytesIO()
        pdf_canvas = canvas.Canvas(output_pdf)

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text("text")

            # o texto foi extraído; se não, tenta OCR
            if not text.strip():
                pix = page.get_pixmap()  
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)  

            # texto extraído em Base64
            encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')

            # texto para tornar copiável no novo PDF
            decoded_text = base64.b64decode(encoded_text).decode('utf-8')

           
            width, height = page.rect.width, page.rect.height
            pdf_canvas.setPageSize((width, height))

        
            pdf_canvas.setFont("Helvetica", 12)
            text_object = pdf_canvas.beginText(10, height - 20)
            text_object.textLines(decoded_text)
            pdf_canvas.drawText(text_object)

            
            if page_num < len(pdf_document) - 1:
                pdf_canvas.showPage()

        # Finalizar o PDF
        pdf_canvas.save()
        output_pdf.seek(0)

        return send_file(output_pdf, as_attachment=True, download_name="new_file.pdf")

if __name__ == '__main__':
    app.run(debug=True)

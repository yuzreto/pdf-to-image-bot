from flask import Flask, request, jsonify, send_file
from pdf2image import convert_from_bytes
import io
import zipfile

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_images():
    if 'file' not in request.files:
        return jsonify({"error": "No file found"}), 400
    
    pdf_file = request.files['file']
    try:
        images = convert_from_bytes(pdf_file.read(), dpi=150)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for i, image in enumerate(images):
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                zip_file.writestr(f'page_{i+1}.png', img_buffer.read())
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

from flask import Flask, request, jsonify, send_file
from pypdf import PdfMerger
import img2pdf
import io

app = Flask(__name__)

@app.route('/merge_all', methods=['POST'])
def merge_all_files():
    # --- 【修正】連番（files[0], files[1]...）で届くファイルをすべて集める ---
    files = []
    index = 0
    while True:
        file_key = f'files[{index}]'
        if file_key in request.files:
            files.append(request.files[file_key])
            index += 1
        else:
            break

    # 1つもファイルが見つからなかった場合のエラー
    if not files:
        return jsonify({"error": "ファイルが送信されていません"}), 400
    
    merger = PdfMerger()
    temp_buffers = []

    try:
        for file in files:
            filename = file.filename.lower()
            file_bytes = file.read()
            
            # ① 画像（PNG / JPG）の場合
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                pdf_data = img2pdf.convert(file_bytes)
                pdf_buf = io.BytesIO(pdf_data)
                merger.append(pdf_buf)
                temp_buffers.append(pdf_buf)
                
            # ② PDFの場合
            elif filename.endswith('.pdf'):
                pdf_buf = io.BytesIO(file_bytes)
                merger.append(pdf_buf)
                temp_buffers.append(pdf_buf)

        output_pdf_buffer = io.BytesIO()
        merger.write(output_pdf_buffer)
        output_pdf_buffer.seek(0)
        merger.close()

        for buf in temp_buffers:
            buf.close()

        return send_file(
            output_pdf_buffer, 
            mimetype='application/pdf', 
            as_attachment=True, 
            download_name='merged.pdf'
        )

    except Exception as e:
        merger.close()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

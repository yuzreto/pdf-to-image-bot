from flask import Flask, request, jsonify, send_file
from pdf2image import convert_from_bytes
from pypdf import PdfMerger, PdfReader
import img2pdf
import io

app = Flask(__name__)

@app.route('/merge_all', methods=['POST'])
def merge_all_files():
    # GASから送られてきた複数のファイルを順番通りに受け取る
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "ファイルが送信されていません"}), 400
    
    merger = PdfMerger()
    temp_buffers = [] # 一時的なデータを溜める箱

    try:
        for file in files:
            filename = file.filename.lower()
            file_bytes = file.read()
            
            # --- ① 元が画像（PNG / JPG）の場合 ---
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                # img2pdf を使うと、画像の縦横サイズ・比率を100%維持した「余白ゼロのPDF」が一瞬で作れます
                pdf_data = img2pdf.convert(file_bytes)
                pdf_buf = io.BytesIO(pdf_data)
                merger.append(pdf_buf)
                temp_buffers.append(pdf_buf)
                
            # --- ② 元がPDFの場合 ---
            elif filename.endswith('.pdf'):
                # ネット印刷のPDFであっても、文字化けやレイアウト崩れ、見切れを絶対に起こさず、
                # 1ページずつの縦・横サイズを完全に保ったまま、バイナリレベルでそのまま結合します
                pdf_buf = io.BytesIO(file_bytes)
                merger.append(pdf_buf)
                temp_buffers.append(pdf_buf)

        # すべてを合体した1つのPDFデータを作成
        output_pdf_buffer = io.BytesIO()
        merger.write(output_pdf_buffer)
        output_pdf_buffer.seek(0)
        merger.close()

        # 使い終わった一時バッファを閉じる
        for buf in temp_buffers:
            buf.close()

        # 完成した完璧なPDFをGASに送り返す
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

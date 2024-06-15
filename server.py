from flask import Flask, request, send_file, jsonify, redirect, url_for
from flask_cors import CORS
from openpyxl import Workbook
import os

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def adjust_column_width(sheet):
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except TypeError:
                pass
        adjusted_width = max_length + 2
        sheet.column_dimensions[column].width = adjusted_width

@app.route('/save_report', methods=['POST', 'GET'])
def save_report():
    data = request.json.get('data', [])

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Criar um novo workbook do Excel
    wb = Workbook()
    ws = wb.active

    # Definir os cabeçalhos das colunas
    ws.append(["Descrição", "EAN", "Quantidade", "Validade"])

    # Preencher o workbook com os dados recebidos
    for item in data:
        ws.append([item['descrição'], item['ean'], item['quantidade'], item['validade']])

    # Ajustar a largura das colunas
    adjust_column_width(ws)

    # Garantir que o diretório de uploads existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Salvar o workbook como um arquivo temporário
    relatorio_path = os.path.join(UPLOAD_FOLDER, 'relatorio.xlsx')
    wb.save(relatorio_path)

    # Retornar o link do arquivo como uma resposta de redirecionamento
    return redirect(url_for('download', filename='relatorio.xlsx'))

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

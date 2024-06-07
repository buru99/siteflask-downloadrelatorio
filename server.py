from flask import Flask, request, send_file, jsonify, redirect
from openpyxl import Workbook
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/save_report', methods=['POST'])
def save_report():
    data = request.json.get('data', [])

    # Criar um novo workbook do Excel
    wb = Workbook()
    ws = wb.active

    # Definir os cabeçalhos das colunas
    ws.append(["Descrição", "EAN", "Quantidade", "Validade"])

    # Preencher o workbook com os dados recebidos
    for item in data:
        ws.append([item['descrição'], item['ean'], item['quantidade'], item['validade']])

    # Salvar o workbook como um arquivo temporário
    relatorio_path = 'relatorio.xlsx'
    wb.save(relatorio_path)

    # Retornar o link do arquivo como uma resposta de redirecionamento
    return redirect(f'/download/{relatorio_path}')


@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

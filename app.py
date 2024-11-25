from flask import Flask, request, render_template, send_file
import openai
import fitz  # PyMuPDF for PDF handling
import os
from dotenv import load_dotenv

load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)


def pdf_to_text(file_path):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Hata: {str(e)}"


def analyze_project(project_text):
    try:
        prompt = f"Projenin güçlü ve zayıf yönlerini proje rehberlerini esas alarak özetle.\n\n{project_text}"
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000
        )
        
        return response.choices[0].message['content']
    except Exception as e:
        return f"Hata: {str(e)}"


def save_result_as_text(content):
    try:
        result_text_path = os.path.join(os.getcwd(), "result.txt")
        with open(result_text_path, "w", encoding="utf-8") as f:
            f.write(content)
        return result_text_path
    except Exception as e:
        return f"Hata: {str(e)}"


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'project_pdf' not in request.files:
            return "Dosya yüklenmedi", 400
        
        project_pdf = request.files['project_pdf']
        

        project_path = os.path.join(os.getcwd(), "temp_project.pdf")
        project_pdf.save(project_path)
        project_text = pdf_to_text(project_path)
        

        result_text = analyze_project(project_text)
        

        result_text_path = save_result_as_text(result_text)
        

        os.remove(project_path)
        

        return f'''
        <p>Analiz tamamlandı! Aşağıdaki bağlantıdan sonucu indirebilirsiniz:</p>
        <a href="/download" style="color: white; text-decoration: underline;">Sonucu İndir</a>
        '''
    except Exception as e:
        return f"Hata: {str(e)}", 500


@app.route('/download')
def download_file():
    try:
        result_file_path = os.path.join(os.getcwd(), "result.txt")
        return send_file(result_file_path, as_attachment=True)
    except Exception as e:
        return f"Dosya indirilemedi: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

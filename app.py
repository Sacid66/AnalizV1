from flask import Flask, request, render_template, send_file
import openai
import fitz  # PyMuPDF for PDF handling
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# OpenAI API anahtarını .env'den al
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Sistemdeki 'puantaj.pdf' dosyasının yolunu belirtin
PUNTUATION_FILE_PATH = "puantaj.pdf"

# PDF dosyasını metne dönüştüren yardımcı fonksiyon
def pdf_to_text(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# OpenAI API'ye projeyi ve puantaj dökümanını gönderen fonksiyon
def analyze_project_with_punctuation(project_text, punctuation_text):
    prompt = f"Dosyadaki projeyi  puantaj tablosuna göre güçlü ve zayıf yönleri ile 'detaylı bir şekilde' açıklamalı olarak puanla. Puan kırılacak yerde puanı kır, çekinme yani çok düşük puanlar da verebilirsin, gerçekçi olsun sonuç.\n\nProje:\n{project_text}\n\nPuanlama Kriterleri:\n{punctuation_text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000
    )
    
    return response.choices[0].message['content']

# Sonucu metin dosyası olarak kaydetme fonksiyonu
def save_result_as_text(content):
    result_text_path = "result.txt"
    with open(result_text_path, "w", encoding="utf-8") as f:
        f.write(content)
    return result_text_path

# Ana sayfa - Dosya yükleme formu
@app.route('/')
def index():
    return render_template("index.html")

# PDF yükleme ve analiz işlemi
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'project_pdf' not in request.files:
        return "Dosya yüklenmedi", 400
    
    project_pdf = request.files['project_pdf']
    
    # Proje dosyasını geçici bir yere kaydet ve metne çevir
    project_path = "temp_project.pdf"
    project_pdf.save(project_path)
    project_text = pdf_to_text(project_path)
    
    # Puantaj dökümanını yükle ve metne çevir
    punctuation_text = pdf_to_text(PUNTUATION_FILE_PATH)
    
    # OpenAI API'ye gönder ve yanıt al
    result_text = analyze_project_with_punctuation(project_text, punctuation_text)
    
    # Sonucu metin dosyası olarak kaydet
    result_text_path = save_result_as_text(result_text)
    
    # Geçici proje dosyasını sil
    os.remove(project_path)
    
    # İndirilebilir link sağla
    return f'''
    <p>Analiz tamamlandı! Aşağıdaki bağlantıdan sonucu indirebilirsiniz.</p>
    <a href="/download" style="color: white; text-decoration: underline;">Sonucu İndir</a>
    '''

# Sonuç dosyasını indirme
@app.route('/download')
def download_file():
    return send_file("result.txt", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

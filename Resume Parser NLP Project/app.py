from flask import Flask, render_template, request
import pdfplumber

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', message="")

@app.route('/upload', methods=['POST'])
def upload_resume():
    keywords = request.form.get('keywords', '').split(',')
    num_resumes_processed = 0

    for uploaded_file in request.files.getlist('resumes'):
        if uploaded_file.filename:
            if check_keywords(uploaded_file, keywords):
                save_to_folder(uploaded_file, "successful_resumes")
            else:
                save_to_folder(uploaded_file, "failed_resumes")
            num_resumes_processed += 1

    if num_resumes_processed > 0:
        message = f"{num_resumes_processed} resume(s) processed successfully!"
    else:
        message = "No resumes uploaded."

    return render_template('index.html', message=message)

def check_keywords(resume, keywords):
    content = extract_text_from_pdf(resume)
    return any(keyword.strip().lower() in content.lower() for keyword in keywords)

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def save_to_folder(resume, folder):
    destination = f"./{folder}/{resume.filename}"
    resume.save(destination)

if __name__ == '__main__':
    app.run(debug=True)

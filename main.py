from flask import Flask, render_template, request
import os
from ocr_module import extract_text  # your existing OCR code

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    filename = None

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Call your existing OCR function
            result = extract_text(filepath)

    return render_template('index.html', result=result, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, send_file
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import os
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🌈 NEON UI
@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Neon File Tool</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial;
                background: black;
                color: #0ff;
                text-align: center;
            }
            h1 {
                text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
            }
            .box {
                border: 1px solid #0ff;
                padding: 15px;
                margin: 15px auto;
                width: 90%;
                max-width: 400px;
                border-radius: 10px;
                box-shadow: 0 0 15px #0ff;
            }
            button {
                background: black;
                color: #0ff;
                border: 1px solid #0ff;
                padding: 10px;
                width: 100%;
                margin-top: 5px;
            }
            input, select {
                width: 90%;
                margin: 5px;
                background: black;
                color: #0ff;
                border: 1px solid #0ff;
            }
        </style>
    </head>
    <body>

    <h1>⚡ Neon File Converter ⚡</h1>

    <div class="box">
        <h3>Images → ONE PDF</h3>
        <form action="/multi/image-to-one-pdf" method="post" enctype="multipart/form-data">
            <input type="file" name="files" multiple><br>
            <button>Create PDF</button>
        </form>
    </div>

    <div class="box">
        <h3>Merge PDFs</h3>
        <form action="/multi/pdf-merge" method="post" enctype="multipart/form-data">
            <input type="file" name="files" multiple><br>
            <button>Merge PDFs</button>
        </form>
    </div>

    <div class="box">
        <h3>PDF → Images (ZIP)</h3>
        <form action="/multi/pdf-to-images" method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <button>Convert</button>
        </form>
    </div>

    </body>
    </html>
    '''

# ---------------- MULTI IMAGE → ONE PDF ----------------
@app.route('/multi/image-to-one-pdf', methods=['POST'])
def images_to_pdf():
    files = request.files.getlist('files')

    images = []
    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        img = Image.open(path).convert('RGB')
        images.append(img)

    output_path = os.path.join(UPLOAD_FOLDER, "combined.pdf")

    images[0].save(output_path, save_all=True, append_images=images[1:])

    return send_file(output_path, as_attachment=True)

# ---------------- MERGE PDF ----------------
@app.route('/multi/pdf-merge', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('files')
    writer = PdfWriter()

    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    output_path = os.path.join(UPLOAD_FOLDER, "merged.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    return send_file(output_path, as_attachment=True)

# ---------------- PDF → IMAGES ZIP ----------------
@app.route('/multi/pdf-to-images', methods=['POST'])
def pdf_to_images():
    from pdf2image import convert_from_path

    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    images = convert_from_path(path)

    zip_path = os.path.join(UPLOAD_FOLDER, "pdf_images.zip")

    with zipfile.ZipFile(zip_path, 'w') as z:
        for i, img in enumerate(images):
            img_path = os.path.join(UPLOAD_FOLDER, f"page_{i}.jpg")
            img.save(img_path)
            z.write(img_path, os.path.basename(img_path))

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

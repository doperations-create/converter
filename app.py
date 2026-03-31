from flask import Flask, request, send_file
from PIL import Image
from docx import Document
from PyPDF2 import PdfReader, PdfMerger, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os, zipfile, time

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def unique_path(filename):
    name, ext = os.path.splitext(filename)
    return os.path.join(UPLOAD_FOLDER, f"{name}_{int(time.time()*1000)}{ext}")

# 🌈 HOME
@app.route('/')
def home():
    return '''
    <html>
    <head>
    <style>
    body {font-family: Arial; background: linear-gradient(135deg,#ff7e5f,#feb47b); text-align:center; color:white;}
    .box {background:white; color:black; padding:15px; margin:10px auto; width:90%; max-width:400px; border-radius:15px;}
    button {background:#ff7e5f; color:white; border:none; padding:10px; width:100%;}
    input,select {margin:5px; width:90%;}
    </style>
    </head>
    <body>

    <h1>🔥 File Converter Tool</h1>

    <!-- IMAGE COMPRESS -->
    <div class="box">
    <h3>Compress Image (KB)</h3>
    <form action="/compress/image" method="post" enctype="multipart/form-data">
    <input type="file" name="file" multiple><br>
    Target KB: <input type="number" name="size_kb" required><br>
    <button>Compress</button>
    </form></div>

    <!-- PDF COMPRESS -->
    <div class="box">
    <h3>Compress PDF (KB)</h3>
    <form action="/compress/pdf" method="post" enctype="multipart/form-data">
    <input type="file" name="file" multiple><br>
    Target KB: <input type="number" name="size_kb" required><br>
    <button>Compress</button>
    </form></div>

    <!-- IMAGE CONVERT -->
    <div class="box">
    <h3>Convert Image</h3>
    <form action="/convert/image" method="post" enctype="multipart/form-data">
    <input type="file" name="file" multiple><br>
    <select name="format"><option>png</option><option>webp</option></select>
    <button>Convert</button>
    </form></div>

    <!-- IMAGE TO PDF -->
    <div class="box">
    <h3>Image → PDF</h3>
    <form action="/convert/image-to-pdf" method="post" enctype="multipart/form-data">
    <input type="file" name="file" multiple>
    <button>Convert</button>
    </form></div>

    <!-- WORD TO PDF -->
    <div class="box">
    <h3>Word → PDF</h3>
    <form action="/convert/word-to-pdf" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <button>Convert</button>
    </form></div>

    <!-- RESIZE -->
    <div class="box">
    <h3>Resize Image</h3>
    <form action="/resize/image" method="post" enctype="multipart/form-data">
    <input type="file" name="file"><br>
    Width:<input type="number" name="width">
    Height:<input type="number" name="height">
    <button>Resize</button>
    </form></div>

    <!-- PDF MERGE -->
    <div class="box">
    <h3>PDF Merge</h3>
    <form action="/merge/pdf" method="post" enctype="multipart/form-data">
    <input type="file" name="file" multiple>
    <button>Merge</button>
    </form></div>

    <!-- PDF SPLIT -->
    <div class="box">
    <h3>PDF Split</h3>
    <form action="/split/pdf" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <button>Split</button>
    </form></div>

    </body></html>
    '''

# ⭐ IMAGE COMPRESS (KB)
@app.route('/compress/image', methods=['POST'])
def compress_image():
    files = request.files.getlist('file')
    target_kb = int(request.form.get('size_kb'))
    outputs = []

    for file in files:
        path = unique_path(file.filename)
        file.save(path)

        out = path + "_compressed.jpg"
        img = Image.open(path).convert("RGB")

        quality = 95
        while quality > 5:
            img.save(out, "JPEG", quality=quality)
            if os.path.getsize(out)/1024 <= target_kb:
                break
            quality -= 5

        outputs.append(out)

    return send_file(outputs[0], as_attachment=True)

# ⭐ PDF COMPRESS (basic)
@app.route('/compress/pdf', methods=['POST'])
def compress_pdf():
    files = request.files.getlist('file')
    outputs = []

    for file in files:
        path = unique_path(file.filename)
        file.save(path)

        reader = PdfReader(path)
        writer = PdfWriter()

        for p in reader.pages:
            writer.add_page(p)

        out = path + "_compressed.pdf"
        with open(out, "wb") as f:
            writer.write(f)

        outputs.append(out)

    return send_file(outputs[0], as_attachment=True)

# IMAGE CONVERT
@app.route('/convert/image', methods=['POST'])
def convert_image():
    file = request.files['file']
    fmt = request.form.get('format')

    path = unique_path(file.filename)
    file.save(path)

    out = path.rsplit('.',1)[0]+"."+fmt
    Image.open(path).save(out)

    return send_file(out, as_attachment=True)

# IMAGE → PDF
@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf():
    file = request.files['file']
    path = unique_path(file.filename)
    file.save(path)

    out = path+".pdf"
    Image.open(path).convert("RGB").save(out)

    return send_file(out, as_attachment=True)

# WORD → PDF
@app.route('/convert/word-to-pdf', methods=['POST'])
def word_to_pdf():
    file = request.files['file']
    path = unique_path(file.filename)
    file.save(path)

    doc = Document(path)
    out = path+".pdf"
    c = canvas.Canvas(out, pagesize=letter)

    y = 750
    for para in doc.paragraphs:
        c.drawString(40, y, para.text)
        y -= 20

    c.save()
    return send_file(out, as_attachment=True)

# RESIZE
@app.route('/resize/image', methods=['POST'])
def resize_image():
    file = request.files['file']
    w = int(request.form.get('width'))
    h = int(request.form.get('height'))

    path = unique_path(file.filename)
    file.save(path)

    out = path+"_resized.jpg"
    Image.open(path).resize((w,h)).save(out)

    return send_file(out, as_attachment=True)

# PDF MERGE
@app.route('/merge/pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('file')
    merger = PdfMerger()

    for f in files:
        path = unique_path(f.filename)
        f.save(path)
        merger.append(path)

    out = os.path.join(UPLOAD_FOLDER, "merged.pdf")
    merger.write(out)
    merger.close()

    return send_file(out, as_attachment=True)

# PDF SPLIT
@app.route('/split/pdf', methods=['POST'])
def split_pdf():
    file = request.files['file']
    path = unique_path(file.filename)
    file.save(path)

    reader = PdfReader(path)
    zip_path = os.path.join(UPLOAD_FOLDER, "split.zip")

    with zipfile.ZipFile(zip_path, 'w') as z:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            out = os.path.join(UPLOAD_FOLDER, f"page_{i}.pdf")
            with open(out, "wb") as f:
                writer.write(f)

            z.write(out, f"page_{i}.pdf")

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

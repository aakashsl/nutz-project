from flask import Flask, render_template, send_file
import requests
from io import BytesIO
import zipfile
app = Flask(__name__)


IMAGE_URLS = [
    "https://www.nediveil.in/static/images/logo-design.png",
    "https://example.com/another-image.png"  # Add more URLs as needed
]
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/download')
def download_images():
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for idx, url in enumerate(IMAGE_URLS):
            response = requests.get(url)
            image = BytesIO(response.content)
            zf.writestr(f'image_{idx + 1}.png', image.getvalue())
    memory_file.seek(0)
    return send_file(memory_file, as_attachment=True, download_name='images.zip')

if __name__ == '__main__':
    app.run(debug=True)
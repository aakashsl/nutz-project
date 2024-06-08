from PIL import Image
from paddleocr import PaddleOCR
import os
import sqlite3


def zoom_at(img, x, y, zoom):
    w, h = img.size
    zoom2 = zoom * 2
    cropped_img = img.crop((x - w / zoom2, y - h / zoom2, x + w / zoom2, y + h / zoom2))
    return cropped_img.resize((w, h), Image.LANCZOS)


def resize_images(input_folder, output_folder, size):
    for filename in os.listdir(input_folder):
        os.makedirs(output_folder, exist_ok=True)
        try:
            with Image.open(os.path.join(input_folder, filename)) as img:
                img_resized = img.resize(size)
                img_resized = zoom_at(img_resized, x=4000, y=5000, zoom=1)
                img_resized.save(os.path.join(output_folder, filename))

        except Exception as e:
            print(f"Failed to resize {filename}: {e}")


def image_text(ocr_model):
    img_name = []
    img_name_dict = {}
    # Example usage:
    input_folder = "inputdata/"
    output_folder = "outputdata/"
    resize_images(input_folder, output_folder, size=(8000, 8000))
    for file in os.listdir(output_folder):
        img_path = os.path.join(output_folder, file)
        # Run the ocr method on the ocr model
        result = ocr_model.ocr(img_path)
        
        if None != result[0]:
            for data in result:
                for i in data:
                    img_name.append(i[1][0])
            img_name_dict[file] = img_name
            img_name = []
    return img_name_dict


def create_table(dict_data):
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    key = []
    values = []
    for k, v in dict_data.items():
        key.append(k)
        for data in v:
            values.append((k, data))
    c.execute("CREATE TABLE IF NOT EXISTS image1 (key INTEGER PRIMARY KEY AUTOINCREMENT, image_text TEXT);")
    c.execute("""
        CREATE TABLE IF NOT EXISTS value1 (
            id INTEGER PRIMARY KEY,
            image_id INTEGER NOT NULL,
            image_data TEXT
        )
    """)
    keys_tuple = tuple(key)  # Convert 'key' to a tuple
    for key in keys_tuple:
        # Execute the query
        c.execute("INSERT INTO image1 (image_text) VALUES (?)", (key,))
    values_tuple = tuple(values)
    for value, value2 in values_tuple:
        c.execute("INSERT INTO value1 (image_id, image_data) VALUES (?, ?)", (value, value2))
    conn.commit()
    conn.close()


def model_train():
    ocr_model = PaddleOCR(lang='en')
    img_dict = image_text(ocr_model)
    create_table(img_dict)


def check_with_data(input_data):
    img_list = []
    conn = sqlite3.connect("my_database.db")
    data_image = conn.execute(
        "SELECT value1.image_id FROM value1 WHERE value1.image_data = {}".format(input_data))
    for data in data_image:
        for img in data:
            img_list.append(img)
    return img_list


from flask import Flask, render_template, request,url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    input_data = request.form['bib_number']
    conn = sqlite3.connect('my_database.db')
    com = conn.cursor()
    com.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image1'")
    result = com.fetchall()

    images = []
    if input_data:
        if len(result) == 1:
            data = check_with_data(input_data)
            if not data:
                message = "No image is found"
            else:
                images = ["inputdata/{}".format(img) for img in data]
                
                message = ""
        else:
            message = "No data in database"
        conn.close()
    else:
        message = "Please enter a BIB number"

    return render_template('index.html', images=images, message=message)

if __name__ == '__main__':
    app.run(debug=True)
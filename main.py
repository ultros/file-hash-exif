import hashlib
import sys
import sqlite3
import os
from PIL import Image
from PIL.ExifTags import TAGS


def calculate_hash(fn):
    buffer_size = 65536
    sha256 = hashlib.sha256()
    # md5 = hashlib.sha256()

    with open(fn, 'rb') as file:
        while True:
            data = file.read(buffer_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def create_db():
    connection = sqlite3.connect(database_name)
    cur = connection.cursor()
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='images'")

    if cur.fetchone()[0] == 1:
        print('Table exists.')
    else:
        cur.execute("CREATE TABLE images (id, path, sha256, model, make, datetime)")

    connection.close()


def insert_rows(directory):
    connection = sqlite3.connect(database_name)
    cur = connection.cursor()
    i = 0
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        name, ext = os.path.splitext(f)
        # magic number check for incorrect file extension
        if ext == '.JPG' or ext == '.jpg' or ext == '.jpeg' or ext == '.JPEG':
            working_image = Image.open(directory + "/" + filename, "r")
            exif_data = working_image.getexif()
            for tag_id in exif_data:
                exif_tag_name = TAGS.get(tag_id, tag_id)
                value = exif_data.get(tag_id)

                try:
                    if exif_tag_name == "Model":
                        model = value
                except NameError as ex:
                    print('Exception:', ex)

                try:
                    if exif_tag_name == "Make":
                        make = value
                except NameError as ex:
                    print('Exception:', ex)

                try:
                    if exif_tag_name == "DateTime":
                        date_time = value
                except NameError as ex:
                    print('Exception:', ex)

            if os.path.isfile(f):
                file_hash = calculate_hash(f)
                i = i + 1
                cur.execute("INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)", (i, f, file_hash, model, make, date_time))
                connection.commit()
    connection.close()


def html_report():
    connection = sqlite3.connect(database_name)
    cur = connection.cursor()
    cur.execute("SELECT DISTINCT id, path, sha256, make, model, datetime FROM images")
    rows = cur.fetchall()
    print("<html><head></head><body>")
    for row in rows:
        file_id = (row[0])
        path = (row[1])
        sha256 = (row[2])
        model = (row[3])
        make = (row[4])
        datetime = (row[5])
        print(f"<p>{file_id} {path} {sha256} {make} {model} {datetime}</p>\n")
    print("</body></html>")
    connection.close()


# if __name__ == '__main__':

if sys.argv[1] == "--input":
    if sys.argv[2]:
        directory = sys.argv[2]
    else:
        print("Usage: python main.py --input 'directory' 'database_name'")

    if sys.argv[3]:
        database_name = f"databases\{sys.argv[3]}"
    else:
        print("Usage: python main.py --input 'full-path-to-images' 'database_name'")

create_db()
insert_rows(directory)
# html_report()

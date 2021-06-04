import hashlib
import sys
import sqlite3
import os
from PIL import Image
from PIL.ExifTags import TAGS

directory = ""
file_path = ""


def calculate_hash(f):
    buffer_size = 65536
    sha256 = hashlib.sha256()

    with open(f, 'rb') as file:
        while True:
            data = file.read(buffer_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def create_db():
    connection = sqlite3.connect("test16.db")
    cur = connection.cursor()
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='images'")

    if cur.fetchone()[0] == 1:
        print('Table exists.')
    else:
        cur.execute("CREATE TABLE images (id, path, sha256, model, make, datetime)")

    connection.close()


def insert_rows():
    connection = sqlite3.connect("test16.db")
    cur = connection.cursor()
    i = 0
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        name, ext = os.path.splitext(f)
        if ext == '.JPG' or ext == '.jpg' or ext == '.jpeg' or ext == '.JPEG':
            working_image = Image.open(filename, "r")
            exif_data = working_image.getexif()
            for tag_id in exif_data: # REPLACE ELIFS WITH TRY, EXCEPT, ELSE STRUCTURE
                exif_tag_name = TAGS.get(tag_id, tag_id)
                value = exif_data.get(tag_id)
                if exif_tag_name == "Model":
                    model = value
                elif exif_tag_name == "Make":
                    make = value
                elif exif_tag_name == "DateTime":
                    date_time = value

            if os.path.isfile(f):
                file_hash = calculate_hash(f)
                i = i + 1
                cur.execute("INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)", (i, f, file_hash, model, make, date_time))
                connection.commit()
        # else:
        # print("not a jpg")

    connection.close()


def html_report():
    connection = sqlite3.connect("test16.db")
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

if sys.argv[1] == "-d":
    if sys.argv[2]:
        directory = sys.argv[2]
    else:
        print("Usage: python main.py -d 'directory'")

# if sys.argv[1] == "-f":
#   if sys.argv[2]:
#      file_path = sys.argv[2]
# else:
#    print("Usage: python main.py -f 'file'")

create_db()
insert_rows()
# html_report()

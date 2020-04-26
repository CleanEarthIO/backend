# seeder.py by Noah Krause
import google_streetview.api
import random
import os
import sqlite3
from time import sleep, time

def create_connection():
    conn = None
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
    print(database_file)
    try:
        conn = sqlite3.connect(database_file)
    except Exception as e:
        print(e)
    
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS street_images (id INTEGER PRIMARY KEY AUTOINCREMENT, latitude VARCHAR(255) NOT NULL, longitude VARCHAR(255) NOT NULL, file_name VARCHAR(255) NOT NULL, contains_litter TINYINT(1) NOT NULL DEFAULT 0, evaluated_filename VARCHAR(255) DEFAULT NULL);")
    return conn

def insert_file(conn, latitude, longitude, file_name):
    cur = conn.cursor()
    cur.execute("INSERT INTO street_images (latitude, longitude, file_name) VALUES (" + latitude + ", " + longitude + ", " + file_name + ";")

def seed(conn, topLeft, bottomRight):
    params = [{
        'size': '960x540',
        'location': 'temp',
        'heading': '270',
        'pitch': '-0.76',
        'key': ""
    }]

    for _ in range(100):
        latitude = str(random.uniform(topLeft[0], bottomRight[0]))
        longitude = str(random.uniform(topLeft[1], bottomRight[1]))
        file_name = time()
        params[0]['location'] = str(random.uniform(topLeft[0], bottomRight[0])) + ',' + str(random.uniform(topLeft[1], bottomRight[1]))
        results = google_streetview.api.results(params)
        results.download_links('photos')
        sleep(2)
        if (results.metadata[0]['status'] == "OK"):
            os.rename("photos/gsv_0.jpg", "photos/" + str(time()) + ".jpg")
            insert_file(conn, latitude, longitude, file_name)
        

if __name__ == "__main__":
    # lat, lon
    topLeft = [29.440235, -98.503513]
    bottomRight = [29.410889, -98.481520]
    conn = create_connection()
    with conn:
        seed(conn, topLeft, bottomRight)

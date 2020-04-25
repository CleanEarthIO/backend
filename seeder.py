# seeder.py by Noah Krause
import google_streetview.api
import random
from time import sleep, time
from os import rename

def seed(topLeft, bottomRight):
    params = [{
        'size': '960x540',
        'location': 'temp',
        'heading': '270',
        'pitch': '-0.76',
        'key': ""
    }]

    for _ in range(100):
        params[0]['location'] = str(random.uniform(topLeft[0], bottomRight[0])) + ',' + str(random.uniform(topLeft[1], bottomRight[1]))
        results = google_streetview.api.results(params)
        print(vars(results))
        results.download_links('photos')
        sleep(2)
        if (results.metadata[0]['status'] == "OK"):
            rename("photos/gsv_0.jpg", "photos/" + str(time()) + ".jpg")
        

if __name__ == "__main__":
    # lat, lon
    topLeft = [29.440235, -98.503513]
    bottomRight = [29.410889, -98.481520]
    seed(topLeft, bottomRight)

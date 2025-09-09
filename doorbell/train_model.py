import face_recognition
import pickle
import os
from memory_profiler import profile

@profile
def process_image(image_path, name, known_faces_path):
    print(name + " initializing")
    encoding = None
    image = face_recognition.load_image_file(image_path)
    try:
        encoding = face_recognition.face_encodings(image, num_jitters=1, model="small")[0]
    except IndexError: 
        print("No face found in the image:", name)
    
    with open(known_faces_path, "ab") as f:  # Use append mode to add to the existing file
        pickle.dump((encoding, name), f)

# Sammle Bilder und Namen der Personen
image_paths = ["./persons/adunka.jpg", "./persons/blasge.jpg", "./persons/rabitsch.jpg", "./persons/ludolf.jpg", "./persons/thomas.jpg"]
person_names = ["Adunka", "Blasge", "Rabitsch", "Ludolf", "Der König"]

# Pfad zur Datei, in der die bekannten Gesichts-Codierungen gespeichert sind
known_faces_path = "./persons/known_faces.pkl"

# Gesichtscodierungen für jede Person vorbereiten und zur Datei hinzufügen
for image_path, name in zip(image_paths, person_names):
    process_image(image_path, name, known_faces_path)

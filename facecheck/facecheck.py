import json
import time
import cv2
import mysql.connector

with open('credentials.JSON') as file:
    db_creds = json.load(file)

connection = mysql.connector.connect(
    host=db_creds['host'],
    user=db_creds['user'],
    password=db_creds['password'],
    database=db_creds['database']
)
cursor = connection.cursor()

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

capture = cv2.VideoCapture(0)

while True:
    ret, frame = capture.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, a, b) in faces:
        cv2.rectangle(frame, (x, y), (x+a, y+b), (255, 0, 0), 2)

        face = gray[y:y+b, x:x+a]
        _, buffer = cv2.imencode(ext='.jpg', img=face)
        face_data = buffer.tobytes()
        print(face_data)

        cursor.execute('INSERT INTO faces (image) VALUES (%s)', (face_data,))
        connection.commit()

    cv2.imshow('Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()

# Cerrar la conexión a la base de datos
cursor.close()
connection.close()

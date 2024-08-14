import json
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
    cv2.data.haarcascades + 'haarscascade_frontalface_default.xml'
)

capture = cv2.VideoCapture(0)

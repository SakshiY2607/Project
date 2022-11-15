from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

    
font = cv2.FONT_HERSHEY_SIMPLEX
red = (0, 0, 255)
green = (0, 255, 0)
blue= (255, 0, 0)
white=(255, 255, 255)
screen_height = 480*2
screen_width = 640*2

Base = declarative_base()
class Quiz(Base):
    __tablename__ = 'quiz'
    id = Column(Integer, primary_key=True)
    question= Column(String(1024), unique=True, nullable=False)
    option_A = Column(String(500), nullable=False)
    option_B = Column(String(500), nullable=False)
    option_C = Column(String(500), nullable=False)
    option_D = Column(String(500), nullable=False)
    answer= Column(String(500),nullable=False)
    category = Column(String(80), nullable=False)
    created_on = Column(DateTime, default=datetime.now)    

    def __str__(self):
        return f'{self.question}'

def open_db(path = 'database/app.sqlite'):
    engine = create_engine('sqlite:///' + path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def display_question(image, start=1):
    h,w,_ = image.shape
    session = open_db()
    quiz_data = session.query(Quiz).all()
    quiz = quiz_data[start]
    session.close()
    q =quiz.question
    a = quiz.option_A
    b = quiz.option_B
    c = quiz.option_C
    d = quiz.option_D
    cat = quiz.category
    print(q,a,b,c,d,cat,quiz.answer)
    cv2.rectangle(image, (0,h-300),(w,h),(0,0,0),-1)
    cv2.putText(image, q, (30, h - 200), font, 1, white, 2, cv2.LINE_AA)
    cv2.rectangle(image, (20, 90), (200,170), blue, 2)
    cv2.putText(image, "category", (50, 130), font, 1, blue, 2, cv2.LINE_AA)
    cv2.rectangle(image, (230, 20), (410,100), red, 2)
    cv2.putText(image, a, (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(image, (440, 20), (620,100), red, 2)
    # cv2.putText(frame, "B", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(image, (20, 200), (200,240), blue, 2)
    # cv2.putText(frame, "score", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(image, (230,130), (410,210), red, 2)
    # cv2.putText(frame, "B", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(image, (440, 130), (620,210), red, 2)
    # cv2.putText(frame, "B", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    return image

def distanceCalculate(p1, p2):
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
       
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
        image = cv2.resize(image, (screen_width, screen_height))
        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                coords_1 = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                coords_2 = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                try:
                    # normalize the coordinates
                    x1, y1 = int(coords_1.x * w), int(coords_1.y * h)
                    x2, y2 = int(coords_2.x * w), int(coords_2.y * h)
                    cv2.circle(image, (x1, y1), 25, (255, 0, 0), -1)
                    cv2.circle(image, (x2, y2), 25, (0, 255, 0), -1)
                    
                    # calculate the distance
                    dis = distanceCalculate((x1, y1), (x2, y2))
                    # draw the distance at the bottom of the image
                    cv2.putText(image, str(int(dis)), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    
                    # logic 
                    if dis < 30:
                        # display joined
                        cv2.putText(image, "Selector", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        # display not joined
                        cv2.putText(image, "Pointer", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                except Exception as e:
                    print(e)
        # display quiz ui
        image = display_question(image)
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
        
cap.release()
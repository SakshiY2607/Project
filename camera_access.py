from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from time import sleep
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
screen_height = 480
screen_width = 640

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    created_on = Column(DateTime, default=datetime.now)

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

class Score(Base):
    __tablename__ = 'score'
    id = Column(Integer, primary_key=True)
    score = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    created_on = Column(DateTime, default=datetime.now)

    def __str__(self):
        return f'{self.score} of {self.user_id}'

def open_db(path = 'database/app.sqlite'):
    engine = create_engine('sqlite:///' + path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def display_question(image, question=2):
    h,w,_ = image.shape
    session = open_db()
    quiz = session.query(Quiz).get(question)
    session.close()
    print(quiz)
    q =quiz.question
    a = quiz.option_A
    b = quiz.option_B
    c = quiz.option_C
    d = quiz.option_D
    cat = quiz.category
    print(q,a,b,c,d,cat,quiz.answer)
    cv2.rectangle(image, (0,h-150),(w,h),(0,0,0),-1)
    cv2.putText(image, q, (0, h -100), font, 1, white, 2, cv2.LINE_AA)
    cv2.rectangle(image, (20, 90), (200,170), blue, -1)
    cv2.putText(image, cat, (50, 130), font, 1, blue, 2, cv2.LINE_AA)
    cv2.rectangle(image, (230, 20), (410,100), red, -1)
    cv2.putText(image, a, (w - 400, 50), font, 1, green, 2, cv2.LINE_AA)
    cv2.rectangle(image, (440, 20), (620,100), red, -1)
    cv2.putText(image, b, (w - 190, 50), font, 1, green, 2, cv2.LINE_AA)
    cv2.rectangle(image, (20, 200), (200,240), blue, -1)
    cv2.putText(image, "score", (w - 600, 225), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(image, (230,130), (410,210), red, -1)
    cv2.putText(image, c, (w -400, 160), font, 1, green, 2, cv2.LINE_AA)
    cv2.rectangle(image, (440, 130), (620,210), red, -1)
    cv2.putText(image, d, (w - 190, 160), font, 1, green, 2, cv2.LINE_AA)
    return image

def distanceCalculate(p1, p2):
    dis = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
    return dis



# For webcam input:
cap = cv2.VideoCapture(0)
question = 2

def check_answer(question, option_selected):
    session = open_db()
    quiz = session.query(Quiz).get(question)
    user = session.query(User).get(1)
    # load score of user
    score = session.query(Score).filter(Score.user_id == user.id).order_by(Score.id.desc()).first()
    if score is None:
        score = Score(score=0, user_id=user.id)
    # if answer is correct add 10 to score
    if quiz.answer == option_selected:
        score.score += 10
    # save score
    session.add(score)
    session.commit()
    session.close()
    return question + 1

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
                    cv2.circle(image, (x1, y1), 15, (255, 0, 0), -1)
                    cv2.circle(image, (x2, y2), 15, (0, 255, 0), -1)
                    
                    # calculate the distance
                    dis = distanceCalculate((x1, y1), (x2, y2))
                    # draw the distance at the bottom of the image
                    cv2.putText(image, str(int(dis)), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    
                    # logic 
                    print('question no is', question)
                    if dis < 30:
                        # display joined
                        # check if the coords fall in an option box
                        if x1 > 230 and x1 < 410 and y1 > 20 and y1 < 100:
                            print("A")
                            question = check_answer(question, option_selected='A')
                        elif x1 > 440 and x1 < 620 and y1 > 20 and y1 < 100:
                            print("B")
                            question = check_answer(question, option_selected='B')
                        elif x1 > 230 and x1 < 410 and y1 > 130 and y1 < 210:
                            print("C")
                            question = check_answer(question, option_selected='C')
                        elif x1 > 440 and x1 < 620 and y1 > 130 and y1 < 210:
                            print("D")
                            question = check_answer(question, option_selected="D")
                        cv2.putText(image, "Selector", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        # display not joined
                        cv2.putText(image, "Pointer", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                except Exception as e:
                    print(e)
        # display quiz ui
        image = display_question(image,question)
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
        
cap.release()
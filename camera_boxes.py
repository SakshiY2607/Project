import cv2

cam = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_SIMPLEX
red = (0, 0, 255)
green = (0, 255, 0)
white = (255, 255, 255)

while cam.isOpened():
    ret, frame = cam.read()
    h, w, _ = frame.shape
    if not ret:
        print("Ignoring empty camera frame.")
        continue
    # add a question on the screen bottom
    q ="Is this a hand?"
    cv2.putText(frame, q, (30, h - 50), font, 1, white, 2, cv2.LINE_AA)
    cv2.rectangle(frame, (20, 20), (200,100), green, 2)
    cv2.putText(frame, "category", (50, 50), font, 1, green, 2, cv2.LINE_AA)
    cv2.rectangle(frame, (230, 20), (410,100), red, 2)
    #cv2.putText(frame, "A", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(frame, (440, 20), (620,100), red, 2)
   # cv2.putText(frame, "B", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(frame, (20, 130), (200,170), green, 2)
   # cv2.putText(frame, "B", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(frame, (230,130), (410,210), red, 2)
   # cv2.putText(frame, "B", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.rectangle(frame, (440, 130), (620,210), red, 2)
   # cv2.putText(frame, "B", (w - 70, 30), font, 1, red, 2, cv2.LINE_AA)
    cv2.imshow('Camera', frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break
cam.release()
cv2.destroyAllWindows()
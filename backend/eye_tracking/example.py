"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
from gaze_tracking import GazeTracking
import time


gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

looking_away_start_time = None
strikes = 0

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

       # Strike system
    if gaze.is_center():
        looking_away_start_time = None
    else:
        if looking_away_start_time is None:
            looking_away_start_time = time.time()
        elif time.time() - looking_away_start_time >= 15:
            strikes += 1
            if strikes == 1:
                print("Strike 1, you've been distracted get back to studying.")
            elif strikes == 2:
                print("Strike 2, you're losing focus, don't give up.")
            elif strikes == 3:
                print("Strike 3: helloooooo")
            looking_away_start_time = time.time() #reset the timer, if it's already at 15


    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break
   
webcam.release()
cv2.destroyAllWindows()

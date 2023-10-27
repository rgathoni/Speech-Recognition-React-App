import pickle

import cv2
import mediapipe as mp
import numpy as np

#load trained Random Forest Classifier model from pickle file
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

#initialize video capture from default camera (webcam)
cap = cv2.VideoCapture(0)

#initialize MediaPipe Hands module for hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

#dictionary -- map numerical predictions to corresponding signs
labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'I love You', 4: 'Hello'}
while True:

    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()
    #print(ret)
    H, W, _ = frame.shape

    #convert frame from BGR to RGB format
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #MediaPipe Hands module -- detect hand landmarks in the frame
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,  # image to draw on
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

        #extract X and Y coordinates of hand landmarks
        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y

                x_.append(x)
                y_.append(y)

            #normalize the coordinates
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

        #bounding box coordinates for detected hand
        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10

        x2 = int(max(x_) * W) - 10
        y2 = int(max(y_) * H) - 10

        #make prediction if #detected landmarks is within a given range
        if len(data_aux) <= 42:
            #predict sign based on the trained model
            prediction = model.predict([np.asarray(data_aux)])
            #map numerical prediction to corresponding sign
            predicted_character = labels_dict[int(prediction[0])]
       
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3,
                    cv2.LINE_AA)

    #display processed frame with predictions
    cv2.imshow('frame', frame)
    cv2.waitKey(120)

#release video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

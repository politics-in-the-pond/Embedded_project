import matplotlib.pyplot as plt
from sys import stdout
import mediapipe as mp
import numpy as np
import pygame
import time
import cv2
import sys


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True,
                       max_num_hands=2, min_detection_confidence=0.5)
hands_videos = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils


def detectHandsLandmarks(image, hands, draw=True, display=True):

    output_image = image.copy()

    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = hands.process(imgRGB)

    if results.multi_hand_landmarks and draw:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_drawing.draw_landmarks(
                image=output_image, landmark_list=hand_landmarks,
                connections=mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255),
                                                             thickness=2, circle_radius=2),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0),
                                                               thickness=2, circle_radius=2))

    if display:

        plt.figure(figsize=[15, 15])
        plt.subplot(121)
        plt.imshow(image[:, :, ::-1])
        plt.title("Original Image")
        plt.axis('off')
        plt.subplot(122)
        plt.imshow(output_image[:, :, ::-1])
        plt.title("Output")
        plt.axis('off')

    else:

        return output_image, results


def countFingers(image, results, draw=True, display=True):

    height, width, _ = image.shape

    output_image = image.copy()

    count = {'RIGHT': 0, 'LEFT': 0}

    fingers_tips_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                        mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]

    fingers_statuses = {'RIGHT_THUMB': False, 'RIGHT_INDEX': False, 'RIGHT_MIDDLE': False, 'RIGHT_RING': False,
                        'RIGHT_PINKY': False, 'LEFT_THUMB': False, 'LEFT_INDEX': False, 'LEFT_MIDDLE': False,
                        'LEFT_RING': False, 'LEFT_PINKY': False}

    for hand_index, hand_info in enumerate(results.multi_handedness):

        hand_label = hand_info.classification[0].label

        hand_landmarks = results.multi_hand_landmarks[hand_index]

        for tip_index in fingers_tips_ids:

            finger_name = tip_index.name.split("_")[0]

            if (hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y):

                fingers_statuses[hand_label.upper()+"_"+finger_name] = True

                count[hand_label.upper()] += 1

        thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
        thumb_mcp_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP - 2].x

        if (hand_label == 'Right' and (thumb_tip_x < thumb_mcp_x)) or (hand_label == 'Left' and (thumb_tip_x > thumb_mcp_x)):

            fingers_statuses[hand_label.upper()+"_THUMB"] = True

            count[hand_label.upper()] += 1

    if draw:
        pass

    if display:

        pass

    else:

        return output_image, fingers_statuses, count


def recognizeGestures(image, fingers_statuses, count, draw=True, display=True):

    output_image = image.copy()

    hands_labels = ['RIGHT', 'LEFT']

    hands_gestures = {'RIGHT': "UNKNOWN", 'LEFT': "UNKNOWN"}

    for hand_index, hand_label in enumerate(hands_labels):

       # color = (0, 0, 255)

        if count[hand_label] == 2 and fingers_statuses[hand_label+'_MIDDLE'] and fingers_statuses[hand_label+'_INDEX']:

            if hand_index == 0:
                hands_gestures[hand_label] = "RIGHT_V_SIGN"

            elif hand_index == 1:
                hands_gestures[hand_label] = "LEFT_V_SIGN"

           # color = (0, 255, 0)

        elif count[hand_label] == 1 and fingers_statuses[hand_label+'_INDEX']:

            if hand_index == 0:
                hands_gestures[hand_label] = "RIGHT_STOP_SIGN"

            elif hand_index == 1:
                hands_gestures[hand_label] = "RIGHT_STOP_SIGN"

          #  color = (0, 255, 0)

        elif count[hand_label] == 5:

            if hand_index == 0:
                hands_gestures[hand_label] = "RIGHT_HIGH_FIVE_SIGN"
            elif hand_index == 1:
                hands_gestures[hand_label] = "LEFT_HIGH_FIVE_SIGN"

    if display:
        pass

    else:

        return output_image, hands_gestures


camera_video = cv2.VideoCapture(0)
camera_video.set(3, 480)
camera_video.set(4, 320)


pygame.init()


num_of_frames = 5

counter = {'RIGHT_V_SIGN': 0, 'LEFT_V_SIGN': 0, 'RIGHT_SPIDERMAN_SIGN': 0, 'LEFT_SPIDERMAN_SIGN': 0, 'LEFT_HIGH_FIVE_SIGN': 0, 'RIGHT_HIGH_FIVE_SIGN': 0,
           'RIGHT_STOP_SIGN': 0, 'LEFT_STOP_SIGN': 0}

captured_image = None

while camera_video.isOpened():

    ok, frame = camera_video.read()

    if not ok:
        continue

    frame = cv2.flip(frame, 1)

    frame_height, frame_width, _ = frame.shape

    frame, results = detectHandsLandmarks(
        frame, hands_videos, draw=False, display=False)

    if results.multi_hand_landmarks:

        frame, fingers_statuses, count = countFingers(
            frame, results, draw=False, display=False)

        _, hands_gestures = recognizeGestures(
            frame, fingers_statuses, count, draw=False, display=False)

        if any(hand_gesture == "LEFT_HIGH_FIVE_SIGN" for hand_gesture in hands_gestures.values()):

            counter['LEFT_HIGH_FIVE_SIGN'] += 1

            if counter['LEFT_HIGH_FIVE_SIGN'] == num_of_frames:

                #filter_on = True
                # print("LEFT_HIGH_FIVE_SIGN")
                sys.stdout.write('J')
                sys.stdout.flush()
                time.sleep(0.1)

                counter['LEFT_HIGH_FIVE_SIGN'] = 0

        else:

            counter['LEFT_HIGH_FIVE_SIGN'] = 0

        if any(hand_gesture == "RIGHT_HIGH_FIVE_SIGN" for hand_gesture in hands_gestures.values()):

            counter['RIGHT_HIGH_FIVE_SIGN'] += 1

            if counter['RIGHT_HIGH_FIVE_SIGN'] == num_of_frames:

                sys.stdout.write('J')
                sys.stdout.flush()
                time.sleep(0.1)

                counter['RIGHT_HIGH_FIVE_SIGN'] = 0

        else:

            counter['RIGHT_HIGH_FIVE_SIGN'] = 0

        if any(hand_gesture == "LEFT_STOP_SIGN" for hand_gesture in hands_gestures.values()):

            counter['LEFT_STOP_SIGN'] += 1

            if counter['LEFT_STOP_SIGN'] == num_of_frames:

                sys.stdout.write('S')
                sys.stdout.flush()
                time.sleep(0.1)

                counter['LEFT_STOP_SIGN'] = 0

        else:

            counter['LEFT_STOP_SIGN'] = 0

        if any(hand_gesture == "RIGHT_STOP_SIGN" for hand_gesture in hands_gestures.values()):

            counter['RIGHT_STOP_SIGN'] += 1

            if counter['RIGHT_STOP_SIGN'] == num_of_frames:

                sys.stdout.write('S')
                sys.stdout.flush()
                time.sleep(0.1)

                counter['RIGHT_STOP_SIGN'] = 0

        else:

            counter['RIGHT_STOP_SIGN'] = 0

    # if filter_on:

    #     frame[filter_imageBGRA[:, :, -1] ==
    #           255] = filter_imageBGR[filter_imageBGRA[:, :, -1] == 255]

    if results.multi_hand_landmarks and any(hand_gesture == "LEFT_V_SIGN" for hand_gesture in hands_gestures.values()):

        counter['LEFT_V_SIGN'] += 1

        if counter['LEFT_V_SIGN'] == num_of_frames:

            # captured_image = cv2.copyMakeBorder(src=frame, top=10, bottom=10, left=10, right=10,
            #                                     borderType=cv2.BORDER_CONSTANT, value=(255, 255, 255))

            # cv2.imwrite('Captured_Image.png', captured_image)

            # cv2.imshow('Selfie-Capturing System',
            #            np.zeros((frame_height, frame_width)))

            # pygame.mixer.music.play()
            # cv2.waitKey(100)

            # plt.close()
            # plt.figure(figsize=[10, 10])
            # plt.imshow(frame[:, :, ::-1])
            # plt.title("Captured Image")
            # plt.axis('off')
            sys.stdout.write('L')
            sys.stdout.flush()
            time.sleep(0.1)
            counter['LEFT_V_SIGN'] = 0

    else:

        counter['LEFT_V_SIGN'] = 0

    if results.multi_hand_landmarks and any(hand_gesture == "RIGHT_V_SIGN" for hand_gesture in hands_gestures.values()):

        counter['RIGHT_V_SIGN'] += 1

        if counter['RIGHT_V_SIGN'] == num_of_frames:

            # captured_image = cv2.copyMakeBorder(src=frame, top=10, bottom=10, left=10, right=10,
            #                                     borderType=cv2.BORDER_CONSTANT, value=(255, 255, 255))

            # cv2.imwrite('Captured_Image.png', captured_image)

            # cv2.imshow('Selfie-Capturing System',
            #            np.zeros((frame_height, frame_width)))

            # pygame.mixer.music.play()
            # cv2.waitKey(100)

            # plt.close()
            # plt.figure(figsize=[10, 10])
            # plt.imshow(frame[:, :, ::-1])
            # plt.title("Captured Image")
            # plt.axis('off')
            sys.stdout.write('R')
            sys.stdout.flush()
            time.sleep(0.1)
            counter['RIGHT_V_SIGN'] = 0

    else:

        counter['RIGHT_V_SIGN'] = 0

    # if captured_image is not None:

    #     captured_image = cv2.resize(
    #         captured_image, (frame_width//5, int(((frame_width//5) / frame_width) * frame_height)))

    #     img_height, img_width, _ = captured_image.shape

    #     frame[10: 10+img_height, 10: 10+img_width] = captured_image

    cv2.imshow('Selfie-Capturing System', frame)

    k = cv2.waitKey(1) & 0xFF

    if(k == 27):
        break

camera_video.release()
cv2.destroyAllWindows()

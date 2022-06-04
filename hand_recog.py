from sys import stdout
import time
import sys
import matplotlib.pyplot as plt
import mediapipe as mp
import numpy as np
import time
import cv2

# mp.solutions.hands 클래스를 초기화하고 mp.solutions.hands를 설정해야 합니다.Hands()는 적절한 인수로 작동하며 탐지된 랜드마크를 시각화하는 데 필요한 mp.solutions.drawing_utils 클래스도 초기화합니다
#
# static_image_mode 인수를 True로 설정하면 이미지에 사용할 수 있고, static_image_mode를 False로 설정하면 비디오에 사용할 수 있습니다


# Initialize the mediapipe hands class.
# 기본세팅
# mediapipe 클래스 초기화
mp_hands = mp.solutions.hands

# Set up the Hands functions for images and videos.
hands = mp_hands.Hands(static_image_mode=True,
                       max_num_hands=2, min_detection_confidence=0.5)
hands_videos = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

# Initialize the mediapipe drawing class.
mp_drawing = mp.solutions.drawing_utils


# 이 단계에서는 이미지/프레임을 입력으로 사용하고 Media pipe에서 제공하는 솔루션을 사용하여 이미지/프레임의
# 손에서 랜드마크 검출을 수행하고 이미지의 각 손에 대해 21개의 3D 랜드마크를 얻는 detect Hands Landmarks() 기능을 만듭니다.
# 함수는 전달된 인수에 따라 결과를 표시하거나 반환합니다.

def detectHandsLandmarks(image, hands, draw=True, display=True):
    '''

        image: 랜드마크를 감지해야 하는 눈에 띄는 손이 있는 입력 이미지.
        hands: 핸드 랜드마크 감지를 수행하는 데 필요한 Hands 기능.
        draw: 함수가 true로 설정된 경우 출력 이미지에 핸즈 랜드마크를 그리는 부울 값입니다.
        display: 함수가 true로 설정된 경우 원래 입력 이미지와 출력을 표시하는 부울 값
        지정된 경우 아무것도 반환하지 않는 손 랜드마크가 그려진 이미지.
    return:
        output_image: 지정된 경우 탐지된 손 랜드마크가 그려진 입력 이미지의 복사본입니다.
        결과: 입력 영상에서 손 랜드마크 검출의 출력.
    '''

    # Create a copy of the input image to draw landmarks on.
    # 복사본 만들기
    output_image = image.copy()

    # Convert the image from BGR into RGB format.
    # BGR - RGB
    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform the Hands Landmarks Detection.
    results = hands.process(imgRGB)

    # Check if landmarks are found and are specified to be drawn.
    if results.multi_hand_landmarks and draw:

        # Iterate over the found hands.
        for hand_landmarks in results.multi_hand_landmarks:

            # Draw the hand landmarks on the copy of the input image.
            # 핸드 랜드만크 그리기
            mp_drawing.draw_landmarks(
                image=output_image, landmark_list=hand_landmarks,
                connections=mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255),
                                                             thickness=2, circle_radius=2),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0),
                                                               thickness=2, circle_radius=2))

    # Check if the original input image and the output image are specified to be displayed.
    if display:

        # Display the original input image and the output image.
        plt.figure(figsize=[15, 15])
        plt.subplot(121)
        plt.imshow(image[:, :, ::-1])
        plt.title("Original Image")
        plt.axis('off')
        plt.subplot(122)
        plt.imshow(output_image[:, :, ::-1])
        plt.title("Output")
        plt.axis('off')

    # Otherwise
    else:

        # Return the output image and results of hands landmarks detection.
        return output_image, results


# 이제 이 단계에서는 detect Hands Landmarks() 기능에 의해 반환되는 랜드마크 감지 결과를 가져오고 랜드마크를 활용하여 이미지/프레임의 각 손의 손가락 수를 세고
# 이미지에 있는 각 손가락의 수와 상태를 반환하는 기능 카운트()를 만듭니다.
# 손가락의 끝과 중간마디를 비교한다 Y의 좌표가 아래로 내려갈수로 커지니깐 손가락이 펴지는경우
# FINGER_TIP =손가락 끝이 FINGER_PIP 손가락 중간마디보다 높이 있으므로 Y좌표는 0에 가깝기때문에
# 더 작은 값을 가진다

# 그러나 엄지손가락의 경우 TUMB_TIP 랜드마크와 TUMB_MCP 랜드마크의 x 좌표를 비교해야 하기 때문에 시나리오가 조금 다를 것이고,
# 손이 왼쪽인지 오른쪽인지에 따라 조건이 달라질 것이다.

# 오른손의 경우 오른손엄지의 끝이 오른손 마디 끝보다 낮은 X 의 값
# 그러나 왼손의경우 왼손 엄지의 끝이 왼손 마디 끝보다 높은 x 의 값


def countFingers(image, results, draw=True, display=True):
    '''
    This function will count the number of fingers up for each hand in the image.
    Args:
        image:   The image of the hands on which the fingers counting is required to be performed.
        results: The output of the hands landmarks detection performed on the image of the hands.
        draw:    A boolean value that is if set to true the function writes the total count of fingers of the hands on the
                output image.
        display: A boolean value that is if set to true the function displays the resultant image and returns nothing.
    Returns:
        output_image:     A copy of the input image with the fingers count written, if it was specified.
        fingers_statuses: A dictionary containing the status (i.e., open or close) of each finger of both hands.
        count:            A dictionary containing the count of the fingers that are up, of both hands.
    '''

    # Get the height and width of the input image.
    height, width, _ = image.shape

    # Create a copy of the input image to write the count of fingers on.
    output_image = image.copy()

    # Initialize a dictionary to store the count of fingers of both hands.
    count = {'RIGHT': 0, 'LEFT': 0}

    # Store the indexes of the tips landmarks of each finger of a hand in a list.
    # 엄지 손가락을 제외한 인덱스 설정
    # 손가락끝  idx 저장
    fingers_tips_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                        mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]

    # Initialize a dictionary to store the status (i.e., True for open and False for close) of each finger of both hands.
    # 손가락 열리면 true로
    fingers_statuses = {'RIGHT_THUMB': False, 'RIGHT_INDEX': False, 'RIGHT_MIDDLE': False, 'RIGHT_RING': False,
                        'RIGHT_PINKY': False, 'LEFT_THUMB': False, 'LEFT_INDEX': False, 'LEFT_MIDDLE': False,
                        'LEFT_RING': False, 'LEFT_PINKY': False}

    # Iterate over the found hands in the image.
    for hand_index, hand_info in enumerate(results.multi_handedness):

        # Retrieve the label of the found hand.
        # 손 검색
        hand_label = hand_info.classification[0].label

        # Retrieve the landmarks of the found hand.
        hand_landmarks = results.multi_hand_landmarks[hand_index]

        # Iterate over the indexes of the tips landmarks of each finger of the hand.
        for tip_index in fingers_tips_ids:

            # Retrieve the label (i.e., index, middle, etc.) of the finger on which we are iterating upon.
            finger_name = tip_index.name.split("_")[0]

            # Check if the finger is up by comparing the y-coordinates of the tip and pip landmarks.
            # 손가락이 펴졌는지 확인
            if (hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y):

                # Update the status of the finger in the dictionary to true.
                # 손가락이 펴친상태이므로 true로 바꾸자
                fingers_statuses[hand_label.upper()+"_"+finger_name] = True

                # Increment the count of the fingers up of the hand by 1.
                # 개수 늘려 늘려
                count[hand_label.upper()] += 1

        # Retrieve the y-coordinates of the tip and mcp landmarks of the thumb of the hand.
        # 엄지손가락 검색
        thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
        thumb_mcp_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP - 2].x

        # Check if the thumb is up by comparing the hand label and the x-coordinates of the retrieved landmarks.
        # 왼손과 오른손은 따로 따로 구별해서 적용해야함
        if (hand_label == 'Right' and (thumb_tip_x < thumb_mcp_x)) or (hand_label == 'Left' and (thumb_tip_x > thumb_mcp_x)):

            # Update the status of the thumb in the dictionary to true.
            # 손가락이 펴친상태이므로 true로 바꾸자
            fingers_statuses[hand_label.upper()+"_THUMB"] = True

            # Increment the count of the fingers up of the hand by 1.
            # 개수 늘려 늘려
            count[hand_label.upper()] += 1

    # Check if the total count of the fingers of both hands are specified to be written on the output image.
    if draw:

        # Write the total count of the fingers of both hands on the output image.
        # 출력 이미지에 양손의 총 손가락 수를 기록합니다.
        cv2.putText(output_image, " Total Fingers: ", (10, 25),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (20, 255, 155), 2)
        cv2.putText(output_image, str(sum(count.values())), (width//2-150, 240), cv2.FONT_HERSHEY_SIMPLEX,
                    8.9, (20, 255, 155), 10, 10)

    # Check if the output image is specified to be displayed.
    if display:

        # Display the output image.
        plt.figure(figsize=[10, 10])
        plt.imshow(output_image[:, :, ::-1])
        plt.title("Output Image")
        plt.axis('off')

    # Otherwise
    else:

        # Return the output image, the status of each finger and the count of the fingers up of both hands.
        return output_image, fingers_statuses, count


# 이 단계에서 기능 카운트 Fingers()에서 출력된 손가락의 상태(즉, 위 또는 아래)를 사용하여 이미지에서 손의 제스처를 결정하는 기능 recognizeGestures()를 만들 것이다. 이 기능은 다음과 같은 손동작을 식별할 수 있습니다.
#
# V Hand Gesture(V 손 제스처) ✌1900(예: 검지와 가운데 손가락만 위로)
# 스파이더맨 손 제스처 🤟(예: 엄지, 검지, 손가락 위로)
# HIGH-FIVE 손동작 ✋ (즉, 다섯 손가락 모두 위로)
# 단순성을 위해, 우리는 이것을 세 가지 손짓으로만 제한하고 있다. 그러나 원하는 경우 이 기능을 쉽게 확장하여 조건문을 추가하는 것만으로 더 많은 제스처를 식별할 수 있습니다.


def recognizeGestures(image, fingers_statuses, count, draw=True, display=True):
    '''
    This function will determine the gesture of the left and right hand in the image.
    Args:
        image:            The image of the hands on which the hand gesture recognition is required to be performed.
        fingers_statuses: A dictionary containing the status (i.e., open or close) of each finger of both hands. 
        count:            A dictionary containing the count of the fingers that are up, of both hands.
        draw:             A boolean value that is if set to true the function writes the gestures of the hands on the
                        output image, after recognition.
        display:          A boolean value that is if set to true the function displays the resultant image and 
                        returns nothing.
    Returns:
        output_image:   A copy of the input image with the left and right hand recognized gestures written if it was 
                        specified.
        hands_gestures: A dictionary containing the recognized gestures of the right and left hand.
    '''

    '''
     fingers_statuses = {'RIGHT_THUMB': False, 'RIGHT_INDEX': False, 'RIGHT_MIDDLE': False, 'RIGHT_RING': False,
                        'RIGHT_PINKY': False, 'LEFT_THUMB': False, 'LEFT_INDEX': False, 'LEFT_MIDDLE': False,
                        'LEFT_RING': False, 'LEFT_PINKY': False}
    '''
    # Create a copy of the input image.
    output_image = image.copy()

    # Store the labels of both hands in a list.
    hands_labels = ['RIGHT', 'LEFT']

    # Initialize a dictionary to store the gestures of both hands in the image.
    hands_gestures = {'RIGHT': "UNKNOWN", 'LEFT': "UNKNOWN"}

    # Iterate over the left and right hand.
    for hand_index, hand_label in enumerate(hands_labels):

        # Initialize a variable to store the color we will use to write the hands gestures on the image.
        # Initially it is red which represents that the gesture is not recognized.
        color = (0, 0, 255)
        # ------------------------------------여기서 손 동작 체크하기  ------------------------------------

        # Check if the person is making the 'V' gesture with the hand.
        ####################################################################################################################

        # Check if the number of fingers up is 2 and the fingers that are up, are the index and the middle finger.
        if count[hand_label] == 2 and fingers_statuses[hand_label+'_MIDDLE'] and fingers_statuses[hand_label+'_INDEX']:

            # Update the gesture value of the hand that we are iterating upon to V SIGN.
            # hand_index = 0 일떄는 오른손 hand_index =1 일떄는 왼손 조건 주기

            # 오른손
            if hand_index == 0:
                hands_gestures[hand_label] = "RIGHT_V_SIGN"
            # 왼손
            elif hand_index == 1:
                hands_gestures[hand_label] = "LEFT_V_SIGN"

            # Update the color value to green.
            color = (0, 255, 0)

        ####################################################################################################################

        # Check if the person is making the 'SPIDERMAN' gesture with the hand.
        ##########################################################################################################################################################

        # Check if the number of fingers up is 3 and the fingers that are up, are the thumb, index and the pinky finger.
        elif count[hand_label] == 3 and fingers_statuses[hand_label+'_THUMB'] and fingers_statuses[hand_label+'_INDEX'] and fingers_statuses[hand_label+'_PINKY']:

            # Update the gesture value of the hand that we are iterating upon to SPIDERMAN SIGN.
            #hands_gestures[hand_label] = "SPIDERMAN SIGN"

            # 오른손
            if hand_index == 0:
                hands_gestures[hand_label] = "RIGHT_SPIDERMAN_SIGN"
            # 왼손
            elif hand_index == 1:
                hands_gestures[hand_label] = "LEFT_SPIDERMAN_SIGN"

            # Update the color value to green.
            color = (0, 255, 0)

        ##########################################################################################################################################################

        # Check if the person is making the 'HIGH-FIVE' gesture with the hand.
        ####################################################################################################################

        # 하이파이브 체크

        # Check if the number of fingers up is 5, which means that all the fingers are up.
        elif count[hand_label] == 5:

            # Update the gesture value of the hand that we are iterating upon to HIGH-FIVE SIGN.
            if hand_index == 1:
                hands_gestures[hand_label] = "RIGHT_HIGH_FIVE_SIGN"
            elif hand_index == 0:
                hands_gestures[hand_label] = "LEFT_HIGH_FIVE_SIGN"

            # Update the color value to green.
            color = (0, 255, 0)

        ####################################################################################################################

        # 주먹 쥔거 체크

        elif count[hand_label] == 0:
            #hands_gestures[hand_label] = "STOP"
            if hand_index == 0:
                hands_gestures[hand_label] = "RIGHT_STOP_SIGN"
            elif hand_index == 1:
                hands_gestures[hand_label] = "LEFT_STOP_SIGN"

            # Update the color value to green.
            color = (0, 255, 0)

        ####################################################################################################################

        # Check if the hands gestures are specified to be written.
        if draw:

            # Write the hand gesture on the output image.
            cv2.putText(output_image, hand_label + ': ' + hands_gestures[hand_label], (10, (hand_index+1) * 60),
                        cv2.FONT_HERSHEY_PLAIN, 4, color, 5)

    # Check if the output image is specified to be displayed.
    if display:

        # Display the output image.
        plt.figure(figsize=[10, 10])
        plt.imshow(output_image[:, :, ::-1])
        plt.title("Output Image")
        plt.axis('off')

    # Otherwise
    else:

        # Return the output image and the gestures of the both hands.
        return output_image, hands_gestures


# Initialize the VideoCapture object to read from the webcam.
camera_video = cv2.VideoCapture(0)
camera_video.set(3, 1280)
camera_video.set(4, 960)

# 양손
# 왼쪽 가기 멈추기 왼쪽 점프
# <--       주먹    왼손 하이파이브
# 오른쪽 가기 멈추기 오른쪽 점프
# ->          주먹     오른손 하이파이브

# Create named window for resizing purposes.
#cv2.namedWindow('test_finger ', cv2.WINDOW_NORMAL)

# Read the filter image with its blue, green, red, and alpha channel.
filter_imageBGRA = cv2.imread('media/filter.png', cv2.IMREAD_UNCHANGED)

# Initialize a variable to store the status of the filter (i.e., whether to apply the filter or not).
filter_on = False

# Initialize the number of consecutive frames on which we want to check the hand gestures before triggering the events.
num_of_frames = 5

# Initialize a dictionary to store the counts of the consecutive frames with the hand gestures recognized.
counter = {'RIGHT_V_SIGN': 0, 'LEFT_V_SIGN': 0, 'RIGHT_SPIDERMAN_SIGN': 0, 'LEFT_SPIDERMAN_SIGN': 0, 'LEFT_HIGH_FIVE_SIGN': 0, 'RIGHT_HIGH_FIVE_SIGN': 0,
           'RIGHT_STOP_SIGN': 0, 'LEFT_STOP_SIGN': 0}

# Initialize a variable to store the captured image.
captured_image = None

# Iterate until the webcam is accessed successfully.
while camera_video.isOpened():

    # Read a frame.
    ok, frame = camera_video.read()

    # Check if frame is not read properly then continue to the next iteration to read the next frame.
    if not ok:
        continue

    # Flip the frame horizontally for natural (selfie-view) visualization.
    frame = cv2.flip(frame, 1)

    # Get the height and width of the frame of the webcam video.
    frame_height, frame_width, _ = frame.shape

    # Resize the filter image to the size of the frame.
    filter_imageBGRA = cv2.resize(
        filter_imageBGRA, (frame_width, frame_height))

    # Get the three-channel (BGR) image version of the filter image.
    filter_imageBGR = filter_imageBGRA[:, :, :-1]

    # Perform Hands landmarks detection on the frame.
    frame, results = detectHandsLandmarks(
        frame, hands_videos, draw=False, display=False)

    # Check if the hands landmarks in the frame are detected.
    if results.multi_hand_landmarks:

        # Count the number of fingers up of each hand in the frame.
        frame, fingers_statuses, count = countFingers(
            frame, results, draw=False, display=False)

        # Perform the hand gesture recognition on the hands in the frame.
        _, hands_gestures = recognizeGestures(
            frame, fingers_statuses, count, draw=False, display=False)

        # 왼손 하이파이브
        ####################################################################################################################
        if any(hand_gesture == "LEFT_HIGH_FIVE_SIGN" for hand_gesture in hands_gestures.values()):

            # Increment the count of consecutive frames with SPIDERMAN hand gesture recognized.
            counter['LEFT_HIGH_FIVE_SIGN'] += 1

            # Check if the counter is equal to the required number of consecutive frames.
            if counter['LEFT_HIGH_FIVE_SIGN'] == num_of_frames:

                # Turn on the filter by updating the value of the filter status variable to true.
                filter_on = True

                # Update the counter value to zero.
                counter['LEFT_HIGH_FIVE_SIGN'] = 0

        # Otherwise if the gesture of any hand in the frame is not SPIDERMAN SIGN.
        else:

            # Update the counter value to zero. As we are counting the consective frames with SPIDERMAN hand gesture.
            counter['LEFT_HIGH_FIVE_SIGN'] = 0

        ####################################################################################################################

        # 오른손 하이파이브
        ####################################################################################################################
        if any(hand_gesture == "RIGHT_HIGH_FIVE_SIGN" for hand_gesture in hands_gestures.values()):

            # Increment the count of consecutive frames with SPIDERMAN hand gesture recognized.
            counter['RIGHT_HIGH_FIVE_SIGN'] += 1

            # Check if the counter is equal to the required number of consecutive frames.
            if counter['RIGHT_HIGH_FIVE_SIGN'] == num_of_frames:

                # Turn on the filter by updating the value of the filter status variable to true.
                filter_on = True

                # Update the counter value to zero.
                counter['RIGHT_HIGH_FIVE_SIGN'] = 0

        # Otherwise if the gesture of any hand in the frame is not SPIDERMAN SIGN.
        else:

            # Update the counter value to zero. As we are counting the consective frames with SPIDERMAN hand gesture.
            counter['RIGHT_HIGH_FIVE_SIGN'] = 0

        ####################################################################################################################

        # Check if any hand is making the HIGH-FIVE hand gesture in the required number of consecutive frames.
        ####################################################################################################################

#         # Check if the gesture of any hand in the frame is HIGH-FIVE SIGN.
#         if any(hand_gesture == "HIGH-FIVE SIGN" for hand_gesture in hands_gestures.values()):

#             # Increment the count of consecutive frames with HIGH-FIVE hand gesture recognized.
#             counter['HIGH-FIVE SIGN'] += 1

#             # Check if the counter is equal to the required number of consecutive frames.
#             if counter['HIGH-FIVE SIGN'] == num_of_frames:

#                 # Turn off the filter by updating the value of the filter status variable to False.
#                 filter_on = False

#                 # Update the counter value to zero.
#                 counter['HIGH-FIVE SIGN'] = 0

#         # Otherwise if the gesture of any hand in the frame is not HIGH-FIVE SIGN.
#         else:

#             # Update the counter value to zero. As we are counting the consective frames with HIGH-FIVE hand gesture.
#             counter['HIGH-FIVE SIGN'] = 0

        ####################################################################################################################

         # Check if any hand is making the HIGH-FIVE hand gesture in the required number of consecutive frames.
        ####################################################################################################################

        # Check if the gesture of any hand in the frame is HIGH-FIVE SIGN.
        # 왼손 스탑 사인
        ####################################################################################################################
        if any(hand_gesture == "LEFT_STOP_SIGN" for hand_gesture in hands_gestures.values()):

            # Increment the count of consecutive frames with HIGH-FIVE hand gesture recognized.
            counter['LEFT_STOP_SIGN'] += 1

            # Check if the counter is equal to the required number of consecutive frames.
            if counter['LEFT_STOP_SIGN'] == num_of_frames:

                # Turn off the filter by updating the value of the filter status variable to False.
                filter_on = False

                # Update the counter value to zero.
                counter['LEFT_STOP_SIGN'] = 0

        # Otherwise if the gesture of any hand in the frame is not HIGH-FIVE SIGN.
        else:

            # Update the counter value to zero. As we are counting the consective frames with HIGH-FIVE hand gesture.
            counter['LEFT_STOP_SIGN'] = 0

        ####################################################################################################################

        # 오른손 스탑 사인
        ####################################################################################################################
        if any(hand_gesture == "RIGHT_STOP_SIGN" for hand_gesture in hands_gestures.values()):

            # Increment the count of consecutive frames with HIGH-FIVE hand gesture recognized.
            counter['RIGHT_STOP_SIGN'] += 1

            # Check if the counter is equal to the required number of consecutive frames.
            if counter['RIGHT_STOP_SIGN'] == num_of_frames:

                # Turn off the filter by updating the value of the filter status variable to False.
                filter_on = False

                # Update the counter value to zero.
                counter['RIGHT_STOP_SIGN'] = 0

        # Otherwise if the gesture of any hand in the frame is not HIGH-FIVE SIGN.
        else:

            # Update the counter value to zero. As we are counting the consective frames with HIGH-FIVE hand gesture.
            counter['RIGHT_STOP_SIGN'] = 0

        ####################################################################################################################

    # Check if the filter is turned on.
    if filter_on:

        # Apply the filter by updating the pixel values of the frame at the indexes where the
        # alpha channel of the filter image has the value 255.
        frame[filter_imageBGRA[:, :, -1] ==
              255] = filter_imageBGR[filter_imageBGRA[:, :, -1] == 255]

        ####################################################################################################################

    # Image Capture Functionality.
    ########################################################################################################################

    # Check if the hands landmarks are detected and the gesture of any hand in the frame is V SIGN.

    # 왼손 v 사인
    ####################################################################################################################

    if results.multi_hand_landmarks and any(hand_gesture == "LEFT_V_SIGN" for hand_gesture in hands_gestures.values()):

        # Increment the count of consecutive frames with V hand gesture recognized.
        counter['LEFT_V_SIGN'] += 1

        # Check if the counter is equal to the required number of consecutive frames.
        if counter['LEFT_V_SIGN'] == num_of_frames:

            # Make a border around a copy of the current frame.
            captured_image = cv2.copyMakeBorder(src=frame, top=10, bottom=10, left=10, right=10,
                                                borderType=cv2.BORDER_CONSTANT, value=(255, 255, 255))

            # Capture an image and store it in the disk.
            cv2.imwrite('Captured_Image.png', captured_image)

            # Display a black image.
            cv2.imshow('Selfie-Capturing System',
                       np.zeros((frame_height, frame_width)))

            # Play the image capture music to indicate the an image is captured and wait for 100 milliseconds.
            cv2.waitKey(100)

            # Display the captured image.
            plt.close()
            plt.figure(figsize=[10, 10])
            plt.imshow(frame[:, :, ::-1])
            plt.title("Captured Image")
            plt.axis('off')

            # Update the counter value to zero.
            counter['LEFT_V_SIGN'] = 0

    # Otherwise if the gesture of any hand in the frame is not V SIGN.
    else:

        # Update the counter value to zero. As we are counting the consective frames with V hand gesture.
        counter['LEFT_V_SIGN'] = 0

    ########################################################################################################################

      # 오른손 v 사인
    ####################################################################################################################

    if results.multi_hand_landmarks and any(hand_gesture == "RIGHT_V_SIGN" for hand_gesture in hands_gestures.values()):

        # Increment the count of consecutive frames with V hand gesture recognized.
        counter['RIGHT_V_SIGN'] += 1

        # Check if the counter is equal to the required number of consecutive frames.
        if counter['RIGHT_V_SIGN'] == num_of_frames:

            # Make a border around a copy of the current frame.
            captured_image = cv2.copyMakeBorder(src=frame, top=10, bottom=10, left=10, right=10,
                                                borderType=cv2.BORDER_CONSTANT, value=(255, 255, 255))

            # Capture an image and store it in the disk.
            cv2.imwrite('Captured_Image.png', captured_image)

            # Display a black image.
            cv2.imshow('Selfie-Capturing System',
                       np.zeros((frame_height, frame_width)))

            # Play the image capture music to indicate the an image is captured and wait for 100 milliseconds.
            cv2.waitKey(100)

            # Display the captured image.
            plt.close()
            plt.figure(figsize=[10, 10])
            plt.imshow(frame[:, :, ::-1])
            plt.title("Captured Image")
            plt.axis('off')

            # Update the counter value to zero.
            counter['RIGHT_V_SIGN'] = 0

    # Otherwise if the gesture of any hand in the frame is not V SIGN.
    else:

        # Update the counter value to zero. As we are counting the consective frames with V hand gesture.
        counter['RIGHT_V_SIGN'] = 0

    ########################################################################################################################

    # Check if we have captured an image.
    if captured_image is not None:

        # Resize the image to the 1/5th of its current width while keeping the aspect ratio constant.
        captured_image = cv2.resize(
            captured_image, (frame_width//5, int(((frame_width//5) / frame_width) * frame_height)))

        # Get the new height and width of the image.
        img_height, img_width, _ = captured_image.shape

        # Overlay the resized captured image over the frame by updating its pixel values in the region of interest.
        frame[10: 10+img_height, 10: 10+img_width] = captured_image

    # Display the frame.
    cv2.imshow('Selfie-Capturing System', frame)

    # Wait for 1ms. If a key is pressed, retreive the ASCII code of the key.
    k = cv2.waitKey(1) & 0xFF

    # Check if 'ESC' is pressed and break the loop.
    if(k == 27):
        break

# Release the VideoCapture Object and close the windows.
camera_video.release()
cv2.destroyAllWindows()

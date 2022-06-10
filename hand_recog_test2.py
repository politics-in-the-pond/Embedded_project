import socket
import time
import cv2
import numpy as np
import threading
import sys

gesture = "0"
duty = 0
recordcnt = 0
mode = 0
direction = "S"


def setCount(cnt):
    global recordcnt
    recordcnt = cnt


def setDirection(d):
    global direction
    direction = d


def hand():

    cap = cv2.VideoCapture(0)
    cap.set(3, 1080)
    cap.set(4, 720)

    while True:

        ret, frame = cap.read()

        if not ret:
            print('camera_error')
            break

        dst = frame.copy()
        test = cv2.cvtColor(dst, cv2.COLOR_BGR2YCrCb)
        mask_hand = cv2.inRange(test, np.array(
            [0, 132, 77], dtype="uint8"), np.array([255, 173, 133], dtype="uint8"))
        blur = cv2.blur(mask_hand, (2, 2))
        ret, thr = cv2.threshold(blur, 132, 255, cv2.THRESH_BINARY)
        contours, hierachy = cv2.findContours(
            thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = 0
        nowdirection = "S"

        if contours:
            contours = max(contours, key=lambda x: cv2.contourArea(x))
            mmt = cv2.moments(contours)
            cx = int(mmt['m10']/mmt['m00'])
            hull = cv2.convexHull(contours, returnPoints=False)
            defects = cv2.convexityDefects(contours, hull)
            #cv2.drawContours(dst, contours, -1, (0, 255, 255), 2)
            if defects is not None:
                cnt = 0
                for i in range(defects.shape[0]):
                    startd, endd, fard, d = defects[i][0]
                    start = tuple(contours[startd][0])
                    end = tuple(contours[endd][0])
                    far = tuple(contours[fard][0])
                    a = np.sqrt((end[0] - start[0]) ** 2 +
                                (end[1] - start[1]) ** 2)
                    b = np.sqrt((far[0] - start[0]) ** 2 +
                                (far[1] - start[1]) ** 2)
                    c = np.sqrt((end[0] - far[0]) ** 2 +
                                (end[1] - far[1]) ** 2)
                    angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))

                    if angle >= np.pi / 10 and angle <= np.pi / 2.3:
                        cnt += 1
                        cv2.circle(dst, far, 4, [0, 0, 255], -1)
                if cnt > 0:
                    cnt = cnt+1

        else:
            cnt = 0

        if cnt > 3 and cnt < 6:
            if recordcnt <= 3:
                print("J")
                sys.stdout.flush()

        if cx > 417:
            nowdirection = "L"
        elif cx > 214:
            nowdirection = "S"
        else:
            nowdirection = "R"

        if nowdirection != direction:
            print(nowdirection)
            sys.stdout.flush()

        setDirection(nowdirection)

        setCount(cnt)

        # cv2.putText(dst, str(round(recordcnt)), (0, 130),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
        # 왼쪽
        cv2.putText(dst, "<=", (45, 300), cv2.FONT_HERSHEY_SIMPLEX,
                    3, (255, 255, 255), 2, cv2.LINE_AA)

        # 가운데
        cv2.putText(dst, "O", (415, 300), cv2.FONT_HERSHEY_SIMPLEX,
                    3, (255, 255, 255), 2, cv2.LINE_AA)

        # 오른쪽
        cv2.putText(dst, "=>", (755, 300), cv2.FONT_HERSHEY_SIMPLEX,
                    3, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow('dst', dst)
        #cv2.imshow('ret', thr)
        #cv2.imshow('key', test)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


hand()

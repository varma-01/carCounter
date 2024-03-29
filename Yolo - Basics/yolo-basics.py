import cvzone
from ultralytics import YOLO
import cv2
import math
from sort import *

# cap = cv2.VideoCapture(0) # FOR WEBCAM
cap = cv2.VideoCapture("Videos/traffic1.mp4")  # FOR VIDEOS
cap.set(3, 1280)
cap.set(4, 720)

model = YOLO('../Yolo-Weights/yolov8n.pt')

mask = cv2.imread("mask.png")

# Tracking
tracker = Sort(max_age=20)

limits = [50, 315, 573, 315]
totalCount = []

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]



while True:
    success, img = cap.read()
    imgRegion = cv2.bitwise_and(img, mask)

    results = model(imgRegion, stream=True)
    cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 0, 255), thickness=5)

    detections = np.empty((0, 5))

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bounding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Confidence Level
            conf = math.ceil((box.conf[0]*100))/100

            #Class Names
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass == 'car' or currentClass == "bus" or currentClass == "truck" and conf > 0.5:
                # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 2)
                cvzone.putTextRect(img, f'{currentClass}  {conf}', (max(0, x1), max(30, y1)), scale=1.2, thickness=2)
                currentArray = np.array([x1,y1, x2, y2, conf])
                detections = np.vstack((detections, currentArray))

    resultsTracker = tracker.update(detections)

    for result in resultsTracker:
        x1, y1, x2, y2, id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        w, h = x2-x1, y2-y1

        cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 0))
        # cvzone.putTextRect(img, f' {int(id)}', (max(0, x1), max(30, y1)), scale=1.2, thickness=2)

        cx, cy = x1+w//2, y1+h//2
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        if limits[0]<cx<limits[2] and limits[1]-20<cy<limits[1]+20:
            if totalCount.count(id) == 0:
                totalCount.append(id)
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), thickness=5)

    cvzone.putTextRect(img, f'Count: {len(totalCount)}', (50, 50), scale=1.2, thickness=2)

    cv2.imshow("WebCam", img)
    # cv2.imshow("WebCam", imgRegion)
    cv2.waitKey(0)





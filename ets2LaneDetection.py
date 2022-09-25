"""
LaneDetection bridge for Euro-Truck-Simulator-2-Lane-Assist
Original file : ibaiGorordo @ https://github.com/ibaiGorordo/Ultrafast-Lane-Detection-Inference-Pytorch-
Modified to be used with ETS2 : Tumppi066 @ https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist
"""


# Rest of the imports
from ast import Load
from statistics import mode
import cv2
import time
from mss import mss
import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageColor
import json
from ultrafastLaneDetector import UltrafastLaneDetector, ModelType

# CHANGE THESE VALUES IN THE SETTINGS.JSON FILE
# THEY WILL NOT UPDATE IF CHANGED HERE
w, h = 1280, 720
x, y = 0, 0
useDirectX = False
DXframerate = 0
steeringOffset = -150
showPreview = True
previewOnTop = True
computeGreenDots = True
drawSteeringLine = True
showLanePoints = True
showLanes = True
# Default model
model_path = "models/tusimple_34.pth" # When changing this (Keep the "")...
model_type = ModelType.TUSIMPLE # Change the model type (ModelType.CULANE or ModelType.TUSIMPLE) and...
model_depth = "34" # Change the depth of the model (Keep the "")
useGPUByDefault = False
color = "00bfff"

def SaveSettings(category, name, value):
    # This function is used to save the settings.
    file = "settings.json"
    data = json.load(open(file))
    data[category][name] = value
    with open(file, 'w') as f:
        json.dump(data, f, indent=6)

def LoadSettings(onlyGeneral = False):
    global steeringOffset
    global showPreview
    global previewOnTop
    global computeGreenDots
    global drawSteeringLine
    global model_path
    global model_type
    global model_depth
    global useGPUByDefault
    global w
    global h
    global x
    global y
    global useDirectX
    global DXframerate
    global showLanePoints
    global showLanes
    global color

    file = "settings.json"
    data = json.load(open(file))
    
    if not onlyGeneral:
        # Screen settings
        w = data["screenCapture"]["width"]
        h = data["screenCapture"]["height"]
        x = data["screenCapture"]["x"]
        y = data["screenCapture"]["y"]
        useDirectX = data["screenCapture"]["useDirectX"]
        DXframerate = data["screenCapture"]["DXframerate"]

        # Model settings
        model_path = data["modelSettings"]["modelPath"]

        if(data["modelSettings"]["modelType"] == "culane"): model_type = ModelType.CULANE
        elif(data["modelSettings"]["modelType"] == "tusimple"): model_type = ModelType.TUSIMPLE
        else: print("Invalid model type")

        model_depth = data["modelSettings"]["modelDepth"]
        useGPUByDefault = data["modelSettings"]["useGPU"]
        # Lane assist settings
        steeringOffset = data["controlSettings"]["steeringOffset"]
        previewOnTop = data["generalSettings"]["previewOnTop"]
        computeGreenDots = data["generalSettings"]["computeGreenDots"]
        drawSteeringLine = data["generalSettings"]["drawSteeringLine"]
        showLanePoints = data["generalSettings"]["showLanePoints"]
        showLanes = data["generalSettings"]["fillLane"]
        color = data["generalSettings"]["laneColor"]
        print("\033[92mSuccessfully loaded all settings \033[00m")
    else:
        # General settings
        steeringOffset = data["controlSettings"]["steeringOffset"]
        previewOnTop = data["generalSettings"]["previewOnTop"]
        computeGreenDots = data["generalSettings"]["computeGreenDots"]
        drawSteeringLine = data["generalSettings"]["drawSteeringLine"]
        showLanePoints = data["generalSettings"]["showLanePoints"]
        showLanes = data["generalSettings"]["fillLane"]
        color = data["generalSettings"]["laneColor"]
        print("\033[92mSuccessfully loaded general settings \033[00m")


LoadSettings()

# Do not change these.
if not useDirectX:
    monitor = {'top': y, 'left': x, 'width': w, 'height': h}
    sct = mss()
else:
    import dxcam
    
    left, top = x, y
    right, bottom = left + w, top + h
    
    monitor = (left,top,right,bottom)

    camera = dxcam.create(region=monitor, output_color="BGR")
    camera.start(target_fps=DXframerate)


close = False
isIndicating = 0 # 1 = Right, 2 = Left, 0 = None

# Initialize lane detection model with default settings
try:
    lane_detector = UltrafastLaneDetector("models/" + model_path, model_type, use_gpu=useGPUByDefault, modelDepth = model_depth)
except Exception as e:
    print(e.args)
    print("\033[93mDefault model not installed, please select one in the settings\033[00m")

def LoadModelFromSettings():
    global model_path
    global model_type
    global model_depth
    global useGPUByDefault
    global lane_detector

    file = "settings.json"
    data = json.load(open(file))

    # Model settings
    model_path = data["modelSettings"]["modelPath"]
    useGPUByDefault = data["modelSettings"]["useGPU"]

    if "tusimple" in model_path:
        model_type = ModelType.TUSIMPLE
    elif "culane" in model_path:
        model_type = ModelType.CULANE
    
    model_depth = (model_path.split("_")[1].split(".")[0])

    with open("settings.json", "w") as f:
        if model_type == ModelType.TUSIMPLE:
            data["modelSettings"]["modelType"] = "tusimple"
        elif model_type == ModelType.CULANE:
            data["modelSettings"]["modelType"] = "culane"
        
        data["modelSettings"]["modelDepth"] = model_depth

        json.dump(data, f, indent=6)

    lane_detector = UltrafastLaneDetector("models/" + model_path, model_type, use_gpu=useGPUByDefault, modelDepth = str(model_depth))



def ChangeVideoDimension(value, value2):
    # This function is used to change the video dimension.
    global w
    global h
    global x
    global y
    global monitor
    global camera
    value[0] = int(value[0])
    value[1] = int(value[1])
    value2[0] = int(value2[0])
    value2[1] = int(value2[1])
    w = value[0]
    h = value[1]
    x,y = value2
    if useDirectX:
        left, top = x, y
        right, bottom = left + w, top + h
        monitor = (left,top,right,bottom)
        camera.stop()
        del camera
        camera = dxcam.create(region=monitor, output_color="BGR")
        camera.start(target_fps=DXframerate)

    else:
        monitor = {'top': y, 'left': x, 'width': w, 'height': h}

    SaveSettings("screenCapture", "width", w)
    SaveSettings("screenCapture", "height", h)
    SaveSettings("screenCapture", "x", x)
    SaveSettings("screenCapture", "y", y)

def UpdateDXcam():
    global w
    global h
    global x
    global y
    global DXframerate
    global camera

    # Load new settings
    file = "settings.json"
    data = json.load(open(file))
    w = data["screenCapture"]["width"]
    h = data["screenCapture"]["height"]
    x = data["screenCapture"]["x"]
    y = data["screenCapture"]["y"]
    DXframerate = data["screenCapture"]["DXframerate"]

    # Update camera
    left, top = x, y
    right, bottom = left + w, top + h
    monitor = (left,top,right,bottom)
    camera.stop()
    del camera
    camera = dxcam.create(region=monitor, output_color="BGR")
    camera.start(target_fps=DXframerate)

def ChangeLaneAssist(value):
    # Update steering offset
    global steeringOffset
    steeringOffset = value
    SaveSettings("controlSettings", "steeringOffset", steeringOffset)
    

# Make the lane detection preview window.
cv2.namedWindow("Detected lanes", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Detected lanes", w, h)
if(previewOnTop):
    cv2.setWindowProperty("Detected lanes", cv2.WND_PROP_TOPMOST, 1)

# I like to put all my variables outside the function
# these should not be changed.  
difference = 0
fps = 0
image = None
def UpdateLanes():
    global difference
    global fps
    global image
    global camera
    startTime = time.time_ns() # For FPS calculation
    if not useDirectX:
        frame = np.array(Image.frombytes('RGB', (w,h), sct.grab(monitor).rgb)) # Get a new frame
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convert to BGR (OpenCV uses BGR, rather than RGB)
    else:
        frame = camera.get_latest_frame() # Get a new frame

    # Detect the lanes (input image, draw dots, draw lane)
    laneColor = ImageColor.getrgb(color)
    laneColor = (laneColor[2], laneColor[1], laneColor[0])
    output_img = lane_detector.detect_lanes(frame, showLanePoints, showLanes, color=laneColor)
    try:
        # Compute the distance from the center of the screen to the average between lanes
        difference = (lane_detector.lanes_points[1][0][0] + lane_detector.lanes_points[2][0][0]) / 2
        difference = difference - (w / 2)
        difference = difference + steeringOffset
    except Exception as ex:
        pass
    
    # This will show green dots in the center of the lanes.
    # It's just a lot of comparing and math, I don't really want to explain.
    lane1Points = None
    lane2Points = None
    drivingPoints = None
    if computeGreenDots:
        try:
            lane1Points = []
            lane2Points = []
            drivingPoints = []
            for lane_num,lane_points in enumerate(lane_detector.lanes_points):
                for lane_point in lane_points:
                    if(lane_num == 1):
                        lane1Points.append(lane_point)
                    elif(lane_num == 2):
                        lane2Points.append(lane_point)
            if(len(lane1Points) > len(lane2Points)):
                for i in range(len(lane2Points)):
                    if i % 10 != 0:
                        continue
                    if(lane1Points[i][0] != 0):
                        cv2.circle(output_img, (int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]), 5, (0, 255, 0), -1)
                        drivingPoints.append((int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]))
            else:
                for i in range(len(lane1Points)):
                    if i % 10 != 0:
                        continue
                    if(lane1Points[i][0] != 0):
                        cv2.circle(output_img, (int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]), 5, (0, 255, 0), -1)
                        drivingPoints.append((int((lane1Points[i][0] + lane2Points[i][0]) / 2), lane1Points[i][1]))
        except Exception as ex:
            pass
    
    if drawSteeringLine:
        try:
            cv2.line(output_img, (int(w/2 + steeringOffset), drivingPoints[0][1]), (drivingPoints[0][0], drivingPoints[0][1]), (0, 0, 255), 2)
        except:
            pass
    
    endTime = time.time_ns()
    fps = 1000000000 / (endTime - startTime)
    cv2.putText(output_img, "FPS : " + str(round(fps, 0)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2) # Overlay FPS on the image.
    # Tell the user if we are indicating left or right.
    if(isIndicating == 1):
        cv2.putText(output_img, "Indicating Right", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if(isIndicating == 2):
        cv2.putText(output_img, "Indicating Left", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # Show preview
    image = output_img
    if(showPreview):
        cv2.imshow("Detected lanes", output_img)
    else:
        cv2.destroyAllWindows()
        
    if cv2.waitKey(1) & 0xFF == ord('q') or close:
        del camera
        exit()

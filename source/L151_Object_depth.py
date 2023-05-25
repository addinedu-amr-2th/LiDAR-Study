import pyrealsense2 as rs
import numpy as np
import cv2
import supervision as sv
from ultralytics import YOLO

# Set threshold for depth value
depth_threshold = 1  # Set your desired threshold value here

def start_lidar():

    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    if device_product_line == 'L515C':
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    return pipeline

def box_gen(frame, detections, labels):
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )
    
    frame_box = box_annotator.annotate(
        scene=frame,
        detections=detections,
        labels=labels
            )
    return frame_box

def coordi_gen(detections):
    # Bounding BOX 좌표 중심 구하기
    append_on = False
    global coords

    if len(detections.xyxy) == 0:  # 감지된 물체가 없는 경우
        print("No objects detected.")
        center_x = 0
        center_y = 0 
    else:  # 감지된 물체가 있는 경우
        x1, y1, x2, y2 = detections.xyxy[0]

        center_x = (x1+x2)//2
        center_y = (y1+y2)//2
    return center_x, center_y

def main():
    pipeline = start_lidar()
    model = YOLO("yolov8n.pt")

    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))
        
        result = model(color_image)[0]

        detections = sv.Detections.from_yolov8(result)

        coord = coordi_gen(detections)
    
        # coord 변수에서 인덱스를 사용하여 center_x와 center_y 값 추출
        center_x = coord[0]
        center_y = coord[1]


        # Get depth value at the center of the image
        depth_width, depth_height = depth_frame.get_width(), depth_frame.get_height()
        if center_x >= 0 and center_x < depth_width and center_y >= 0 and center_y < depth_height:
            depth_center = depth_frame.get_distance(int(center_x), int(center_y))
        else:
            depth_center = 0.0 # 예외처리
        
        # Check if depth value is below the threshold
        if depth_center < depth_threshold:
            print("Object is too close! Stop the vehicle.")
            # Perform action to stop the vehicle, e.g. send a stop command to the motor control


        labels = [
            f"{model.model.names[class_id]} {depth_center:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]

        frame_box = box_gen(images, detections, labels)

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', frame_box)

        # Exit loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()
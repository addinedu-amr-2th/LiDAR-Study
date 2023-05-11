## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
# 파이프 라인을 래핑하여 추가 기능을 제공하는 파이프 라인 래퍼(wrapper) 객체를 반환
# 파이프 라인에 추가적인 구성 옵션을 쉽게 추가하거나, 여러 파이프 라인을 동시에 실행하거나, 파이프 라인을 비동기식으로 실행하는 등의 작업을 수행할 수 있음

pipeline_profile = config.resolve(pipeline_wrapper)
#  `pipeline_wrapper`를 사용하여 가져온 파이프라인 구성을 `config.resolve`를 사용하여 파이프라인 프로파일로 해석
#  만약 `config.resolve()`이 없으면 파이프라인 정의되지 않기 때문에 프로그램이 파이프라인을 시작할 수 없음. `config.enable_stream()` 함수를 사용하여 스트림을 구성할 수는 있지만, 이는 파이프라인 전체의 구성을 정의하는 것이 아니라 개별 스트림만 구성하는 것
#  `config.resolve()` 함수를 사용하여 파이프라인 구성을 해석하면, 구성이 확실히 정의되어 파이프라인을 시작할 수 있음.
#  즉, pipeline_wrapper()로 파이프라인의 추가적인 기능을 실행하려면 `config.resolve`를 사용해야 함.

device = pipeline_profile.get_device()
# get_device()는 RealSense 카메라 장치를 가져오는 데 사용됨

device_product_line = str(device.get_info(rs.camera_info.product_line))
# `rs.camera_info.product_line`은 카메라 정보에서 제품 라인을 나타내는 하나의 매개변수
#     - D400, T200  등의 모델명의 정보 등을 읽어 온다는 느낌인듯
# `device.get_info()`는 RealSense 카메라에서 제공하는 여러 가지 정보 중에서, 특정 정보를 가져오기 위한 메서드.  다음과 같은 정보들을 가져올 수 있다.
#     - `rs.camera_info.name`: 카메라의 이름 (예: "Intel RealSense D435i")
#     - `rs.camera_info.serial_number`: 카메라의 일련번호 (예: "808412060004")
#     - `rs.camera_info.firmware_version`: 카메라의 펌웨어 버전 (예: "05.12.06.00")
#     - `rs.camera_info.physical_port`: 카메라가 연결된 물리적인 포트 (예: "3-3.3")
#     - `rs.camera_info.product_id`: 카메라의 제품 ID (예: 0x0B07)
#     - `rs.camera_info.sensor_type`: 카메라에서 사용되는 센서 타입 (예: "RGB+Depth")
#     - `rs.camera_info.product_line`: 카메라의 제품 라인 (예: "D400")
#     - `rs.camera_info.asic_serial_number`: 카메라의 ASIC(응용통합회로) 일련번호 (예: "Y734071500416")


found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)
# `device.sensors`는 RealSense 카메라의 모든 센서에 대한 정보를 제공하는 객체
# 따라서 해당 코드는 현재 사용되는 카메라(라이다 등)에 "RGB Camera"라는 이름을 가진 색상 센서가 없으면 종료되도록 코딩

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L515C':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# L515C 제품 라인과 그 외 제품 라인에 대해 서로 다른 색상 스트림 설정
#이러한 이유는 각 제품 라인마다 색상 센서의 해상도가 달라서임


# Start streaming
pipeline.start(config)

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        #wait_for_frames() 새로운 프레임이 나타날 때까지 기다림.

        depth_frame = frames.get_depth_frame()
        # frames.get_depth_frame() : 깊이 정보를 가져옴

        color_frame = frames.get_color_frame()
        #color_frame = frames.get_color_frame() : 색상 정보를 가져옴

        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # `cv2.convertScaleAbs()`함수는 입력 이미지 데이터의 값(여기선 깊이 값)을 스케일링하고 절대값을 취한 후, uint8 자료형으로 변환함
        # `alpha`는 결과값의 비율을 조정하는 데 사용됨. 이 값이 클수록 결과 이미지의 밝기가 높아지고, 작을수록 어두워짐
        # `cv2.COLORMAP_JET`은 OpenCV에서 제공하는 colormap 중 하나. 0~255 사이의 값에 대해 다음과 같은 색상을 적용
        #     - 값이 0일 때: 파랑색
        #     - 값이 128일 때: 녹색
        #     - 값이 255일 때: 빨강색


        depth_colormap_dim = depth_colormap.shape
        # depth_colormap.shape은 깊이 맵 이미지의 형태를 나타내는 튜플. 이 튜플의 첫 번째 요소는 이미지의 높이(height)를, 두 번째 요소는 이미지의 너비(width)를 나타냄. 
        # 따라서 depth_colormap_dim변수에는 depth_colormap이미지의 높이와 너비가 저장됨.
        
        color_colormap_dim = color_image.shape
        # color_image.shape도 마찬가지로 color_image이미지의 형태를 나타내는 튜플. 
        # 이 경우에도 첫 번째 요소는 이미지의 높이를, 두 번째 요소는 이미지의 너비를 나타냄. 
        # 따라서 color_colormap_dim변수에는 color_image이미지의 높이와 너비가 저장.
    

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
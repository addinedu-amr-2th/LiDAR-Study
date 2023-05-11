import pyrealsense2 as rs

try:
    # Create a context object. This object owns the handles to all connected realsense devices
    pipeline = rs.pipeline()
    ## 파이프라인은 장치와 컴퓨터 비전 처리 모듈 간의 사용자 Interaction을 간단하게 해줌.
    ## 어플리케이션이 컴퓨터 비전 모듈의 출력과 장치의 출력 데이터에만 집중하도록 함.
    ## 라이다의 데이터(이미지)를 가져오는 함수인 느낌.

    # Configure streams
    config = rs.config()
    ## Config는 사용자에게 필터를 설정하고 장치의 파이프라인 요구 사항과 충돌하지 않는지 테스트할 수 있는 방법을 제공
    ## 사용자는 장치를 명시적으로 선택하고 스트리밍이 시작되기 전에 컨트롤을 수정하기 위해 구성 필터 및 파이프라인에 대해 일치하는 장치를 찾을 수 있습니다.
    ## 사용할 라이다 선택하고 그 라이다에 대한 전반적인 설정 하는 함수 느낌.
    
    # 깊이
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30) ## 크기 , 포맷, 프레임 설정
    ## stream.depth 이므로 깊이를 가져옴. stream.color, stream.infrared를 통해 색깔, 인프라레드(적외선) 등을 가져올 수 있음
    
    # # 색깔
    # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # # 적외선
    # config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
    
    #################################################################################################
    # - rs.stream.‘스트림 유형’: 활성화할 스트림 유형을 지정. (color, infraread)
    # - 1: 스트림의 인덱스를 지정. 이 경우, 인프라레드 카메라 중 첫 번째 카메라를 선택. (인프라레드에만 해당)
    # - 640: 이미지의 너비를 지정. 이 경우, 640 픽셀.
    # - 480: 이미지의 높이를 지정. 이 경우, 480 픽셀.
    # - rs.format.y8: 이미지의 색상 포맷을 지정. 이 경우, 8비트 그레이스케일(y8). 
    #                 이는 이미지의 각 픽셀이 8비트로 표현되며, 색상 정보가 없으며 그레이스케일 값만 있음을 의미.
    # - 30: 스트림의 프레임 속도를 지정. 이 경우, 초당 30프레임.
    #################################################################################################

    # Start streaming
    pipeline.start(config) ## config에서 적용한 프레임 등의 설정을 적용하여 스트리밍 시작

    while True:
        # This call waits until a new coherent set of frames is available on a device
        # Calls to get_frame_data(...) and get_frame_timestamp(...) on a device will return stable values until wait_for_frames(...) is called
        frames = pipeline.wait_for_frames()
        ## 새로운 프레임을 사용할 때까지 기다림. 이 함수가 호출되지 않는 상태에서 생성된 프레임은 삭제됨.
        
        depth = frames.get_depth_frame()
        # 깊이 데이터 프레임을 가져오는 메서드
        if not depth: 
            continue

        # Print a simple text-based representation of the image, by breaking it into 10x20 pixel regions and approximating the coverage of pixels within one meter
        coverage = [0]*64
        for y in range(480):
            for x in range(640):
                dist = depth.get_distance(x, y)
                # 픽셀 x,y 위치에서 깊이 데이터를 가져오는 메소드
                if 0 < dist and dist < 1:
                    coverage[x//10] += 1
            
            if y%20 is 19:
                line = ""
                for c in coverage:
                    line += " .:nhBXWW"[c//25]
                coverage = [0]*64
                print(line)
        exit(0)
    
except Exception as e:
    print(e)
    pass
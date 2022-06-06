import client
import time


if __name__ == '__main__':
    video_types = ['DIVX', 'XVID', 'MJPG', 'X264', 'WMV1', 'WMV2']
    for video_type in video_types:
        client.process_webcam_video(1000, video_type, output_name="%s_200.avi" % video_type, max_time=200)
        time.sleep(2)

import cv2
import numpy as np

from .cache import get_cached, set_cached


def frames(file_name: str, step: int = 1):
    current_frame = 0

    cap = cv2.VideoCapture(file_name)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("total_frames", total_frames)

    while cap.isOpened() and current_frame < total_frames:
        frame_data = get_cached(file_name, f"frame_{current_frame:08}.png")
        if frame_data:
            array = np.frombuffer(frame_data, dtype=np.uint8)

            yield cv2.imdecode(array, cv2.IMREAD_UNCHANGED)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

            ret, frame = cap.read()
            if not ret:
                break
            frame_data = cv2.imencode(".png", frame)[1].tobytes()
            set_cached(file_name, f"frame_{current_frame:08}.png", frame_data)
            set_cached(file_name, "frame_count", str(current_frame).encode())

            yield frame
        current_frame += step

    cap.release()

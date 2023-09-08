from matplotlib import pyplot as plt
from video.frame_extractor import frames
from video.ocr import ocr

file_name = "video.mkv"

skip = 3700

# Usage
for i, frame in enumerate(frames(file_name, skip)):
    frame, results = ocr(frame)
    print(i, results["text"])
    plt.imshow(frame)
    plt.show()

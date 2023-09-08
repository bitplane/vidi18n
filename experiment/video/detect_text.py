import cv2


class TextDetector:
    def __init__(self, model_path, confThreshold=0.0001, nmsThreshold=0.1):
        self.model = cv2.dnn.TextDetectionModel_EAST(model_path)
        self.model.setConfidenceThreshold(confThreshold).setNMSThreshold(nmsThreshold)

        self.detScale = 1.0
        self.detInputSize = (320, 320)
        self.detMean = (123.68, 116.78, 103.94)
        self.swapRB = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del self.model

    def detect(self, frame):
        self.model.setInputParams(
            scale=self.detScale,
            size=self.detInputSize,
            mean=self.detMean,
            swapRB=self.swapRB,
        )

        # Text Detection
        results, _ = self.model.detect(frame)

        # Draw bounding boxes
        for box in results:
            top_left = tuple(box[0])
            bottom_right = tuple(box[2])
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        return frame, results

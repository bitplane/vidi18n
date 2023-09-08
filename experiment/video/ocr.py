import cv2
import pytesseract

# lang = "eng+chi_sim"
lang = "chi_sim"


def ocr(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(
        gray_frame,
        output_type=pytesseract.Output.DICT,
        lang="chi_sim"
    )
    n_boxes = len(data["level"])
    for i in range(n_boxes):
        (x, y, w, h) = (
            data["left"][i],
            data["top"][i],
            data["width"][i],
            data["height"][i],
        )
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return frame, data

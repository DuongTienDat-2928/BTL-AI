# utils.py
import cv2
import numpy as np
from PIL import Image, ExifTags

def load_image_unicode(path):
    """Đọc ảnh có tên file Unicode và tự xoay theo EXIF nếu có"""
    pil_img = Image.open(path)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        exif = pil_img._getexif()
        if exif is not None:
            if exif.get(orientation) == 3:
                pil_img = pil_img.rotate(180, expand=True)
            elif exif.get(orientation) == 6:
                pil_img = pil_img.rotate(270, expand=True)
            elif exif.get(orientation) == 8:
                pil_img = pil_img.rotate(90, expand=True)
    except Exception:
        pass
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def draw_results(img, results):
    """Vẽ bounding box và thông tin tuổi/giới tính lên ảnh"""
    for i, res in enumerate(results, start=1):
        region = res.get("region")
        if region:
            x, y, w, h = region["x"], region["y"], region["w"], region["h"]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = f"Face{i}: {res['dominant_gender']} ({res['gender_confidence']:.1f}%) - Age {res['age']}"
            cv2.putText(img, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return img

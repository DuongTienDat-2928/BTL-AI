import cv2
import numpy as np

def read_image_unicode(path):
    """
    Đọc ảnh từ đường dẫn có Unicode.
    """
    try:
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Lỗi đọc ảnh: {str(e)}")
        return None

def resize_image(image, max_size=640):
    """
    Resize ảnh để giảm kích thước.
    """
    h, w = image.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)))
    return image

def draw_results_on_image(image, x, y, w, h, gender_vn, age):
    """
    Vẽ bounding box và text lên ảnh.
    """
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(image, f"{gender_vn}, {age}", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

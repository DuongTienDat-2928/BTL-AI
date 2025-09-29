import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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
    Vẽ bounding box và text Unicode lên ảnh bằng Pillow.
    """
    # Vẽ khung bằng OpenCV
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Chuyển sang PIL để vẽ text Unicode
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    try:
        # Font Unicode (chỉnh path nếu cần)
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    text = f"{gender_vn}, {age}"
    draw.text((x, y - 30), text, font=font, fill=(0, 255, 0))

    # Trả lại ảnh về OpenCV (BGR)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

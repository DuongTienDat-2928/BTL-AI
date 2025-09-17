from deepface import DeepFace

def analyze_face(image, backend="retinaface"):
    """
    Phân tích khuôn mặt bằng DeepFace.
    Trả về list kết quả (có thể chứa nhiều khuôn mặt).
    """
    return DeepFace.analyze(
        img_path=image,
        actions=['age', 'gender'],
        enforce_detection=True,
        detector_backend=backend
    )

def compute_age_and_gender(result):
    """
    Tính toán tuổi và giới tính từ kết quả DeepFace.
    """
    age = int(result['age'])
    gender = result['dominant_gender']
    gender_vn = "Nữ" if gender == "Woman" else "Nam"

    # Tinh chỉnh tuổi cho trẻ em
    if age < 18:
        age = max(1, min(age, 17))

    return age, gender_vn

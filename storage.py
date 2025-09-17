import json
from tkinter import messagebox

def save_results_to_json(images_data, file_name="face_analysis_results.json"):
    """
    Lưu danh sách kết quả phân tích vào file JSON.
    """
    if not images_data:
        messagebox.showwarning("Cảnh báo", "Không có kết quả để lưu!")
        return

    results = []
    for _, file_name_img, info_text in images_data:
        lines = info_text.split("\n")
        face_info = next((line for line in lines if "Khuôn mặt" in line), None)
        if face_info:
            parts = face_info.split(", ")
            age = parts[0].split(": ")[1]
            gender = parts[1].split(": ")[1]
            results.append({
                "file_name": file_name_img,
                "age": age,
                "gender": gender
            })
        else:
            results.append({
                "file_name": file_name_img,
                "age": None,
                "gender": None,
                "error": info_text
            })

    try:
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Thành công", f"Kết quả đã được lưu vào {file_name}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file JSON: {str(e)}")

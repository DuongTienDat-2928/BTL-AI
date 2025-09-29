import json
from tkinter import messagebox

def save_results_to_json(images_data, file_name="face_analysis_results.json"):
    """
    Lưu tất cả kết quả phân tích (nhiều ảnh) vào file JSON.
    """
    if not images_data:
        messagebox.showwarning("Cảnh báo", "Không có kết quả để lưu!")
        return

    results = []
    for _, file_name_img, info_text in images_data:
        age, gender = None, None

        # Parse từ info_text
        lines = info_text.split("\n")
        for line in lines:
            if "Tuổi" in line:
                try:
                    age = int(line.split(":")[1].strip())
                except:
                    age = None
            elif "Giới tính" in line:
                gender = line.split(":")[1].strip()

        results.append({
            "file_name": file_name_img,
            "age": age,
            "gender": gender
        })

    try:
        # 🚀 Lưu toàn bộ danh sách, không bị ghi đè mỗi ảnh
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Thành công", f"Tất cả kết quả đã được lưu vào {file_name}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file JSON: {str(e)}")

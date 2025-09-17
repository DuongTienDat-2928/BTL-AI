import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from analyzer import analyze_face, compute_age_and_gender
from image_utils import read_image_unicode, resize_image, draw_results_on_image
from storage import save_results_to_json
from camera import CameraHandler

class FaceAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phân tích khuôn mặt - Tuổi & Giới tính")

        # Giao diện
        self.label = tk.Label(root, text="Chọn ảnh hoặc mở camera")
        self.label.pack(pady=10)

        self.btn_select = tk.Button(root, text="Chọn ảnh", command=self.load_images)
        self.btn_select.pack(pady=5)

        self.btn_camera = tk.Button(root, text="Mở Camera", command=self.toggle_camera)
        self.btn_camera.pack(pady=5)

        self.btn_save = tk.Button(root, text="Lưu kết quả (JSON)", command=lambda: save_results_to_json(self.images_data))
        self.btn_save.pack(pady=5)

        self.backend_label = tk.Label(root, text="Chọn backend phát hiện khuôn mặt")
        self.backend_label.pack(pady=5)
        self.backend_var = tk.StringVar(value="retinaface")
        self.backend_menu = tk.OptionMenu(root, self.backend_var, "retinaface", "ssd", "mtcnn", "dlib")
        self.backend_menu.pack(pady=5)

        self.canvas = tk.Canvas(root, width=600, height=400)
        self.canvas.pack(pady=10)

        self.thumb_frame = tk.Frame(root)
        self.thumb_frame.pack(pady=5)

        self.result_text = tk.Text(root, height=15, width=70)
        self.result_text.pack(pady=10)

        # Dữ liệu
        self.images_data = []
        self.photo_refs = []
        self.current_photo = None

        # Camera
        self.camera = CameraHandler()
        self.camera_photo = None

    def load_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_paths:
            self._clear_results()
            self.result_text.insert(tk.END, "Không có file nào được chọn!\n")
            return

        self.images_data.clear()
        self.photo_refs.clear()
        for widget in self.thumb_frame.winfo_children():
            widget.destroy()
        self._clear_results()

        for img_path in file_paths:
            analyzed_img, info_text = self._process_single_image(img_path)
            if analyzed_img is not None:
                self.images_data.append((analyzed_img, os.path.basename(img_path), info_text))
                self._add_thumbnail(analyzed_img, len(self.images_data) - 1)

        if self.images_data:
            self._show_image(0)

    def toggle_camera(self):
        if self.camera.camera_running:
            self.camera.stop()
            self.btn_camera.config(text="Mở Camera")
            self._clear_results()
        else:
            if not self.camera.start():
                messagebox.showerror("Lỗi", "Không thể mở camera!")
                return
            self.btn_camera.config(text="Dừng Camera")
            self._clear_results()
            self._update_camera_frame()

    def _update_camera_frame(self):
        if not self.camera.camera_running:
            return

        ret, frame = self.camera.read_frame()
        if ret:
            frame = resize_image(frame, max_size=640)
            analyzed_frame, info_text = self._process_frame(frame)
            frame_rgb = cv2.cvtColor(analyzed_frame, cv2.COLOR_BGR2RGB)

            img_pil = Image.fromarray(frame_rgb)
            img_pil.thumbnail((600, 400), Image.Resampling.LANCZOS)
            self.camera_photo = ImageTk.PhotoImage(img_pil)
            self.canvas.delete("all")
            self.canvas.create_image(300, 200, anchor=tk.CENTER, image=self.camera_photo)

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, info_text)

        self.root.after(300, self._update_camera_frame)

    def _process_frame(self, frame):
        try:
            results = analyze_face(frame, backend=self.backend_var.get())
            result = results[0]
            age, gender_vn = compute_age_and_gender(result)

            region = result['region']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            info_text = self._generate_result_text("Camera Frame", age, gender_vn)
            draw_results_on_image(frame, x, y, w, h, gender_vn, age)

            return frame, info_text
        except Exception as e:
            return frame, f"⚠ Lỗi khi phân tích frame camera: {str(e)}"

    def _process_single_image(self, img_path):
        image = read_image_unicode(img_path)
        if image is None:
            return None, f"❌ Không thể đọc ảnh: {os.path.basename(img_path)}"

        image = resize_image(image, max_size=640)

        try:
            results = analyze_face(image, backend=self.backend_var.get())
            result = results[0]
            age, gender_vn = compute_age_and_gender(result)

            region = result['region']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            info_text = self._generate_result_text(os.path.basename(img_path), age, gender_vn)
            draw_results_on_image(image, x, y, w, h, gender_vn, age)

            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), info_text
        except Exception as e:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), f"⚠ Lỗi khi phân tích ảnh: {str(e)}"

    def _generate_result_text(self, file_name, age, gender_vn):
        result_text = f"📷 {file_name}\n"
        result_text += f"  - Khuôn mặt: Tuổi: {age}, Giới tính: {gender_vn}\n"
        if age < 18:
            result_text += "  *Lưu ý: Tuổi trẻ em được điều chỉnh để tăng độ chính xác.\n"
        return result_text

    def _add_thumbnail(self, image_rgb, index):
        img_pil = Image.fromarray(image_rgb)
        img_pil.thumbnail((100, 100))
        thumb = ImageTk.PhotoImage(img_pil)
        self.photo_refs.append(thumb)

        btn = tk.Button(self.thumb_frame, image=thumb, command=lambda i=index: self._show_image(i))
        btn.pack(side=tk.LEFT, padx=5)

    def _show_image(self, index):
        img_rgb, name, info_text = self.images_data[index]
        img_pil = Image.fromarray(img_rgb)

        canvas_width = 600
        canvas_height = 400
        img_pil.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)

        self.current_photo = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=self.current_photo)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, info_text)

    def _clear_results(self):
        self.canvas.delete("all")
        self.result_text.delete(1.0, tk.END)


import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from analyzer import analyze_face, compute_age_and_gender
from image_utils import read_image_unicode, resize_image, draw_results_on_image
from storage import save_results_to_json
from camera import CameraHandler


class FaceAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖤 Face Analysis - Dark Mode")
        self.root.geometry("950x750")
        self.root.configure(bg="#1e1e2f")

        # ========== ttk Style (Dark) ==========
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=8,
                        relief="flat",
                        background="#00d4ff",
                        foreground="black")
        style.map("Dark.TButton",
                  background=[("active", "#00aacc")])

        style.configure("Dark.TLabel",
                        background="#1e1e2f",
                        foreground="#f5f5f5",
                        font=("Segoe UI", 11))

        # ========== Title ==========
        title = ttk.Label(root, text="Phân tích khuôn mặt 👤", style="Dark.TLabel",
                          font=("Segoe UI", 20, "bold"), foreground="#00d4ff")
        title.pack(pady=15)

        # ========== Button Frame ==========
        btn_frame = ttk.Frame(root, style="Dark.TLabel")
        btn_frame.pack(pady=10)

        self.btn_select = ttk.Button(btn_frame, text="📂 Chọn ảnh",
                                     command=self.load_images, style="Dark.TButton")
        self.btn_select.grid(row=0, column=0, padx=10)

        self.btn_camera = ttk.Button(btn_frame, text="📷 Mở Camera",
                                     command=self.toggle_camera, style="Dark.TButton")
        self.btn_camera.grid(row=0, column=1, padx=10)

        self.btn_save = ttk.Button(btn_frame, text="💾 Lưu JSON",
                                   command=lambda: save_results_to_json(self.images_data), style="Dark.TButton")
        self.btn_save.grid(row=0, column=2, padx=10)

        # Backend chọn
        backend_label = ttk.Label(root, text="🔍 Chọn backend phát hiện khuôn mặt:",
                                  style="Dark.TLabel", font=("Segoe UI", 11, "bold"))
        backend_label.pack(pady=5)

        self.backend_var = tk.StringVar(value="retinaface")
        self.backend_menu = ttk.Combobox(root, textvariable=self.backend_var,
                                         values=["retinaface", "ssd", "mtcnn", "dlib"],
                                         state="readonly", width=15)
        self.backend_menu.pack(pady=5)

        # ========== Canvas ==========
        self.canvas = tk.Canvas(root, width=640, height=420, bg="#2c2c3c", highlightthickness=0)
        self.canvas.pack(pady=10)

        # ========== Thumbnails ==========
        self.thumb_frame = ttk.Frame(root, style="Dark.TLabel")
        self.thumb_frame.pack(pady=5)

        # ========== Result box ==========
        result_label = ttk.Label(root, text="📑 Kết quả phân tích", style="Dark.TLabel",
                                 font=("Segoe UI", 13, "bold"), foreground="#00d4ff")
        result_label.pack(pady=5)

        self.result_text = tk.Text(root, height=12, width=80, font=("Consolas", 11),
                                   bg="#2c2c3c", fg="#f5f5f5", relief="flat", wrap="word",
                                   insertbackground="white")
        self.result_text.pack(pady=10)

        # ========== Data ==========
        self.images_data = []
        self.photo_refs = []
        self.current_photo = None

        # Camera
        self.camera = CameraHandler()
        self.camera_photo = None

    # =============================
    # Load & process images
    # =============================
    def load_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not file_paths:
            if not self.images_data:  # Nếu chưa có ảnh nào trong bộ nhớ
                self._clear_results()
                self.result_text.insert(tk.END, "❌ Không có file nào được chọn!\n")
            return

        # ❌ Không xóa self.images_data, để giữ ảnh cũ
        # ❌ Không xóa self.photo_refs
        # Chỉ clear thumbnails cũ để vẽ lại toàn bộ
        for widget in self.thumb_frame.winfo_children():
            widget.destroy()
        self._clear_results()

        # Xử lý và thêm ảnh mới
        for img_path in file_paths:
            analyzed_img, info_text = self._process_single_image(img_path)
            if analyzed_img is not None:
                self.images_data.append((analyzed_img, os.path.basename(img_path), info_text))

        # Vẽ lại toàn bộ thumbnails
        for idx, (analyzed_img, _, _) in enumerate(self.images_data):
            self._add_thumbnail(analyzed_img, idx)

        if self.images_data:
            self._show_image(len(self.images_data) - 1)  # hiện ảnh mới nhất

    # =============================
    # Camera toggle
    # =============================
    def toggle_camera(self):
        if self.camera.camera_running:
            self.camera.stop()
            self.btn_camera.config(text="📷 Mở Camera")
            self._clear_results()
        else:
            if not self.camera.start():
                messagebox.showerror("Lỗi", "Không thể mở camera!")
                return
            self.btn_camera.config(text="⏹ Dừng Camera")
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
            img_pil.thumbnail((640, 420), Image.Resampling.LANCZOS)
            self.camera_photo = ImageTk.PhotoImage(img_pil)
            self.canvas.delete("all")
            self.canvas.create_image(320, 210, anchor=tk.CENTER, image=self.camera_photo)

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, info_text)

        self.root.after(300, self._update_camera_frame)

    # =============================
    # Image processing helpers
    # =============================
    def _process_frame(self, frame):
        try:
            results = analyze_face(frame, backend=self.backend_var.get())
            result = results[0]
            age, gender_vn = compute_age_and_gender(result)

            region = result['region']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            info_text = self._generate_result_text("Camera Frame", age, gender_vn)
            frame = draw_results_on_image(frame, x, y, w, h, gender_vn, age)


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
            image = draw_results_on_image(image, x, y, w, h, gender_vn, age)


            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), info_text
        except Exception as e:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), f"⚠ Lỗi khi phân tích ảnh: {str(e)}"

    def _generate_result_text(self, file_name, age, gender_vn):
        result_text = f"📷 {file_name}\n"
        result_text += f"  - Tuổi: {age}\n"
        result_text += f"  - Giới tính: {gender_vn}\n"
        if age < 18:
            result_text += "  ⚠ Lưu ý: Tuổi < 18, kết quả chỉ tham khảo.\n"
        return result_text

    # =============================
    # Thumbnail & canvas
    # =============================
    def _add_thumbnail(self, image_rgb, index):
        img_pil = Image.fromarray(image_rgb)
        img_pil.thumbnail((90, 90))
        thumb = ImageTk.PhotoImage(img_pil)
        self.photo_refs.append(thumb)

        btn = tk.Button(self.thumb_frame, image=thumb, relief="flat", bg="#1e1e2f", activebackground="#333",
                        command=lambda i=index: self._show_image(i))
        btn.pack(side=tk.LEFT, padx=5, pady=5)

    def _show_image(self, index):
        img_rgb, name, info_text = self.images_data[index]
        img_pil = Image.fromarray(img_rgb)
        img_pil.thumbnail((640, 420), Image.Resampling.LANCZOS)

        self.current_photo = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(320, 210, anchor=tk.CENTER, image=self.current_photo)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, info_text)

    def _clear_results(self):
        self.canvas.delete("all")
        self.result_text.delete(1.0, tk.END)


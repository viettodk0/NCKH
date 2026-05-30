import cv2
import numpy as np
import os
import sys
import threading
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Đảm bảo hiển thị tiếng Việt trên Terminal Windows không lỗi
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Cấu hình giao diện CustomTkinter
ctk.set_appearance_mode("dark")  # Giao diện tối
ctk.set_default_color_theme("blue")  # Màu chủ đạo xanh dương

class PhotoEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Thiết lập cửa sổ chính
        self.title("Phần mềm chỉnh sửa màu sắc & tách nền - OpenCV & CustomTkinter")
        self.geometry("1000, 700")
        self.minsize(900, 600)
        
        # Biến chứa dữ liệu ảnh nền chính
        self.full_original_cv_img = None     # Ảnh gốc độ phân giải cao
        self.preview_original_cv_img = None  # Ảnh gốc đã thu nhỏ để xem trước mượt mà
        self.preview_processed_cv_img = None # Ảnh sau khi chỉnh màu/hiệu ứng để hiển thị
        self.image_path = None
        
        self.max_preview_size = 550          # Kích thước xem trước tối đa

        # Cấu hình bố cục lưới (Grid) 2 cột chính
        self.grid_columnconfigure(0, weight=0, minsize=320) # Cột điều khiển bên trái
        self.grid_columnconfigure(1, weight=1)              # Cột hiển thị ảnh bên phải
        self.grid_rowconfigure(0, weight=1)

        # Khởi tạo các thành phần giao diện
        self.create_control_panel()
        self.create_preview_panel()

    def create_control_panel(self):
        """Tạo bảng điều khiển bên trái chứa các nút bấm và thanh trượt."""
        self.control_frame = ctk.CTkFrame(self, corner_radius=0, width=320)
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tiêu đề App
        self.title_label = ctk.CTkLabel(
            self.control_frame, 
            text="PHOTO COLOR EDITOR", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(20, 20), padx=20)

        # Nút Import ảnh chính
        self.btn_import = ctk.CTkButton(
            self.control_frame, 
            text="Chọn ảnh chính (Import)", 
            command=self.import_image,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.btn_import.pack(fill="x", padx=20, pady=(0, 20))

        # ==========================================
        # PHẦN 1: ĐIỀU CHỈNH MÀU SẮC (COLOR ADJUST)
        # ==========================================
        self.header_color = ctk.CTkLabel(
            self.control_frame, 
            text="1. ĐIỀU CHỈNH MÀU SẮC", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="gray"
        )
        self.header_color.pack(anchor="w", padx=20, pady=(10, 5))

        self.color_frame = ctk.CTkFrame(self.control_frame)
        self.color_frame.pack(fill="x", padx=15, pady=5)

        # Slider Red
        self.lbl_red = ctk.CTkLabel(self.color_frame, text="Kênh màu Đỏ (Red): 0", font=ctk.CTkFont(size=12))
        self.lbl_red.pack(anchor="w", padx=15, pady=(10, 0))
        self.slider_red = ctk.CTkSlider(self.color_frame, from_=-100, to=100, command=self.update_image)
        self.slider_red.set(0)
        self.slider_red.pack(fill="x", padx=15, pady=(0, 10))

        # Slider Green
        self.lbl_green = ctk.CTkLabel(self.color_frame, text="Kênh màu Xanh lá (Green): 0", font=ctk.CTkFont(size=12))
        self.lbl_green.pack(anchor="w", padx=15, pady=(5, 0))
        self.slider_green = ctk.CTkSlider(self.color_frame, from_=-100, to=100, command=self.update_image)
        self.slider_green.set(0)
        self.slider_green.pack(fill="x", padx=15, pady=(0, 10))

        # Slider Blue
        self.lbl_blue = ctk.CTkLabel(self.color_frame, text="Kênh màu Xanh dương (Blue): 0", font=ctk.CTkFont(size=12))
        self.lbl_blue.pack(anchor="w", padx=15, pady=(5, 0))
        self.slider_blue = ctk.CTkSlider(self.color_frame, from_=-100, to=100, command=self.update_image)
        self.slider_blue.set(0)
        self.slider_blue.pack(fill="x", padx=15, pady=(0, 10))

        # Slider Brightness
        self.lbl_brightness = ctk.CTkLabel(self.color_frame, text="Độ sáng (Brightness): 0", font=ctk.CTkFont(size=12))
        self.lbl_brightness.pack(anchor="w", padx=15, pady=(5, 0))
        self.slider_brightness = ctk.CTkSlider(self.color_frame, from_=-100, to=100, command=self.update_image)
        self.slider_brightness.set(0)
        self.slider_brightness.pack(fill="x", padx=15, pady=(0, 10))

        # Slider Contrast
        self.lbl_contrast = ctk.CTkLabel(self.color_frame, text="Độ tương phản (Contrast): 0", font=ctk.CTkFont(size=12))
        self.lbl_contrast.pack(anchor="w", padx=15, pady=(5, 0))
        self.slider_contrast = ctk.CTkSlider(self.color_frame, from_=-100, to=100, command=self.update_image)
        self.slider_contrast.set(0)
        self.slider_contrast.pack(fill="x", padx=15, pady=(0, 15))

        # ==========================================
        # PHẦN 2: TÁCH NỀN AI (BACKGROUND REMOVAL)
        # ==========================================
        self.header_bg = ctk.CTkLabel(
            self.control_frame, 
            text="2. TÁCH NỀN BẰNG AI", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="gray"
        )
        self.header_bg.pack(anchor="w", padx=20, pady=(15, 5))

        self.bg_frame = ctk.CTkFrame(self.control_frame)
        self.bg_frame.pack(fill="x", padx=15, pady=5)

        self.btn_remove_bg = ctk.CTkButton(
            self.bg_frame,
            text="Tách nền bằng AI",
            command=self.remove_background,
            fg_color="#8e44ad",
            hover_color="#7d3c98",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_remove_bg.pack(fill="x", padx=15, pady=(10, 5))

        self.lbl_status_ai = ctk.CTkLabel(
            self.bg_frame, 
            text="Trạng thái AI: Sẵn sàng", 
            font=ctk.CTkFont(size=11, slant="italic")
        )
        self.lbl_status_ai.pack(padx=15, pady=(0, 10))

        # ==========================================
        # NÚT CHỨC NĂNG CHÍNH (SAVE & RESET)
        # ==========================================
        self.btn_reset = ctk.CTkButton(
            self.control_frame, 
            text="Khôi phục gốc (Reset)", 
            command=self.reset_sliders,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90")
        )
        self.btn_reset.pack(fill="x", padx=20, pady=(20, 10))

        self.btn_save = ctk.CTkButton(
            self.control_frame, 
            text="Lưu ảnh (Export)", 
            command=self.save_image,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.btn_save.pack(fill="x", padx=20, pady=(0, 20))

    def create_preview_panel(self):
        """Tạo bảng bên phải để hiển thị ảnh preview."""
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)

        # Dòng chữ gợi ý lúc chưa mở ảnh
        self.placeholder_label = ctk.CTkLabel(
            self.preview_frame,
            text="Hãy nhấn nút 'Chọn ảnh chính (Import)' để bắt đầu chỉnh sửa",
            font=ctk.CTkFont(size=16, slant="italic"),
            text_color="gray"
        )
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")

        # Label để chứa ảnh thực tế
        self.image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.image_label.grid_forget()

    def import_image(self):
        """Mở cửa sổ chọn file ảnh nền chính."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.webp;*.bmp")]
        )
        if not file_path:
            return

        self.image_path = file_path
        
        # Đọc ảnh hỗ trợ đường dẫn chứa chữ tiếng Việt có dấu (Unicode)
        try:
            file_bytes = np.fromfile(file_path, dtype=np.uint8)
            # OpenCV tự động nhận biết số kênh màu và hệ màu của ảnh
            self.full_original_cv_img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
        except Exception:
            self.full_original_cv_img = None

        if self.full_original_cv_img is None:
            messagebox.showerror("Lỗi", "Không thể đọc được file ảnh chính.")
            return

        # Tính toán kích thước thu nhỏ phù hợp để làm ảnh preview
        h, w = self.full_original_cv_img.shape[:2]
        scaling = min(self.max_preview_size / h, self.max_preview_size / w)
        new_w = int(w * scaling)
        new_h = int(h * scaling)
        
        self.preview_original_cv_img = cv2.resize(self.full_original_cv_img, (new_w, new_h))
        
        # Reset các thanh trượt về 0 trước khi nạp ảnh mới
        self.reset_sliders(silent=True)
        self.lbl_status_ai.configure(text="Trạng thái AI: Sẵn sàng", text_color="white")
        
        # Cập nhật hiển thị
        self.update_image()
        
        # Cập nhật UI
        self.placeholder_label.grid_forget()
        self.image_label.grid(row=0, column=0)

    def remove_background(self):
        """Kích hoạt tiến trình tách nền bằng AI trong một Thread ngầm."""
        if self.full_original_cv_img is None:
            messagebox.showwarning("Cảnh báo", "Bạn chưa import ảnh chính để tách nền.")
            return

        # Vô hiệu hóa nút bấm để tránh click trùng lặp
        self.btn_remove_bg.configure(state="disabled")
        self.lbl_status_ai.configure(text="Đang xử lý tách nền AI (Xin vui lòng đợi)...", text_color="yellow")

        def worker():
            try:
                # Import rembg bên trong để giảm thời gian load ban đầu của app
                from rembg import remove
                
                # Chuyển ảnh BGR/BGRA OpenCV sang RGB PIL Image
                # Nếu ảnh đã có sẵn kênh alpha, chuyển đổi phù hợp
                if self.full_original_cv_img.shape[2] == 4:
                    rgb_img = cv2.cvtColor(self.full_original_cv_img, cv2.COLOR_BGRA2RGBA)
                else:
                    rgb_img = cv2.cvtColor(self.full_original_cv_img, cv2.COLOR_BGR2RGB)
                
                pil_img = Image.fromarray(rgb_img)
                
                # Xử lý tách nền bằng AI
                result_pil = remove(pil_img)
                
                # Chuyển PIL Image RGBA về dạng BGRA OpenCV
                rgba_array = np.array(result_pil)
                bgra_img = cv2.cvtColor(rgba_array, cv2.COLOR_RGBA2BGRA)
                
                # Cập nhật lại ảnh gốc và ảnh preview
                self.full_original_cv_img = bgra_img
                
                # Thay đổi kích thước preview
                h, w = self.full_original_cv_img.shape[:2]
                scaling = min(self.max_preview_size / h, self.max_preview_size / w)
                new_w = int(w * scaling)
                new_h = int(h * scaling)
                self.preview_original_cv_img = cv2.resize(self.full_original_cv_img, (new_w, new_h))
                
                # Cập nhật giao diện (Thread-safe thông qua after)
                self.after(0, self.on_remove_bg_success)
            except Exception as e:
                self.after(0, lambda: self.on_remove_bg_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def on_remove_bg_success(self):
        self.btn_remove_bg.configure(state="normal")
        self.lbl_status_ai.configure(text="Trạng thái AI: Tách nền thành công!", text_color="green")
        self.update_image()

    def on_remove_bg_error(self, err_msg):
        self.btn_remove_bg.configure(state="normal")
        self.lbl_status_ai.configure(text="Trạng thái AI: Lỗi xử lý!", text_color="red")
        messagebox.showerror("Lỗi tách nền", f"Đã xảy ra lỗi khi tách nền:\n{err_msg}")

    def process_core(self, cv_img, r_val, g_val, b_val, brightness, contrast):
        """Hàm xử lý các hiệu ứng màu sắc trên ảnh chính."""
        # 1. Tách các kênh màu (Hỗ trợ cả ảnh 3 kênh BGR và 4 kênh BGRA)
        if cv_img.shape[2] == 4:
            b, g, r, a = cv2.split(cv_img)
        else:
            b, g, r = cv2.split(cv_img)
            a = None
        
        # 2. Cộng lượng màu tương ứng
        r = np.clip(r.astype(np.int16) + r_val, 0, 255).astype(np.uint8)
        g = np.clip(g.astype(np.int16) + g_val, 0, 255).astype(np.uint8)
        b = np.clip(b.astype(np.int16) + b_val, 0, 255).astype(np.uint8)
        
        # Gộp lại thành ảnh màu
        if a is not None:
            merged = cv2.merge((b, g, r, a))
        else:
            merged = cv2.merge((b, g, r))
        
        # 3. Điều chỉnh Độ sáng và Độ tương phản (chỉ thực hiện trên kênh màu BGR)
        scale = 1.0 + (contrast / 100.0)
        if a is not None:
            rgb = merged[:, :, :3]
            adjusted_rgb = scale * (rgb.astype(np.float32) - 127.0) + 127.0 + brightness
            adjusted_rgb = np.clip(adjusted_rgb, 0, 255).astype(np.uint8)
            # Gộp lại kèm kênh alpha gốc
            adjusted = cv2.merge((adjusted_rgb[:,:,0], adjusted_rgb[:,:,1], adjusted_rgb[:,:,2], a))
        else:
            adjusted = scale * (merged.astype(np.float32) - 127.0) + 127.0 + brightness
            adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return adjusted

    def update_image(self, event=None):
        """Cập nhật ảnh xem trước khi có bất cứ sự thay đổi nào từ slider."""
        if self.preview_original_cv_img is None:
            return

        # Lấy thông số màu sắc
        r_val = int(self.slider_red.get())
        g_val = int(self.slider_green.get())
        b_val = int(self.slider_blue.get())
        bright_val = int(self.slider_brightness.get())
        contrast_val = int(self.slider_contrast.get())

        # Cập nhật nhãn chữ tương ứng
        self.lbl_red.configure(text=f"Kênh màu Đỏ (Red): {r_val}")
        self.lbl_green.configure(text=f"Kênh màu Xanh lá (Green): {g_val}")
        self.lbl_blue.configure(text=f"Kênh màu Xanh dương (Blue): {b_val}")
        self.lbl_brightness.configure(text=f"Độ sáng (Brightness): {bright_val}")
        self.lbl_contrast.configure(text=f"Độ tương phản (Contrast): {contrast_val}")

        # Chỉnh màu cho ảnh chính
        self.preview_processed_cv_img = self.process_core(
            self.preview_original_cv_img, r_val, g_val, b_val, bright_val, contrast_val
        )

        # Chuyển định dạng để hiển thị trên giao diện Tkinter
        # Đối với ảnh trong suốt (4 kênh), ta chuyển sang RGBA
        if self.preview_processed_cv_img.shape[2] == 4:
            rgb_img = cv2.cvtColor(self.preview_processed_cv_img, cv2.COLOR_BGRA2RGBA)
            pil_img = Image.fromarray(rgb_img)
        else:
            rgb_img = cv2.cvtColor(self.preview_processed_cv_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)

        # Cập nhật hiển thị lên CTkLabel
        h, w = self.preview_processed_cv_img.shape[:2]
        ctk_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(w, h))
        self.image_label.configure(image=ctk_image)

    def reset_sliders(self, silent=False):
        """Đặt lại bảng điều chỉnh màu về gốc."""
        self.slider_red.set(0)
        self.slider_green.set(0)
        self.slider_blue.set(0)
        self.slider_brightness.set(0)
        self.slider_contrast.set(0)
        if not silent:
            self.update_image()

    def save_image(self):
        """Áp dụng toàn bộ hiệu ứng lên ảnh gốc độ phân giải cao và lưu xuống máy tính."""
        if self.full_original_cv_img is None:
            messagebox.showwarning("Cảnh báo", "Bạn chưa chọn ảnh nào để lưu.")
            return

        # Chọn đường dẫn lưu ảnh
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png", # Mặc định lưu đuôi PNG để giữ độ trong suốt nền nếu đã xóa phông
            filetypes=[
                ("PNG Image (Hỗ trợ nền trong suốt)", "*.png"),
                ("JPEG Image (Tự động trộn nền trắng)", "*.jpg;*.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if not save_path:
            return

        # Đọc thông số chỉnh sửa
        r_val = int(self.slider_red.get())
        g_val = int(self.slider_green.get())
        b_val = int(self.slider_blue.get())
        bright_val = int(self.slider_brightness.get())
        contrast_val = int(self.slider_contrast.get())

        print("Đang xử lý ảnh chất lượng cao...")
        # Chỉnh màu ảnh chính gốc
        full_processed = self.process_core(
            self.full_original_cv_img, r_val, g_val, b_val, bright_val, contrast_val
        )

        # Trích xuất đuôi định dạng file lưu
        ext = os.path.splitext(save_path)[1].lower()
        if not ext:
            ext = ".png"
            save_path += ".png"

        # XỬ LÝ ĐẶC BIỆT KHI LƯU ẢNH ĐÃ XÓA PHÔNG (4 KÊNH) DƯỚI ĐỊNH DẠNG JPG/JPEG
        if ext in ['.jpg', '.jpeg'] and full_processed.shape[2] == 4:
            # JPG không hỗ trợ độ trong suốt (Alpha channel). Nếu lưu trực tiếp sẽ bị lỗi hoặc ra nền đen xì.
            # Giải pháp: Trộn phần tiền cảnh đã tách nền lên một tấm nền màu trắng (255)
            b, g, r, a = cv2.split(full_processed)
            alpha = a / 255.0
            
            # Tạo nền trắng có kích thước bằng ảnh gốc
            bg_b = np.ones_like(b) * 255
            bg_g = np.ones_like(g) * 255
            bg_r = np.ones_like(r) * 255
            
            # Phối trộn alpha: màu_mới = màu_chủ_thể * alpha + màu_nền_trắng * (1 - alpha)
            b = (b * alpha + bg_b * (1.0 - alpha)).astype(np.uint8)
            g = (g * alpha + bg_g * (1.0 - alpha)).astype(np.uint8)
            r = (r * alpha + bg_r * (1.0 - alpha)).astype(np.uint8)
            
            # Gộp lại thành ảnh 3 kênh BGR chuẩn của JPG
            full_processed = cv2.merge((b, g, r))

        # Lưu ảnh sử dụng imencode + tofile hỗ trợ tuyệt đối đường dẫn chứa Tiếng Việt có dấu (Unicode)
        try:
            is_success, im_buf = cv2.imencode(ext, full_processed)
            if is_success:
                im_buf.tofile(save_path)
                messagebox.showinfo("Thành công", f"Đã lưu ảnh thành công tại:\n{save_path}")
            else:
                messagebox.showerror("Lỗi", "Không thể mã hóa định dạng ảnh này.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu được ảnh. Chi tiết lỗi:\n{str(e)}")

if __name__ == "__main__":
    app = PhotoEditorApp()
    app.mainloop()

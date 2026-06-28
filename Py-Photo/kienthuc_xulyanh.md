# KIẾN THỨC XỬ LÝ ẢNH VÀ HƯỚNG DẪN ỨNG DỤNG (PY-PHOTO)

Tài liệu này tổng hợp toàn bộ kiến thức, logic mã nguồn và mở rộng hệ sinh thái các thư viện xử lý ảnh trong Python cho dự án **Py-Photo** sau khi tích hợp các tính năng **Chỉnh màu sắc, Tách nền AI & Nâng cao độ phân giải AI**.

---

## 1. Cấu trúc thư mục `Py-Photo`
*   **`Chay_App.bat`**: File kích đúp chuột trên Windows để khởi chạy nhanh ứng dụng (tự động ẩn cửa sổ dòng lệnh đen).
*   **`photo_editor_app.py`**: Ứng dụng Desktop chỉnh màu, tách nền & tăng độ phân giải bằng AI chính.
*   **`photo_effects.py`**: File chạy thử nghiệm các hiệu ứng cơ bản (Ảnh xám, làm mờ, tách biên, xoay ảnh) hiển thị qua nhiều cửa sổ OpenCV.
    *   Chọn ảnh chính (Import).
    *   Chỉnh màu (Đỏ, Xanh lá, Xanh dương, Sáng tối, Tương phản).
    *   Tách nền bằng trí tuệ nhân tạo (AI Background Removal).
    *   Nâng cao độ phân giải bằng AI (AI Super Resolution 3x).
    *   Xuất ảnh chất lượng cao (Export - hỗ trợ giữ độ trong suốt khi xuất PNG hoặc ghép nền trắng khi xuất JPG).
*   **`input.jpg`**: File ảnh mẫu tự động sinh ra khi chạy chương trình lần đầu.

---

## 2. Các thư viện sử dụng trong dự án
*   **OpenCV (module `cv2`):** Lõi xử lý ảnh nền tảng, thực hiện đọc/ghi ảnh, trích xuất/gộp các kênh màu BGR, resize ảnh và chuyển đổi hệ màu YCrCb.
*   **rembg & onnxruntime:** Sử dụng mô hình Deep Learning học sâu dạng ONNX (`u2net` cho tách nền và `super-resolution-10` cho nâng độ phân giải) để xử lý ảnh thông minh.
*   **NumPy (`numpy`):** Xử lý ma trận điểm ảnh số, tối ưu hóa các phép tính cộng/trừ/phối trộn alpha và padding tile bằng `np.pad`.
*   **CustomTkinter (`customtkinter`):** Giao diện đồ họa cuộn màu tối (Dark Mode) hiện đại.
*   **Pillow (`PIL`):** Chuyển đổi định dạng ảnh BGR/BGRA của OpenCV sang RGB/RGBA để hiển thị tương thích trên Tkinter.

---

## 3. Luồng logic và Chi tiết từng chức năng của ứng dụng

### Chức năng 1: Nhập ảnh (Import Image)
*   **Luồng logic:**
    1. Người dùng bấm nút "Chọn ảnh chính (Import)".
    2. Một hộp thoại chọn file trên Windows mở ra (`filedialog.askopenfilename`).
    3. File ảnh được OpenCV đọc vào bộ nhớ bằng stream nhị phân (`np.fromfile` + `cv2.imdecode`) giúp hỗ trợ đường dẫn tiếng Việt có dấu.
    4. Ảnh gốc chất lượng cao (`full_original_cv_img`) sẽ được tạo một bản sao thu nhỏ (`preview_original_cv_img`) sao cho cạnh dài nhất không vượt quá 550 pixel.
    5. Thiết lập lại các thanh trượt màu sắc về vị trí 0.
    6. Gọi hàm cập nhật hiển thị lên màn hình.

---

### Chức năng 2: Điều chỉnh màu sắc (Color Adjustments)
*   **Luồng logic:**
    1. Người dùng kéo các thanh trượt Red, Green, Blue, Brightness, Contrast.
    2. Chương trình bắt sự kiện kéo trượt và lấy các giá trị hiện tại (từ -100 đến 100).
    3. Tách bức ảnh thành các kênh màu: BGR hoặc BGRA.
    4. Thực hiện các phép toán cộng trừ bù màu trên từng kênh:
        $$\text{Màu}_{\text{mới}} = \text{Màu}_{\text{cũ}} + \text{Giá trị kéo}$$
    5. Điều chỉnh Độ sáng & Độ tương phản trên các kênh màu (kênh Alpha giữ nguyên):
        $$\text{Pixel}_{\text{kết quả}} = \text{Scale} \times (\text{Pixel} - 127) + 127 + \text{Brightness}$$

---

### Chức năng 3: Tách nền bằng AI (AI Background Removal)
*   **Luồng logic:**
    1. Người dùng bấm nút "Tách nền bằng AI".
    2. Khởi tạo luồng phụ (`threading.Thread`) chạy song song dưới nền để giữ giao diện mượt mà.
    3. Chuyển ảnh sang PIL Image và gọi `remove()` từ thư viện `rembg` (mô hình `u2net`).
    4. Cập nhật ma trận kết quả RGBA về dạng BGRA OpenCV và cập nhật giao diện thông qua `self.after()`.

---

### Chức năng 4: Nâng cao độ phân giải bằng AI (AI Super Resolution 3x)
*   **Luồng logic:**
    1. Người dùng bấm nút "Tăng độ phân giải AI (3x)".
    2. Khởi tạo luồng phụ xử lý bất đồng bộ để tránh đơ giao diện.
    3. Mô hình AI `super-resolution-10.onnx` (SubPixelCNN) được tự động tải về thư mục cache hệ thống nếu chưa có.
    4. **Cơ chế xử lý Tile-based & Kênh màu YCrCb:**
        *   Tách ảnh màu thành 3 kênh YCrCb (Kênh Y chứa thông tin độ sáng/chi tiết, Cr và Cb chứa thông tin màu sắc).
        *   Chỉ đưa kênh Y vào mô hình AI để nội suy và tăng độ phân giải lên 3 lần (giúp tiết kiệm tài nguyên và giữ đúng sắc độ màu).
        *   Vì mô hình ONNX nhận đầu vào ô tile cố định $224 \times 224$, chương trình tự động chia kênh Y thành các ô tile nhỏ, dùng `np.pad` đệm lót viền, đưa qua AI xử lý rồi ghép nối lại thành kênh Y độ phân giải siêu nét.
        *   Hai kênh sắc màu Cr và Cb được phóng to bằng thuật toán Bicubic rồi gộp lại với kênh Y mới.
    5. Nếu ảnh có kênh Alpha (đã tách nền), kênh Alpha cũng được phóng to bằng Bicubic để giữ nguyên hình dạng chủ thể.
    6. Cập nhật ảnh gốc và ảnh preview mới lên giao diện.

---

### Chức năng 5: Lưu ảnh sau chỉnh sửa (Export Image)
*   **Luồng logic:**
    1. Người dùng nhấn nút "Lưu ảnh (Export)".
    2. Hộp thoại lưu file mở ra để người dùng chọn tên file và định dạng (`.png`, `.jpg`, `.jpeg`).
    3. Chương trình áp dụng lại các thông số chỉnh màu lên ảnh gốc chất lượng cao.
    4. **Xử lý kênh Alpha khi lưu:**
        *   **Khi lưu dạng PNG:** Giữ nguyên kênh Alpha (nền trong suốt).
        *   **Khi lưu dạng JPG/JPEG:** Tự động trộn chủ thể lên nền màu trắng bằng thuật toán Alpha Blending để tránh lỗi ảnh bị nền đen.
    5. Ghi file an toàn Unicode bằng `cv2.imencode` và `tofile()`.

---

## 4. Mở rộng hệ sinh thái xử lý ảnh Python

Bên cạnh OpenCV và Pillow, Python sở hữu một hệ sinh thái xử lý ảnh vô cùng phong phú:
*   **Scikit-Image (`skimage`):** Chuyên phục vụ cho nghiên cứu khoa học, phân tích cấu trúc hình học.
*   **MediaPipe (Google):** Nhận diện điểm mốc khuôn mặt, bàn tay, cử chỉ thời gian thực từ camera.
*   **Face_recognition:** Nhận diện khuôn mặt người với độ chính xác cao.
*   **Diffusers (Hugging Face):** Tích hợp các mô hình Generative AI (Stable Diffusion) tạo ảnh từ văn bản.

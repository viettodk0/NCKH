# KIẾN THỨC XỬ LÝ ẢNH VÀ HƯỚNG DẪN ỨNG DỤNG (PY-PHOTO)

Tài liệu này tổng hợp toàn bộ kiến thức, logic mã nguồn và mở rộng hệ sinh thái các thư viện xử lý ảnh trong Python cho dự án **Py-Photo** sau khi đã tối giản hóa tính năng chèn ảnh và tập trung vào **Chỉnh màu sắc & Tách nền AI**.

---

## 1. Cấu trúc thư mục `Py-Photo`
*   **`Chay_App.bat`**: File kích đúp chuột trên Windows để khởi chạy nhanh ứng dụng (tự động ẩn cửa sổ dòng lệnh đen).
*   **`photo_editor_app.py`**: Ứng dụng Desktop chỉnh màu & tách nền bằng AI chính.
*   **`photo_effects.py`**: File chạy thử nghiệm các hiệu ứng cơ bản (Ảnh xám, làm mờ, tách biên, xoay ảnh) hiển thị qua nhiều cửa sổ OpenCV.
    *   Chọn ảnh chính (Import).
    *   Chỉnh màu (Đỏ, Xanh lá, Xanh dương, Sáng tối, Tương phản).
    *   Tách nền bằng trí tuệ nhân tạo (AI Background Removal).
    *   Xuất ảnh chất lượng cao (Export - hỗ trợ giữ độ trong suốt khi xuất PNG hoặc ghép nền trắng khi xuất JPG).
*   **`input.jpg`**: File ảnh mẫu tự động sinh ra khi chạy chương trình lần đầu.

---

## 2. Các thư viện sử dụng trong dự án
*   **OpenCV (module `cv2`):** Lõi xử lý ảnh nền tảng, thực hiện đọc/ghi ảnh, trích xuất/gộp các kênh màu BGR, resize ảnh và vẽ hình học.
*   **rembg & onnxruntime:** Sử dụng mô hình Deep Learning học sâu dạng ONNX (`u2net`) để nhận diện và tách biệt vùng chủ thể (tiền cảnh) và hậu cảnh (background), tạo ra ảnh trong suốt.
*   **NumPy (`numpy`):** Xử lý ma trận điểm ảnh số, tối ưu hóa các phép tính cộng/trừ/phối trộn alpha và giới hạn khoảng màu `0-255` bằng `np.clip`.
*   **CustomTkinter (`customtkinter`):** Giao diện đồ họa màu tối (Dark Mode) hiện đại.
*   **Pillow (`PIL`):** Chuyển đổi định dạng ảnh BGR/BGRA của OpenCV sang RGB/RGBA để hiển thị tương thích trên Tkinter.

---

## 3. Luồng logic và Chi tiết từng chức năng của ứng dụng

### Chức năng 1: Nhập ảnh (Import Image)
*   **Luồng logic:**
    1. Người dùng bấm nút "Chọn ảnh chính (Import)".
    2. Một hộp thoại chọn file trên Windows mở ra (`filedialog.askopenfilename`).
    3. File ảnh được OpenCV đọc vào bộ nhớ dưới dạng ma trận điểm ảnh BGR (`cv2.imread`).
    4. Để hiển thị mượt mà trên khung xem trước, ảnh gốc chất lượng cao (`full_original_cv_img`) sẽ được tạo một bản sao thu nhỏ (`preview_original_cv_img`) sao cho cạnh dài nhất không vượt quá 550 pixel.
    5. Thiết lập lại các thanh trượt màu sắc về vị trí 0.
    6. Gọi hàm cập nhật hiển thị lên màn hình.

---

### Chức năng 2: Điều chỉnh màu sắc (Color Adjustments)
*   **Luồng logic:**
    1. Người dùng kéo các thanh trượt Red, Green, Blue, Brightness, Contrast.
    2. Chương trình bắt sự kiện kéo trượt và lấy các giá trị hiện tại (từ -100 đến 100).
    3. Tách bức ảnh thành các kênh màu:
        *   Nếu ảnh 3 kênh màu (BGR): Tách thành 3 ma trận `b`, `g`, `r`.
        *   Nếu ảnh 4 kênh màu (BGRA - đã tách nền): Tách thành 4 ma trận `b`, `g`, `r`, `a`.
    4. Thực hiện các phép toán cộng trừ bù màu trên từng kênh:
        $$\text{Màu}_{\text{mới}} = \text{Màu}_{\text{cũ}} + \text{Giá trị kéo}$$
        *Lưu ý:* Giá trị màu phải được ép kiểu dữ liệu từ `uint8` (8-bit không âm) sang `int16` trước khi cộng để tránh lỗi tràn số, sau đó dùng `np.clip(..., 0, 255)` giới hạn khoảng màu và đưa về lại `uint8`.
    5. Gộp các kênh màu đã chỉnh sửa lại (`cv2.merge`).
    6. Điều chỉnh Độ sáng & Độ tương phản trên các kênh màu (kênh Alpha giữ nguyên):
        $$\text{Pixel}_{\text{kết quả}} = \text{Scale} \times (\text{Pixel} - 127) + 127 + \text{Brightness}$$
        *Trong đó:* $\text{Scale} = 1.0 + \frac{\text{Contrast}}{100.0}$. Khi tương phản tăng (Scale > 1), các pixel sáng hơn 127 sẽ sáng hơn nữa, các pixel tối hơn 127 sẽ tối đi, giúp hình ảnh sắc nét.

---

### Chức năng 3: Tách nền bằng AI (AI Background Removal)
*   **Luồng logic:**
    1. Người dùng bấm nút "Tách nền bằng AI".
    2. Vô hiệu hóa nút bấm và cập nhật nhãn trạng thái hiển thị: "Đang xử lý tách nền AI (Xin vui lòng đợi)...".
    3. Khởi tạo một luồng phụ (`threading.Thread`) chạy song song dưới nền để xử lý tác vụ nặng nhằm giữ cho giao diện chính của người dùng không bị đơ ("Not Responding").
    4. Trong luồng phụ:
        *   Chuyển đổi ma trận ảnh từ định dạng OpenCV (BGR/BGRA) sang đối tượng PIL Image (RGB/RGBA).
        *   Gọi hàm `remove()` từ thư viện `rembg`. Thư viện này chạy mô hình AI `u2net` để phân tích chủ thể và xuất ra ảnh có nền trong suốt (PNG 4 kênh RGBA).
        *   Chuyển ngược ảnh RGBA về dạng BGRA OpenCV.
        *   Cập nhật ma trận này làm ảnh gốc và tự động tạo lại ảnh preview thu nhỏ.
    5. Gọi hàm giao diện thread-safe `self.after()` để cập nhật ảnh mới lên màn hình và mở khóa lại nút bấm, báo trạng thái "Tách nền thành công!".

---

### Chức năng 4: Lưu ảnh sau chỉnh sửa (Export Image)
*   **Luồng logic:**
    1. Người dùng nhấn nút "Lưu ảnh (Export)".
    2. Hộp thoại lưu file mở ra để người dùng chọn tên file và định dạng (`.png`, `.jpg`, `.jpeg`).
    3. Chương trình áp dụng lại toàn bộ công thức chỉnh màu và độ sáng ở bước 2 lên **ảnh gốc chất lượng cao** (`full_original_cv_img`).
    4. **Kiểm tra và xử lý kênh Alpha (Xóa phông) khi lưu:**
        *   **Trường hợp 1 (Lưu dạng PNG):** Định dạng PNG hỗ trợ kênh Alpha (trong suốt), nên ma trận ảnh 4 kênh (BGRA) được lưu trực tiếp xuống ổ cứng, giữ nguyên phần nền trong suốt đã tách.
        *   **Trường hợp 2 (Lưu dạng JPG/JPEG):** Định dạng JPG không hỗ trợ kênh trong suốt Alpha. Nếu lưu trực tiếp ma trận 4 kênh, OpenCV sẽ tự động loại bỏ kênh Alpha khiến nền ảnh bị biến thành màu đen xì hoặc gây crash phần mềm.
            *   *Giải pháp:* Thực hiện thuật toán trộn ảnh đè lên nền trắng:
                $$\text{Kênh Màu}_{\text{kết quả}} = \text{Màu}_{\text{tiền cảnh}} \times \text{Alpha} + 255 \times (1 - \text{Alpha})$$
                *Trong đó:* $\text{Alpha} = \frac{\text{Kênh Alpha}}{255.0}$ (có khoảng giá trị từ 0.0 đến 1.0). Việc nhân chập này giúp ghép chủ thể lên một tấm nền trắng tinh một cách mượt mà ở vùng biên.
            *   Gộp 3 kênh màu mới thành ảnh 3 kênh BGR chuẩn của JPG rồi tiến hành ghi đĩa (`cv2.imwrite`).

---

## 5. Mở rộng hệ sinh thái xử lý ảnh Python

Bên cạnh OpenCV và Pillow, Python sở hữu một hệ sinh thái xử lý ảnh vô cùng phong phú được chia theo mục đích sử dụng:

### A. Thư viện khoa học & Phân tích ảnh
*   **Scikit-Image (`skimage`):** Chuyên phục vụ cho nghiên cứu khoa học, y sinh. Cung cấp các công cụ phân tích cấu trúc tế bào, phân đoạn hình ảnh (segmentation) và trích xuất đặc trưng hình học nâng cao.
*   **Mahotas:** Viết bằng C++ giúp tối ưu tốc độ tối đa, chứa hơn 100 hàm xử lý thị giác máy tính và phân tích kết cấu ảnh.

### B. Thư viện tích hợp Trí tuệ nhân tạo (AI-Driven)
*   **MediaPipe (của Google):** Nhận diện các điểm mốc trên mặt (Face Mesh), bàn tay (Hand Tracking), khớp cơ thể (Pose Estimation) thời gian thực từ ảnh hoặc camera. Rất thích hợp làm các bộ lọc filter làm đẹp dạng Snapchat.
*   **Face_recognition:** Nhận diện khuôn mặt người quen/lạ dựa trên thư viện Dlib với độ chính xác cực cao.
*   **Albumentations:** Thư viện xử lý ảnh siêu nhanh chuyên dùng cho việc chuẩn bị tập dữ liệu huấn luyện Deep Learning (xoay, đổi màu, nhiễu hạt, mờ... ảnh hàng loạt).
*   **Diffusers (của Hugging Face):** Giúp đưa các mô hình tạo ảnh nghệ thuật từ văn bản (Text-to-Image) hoặc vẽ thêm chi tiết vào ảnh (Inpainting) như Stable Diffusion trực tiếp vào ứng dụng Python của bạn.

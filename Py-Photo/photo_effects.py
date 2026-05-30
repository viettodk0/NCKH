import cv2
import numpy as np
import os
import sys

# Đảm bảo in tiếng Việt không bị lỗi encoding trên Windows Console
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def create_sample_image(filename):
    """Tạo một ảnh mẫu chứa các hình khối và chữ để làm mẫu thử nghiệm nếu chưa có ảnh."""
    print("Không tìm thấy ảnh 'input.jpg'. Đang tạo một ảnh mẫu tự động...")
    
    # Tạo ảnh nền kích thước 400x400 pixel, màu xám nhạt
    img = np.ones((400, 400, 3), dtype=np.uint8) * 220
    
    # Vẽ một hình tròn màu xanh lá (Green) ở trung tâm
    cv2.circle(img, (200, 200), 80, (100, 200, 100), -1)
    
    # Vẽ một hình chữ nhật màu đỏ (Red) ở góc trên bên trái
    cv2.rectangle(img, (50, 50), (130, 130), (100, 100, 250), -1)
    
    # Vẽ một hình tam giác màu xanh dương (Blue) ở góc dưới bên phải
    pts = np.array([[300, 300], [350, 250], [380, 320]], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], True, (250, 150, 100), 3)
    
    # Thêm chữ viết lên ảnh
    cv2.putText(img, "OpenCV Python", (70, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (50, 50, 50), 2)
    
    # Lưu ảnh mẫu
    cv2.imwrite(filename, img)
    print(f"Đã tạo ảnh mẫu '{filename}'.")

def apply_image_effects(image_path):
    # Nếu chưa có ảnh thì tự sinh ảnh mẫu để chạy thử
    if not os.path.exists(image_path):
        create_sample_image(image_path)

    # 1. Đọc ảnh từ file
    original = cv2.imread(image_path)
    
    print("\n--- Đang xử lý các hiệu ứng ảnh ---")

    # Hiệu ứng 1: Chuyển sang ảnh xám (Grayscale)
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    # Hiệu ứng 2: Làm mờ ảnh bằng bộ lọc Gaussian (Gaussian Blur)
    # (15, 15) là kích thước hạt lọc (kernel size) - phải là số lẻ.
    blurred = cv2.GaussianBlur(original, (15, 15), 0)

    # Hiệu ứng 3: Phát hiện cạnh/đường viền (Canny Edge Detection)
    edges = cv2.Canny(gray, 50, 150)

    # Hiệu ứng 4: Xoay ảnh 90 độ theo chiều kim đồng hồ
    rotated = cv2.rotate(original, cv2.ROTATE_90_CLOCKWISE)

    # --- LƯU CÁC KẾT QUẢ XUỐNG THƯ MỤC ---
    cv2.imwrite('output_gray.jpg', gray)
    cv2.imwrite('output_blurred.jpg', blurred)
    cv2.imwrite('output_edges.jpg', edges)
    cv2.imwrite('output_rotated.jpg', rotated)
    print("Đã lưu thành công các ảnh sau chỉnh sửa:")
    print(" - output_gray.jpg (Ảnh xám)")
    print(" - output_blurred.jpg (Ảnh mờ)")
    print(" - output_edges.jpg (Ảnh phát hiện cạnh)")
    print(" - output_rotated.jpg (Ảnh xoay 90 độ)")

    # --- HIỂN THỊ CÁC CỬA SỔ HÌNH ẢNH ---
    print("\nĐang mở các cửa sổ hiển thị ảnh...")
    print("Mẹo: Nhấp vào bất kỳ cửa sổ ảnh nào và nhấn phím bất kỳ trên bàn phím để tắt.")
    
    cv2.imshow('1. Original Image (Anh Goc)', original)
    cv2.imshow('2. Grayscale (Anh Xam)', gray)
    cv2.imshow('3. Gaussian Blur (Lam Mo)', blurred)
    cv2.imshow('4. Canny Edges (Tach Bien)', edges)
    cv2.imshow('5. Rotated (Xoay 90 Do)', rotated)

    # Giữ cửa sổ mở cho đến khi người dùng nhấn 1 phím bất kỳ
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Đã đóng chương trình xử lý ảnh.")

if __name__ == "__main__":
    apply_image_effects("input.jpg")

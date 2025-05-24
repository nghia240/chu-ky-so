##
Ứng dụng Truyền File với Ký Số

## Mô tả:
Đây là một ứng dụng desktop được xây dựng bằng Python cho phép truyền file an toàn giữa hai máy tính 
thông qua mạng với khả năng ký số và xác thực file.

## Tính năng chính:
1. Truyền file:
   - Gửi và nhận file giữa hai máy tính
   - Hỗ trợ mọi loại file (không giới hạn kích thước)
   - Hiển thị tiến trình truyền file
   - Tự động xử lý lỗi kết nối

## 2. Bảo mật:
   - Sử dụng RSA 2048-bit cho ký số
   - Tự động tạo cặp khóa khi khởi động
   - Trao đổi khóa công khai an toàn
   - Xác thực tính toàn vẹn file thông qua chữ ký số

## 3. Giao diện:
   - Thiết kế trực quan, dễ sử dụng
   - Hiển thị log chi tiết về mọi hoạt động
   - Hỗ trợ chọn file qua dialog
   - Hiển thị trạng thái kết nối

## Cách sử dụng:
1. Khởi động ứng dụng
2. Chọn vai trò:
   - Server: Nhấn "Tạo Server" và chọn port
   - Client: Nhập IP và port của server, nhấn "Kết nối"
3. Gửi file:
   - Chọn file cần gửi
   - Nhấn "Gửi File"
4. Nhận file:
   - Nhấn "Nhận File"
   - Chọn vị trí lưu file
   - Ứng dụng sẽ tự động xác thực chữ ký

## Yêu cầu hệ thống:
- Python 3.x
- Thư viện:
  + cryptography (mã hóa và ký số)
  + socket (kết nối mạng)
## Cài đặt
1. Clone repository này về máy local của bạn
2. Tạo môi trường ảo Python (khuyến nghị):
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

## Sử dụng
1. Khởi động ứng dụng:
   ```
   python file_transfer.py
   ```
## Bảo mật:
- Sử dụng RSA 2048-bit cho ký số
- PSS padding với SHA-256
- Trao đổi khóa công khai an toàn
- Xác thực tính toàn vẹn file

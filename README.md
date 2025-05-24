##
Ứng dụng Truyền File với Ký Số
##
Đây là một ứng dụng desktop được xây dựng bằng Python và Tkinter, cho phép:
1. Truyền file giữa hai máy tính thông qua mạng
2. Ký số file trước khi gửi để đảm bảo tính toàn vẹn và xác thực
3. Xác thực chữ ký khi nhận file
##
Tính năng chính:
- Giao diện đồ họa thân thiện với người dùng
- Hỗ trợ tạo server hoặc kết nối tới server
- Sử dụng RSA để ký số và xác thực file
- Hiển thị log chi tiết về quá trình truyền file
- Bảo mật thông qua mã hóa khóa công khai
##
Yêu cầu:
- Python 3.x
- Thư viện: cryptography
"""

# Kết quả kiểm tra — 13/11/2026

Đã chạy hai lượt `verify.sh` trên máy mô phỏng, không cấp điện cho robot, không gọi API hay mở mic/loa thật. Cả hai lượt đều đạt:

- 23 kiểm thử lõi điều khiển, tính hiệu cảm biến và bộ lập kế hoạch dock tượng trưng.
- 4 kiểm thử MuJoCo, bao gồm một phép nối `software/core.py` với trạng thái lý tưởng từ mô phỏng.
- 10 kiểm thử hội thoại bằng dịch vụ và thiết bị giả lập, bao gồm bốn ngôn ngữ và chế độ auto.
- Sáu STL kín, không có cạnh phi đa tạp theo phép kiểm tra; tái xuất từ OpenSCAD có kích thước và thể tích tương đồng.

Đầu vào mô phỏng gồm khối lượng giả định 2,7 kg, bánh Ø240 mm, giới hạn mô-men mô hình 1,37 N·m/bánh và bộ điều khiển nhận trạng thái lý tưởng. Với robot nghiêng ban đầu 2°, servo đầu ±0,4 rad và lực đẩy 1 N trong 0,1 giây, mô hình không vượt ngưỡng nghiêng 30° trong 10 giây, góc pitch tối đa khoảng 2°. Đối chứng ngắt điều khiển vượt ngưỡng ở 0,45 giây. Đây không phải thử robot thật, không chứng minh vật liệu/motor đủ bền, khả năng rẽ hay sạc.

Không có kiểm thử phần cứng Pi/motor/driver, độ trễ thực, in lắp, API thật hay chất lượng bốn ngôn ngữ. Các mẫu CAD chưa bao gồm toàn bộ khung chịu lực, gá motor/trục/bánh và dock; phần đầu ra motor chủ động khóa. TTS mặc định dự kiến ngừng ngày 06/01/2027, cần chuyển Realtime API như `voice/README.md`.

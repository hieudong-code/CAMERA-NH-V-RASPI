# Điều khiển Pi 4: bản mẫu phát triển

**Chưa chạy robot thật.** Chương trình giữ thăng bằng là bộ điều khiển thử nghiệm, chưa có hệ số đã hiệu chuẩn, chưa test thời gian thực, chưa xác minh encoder, góc IMU, cực motor, pin, PWM hay bộ driver. Phần xuất lệnh motor ở `motor_hardware.py` cố ý bị khóa; kể cả sửa cấu hình cũng không làm động cơ chạy. `demo.py` dùng số đo giả lập, không phải mô phỏng vật lý. Mọi giá trị điện và góc trong `config.example.json` là giá trị tham khảo, cần thiết kế lại/hiệu chỉnh trước khi nối thật.

Pi 4 chạy Linux có thể treo hoặc mất deadline. `pigpiod` có thể tiếp tục phát PWM kể cả chương trình đã chết. Cần có watchdog phần cứng độc lập đã thử, mạch ngắt hoặc vô hiệu hóa lệnh động cơ và giá đỡ chống đổ trước khi phát triển driver thật. Ngắt PWM có thể làm robot đang đứng bị ngã. Không sử dụng code này để vận hành robot mang tải hay gần người.

## Thử trên máy tính

Dùng Python 3.10 trở lên, không cần GPIO hoặc kết nối mạng:

```bash
python3 software/demo.py
python3 -m unittest discover -s software/tests -v
```

`core.py` có các trạng thái `DISARMED`, `ARMED`, `FAULT`, từ chối dữ liệu không hữu hạn, deadline quá hạn và góc quá giới hạn. `sensors.py` giải mã quadrature và lọc góc mẫu. Đầu vào IMU MPU-6050 phải được hiệu chỉnh hướng trục và độ lệch, đếm xung encoder phải kiểm tra mất xung khi Pi chạy âm thanh; chưa có mã đọc pin hay dừng sạc thật.

## Kiểm tra cảm biến trên Pi — KHÔNG cấp nguồn motor

BCM: I²C SDA2/SCL3; encoder trái A/B GPIO17/27, phải GPIO22/23; PWM bánh GPIO12/13, DIR GPIO5/6; PCA9685 servo kênh 0. `read_sensors.py` chỉ mở cảm biến và bốn chân encoder dưới dạng đầu vào, không cấu hình chân motor. Cần package Python `pigpio`, daemon `pigpiod`, I²C bật và MPU-6050 tại địa chỉ `0x68` (hoặc sửa cấu hình). Các phụ thuộc/cấu hình thực tế của Raspberry Pi OS cần được kiểm tra theo bản OS đang cài. Chỉ cấp nguồn 3,3 V tương thích Pi cho các tín hiệu. Khi đã sẵn sàng:

```bash
python3 software/read_sensors.py --seconds 10
```

`pitch_axis_sign` và offset phải hiệu chuẩn cho vị trí IMU; kết quả thô chưa phải chuẩn để chạy motor. Encoder cần xác nhận là ngõ A/B tối đa 3,3 V khi cấp ở 3,3 V. Chuyển cả hai bánh bằng tay và quan sát đếm xung/invalid; đếm không báo lỗi cũng không chứng minh không mất xung ở tốc độ cao. Servo chưa được điều khiển phần cứng. Không nối đầu ra hiện tại tới động cơ.


### Quy ước trục và dải đo IMU

Chẩn đoán giả định cảm biến đứng thẳng có gia tốc riêng +Z, chuyển động quay quanh +Y cho gia tốc riêng phía −X. Bộ lọc dùng `atan2(-ax, az)` và gyro +Y; `pitch_axis_sign` chỉ đảo dấu kết quả, không tự sửa cảm biến bị xoay sai trục. Khi khởi động, trình đọc chọn dải MPU-6050 ±2 g và ±250 độ/giây, sau đó đọc lại thanh ghi và dừng nếu dải không đúng. Kiểm tra hướng, dấu và hiệu chuẩn bằng tay trước bất kỳ tích hợp thực tế nào; chưa thử trên bo thật.

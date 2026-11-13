# Sơ đồ kết nối thử nghiệm — Pi 4 trực tiếp

**Trạng thái:** sơ đồ kiến trúc và phân bổ chân; chưa kiểm chứng trên bo thật. Phải kiểm tra revision, datasheet và ký hiệu trên từng module, đồng hồ đo điện áp, cấp thử mạch cảm biến bằng nguồn phù hợp có giới hạn dòng; với motor phải đáp ứng thêm điều kiện tái sinh bên dưới. Không áp dụng một sơ đồ pin khi code, thiết bị hoặc wiring khác cấu hình.

## Nguồn

```text
Pack Li-ion 3S + BMS (11,1 V danh định; tối đa 12,6 V)
  │
  ├─ Cầu chì chính gần pin + công tắc nguồn
  │    ├─ bus pin ─── MDD10A VMOTOR ── Motor trái/phải
  │    ├─ bus pin ─── buck 5–5,1 V >=3 A ── USB-C Pi 4
  │    ├─ bus pin ─── buck servo 5–6 V ── PCA9685 V+ ── servo đầu
  │    └─ bus pin ─── chia áp + bảo vệ ── ADS1115 A0
  └─ cổng sạc theo pack/BMS ── bảo vệ nhánh sạc riêng phù hợp ── bộ sạc 3S CC/CV 12,6 V
     (BMS có thể dùng cổng sạc riêng; không bỏ qua bảo vệ nhánh hoặc suy ra chân BMS)

Pi 3,3 V ── IMU I²C, logic PCA9685, ADS1115, encoder 3,3 V
Pi USB ───── micro USB và loa USB (chọn loại có ampli)
Pi CSI ───── camera và cáp Pi 4
```

Các mạch tín hiệu và driver cần **mass chung** theo kiến trúc thực, đường dòng motor đi riêng về nhánh nguồn để giảm nhiễu; không cho dòng motor chạy qua Pi. Nguồn servo V+ không nối vào 3,3 V. Không cấp động cơ hoặc 12,6 V vào GPIO; GPIO chỉ giao tiếp mức 3,3 V. Pi 4 sử dụng nguồn USB-C 5 V 3 A; chọn bộ ổn áp 5,1 V và kiểm tra điện áp tại cổng Pi lúc tải cao, motor khởi động/phanh. Bộ D24V50F5 5 V ±4% có thể xuống 4,8 V trước sụt cáp, không mặc định phù hợp. Ngõ 5 V trên driver MDD10A không chọn làm nguồn Pi khi chưa xác nhận định mức: dùng buck độc lập. Chống cấp ngược giữa các bộ nguồn.

Pin 3S đầy 12,6 V > 12 V danh định motor, cần xác nhận motor, nguồn và driver thực chịu được dải điện áp và xung tái sinh. MDD10A ở chế độ PWM/DIR khi PWM thấp có thể phanh điện, không được mặc định là thả trôi; driver có phanh tái sinh. Pack/BMS cần có đường nhận năng lượng trong điều kiện pin đầy hoặc ngắt BMS; đừng coi BMS là bộ tản năng lượng. Nguồn bàn giới hạn dòng thông thường cũng có thể không hấp thụ được dòng trả. Chưa có mạch clamp/hấp thụ bảo vệ xung hoàn chỉnh, chưa được cấp năng lượng cho động cơ kể cả từ nguồn bàn cho đến khi thiết kế và kiểm nghiệm phương án phù hợp.

## Chân đề xuất

Đánh số BCM và chân vật lý **header 40 chân Pi 4**. Đây là bản quy ước; kiểm tra config và các thiết bị trước đấu. Cổng USB và CSI là riêng.

| Chức năng | BCM | Chân vật lý | Ghi chú |
|---|---:|---:|---|
| I²C SDA1 | GPIO2 | 3 | Bus chung MPU-6050, PCA9685, ADS1115; tất cả logic/pull-up 3,3 V |
| I²C SCL1 | GPIO3 | 5 | Như trên |
| Motor trái PWM | GPIO12 | 32 | hardware PWM channel 0, nối PWM1 MDD10A |
| Motor trái DIR | GPIO5 | 29 | DIR1 MDD10A |
| Motor phải PWM | GPIO13 | 33 | hardware PWM channel 1, nối PWM2 MDD10A |
| Motor phải DIR | GPIO6 | 31 | DIR2 MDD10A |
| Encoder trái A | GPIO17 | 11 | Mức tín hiệu không quá 3,3 V |
| Encoder trái B | GPIO27 | 13 | Như trên |
| Encoder phải A | GPIO22 | 15 | Như trên |
| Encoder phải B | GPIO23 | 16 | Như trên |
| 3,3 V logic | — | 1 hoặc 17 | Xác minh tổng dòng và dây; dùng cho IMU, encoder và logic, không cấp motor/servo |
| GND tín hiệu | — | 6 hoặc GND khác | Mass chung có tổ chức, xem phần nguồn |
| Servo đầu | — | — | PCA9685 kênh 0; GND, tín hiệu và V+ đúng điện áp servo |

GPIO12/13 dùng **hai kênh PWM phần cứng khác nhau** nếu dùng overlay/driver và thư viện thực sự cấu hình hardware PWM. Python RPi.GPIO mặc định không chứng minh có PWM phần cứng. Cả hai kênh có thể chia sẻ clock/tần số: chọn cùng tần số và xác minh.  GPIO18/19 không tạo thêm hai kênh PWM phần cứng độc lập; tránh audio dùng PWM/I²S xung đột, chọn USB audio. Kích hoạt SPI/I²C, phần mềm PWM và overlay phải được xác minh trên bản OS thực; sơ đồ chân đơn thuần không chứng minh điều khiển đúng thời gian.

### Kết nối driver

- MDD10A có hai cặp PWM/DIR điều khiển hai kênh, nhận logic 3,3 V; đấu đúng tên terminal/phiên bản trong [tài liệu hãng](https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels). Không dùng driver khác cùng tên chân khi chưa kiểm tra.
- Hai motor, hai encoder độc lập. Không nối trục hai bánh cứng với nhau. Quy ước chiều tiến là giá trị cấu hình phần mềm; khi test nhấc bánh khỏi mặt đất, kiểm tra từng chiều và encoder trước khi cho giữ cân bằng.
- Encoder NFP có A/B, cấp **3,3 V**, pull-up tích hợp theo [tài liệu hãng](https://microdcmotors.com/product/37mm-12v-24v-permanent-magnet-brush-gear-motor-with-encoder-model-nfp-gm37-3429-en-2). Xác nhận thực tế bằng đồng hồ/logic analyzer, không áp dụng cho mọi encoder cùng dạng.
- Gắn IMU cố định cứng trên thân; đo ma trận phương trục khi lắp, hiệu chỉnh bias và góc. Gắn trên đầu servo sẽ làm cảm biến lắc theo đầu.

## Tư thế an toàn, pin thấp và dock

Robot hai bánh có thể ngã nếu ngắt motor. **Watchdog phần cứng độc lập và trạng thái khởi động an toàn là điều kiện bắt buộc** trước khi cấp động cơ: phần mềm không bảo vệ được Pi treo; pigpio/hardware PWM có thể tiếp tục phát lệnh sau khi process chết. Cần xác minh mạch watchdog, trạng thái điều khiển MDD10A khi hết heartbeat và năng lượng tái sinh của trạng thái đó; thiết kế chưa hoàn thiện, không cấp motor trước khi xác minh. Robot phải ở trong giá chống ngã.  Mất kết nối AI thì đặt mục tiêu vận tốc về 0 và tiếp tục cân bằng *nếu bộ điều khiển và nguồn còn hoạt động*. Nếu Pi treo, không thể hứa có bộ cân bằng dự phòng vì người dùng chọn không có vi điều khiển; dùng giá đỡ khi thử và thiết kế phần cứng bảo vệ độc lập. Không lập trình Pi ra lệnh bánh thực bằng các hệ số mô phỏng chưa kiểm chứng.

Bus pin có thể còn điện trong khi ADS1115 không có VDD: chia áp đơn thuần không đủ, phải có cách ly/clamp/trình tự nguồn được xác minh để tránh điện áp AIN vượt giới hạn hoặc cấp ngược. Chưa thiết kế xong, không đấu AIN.

Pin gần cạn cần dừng tác vụ và vào giá đỡ khi còn năng lượng dự phòng; ngắt BMS ở ngưỡng cuối có thể làm robot ngã. Tự sạc: đế đỡ robot, xác nhận dừng, kết nối tiếp điểm được bảo vệ vào bộ sạc 3S phù hợp và xác nhận dòng/trạng thái sạc. Khả năng vừa sạc vừa cấp Pi phụ thuộc power-path; cần phân tích riêng, không nối nguồn đế thẳng vào cell. Phần auto-dock hiện là yêu cầu thiết kế, chưa kiểm chứng.

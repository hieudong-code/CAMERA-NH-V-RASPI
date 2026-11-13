# BOM điện sơ bộ — robot hai bánh, Raspberry Pi 4

**Mục tiêu:** robot hai bánh tự cân bằng, đầu quay ngang, hội thoại tiếng Việt, Anh, Trung, Nhật qua mạng; dự kiến thêm dock. Pi 4 điều khiển trực tiếp, không dùng ESP32. Đây là BOM làm mẫu thử, **chưa phải danh sách đặt mua hàng loạt**. Mô hình trước dùng bánh Ø240 mm, robot khoảng 2,7 kg và mô-men motor giới hạn 1,37 N·m mỗi bánh; các số này là giả định mô phỏng, không phải phép đo robot thật.

| Mục | SL | Lựa chọn dự kiến và giới hạn |
|---|---:|---|
| Máy tính | 1 | Raspberry Pi 4 Model B 4 GB. Hệ điều hành Raspberry Pi OS 64-bit. |
| microSD | 1 | 32–64 GB, có độ bền ghi phù hợp. |
| Động cơ bánh | 2 | Ứng viên [NFP-GM37-3429-EN](https://microdcmotors.com/product/37mm-12v-24v-permanent-magnet-brush-gear-motor-with-encoder-model-nfp-gm37-3429-en-2), **12 V / 90:1**, encoder A/B cấp 3,3 V. Hãng ghi không tải 110 rpm ±15%, tại tải 65 rpm, mô-men định mức 14 kg·cm ≈1,37 N·m, dòng định mức ≤2,3 A, dòng kẹt ≤7 A mỗi motor. Số là công bố của hãng, không chứng minh robot này đủ lực. Đọc đúng biến thể 12 V và 90:1 khi mua. |
| Driver hai động cơ | 1 | [Cytron MDD10A Rev 2](https://www.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels), 5–30 V, 2 kênh, logic 3,3 V, 10 A/kênh liên tục theo hãng. Driver điều khiển PWM+DIR; 3,3 V là điện áp điều khiển, không phải nguồn motor. Đặc tính dòng phụ thuộc tản nhiệt, đấu dây và thời gian. |
| IMU | 1 | MPU-6050 breakout I²C thật sự tương thích 3,3 V, đo gia tốc + gyro; phải xác minh pull-up I²C không lên 5 V. Mô-đun phổ biến có biến thể khác nhau. |
| PWM servo | 1 | PCA9685 breakout, logic cấp 3,3 V, kênh 0 lái servo; cọc V+ cấp nguồn servo **riêng 5–6 V** phù hợp servo. Xác minh servo nhận tín hiệu 3,3 V. |
| Servo đầu | 1 | Servo quay góc 4,8–6 V; mô-men và dòng đỉnh chọn sau khi cân đầu và xác định tay đòn. Không kết luận servo 9 g đủ lực khi chưa thử. |
| Micro | 1 | Micro USB tương thích Linux, tránh dùng audio PWM/I²S trùng tài nguyên. |
| Loa | 1 | Loa USB chủ động, hoặc USB audio + ampli + loa; chọn theo nguồn và tải thực. |
| Camera | 1 bộ | Camera Pi tương thích CSI Pi 4, đúng loại cáp; phục vụ quan sát và thử nhận marker dock. |
| Pin | 1 bộ | Li-ion **3S**, 11,1 V danh định, 12,6 V khi đầy; pack lắp sẵn có BMS 3S bảo vệ, cân bằng và thông số dòng/nhà sản xuất rõ. Dòng liên tục và đỉnh phải chịu hai motor + buck Pi + servo + xung phanh. Dung lượng cân đối trọng tâm và thời gian chạy; chưa khóa trị số. |
| Bộ sạc | 1 | Bộ sạc **CC/CV 12,6 V cho Li-ion 3S** và dòng sạc theo pack; BMS không thay bộ sạc. Pin LiFePO₄ có điện áp khác, không dùng chung chỉ vì ghi 3S. |
| Buck Pi | 1 | Đầu vào chịu trọn dải pin và xung, đầu ra **5–5,1 V**, ít nhất 3 A ổn định tại đầu Pi dưới tải. Chọn bộ ổn áp 5,1 V có tài liệu rõ, đủ dòng trong điều kiện nhiệt thực tế; đo điện áp ngay tại đầu vào Pi khi tải cao. [D24V50F5](https://www.pololu.com/product/2851) 5 V có sai số ±4% (có thể 4,8 V trước sụt cáp), không mặc định phù hợp Pi 4 và không phải lựa chọn cắm-là-chạy. |
| Buck servo | 1 | Bộ hạ áp riêng, chọn 5–6 V theo servo, dòng đỉnh đủ tải. Không cấp servo bằng chân 3,3 V Pi. |
| Đo điện áp pin | 1 | ADS1115 I²C 3,3 V + chia áp và bảo vệ đầu vào theo điện áp bus, dùng đo điện áp gần đúng; chưa phải fuel gauge chính xác. Khi bus pin còn điện nhưng ADS1115 tắt VDD, AIN không được cấp ngược hoặc vượt giới hạn datasheet: mạch chia áp cần kèm cách ly/clamp và trình tự cấp nguồn đã xác minh, hoặc bỏ kết nối đo pin đến khi thiết kế xong. Không đưa trực tiếp 12,6 V vào ADS1115 hoặc GPIO. |
| Bảo vệ và dây | 1 bộ | Cầu chì chính gần pin; công tắc, dây, đầu nối có dòng định mức và giữ cơ khí phù hợp. Giá trị cụ thể chọn theo dòng đo, BMS, tiết diện dây và xung, không chỉ dòng chạy rỗng. MDD10A không có bảo vệ đảo cực nguồn motor. |
| Watchdog phần cứng độc lập | 1 bộ | Bắt buộc trước thử motor: giám sát heartbeat Pi, mặc định ngăn lệnh lái khi khởi động/treo. Có thể dùng watchdog rời và mạch khóa tín hiệu, **chưa chọn IC hoặc xác minh trạng thái ngõ ra driver**. Thiếu phần này thì không cấp motor. Không dùng bộ điều khiển thứ hai/ESP32. |
| Bảo vệ xung và hấp thụ năng lượng tái sinh | 1 bộ | Bắt buộc hoàn thiện theo dải bus, dòng, phanh MDD10A và pack/BMS; chưa có thiết kế hoặc thông số được xác minh. Cả nguồn bàn giới hạn dòng có thể không hấp thụ được năng lượng hồi tiếp. |
| Đo kiểm | 1 bộ | Đồng hồ điện, nguồn bàn có giới hạn dòng, tốt nhất thêm oscilloscope hoặc logic analyzer; kiểm tra encoder và sụt nguồn. |
| Dock (giai đoạn sau) | 1 bộ | Đế ôm đỡ thân, tiếp điểm chống chạm và ngược cực, charger 3S CC/CV, nhận biết sạc, mạch power-path nếu Pi còn hoạt động. Marker in và camera. Chưa có thiết kế điện hoàn thiện. |

## Trước khi đặt động cơ

- Pin 3S **đầy 12,6 V**, cao hơn 12 V danh định motor. Đề nghị xác nhận dải điện áp/tải và xung phanh với nhà sản xuất; không mặc định đủ tiêu chuẩn.
- Đo khối lượng robot, vị trí trọng tâm, gia tốc mong muốn, đường kính bánh và tải hướng kính. Phải chọn hộp số, động cơ, driver theo mô-men liên tục **và** mô-men/tốc độ đáp ứng khi cân bằng, không lấy mô-men kẹt làm mô-men liên tục. Kiểm tra hộp số có được phép chịu tải bánh hoặc thêm vòng bi đỡ.
- Hãng ghi dòng kẹt ≤7 A/motor ở 12 V; tổng 14 A là phép cộng tham khảo tại điều kiện đó, **không phải giới hạn trên** ở pin 12,6 V, theo sai số motor và xung thực. Pi, servo và khởi động còn tăng yêu cầu nguồn; phải đo. BMS, cầu chì, cáp và sạc phải đồng bộ thông số pack thực.
- Encoder hãng nói A/B với kéo lên tích hợp, hỗ trợ nguồn 3,3 V / 5 V. **Cấp 3,3 V và đo mức A/B thực**, xác minh dây và pull-up đúng trước khi nối vào GPIO. Không dùng loại Pololu 37D encoder 3,5 V tối thiểu như thể cũng chạy 3,3 V.
- Pi GPIO dùng mức 3,3 V và không chịu 5 V; tham khảo [Raspberry Pi GPIO](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html). Đọc hai encoder ở tốc độ thực bằng phần mềm cần benchmark lỗi xung và jitter khi AI, camera cùng chạy. Nếu 11 PPR là số xung của một kênh trên mỗi vòng motor và giải mã cả bốn cạnh, 90:1 × 110 rpm × 11 × 4 / 60 ≈ 7.260 cạnh/s mỗi motor; đây là ước tính có điều kiện, phải xác nhận cách hãng định nghĩa PPR và đo mất xung. Nếu không đạt, dùng bộ đếm encoder phần cứng 3,3 V phù hợp, không bắt buộc ESP32.

Giá, nguồn hàng, thuế, chi phí API AI và phí vận chuyển chưa được báo giá. Không khẳng định bản lắp này đã được kiểm thử phần cứng.

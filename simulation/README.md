# Mô phỏng hai bánh tự cân bằng

Mô hình MuJoCo khái niệm gồm thân cứng, hai bánh đồng trục dẫn động độc lập và đầu quay ngang. Robot có thể giữ tư thế trước–sau và lắc đầu trong thử nghiệm lý tưởng. Tham số hình học và khối lượng là **giả định**, chưa phải bản đo từ CAD, pin hoặc động cơ thực tế. Không dùng mã này để cấp lệnh trực tiếp cho robot.

## Cài trên máy tính Linux

Cần Python, môi trường có thể cài MuJoCo, NumPy và kết nối internet:

```bash
cd simulation
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python simulate.py --seconds 10
```

Để mở cửa sổ mô phỏng cần môi trường đồ họa MuJoCo hoạt động:

```bash
python simulate.py --viewer --seconds 10 --push-newtons 1
```

Tham số khác: `--pitch-deg 2` là góc nghiêng trước ban đầu, `--head-swing 0.4` là biên độ đầu tính bằng radian, `--push-newtons 1` là lực đẩy dọc X đặt tại giây thứ 2 trong 0,1 giây. `--no-control` ngắt điều khiển cả hai bánh để so sánh. Kết quả là JSON; `fell_at_s` xác định khi độ nghiêng vượt 30°, KHÔNG có nghĩa là có thể phát hiện hoặc ngăn ngã trên robot thật.

## Kiểm thử

```bash
python -m unittest -v test_simulation
```

Bài kiểm thử so sánh giữ tư thế với đầu chuyển động, bị đẩy ngắn và đối chứng tắt động cơ. Đây là kiểm thử của mã và vật lý *giả định*; thay tham số robot, độ trễ, ma sát, độ rơ hộp số hoặc va chạm đều có thể làm kết quả thay đổi.

## Giả định chính và giới hạn

- Bánh có bán kính **120 mm**, bề rộng **40 mm**, tâm bánh cách nhau **200 mm**. Mô hình có tổng khối lượng 2,7 kg (gồm hai bánh 0,35 kg, hai khối thân 1,8 kg và đầu 0,2 kg); kích thước, vị trí khối lượng chưa được cân đo.
- Giới hạn mô-men mỗi bánh **1,37 N·m** dùng như một giới hạn không đổi trong mô hình, gần mức 14 kg·cm danh định được nhà sản xuất công bố cho động cơ NFP 12 V/90:1. Đây KHÔNG phải mô hình đường đặc tính mô-men/tốc độ, giới hạn dòng điện, hộp số, pin, nhiệt độ, độ rơ hay bảo đảm động cơ thực chạy được như vậy. Tham khảo [thông số nhà sản xuất](https://microdcmotors.com/product/37mm-12v-24v-permanent-magnet-brush-gear-motor-with-encoder-model-nfp-gm37-3429-en-2).
- Điều khiển giả lập nhận trực tiếp góc, tốc độ và vị trí chính xác từ mô phỏng ở mỗi bước 2 ms. Nó chưa mô phỏng IMU nhiễu, encoder mất xung, trễ GPIO/Linux hay thời gian phản hồi động cơ; chưa dùng chương trình điều khiển Pi thật.
- Lệnh hai bánh hiện giống nhau. Mô hình có hai motor riêng nhưng **chưa kiểm thử rẽ**, dẫn đường đến trạm, tiếp xúc hoặc sạc điện. AI chưa điều khiển mô phỏng.
- Khối lượng Pi, pin, đầu và kích thước giá gắn sau khi chế tạo phải được đo và thay lại mô hình; sau đó đánh giá giữ đứng, phục hồi sau nhiễu, thay đổi tốc độ, nhiệt và lật ngang trước mọi thử nghiệm thật có giám sát.

## Kiểm tra tích hợp bộ điều khiển

Từ thư mục `simulation/`, chạy `python -m unittest -v test_controller_integration`. Bài này dùng `software/core.py` với góc và vận tốc lý tưởng do MuJoCo cung cấp, chuyển đơn vị đầu ra sang mô-men trong mô hình. Các cờ đã hiệu chỉnh chỉ được bật trong bài kiểm thử giả lập; chúng **không chứng nhận phần cứng**. Nó không kiểm tra Raspberry Pi, PWM, encoder hoặc thời gian thực.

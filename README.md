# Robot hai bánh nói chuyện AI — bộ mẫu phát triển

Bộ dự án khởi đầu cho robot hai bánh tự cân bằng theo ảnh tham khảo: Raspberry Pi 4 (không ESP32), cảm biến và encoder 3,3 V, đầu quay ngang và hội thoại tiếng Việt, Anh, Trung Quan thoại, Nhật. Mọi kích thước, khối lượng và lựa chọn linh kiện đều là phương án mẫu cần đo, đánh giá và hoàn thiện trước khi chế tạo.

**Không phải robot hoàn chỉnh sẵn sàng chạy.** Đầu ra động cơ bị khóa cứng: chương trình chưa được hiệu chuẩn, chưa có watchdog phần cứng được xác nhận, chưa có kiểm chứng thời gian thực hoặc bảo vệ nguồn tái sinh. Tự về sạc là bộ lập kế hoạch thử, chưa có camera marker/contact/charger được tích hợp. CAD là mẫu hình học; thiếu gá motor, trục, bánh, vỏ chịu lực và dock đã thiết kế. Không cấp điện động cơ dựa vào bộ mẫu này. Cần thiết kế, thử nghiệm phần cứng và bộ điều khiển thật trước khi sử dụng.

## Nội dung

- `docs/bom.md`: danh sách điện, thông số nguồn và linh kiện ứng viên.
- `docs/wiring.md`: kiến trúc nguồn, bảng chân Pi 4, các điều kiện cần hoàn thiện.
- `cad/`: sơ đồ trước/bên, OpenSCAD và 6 STL in thử hình khối; xem `cad/README.md` trước khi in.
- `simulation/`: mô phỏng hai bánh và servo đầu bằng MuJoCo, cùng thử nghiệm bộ điều khiển với số đo lý tưởng; không điều khiển hardware.
- `software/`: bộ điều khiển mẫu, trạng thái an toàn, đọc thử IMU và encoder, bộ lập kế hoạch dock chưa kết nối, kiểm thử; motor khóa.
- `checks/`: log và kết quả của hai lượt kiểm tra.
- `voice/`: hội thoại thử với dịch vụ AI, mic/loa, vi/en/zh/ja hoặc tự nhận diện; cần API key riêng, Internet, phần cứng audio và có thể phát sinh phí.

## Thử trên máy tính, không dùng robot

```bash
python3 -m unittest discover -s software/tests -v
cd simulation
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest -v test_simulation test_controller_integration
python simulate.py --seconds 10 --push-newtons 1
```

Sau khi cài các thư viện mô phỏng, chạy hai lượt tổng thể từ gốc: `PYTHON=simulation/.venv/bin/python ./verify.sh` (thực hiện hai lần). Từ gốc dự án, `python3 cad/kiemtra_mesh.py` kiểm tra lưới STL; `bash cad/kiemtra_render.sh` cần OpenSCAD và tái xuất để kiểm tra lưới/số đo. Xem riêng `voice/README.md` để cấu hình và thử hội thoại; kiểm thử voice giả lập không cần kết nối mạng và không phát sinh chi phí.

## Trước khi làm robot thật

1. Xác định linh kiện motor, tải, tốc độ và điện áp được phép, đo kích thước và trọng tâm; hoàn thiện khung chịu lực, gối trục, bánh, gá pin và cơ cấu đỡ khi tắt máy.
2. Thiết kế và kiểm tra watchdog phần cứng độc lập, bảo vệ tái sinh, BMS, đường sạc và nguồn. Đấu cảm biến mức 3,3 V, đo tín hiệu trước khi nối Pi; không đưa điện áp motor vào GPIO.
3. Đo và hiệu chuẩn trục IMU, encoder, PWM, độ trễ và mô-men, rồi kiểm thử có giá chống đổ. Kiểm tra hiệu năng khi âm thanh/camera hoạt động; Linux thông thường không bảo đảm thời gian thực.
4. Tích hợp camera, nhận trạm, xác nhận sạc và đế giữ thân; hiện chưa có bộ nguồn sạc tự động hoàn chỉnh.

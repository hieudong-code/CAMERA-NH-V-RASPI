# Bản vẽ cơ khí thử nghiệm — robot hai bánh

Đây là **bộ mẫu nghiên cứu kích thước**, chưa phải một robot có thể lắp và chạy ngay. Các thông số chưa được xác nhận bằng đo linh kiện. Khung mẫu in 3D không được chứng nhận chịu lực hoặc va đập; không dùng để chạy robot thật hoặc làm hộp bảo vệ bánh xe. Tải trọng, gá motor, bố trí pin, trục bánh, độ cứng, trọng tâm và khả năng cân bằng còn phải thiết kế, chế tạo, thử nghiệm.

## Bản vẽ và kích thước giả định

- `00_so_do_tham_khao.png` / `.svg`: phác thảo mặt trước và mặt bên. `00_phoi_canh_tham_khao.scad` là phối cảnh ba chiều để xem, **không xuất để in**; các khối chỉ đại diện cho hình dáng.
- Bánh đường kính **240 mm**, bề rộng giả định **40 mm**, tâm bánh cách **200 mm**. Phủ bì hai bánh khoảng **240 mm**; khoảng giữa hai mặt trong **160 mm**.
- Thân phác rộng **120 mm**, sâu **130 mm**, cao khoảng **240 mm**; có khoảng hở lý thuyết 20 mm mỗi bên trước khi tính gá động cơ, ốc và dây. Tâm bánh cách mặt sàn 120 mm.
- Các tấm sườn mẫu `04` và `05` rộng **130 mm**, khác thân 120 mm trong phối cảnh; nếu đặt giữa hai bánh như phác thảo thì hở lý thuyết **15 mm mỗi bên**. Phối cảnh và tấm mẫu chưa được tích hợp thành một cụm lắp hoàn chỉnh.
- Những con số này là giả định bố trí; phối cảnh không thể hiện toàn bộ dây, Pi, IMU, BMS, động cơ hay hộp số, không chứng minh vừa linh kiện. Tổng khối lượng 2,7 kg trong mô phỏng cũng là giả định, không phải trọng lượng thiết kế đã xác định.

## Các tệp STL để in thử

| Mã | Chi tiết | Số lượng thử | Kích thước bao | Công dụng và giới hạn |
|---|---|---:|---|---|
| `01_gia_pi4.stl` | Giá Pi 4 | 1 | 85 × 76 × 9 mm | Bốn lỗ 2,8 mm cách nhau 58 × 49 mm; trụ cao 6 mm. Dùng vít M2.5; chừa không gian cho đai ốc dưới tấm. Các rãnh ngoài chưa xác minh khớp khung. |
| `02_tam_servo.stl` | Tấm bắt servo | 1 | 80 × 55 × 4 mm | Cửa thân servo 23,5 × 12,5 mm; khe có thể chỉnh. **Chưa chốt servo**; đo thân, tai vít, đĩa servo và sửa SCAD trước khi dùng. |
| `03_tam_thiet_bi.stl` | Tấm phụ | 1–2 | 120 × 80 × 4 mm | Dành cho linh kiện nhẹ, các khe dành cho vít M4. Không phải kết cấu đỡ tải. |
| `04_khung_duoi_mau.stl` | Tấm sườn dưới mẫu | 2 | 130 × 150 × 4 mm | Phác bố trí thân, **không có lỗ motor/gối trục**, không dùng chịu tải. |
| `05_khung_tren_mau.stl` | Tấm sườn trên mẫu | 2 | 130 × 130 × 4 mm | Ghép chồng lên tấm dưới 40 mm: khe ở y=20 thẳng hàng khe y=130 tấm dưới. Chiều cao ghép 240 mm. |
| `06_vo_dau_mau.stl` | Vỏ đầu mẫu | 1 | 110 × 95 × 70 mm | Vỏ rỗng thành 2,4 mm, hai lỗ ăng-ten 6,5 mm. Chưa có gá/horn nối với servo hoặc gá camera. |

Với sáu chi tiết trên đều có file `.scad` cùng tên. Chúng dùng OpenSCAD, đơn vị mm, có thể sửa thông số rồi nhấn F6 và xuất STL. Số lượng là để thử lắp và xem tỷ lệ, không phải đơn đặt hàng linh kiện.

### In thử

Dùng máy in FDM có kích thước bàn ít nhất 130 × 150 mm cho tấm lớn nhất; 0,2 mm mỗi lớp, 3–4 lớp vách và khoảng 30–40% infill là cấu hình **thử**. In các tấm với mặt phẳng lớn nằm trên bàn; in vỏ đầu với mặt phẳng kín ở dưới, miệng hộp hướng lên. Cần in thử một mẫu nhỏ để kiểm tra độ chính xác lỗ; các giá trị in không tạo ra chứng nhận độ bền.

Bánh Ø240 mm lớn hơn nhiều bàn in 3D; dùng bánh có sẵn hoặc sau này thiết kế vành chia mảnh có kiểm tra đồng tâm, độ bền và cơ cấu kẹp. Bộ hiện tại **không có STL bánh, lốp, moay-ơ, vòng bi, gá trục hoặc gá động cơ NFP**, cũng không có vỏ bảo vệ hay cơ cấu dock. Không dùng trục motor chưa xác minh làm gối đỡ toàn bộ tải bánh.

## Kết cấu cơ khí cần hoàn thiện

1. Đo động cơ, lỗ bích và trục thật từ đúng model, có bản vẽ cơ khí nhà sản xuất. Thiết kế hai động cơ/hai trục độc lập để rẽ, cùng đường tâm, có ổ đỡ chịu tải hướng kính phù hợp.
2. Chốt kích thước bánh, trục, pin, driver và khoảng hở; thiết kế khung chịu lực bằng vật liệu đã chọn, giằng ngang và cơ cấu giữ pin. Cần tính/và thử tải, rung và va chạm.
3. Chốt servo và phương án lắp đầu sao cho dây không bị xoắn; thêm gối đỡ nếu cần, không đặt cả tải va đập lên bánh răng servo. Cố định IMU cứng vào thân.
4. Đo và cập nhật khối lượng, tâm khối lượng và mô-men quán tính vào mô phỏng, thử thăng bằng, trước/sau, rẽ, lắc đầu và nhiễu. Chưa thể suy từ bản vẽ hay mô phỏng hiện tại rằng robot thật đứng được.
5. Thiết kế vỏ bánh, kết cấu chống đổ khi thử và đế sạc đỡ thân khi tắt cân bằng. Đế và đường điện sạc chưa được thiết kế trong CAD này.

## Kiểm tra mô hình

Chạy `python cad/kiemtra_mesh.py` từ gốc dự án để kiểm tra lưới STL: tam giác hữu hạn, các cạnh thuộc đúng hai tam giác, thể tích hướng ra dương và kích thước bao. Chạy `bash cad/kiemtra_render.sh` nếu có OpenSCAD để tái xuất SCAD vào thư mục tạm, sau đó kiểm tra lại lưới kín, thể tích và kích thước. Hai phép này kiểm tra hình học số, **không** kiểm chứng dung sai in, độ bền, lắp ráp, an toàn hay khả năng hoạt động của robot thật.

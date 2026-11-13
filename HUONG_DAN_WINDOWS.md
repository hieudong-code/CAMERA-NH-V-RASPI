# Bắt đầu sử dụng trên Windows

Bạn có thể xem bản vẽ và thử mô phỏng trước khi mua linh kiện. Đây là bộ mẫu phát triển: chưa dùng để cấp điện motor thật, phần cứng chưa được kiểm chứng, các mẫu STL chưa phải toàn bộ robot lắp chạy.

## 1. Giải nén

Tải ZIP từ https://github.com/hieudong-code/CAMERA-NH-V-RASPI/releases/download/v0.1.0/robot_hai_banh_v0.1.0.zip . Trong Downloads, nhấp phải ZIP → **Extract All**. Mở thư mục `robot_hai_banh_v0.1.0`; phải thấy `README.md`, `simulation`, `voice`, `cad`, `software` và `docs`. Không chạy trực tiếp bên trong ZIP.

Trong File Explorer, mở thư mục này, bấm thanh địa chỉ, gõ `powershell` rồi Enter. Các lệnh sau chạy trong cửa sổ đó.

## 2. Cài Python và mở mô phỏng

Cài Python 3.12 bản 64-bit từ https://www.python.org/downloads/windows/ nếu chưa có. Cài kèm Python Launcher (`py`). Kiểm tra:

```powershell
py -3.12 --version
```

Tạo môi trường Python riêng trong thư mục dự án; không cần kích hoạt nên không phải sửa ExecutionPolicy:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\simulation\requirements.txt
.\.venv\Scripts\python.exe .\simulation\simulate.py --seconds 10
```

Lệnh cuối chạy kiểm tra không có cửa sổ, in kết quả JSON. Nếu thành công, mở mô phỏng 3D:

```powershell
.\.venv\Scripts\python.exe .\simulation\simulate.py --viewer --seconds 60
```

Mô hình hiện đứng thăng bằng và quay đầu theo kịch bản. Chưa có điều khiển bàn phím tiến/lùi/rẽ. Đóng cửa sổ để dừng. Các số đo là mô phỏng lý tưởng, không chứng minh robot thật chạy được.

Nếu `py` không nhận, cài/kiểm tra Python Launcher rồi mở lại PowerShell. Nếu không tìm thấy `requirements.txt`, kiểm tra đang ở thư mục có `README.md`. Nếu lệnh không cửa sổ chạy được nhưng `--viewer` lỗi OpenGL, cập nhật driver đồ họa hoặc thử trên máy khác; không tự sửa điều khiển cân bằng để chữa lỗi đồ họa.

## 3. Xem bản vẽ và mẫu in

- Mở `cad/00_so_do_tham_khao.png` để xem sơ đồ trước/bên ngay.
- Cài OpenSCAD từ https://openscad.org/downloads.html , mở `cad/00_phoi_canh_tham_khao.scad` để xem hình khối toàn robot. Phối cảnh này chỉ để xem, không xuất để in.
- Các tệp `cad/01_...scad` đến `cad/06_...scad` là mẫu chi tiết. Trong OpenSCAD, sửa kích thước nếu cần, nhấn F6 rồi File → Export → Export as STL. STL có sẵn có thể mở bằng phần mềm cắt lớp máy in.
- Đọc `cad/README.md` trước khi in: chưa có gá motor/trục/bánh và dock hoàn chỉnh, chưa xác nhận độ bền. Các mẫu hiện dùng để thử kích thước.

## 4. Hội thoại tiếng Việt, Anh, Trung hoặc Nhật

Cần mic, loa, Internet và tài khoản OpenAI API có quyền sử dụng model; có thể phát sinh phí. Nội dung giọng nói/văn bản được gửi đến dịch vụ. Kiểm thử hiện chỉ dùng dịch vụ giả lập, chưa thử mic/loa trên Windows hoặc API thật.

Cài các thư viện trong môi trường đã tạo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\voice\requirements.txt
.\.venv\Scripts\python.exe .\voice\voice_chat.py --list-devices
```

Đặt API key trong phiên PowerShell theo cách không in key ra màn hình; tự nhập key vào ô hỏi, không gửi key cho người khác:

```powershell
$robotApiKey = Read-Host 'OpenAI API key' -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $robotApiKey).Password
Remove-Variable robotApiKey
.\.venv\Scripts\python.exe .\voice\voice_chat.py --language auto
```

Nhấn Enter để bắt đầu ghi; nhấn Enter lần nữa để dừng sớm. `/clear` xóa lịch sử trong phiên; `/quit` thoát. Chọn một ngôn ngữ bằng cách thay `auto` bằng `vi`, `en`, `zh` (Trung Quan thoại) hoặc `ja`.

Thử chỉ văn bản, không dùng mic/loa:

```powershell
.\.venv\Scripts\python.exe .\voice\voice_chat.py --language vi --text 'Xin chào' --no-speech
```

Dùng `--input-device` và `--output-device` theo số thiết bị do `--list-devices` in ra nếu mặc định không đúng. Chương trình không cho AI điều khiển động cơ. Model TTS mặc định dự kiến ngừng ngày 06/01/2027; xem `voice/README.md` về giới hạn và nhu cầu cập nhật API.

Khi xong, xóa key khỏi phiên:

```powershell
Remove-Item Env:OPENAI_API_KEY
```

## 5. Linh kiện và Raspberry Pi

`docs/bom.md` là danh sách linh kiện ứng viên; `docs/wiring.md` là phân bổ chân và kiến trúc điện chưa kiểm chứng. `software/demo.py` có thể chạy trên Windows nhưng chỉ dùng dữ liệu giả. `software/read_sensors.py` dành cho Raspberry Pi, không chạy GPIO của Pi trên Windows. Đầu ra motor bị khóa cứng, không thể nạp vào Pi rồi cho robot chạy ngay. Giữ nguyên khóa cho đến khi nguồn, watchdog, cơ khí và hiệu chỉnh đã được hoàn thiện/thử thực tế.

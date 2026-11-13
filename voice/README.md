# Hội thoại bốn ngôn ngữ

Module này tách rời điều khiển động cơ. Khi nhấn Enter trên terminal, nó ghi tối đa 8 giây (mặc định), gửi âm thanh tới OpenAI để nhận dạng, tạo câu trả lời, rồi phát giọng tổng hợp. Mặc định `auto` chọn theo câu nói; `vi` tiếng Việt, `en` tiếng Anh, `zh` tiếng Trung Quan thoại, `ja` tiếng Nhật. Chất lượng và độ trễ phụ thuộc micro, mạng và dịch vụ; tự nhận diện có thể sai.

**Trạng thái:** đã kiểm thử logic qua dịch vụ giả lập. Chưa thử thực tế với micro/loa Pi hay API, vì chưa có thiết bị và khóa của bạn. Cần Internet, tài khoản API có quyền dùng model và có thể phát sinh phí. Âm thanh và văn bản được gửi tới OpenAI; dữ liệu chỉ giữ trong bộ nhớ chương trình phía robot, lịch sử mặc định tối đa sáu lượt. Chương trình thông báo giọng AI được tạo tổng hợp.

## Cài trên Raspberry Pi OS

Tại gốc dự án, tạo môi trường riêng, cài `portaudio` theo hướng dẫn Raspberry Pi OS rồi:

```bash
python3 -m venv .venv-voice
. .venv-voice/bin/activate
python -m pip install -r voice/requirements.txt
python voice/voice_chat.py --list-devices
```

Đặt `OPENAI_API_KEY` trong môi trường an toàn trên máy của bạn. Không ghi key vào mã nguồn, không đưa key vào Git, không gửi key trong cuộc trò chuyện. Sau đó:

```bash
python voice/voice_chat.py --language auto
python voice/voice_chat.py --language vi
python voice/voice_chat.py --language en
python voice/voice_chat.py --language zh
python voice/voice_chat.py --language ja
```

Nhấn Enter để ghi, Enter lần nữa để kết thúc sớm; `/clear` xóa lịch sử trong phiên, `/quit` thoát. Thêm `--input-device 1` hoặc `--output-device 2` theo danh sách thiết bị, nếu cần. Dùng `--text "Xin chào" --no-speech` để thử API văn bản mà không mở âm thanh. Đặt tên model bằng `ROBOT_STT_MODEL`, `ROBOT_CHAT_MODEL`, `ROBOT_TTS_MODEL` và giọng bằng `ROBOT_VOICE` nếu tài khoản và API của bạn hỗ trợ.

## Model và giới hạn sử dụng

Mặc định sử dụng `gpt-transcribe`, `gpt-6-luna`, và `gpt-4o-mini-tts` qua API tương ứng. Theo [lịch ngừng hỗ trợ của OpenAI](https://developers.openai.com/api/docs/deprecations), `gpt-4o-mini-tts` dự kiến ngừng ngày **06/01/2027**. Cần cập nhật code sang Realtime API trước thời điểm đó; không chỉ đổi biến tên model vì giao thức khác. Kiểm tra tài liệu model và tài khoản trước khi triển khai; dự án này chưa triển khai đường Realtime thay thế.

## Kiểm thử không dùng API

```bash
cd voice
python -m unittest -v test_voice_chat
```

Kiểm thử mô phỏng bốn mã ngôn ngữ/auto và lỗi, không gửi yêu cầu thật và không chứng minh chất lượng nhận diện hay phát âm.

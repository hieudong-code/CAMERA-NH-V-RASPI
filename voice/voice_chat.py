"""Four-language push-to-talk companion. No motors, sockets to robot, or disk audio."""

from __future__ import annotations

import argparse
import io
import math
import os
import select
import sys
import wave
from dataclasses import dataclass
from typing import Any, Callable

MAX_TEXT = 2000
MAX_TTS_BYTES = 24000 * 2 * 45
MAX_RECORD_SECONDS = 20
LANGUAGES = {
    "vi": "tiếng Việt", "en": "tiếng Anh", "zh": "tiếng Trung Quan thoại",
    "ja": "tiếng Nhật",
}
INSTRUCTIONS = (
    "Bạn là bạn đồng hành AI của một robot nhỏ. Trò chuyện thân thiện, "
    "trả lời ngắn trong 1–3 câu, không dùng Markdown. Bạn chỉ có chức năng hội thoại. "
    "Bạn không có quyền điều khiển động cơ, đi lại, sạc, hay đọc cảm biến. "
    "Không được nói rằng bạn đã thực hiện hành động vật lý. Nếu được yêu cầu di chuyển, "
    "giải thích rằng chức năng này chưa kết nối."
)


class VoiceError(Exception):
    """A user-facing error that never includes provider response bodies or secrets."""


@dataclass(frozen=True)
class Settings:
    stt_model: str = "gpt-transcribe"
    chat_model: str = "gpt-6-luna"
    tts_model: str = "gpt-4o-mini-tts"
    voice: str = "coral"
    language: str = "auto"
    seconds: float = 8.0
    sample_rate: int | None = None
    input_device: int | None = None
    output_device: int | None = None
    history_turns: int = 6

    def __post_init__(self) -> None:
        if self.language not in {"auto", *LANGUAGES}:
            raise VoiceError("Ngôn ngữ phải là auto, vi, en, zh hoặc ja.")
        if not math.isfinite(self.seconds) or not 0.2 <= self.seconds <= MAX_RECORD_SECONDS:
            raise VoiceError("Thời gian ghi cần từ 0,2 đến 20 giây.")
        if self.sample_rate is not None and not 8000 <= self.sample_rate <= 192000:
            raise VoiceError("Tần số ghi cần từ 8000 đến 192000 Hz.")
        if not 1 <= self.history_turns <= 12:
            raise VoiceError("Lịch sử cần từ 1 đến 12 lượt.")
        for name in (self.stt_model, self.chat_model, self.tts_model, self.voice):
            if not name or len(name) > 100 or any(c.isspace() for c in name):
                raise VoiceError("Tên model hoặc giọng không hợp lệ.")


def api_error(stage: str, exc: Exception) -> VoiceError:
    code = getattr(exc, "status_code", None)
    if code == 401:
        reason = "API key không hợp lệ; kiểm tra OPENAI_API_KEY trên máy của bạn."
    elif code == 429:
        reason = "Đã chạm hạn mức/tốc độ API; kiểm tra billing và thử lại sau."
    elif code in (400, 403, 404):
        reason = "Kiểm tra quyền truy cập và model trong cấu hình."
    else:
        reason = "Kiểm tra Internet hoặc thử lại sau."
    return VoiceError(f"Không thể {stage}. {reason}")


def checked_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VoiceError(f"{label} trống; chưa gửi bước tiếp theo.")
    text = value.strip()
    if len(text) > MAX_TEXT:
        raise VoiceError(f"{label} quá dài (tối đa {MAX_TEXT} ký tự).")
    # Remove control characters before displaying untrusted model/transcript text.
    clean = "".join(c for c in text if c.isprintable() or c in "\n\t").strip()
    if not clean:
        raise VoiceError(f"{label} không có nội dung đọc được.")
    return clean


def language_instruction(language: str) -> str:
    if language == "auto":
        return ("Tự nhận biết ngôn ngữ của câu người dùng mới nhất và trả lời bằng chính "
                "ngôn ngữ đó: tiếng Việt, tiếng Anh, tiếng Trung Quan thoại hoặc tiếng Nhật. "
                "Nếu chưa rõ, hỏi ngắn để làm rõ ngôn ngữ.")
    return f"Luôn trả lời bằng {LANGUAGES[language]}."


def wav_from_pcm(pcm: bytes, sample_rate: int) -> bytes:
    if not pcm or len(pcm) % 2 or not 8000 <= sample_rate <= 192000:
        raise VoiceError("Bản ghi âm không hợp lệ.")
    data = io.BytesIO()
    with wave.open(data, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(pcm)
    return data.getvalue()


class Conversation:
    """OpenAI SDK is injected, so tests require no key, network, or dependencies."""

    def __init__(self, client: Any, settings: Settings):
        self.client = client
        self.settings = settings
        self.history: list[dict[str, str]] = []

    def clear(self) -> None:
        self.history.clear()

    def transcribe(self, wav_audio: bytes) -> str:
        # Validate/bound data before upload, including callers other than the mic.
        valid = False
        if isinstance(wav_audio, bytes) and len(wav_audio) <= 8_000_000:
            try:
                with wave.open(io.BytesIO(wav_audio), "rb") as audio:
                    frames = audio.getnframes()
                    rate = audio.getframerate()
                    duration = frames / rate
                    valid = (audio.getnchannels() == 1 and audio.getsampwidth() == 2
                             and 8000 <= rate <= 192000
                             and 0.2 <= duration <= MAX_RECORD_SECONDS
                             and len(audio.readframes(frames)) == frames * 2)
            except (wave.Error, EOFError, ZeroDivisionError, ValueError):
                valid = False
        if not valid:
            raise VoiceError("Bản ghi cần WAV mono 16-bit, dài từ 0,2 đến 20 giây.")
        args: dict[str, Any] = {
            "model": self.settings.stt_model,
            "file": ("utterance.wav", wav_audio, "audio/wav"),
            "response_format": "json",
        }
        if self.settings.language == "auto":
            pass  # No language hint: let transcription detect the spoken language.
        elif self.settings.stt_model.startswith("gpt-transcribe"):
            # Current API: language hints are a list; extra_body works across SDK versions.
            args["extra_body"] = {"languages": [self.settings.language]}
        else:
            # Compatibility for older transcription models, until their retirement.
            args["language"] = self.settings.language
        try:
            result = self.client.audio.transcriptions.create(**args)
        except Exception as exc:
            raise api_error("nhận dạng lời nói", exc) from None
        return checked_text(getattr(result, "text", None), "Lời nhận dạng")

    def reply(self, text: str) -> str:
        text = checked_text(text, "Câu nói")
        messages = [*self.history, {"role": "user", "content": text}]
        try:
            kwargs = {
                "model": self.settings.chat_model,
                "instructions": INSTRUCTIONS + " " + language_instruction(self.settings.language),
                "input": messages,
                "max_output_tokens": 240,
                "store": False,
            }
            if self.settings.chat_model.startswith("gpt-6"):
                kwargs["reasoning"] = {"effort": "none"}
            result = self.client.responses.create(**kwargs)
        except Exception as exc:
            raise api_error("tạo câu trả lời", exc) from None
        reply = checked_text(getattr(result, "output_text", None), "Câu trả lời")
        # Commit only successful turns; failed requests do not pollute history.
        self.history = [*messages, {"role": "assistant", "content": reply}][
            -2 * self.settings.history_turns:
        ]
        return reply

    def speech(self, text: str) -> bytes:
        text = checked_text(text, "Câu trả lời")
        data = bytearray()
        try:
            with self.client.audio.speech.with_streaming_response.create(
                model=self.settings.tts_model,
                voice=self.settings.voice,
                input=text,
                instructions=("Nói rõ ràng, tự nhiên, thân thiện, tốc độ vừa phải. "
                              + ("Đọc đúng ngôn ngữ của văn bản đầu vào."
                                 if self.settings.language == "auto" else
                                 f"Đọc bằng {LANGUAGES[self.settings.language]}.")),
                response_format="pcm",
            ) as response:
                for chunk in response.iter_bytes(chunk_size=8192):
                    if len(data) + len(chunk) > MAX_TTS_BYTES:
                        raise VoiceError("Âm thanh trả về quá dài; đã dừng tải.")
                    data.extend(chunk)
        except VoiceError:
            raise
        except Exception as exc:
            raise api_error("tạo giọng nói", exc) from None
        if not data or len(data) % 2:
            raise VoiceError("Dịch vụ trả âm thanh PCM không hợp lệ.")
        return bytes(data)


def load_audio() -> Any:
    try:
        import sounddevice
        return sounddevice
    except (ImportError, OSError):
        raise VoiceError("Thiếu sounddevice/PortAudio. Xem phần cài đặt trong voice/README.md.") from None


class AudioDevices:
    """Raw streams avoid a NumPy dependency and keep clips in memory."""

    def __init__(self, settings: Settings, sd: Any):
        self.settings = settings
        self.sd = sd

    def record(self, stop_requested: Callable[[], bool] = lambda: False) -> bytes:
        try:
            rate = self.settings.sample_rate or int(
                self.sd.query_devices(self.settings.input_device, "input")["default_samplerate"]
            )
            if not 8000 <= rate <= 192000:
                raise VoiceError("Tần số micro không phù hợp; chọn --sample-rate.")
            target = int(rate * self.settings.seconds)
            block = max(1, int(rate * 0.05))
            captured = 0
            pcm = bytearray()
            with self.sd.RawInputStream(
                samplerate=rate, channels=1, dtype="int16",
                device=self.settings.input_device,
            ) as stream:
                while captured < target:
                    if stop_requested():
                        break
                    count = min(block, target - captured)
                    chunk, overflow = stream.read(count)
                    if overflow:
                        raise VoiceError("Micro bị mất mẫu; giảm tải CPU hoặc đổi thiết bị.")
                    if len(chunk) != count * 2:
                        raise VoiceError("Micro trả bản ghi thiếu mẫu.")
                    pcm.extend(chunk)
                    captured += count
            if captured < int(0.2 * rate):
                raise VoiceError("Bản ghi dưới 0,2 giây; chưa gửi lên mạng.")
            return wav_from_pcm(bytes(pcm), rate)
        except VoiceError:
            raise
        except Exception:
            raise VoiceError("Không ghi được micro. Kiểm tra --input-device và --sample-rate.") from None

    def play(self, pcm: bytes) -> None:
        if not pcm or len(pcm) % 2 or len(pcm) > MAX_TTS_BYTES:
            raise VoiceError("Âm thanh phát không hợp lệ.")
        try:
            # OpenAI PCM output is signed 16-bit little-endian mono at 24 kHz.
            with self.sd.RawOutputStream(
                samplerate=24000, channels=1, dtype="int16",
                device=self.settings.output_device,
            ) as stream:
                for start in range(0, len(pcm), 8192):
                    if stream.write(pcm[start:start + 8192]):
                        raise VoiceError("Loa bị thiếu dữ liệu; chọn thiết bị âm thanh khác.")
        except VoiceError:
            raise
        except Exception:
            raise VoiceError("Không phát được loa ở 24 kHz. Thử thiết bị ALSA mặc định.") from None


def enter_pressed() -> bool:
    # Pi/Linux terminal in canonical mode: readable when an entire ENTER line arrives.
    if select.select([sys.stdin], [], [], 0)[0]:
        sys.stdin.readline()
        return True
    return False


def create_client() -> Any:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise VoiceError("Chưa đặt OPENAI_API_KEY. Nhập khóa trên máy theo voice/README.md.")
    try:
        from openai import OpenAI
    except ImportError:
        raise VoiceError("Chưa cài OpenAI SDK. Chạy pip install -r voice/requirements.txt.") from None
    # Fixed official endpoint prevents an inherited OPENAI_BASE_URL redirecting audio/key.
    return OpenAI(api_key=key, base_url="https://api.openai.com/v1", timeout=30.0, max_retries=0)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Robot hội thoại 4 ngôn ngữ qua OpenAI, không điều khiển động cơ.")
    p.add_argument("--language", choices=("auto", "vi", "en", "zh", "ja"), default="auto",
                   help="auto tự nhận biết; vi Việt, en Anh, zh Trung Quan thoại, ja Nhật")
    p.add_argument("--list-devices", action="store_true", help="Liệt kê micro/loa, không cần API key")
    p.add_argument("--input-device", type=int, help="ID micro USB từ danh sách thiết bị")
    p.add_argument("--output-device", type=int, help="ID loa từ danh sách thiết bị")
    p.add_argument("--seconds", type=float, default=8.0, help="Giới hạn mỗi bản ghi, mặc định 8, tối đa 20")
    p.add_argument("--sample-rate", type=int, help="Tần số micro; mặc định theo thiết bị")
    p.add_argument("--text", help="Gửi một câu gõ sẵn thay cho mở micro")
    p.add_argument("--no-speech", action="store_true", help="Chỉ in câu trả lời; bỏ TTS/loa")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    client = None
    try:
        if args.list_devices:
            print(load_audio().query_devices())
            return 0
        settings = Settings(
            stt_model=os.environ.get("ROBOT_STT_MODEL", "gpt-transcribe"),
            chat_model=os.environ.get("ROBOT_CHAT_MODEL", "gpt-6-luna"),
            tts_model=os.environ.get("ROBOT_TTS_MODEL", "gpt-4o-mini-tts"),
            voice=os.environ.get("ROBOT_VOICE", "coral"),
            language=args.language,
            seconds=args.seconds, sample_rate=args.sample_rate,
            input_device=args.input_device, output_device=args.output_device,
        )
        if args.text is None and not sys.stdin.isatty():
            raise VoiceError("Chế độ micro cần terminal tương tác. Dùng --text khi không có terminal.")
        audio = None if args.text is not None and args.no_speech else AudioDevices(settings, load_audio())
        client = create_client()
        chat = Conversation(client, settings)
        print("Bạn đang trò chuyện với AI; giọng nói phát ra được AI tạo.")
        print("Âm thanh và nội dung hội thoại được gửi đến OpenAI; chương trình không ghi chúng ra đĩa.")
        if args.text is not None:
            reply = chat.reply(args.text)
            print("Robot:", reply)
            if not args.no_speech:
                audio.play(chat.speech(reply))
            return 0
        print("ENTER để ghi; ENTER lần nữa để dừng sớm. /clear xóa lịch sử; /quit thoát.")
        while True:
            command = input("Sẵn sàng > ").strip()
            if command == "/quit":
                break
            if command == "/clear":
                chat.clear()
                print("Đã xóa lịch sử trong phiên.")
                continue
            if command:
                print("Nhấn ENTER để ghi, hoặc nhập /clear hay /quit.")
                continue
            try:
                print(f"Đang ghi, tối đa {settings.seconds:g} giây… ENTER để dừng.", flush=True)
                wav_audio = audio.record(enter_pressed)
                print("Đã tắt micro. Đang nhận dạng…", flush=True)
                text = chat.transcribe(wav_audio)
                del wav_audio
                print("Bạn:", text)
                reply = chat.reply(text)
                print("Robot:", reply)
                if not args.no_speech:
                    audio.play(chat.speech(reply))
            except VoiceError as exc:
                print("Lỗi:", exc, file=sys.stderr)
        return 0
    except (KeyboardInterrupt, EOFError):
        print("\nĐã dừng; micro/loa đã đóng.")
        return 0
    except VoiceError as exc:
        print("Lỗi:", exc, file=sys.stderr)
        return 2
    except Exception:
        # Never display raw SDK response, traceback, key, URL, or audio payload.
        print("Không thể chạy hội thoại. Kiểm tra cấu hình và hướng dẫn xử lý lỗi.", file=sys.stderr)
        return 2
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

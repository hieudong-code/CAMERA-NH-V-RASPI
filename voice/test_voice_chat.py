import io
import math
import types
import unittest
import wave
from unittest.mock import Mock

import voice_chat as v

class FakeSpeechResponse:
    def __init__(self, chunks): self.chunks = chunks
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def iter_bytes(self, chunk_size): yield from self.chunks

class FakeAudio:
    def __init__(self, overflow=False):
        self.requests = []
        self.overflow = overflow
        self.closed = False
        self.output = []
    def query_devices(self, device, kind): return {'default_samplerate': 8000}
    def RawInputStream(self, **kwargs):
        outer = self
        class Stream:
            def __enter__(self): return self
            def __exit__(self, *args): outer.closed = True
            def read(self, frames):
                outer.requests.append(frames)
                return b'\0\0' * frames, outer.overflow
        return Stream()
    def RawOutputStream(self, **kwargs):
        outer = self
        class Stream:
            def __enter__(self): return self
            def __exit__(self, *args): outer.closed = True
            def write(self, pcm): outer.output.append(bytes(pcm)); return False
        return Stream()

def fake_client():
    stt = Mock(return_value=types.SimpleNamespace(text='  Xin chào  '))
    response = Mock(return_value=types.SimpleNamespace(output_text='  Chào bạn!  '))
    tts = Mock(return_value=FakeSpeechResponse([b'\0\0', b'\1\0']))
    client = types.SimpleNamespace(
        audio=types.SimpleNamespace(transcriptions=types.SimpleNamespace(create=stt),
             speech=types.SimpleNamespace(with_streaming_response=types.SimpleNamespace(create=tts))),
        responses=types.SimpleNamespace(create=response))
    return client, stt, response, tts

def clip(seconds=.25): return v.wav_from_pcm(b'\0\0' * round(8000 * seconds), 8000)

class VoiceTests(unittest.TestCase):
    def test_four_languages_and_auto_transcription_and_reply(self):
        for language in ('vi', 'en', 'zh', 'ja', 'auto'):
            with self.subTest(language=language):
                c, stt, reply, tts = fake_client()
                bot = v.Conversation(c, v.Settings(language=language))
                self.assertEqual(bot.transcribe(clip()), 'Xin chào')
                request = stt.call_args.kwargs
                self.assertEqual(request['model'], 'gpt-transcribe')
                if language == 'auto':
                    self.assertNotIn('language', request)
                    self.assertNotIn('extra_body', request)
                else:
                    self.assertEqual(request['extra_body'], {'languages': [language]})
                self.assertEqual(bot.reply('hello'), 'Chào bạn!')
                kwargs = reply.call_args.kwargs
                self.assertIn(v.language_instruction(language), kwargs['instructions'])
                self.assertEqual(kwargs['store'], False)
                self.assertEqual(bot.speech('hi'), b'\0\0\1\0')
                self.assertIn('instructions', tts.call_args.kwargs)

    def test_legacy_transcription_language_parameter(self):
        c, stt, _, _ = fake_client()
        v.Conversation(c, v.Settings(language='ja', stt_model='whisper-1')).transcribe(clip())
        self.assertEqual(stt.call_args.kwargs['language'], 'ja')
        self.assertNotIn('extra_body', stt.call_args.kwargs)

    def test_config_rejects_invalid_values(self):
        for kwargs in ({'language': 'fr'}, {'seconds': 0}, {'seconds': float('nan')},
                       {'seconds': 21}, {'history_turns': 13}, {'stt_model': 'a\nb'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(v.VoiceError):
                v.Settings(**kwargs)

    def test_wav_rejects_truncation_and_malformed(self):
        c, stt, _, _ = fake_client()
        bot = v.Conversation(c, v.Settings())
        for payload in (b'garbage', clip()[:-4], clip(.1), b'\0' * 8_000_001):
            with self.subTest(length=len(payload)), self.assertRaises(v.VoiceError):
                bot.transcribe(payload)
        stt.assert_not_called()

    def test_history_bounded_and_reset(self):
        c, _, response, _ = fake_client()
        bot = v.Conversation(c, v.Settings(history_turns=2))
        for i in range(3): bot.reply('turn ' + str(i))
        self.assertEqual([x['content'] for x in bot.history if x['role'] == 'user'], ['turn 1', 'turn 2'])
        bot.clear()
        self.assertEqual(bot.history, [])
        self.assertEqual(response.call_count, 3)

    def test_failed_calls_do_not_leak_or_commit_history(self):
        c, stt, response, tts = fake_client()
        secret = 'secret-api-key-please-never-print'
        response.side_effect = TimeoutError(secret)
        bot = v.Conversation(c, v.Settings())
        with self.assertRaises(v.VoiceError) as err: bot.reply('test')
        self.assertNotIn(secret, str(err.exception))
        self.assertEqual(bot.history, [])
        stt.side_effect = TimeoutError(secret)
        with self.assertRaises(v.VoiceError) as err: bot.transcribe(clip())
        self.assertNotIn(secret, str(err.exception))
        tts.side_effect = TimeoutError(secret)
        with self.assertRaises(v.VoiceError) as err: bot.speech('hi')
        self.assertNotIn(secret, str(err.exception))

    def test_oversized_and_invalid_pcm_rejected(self):
        c, _, _, tts = fake_client()
        bot = v.Conversation(c, v.Settings())
        for chunks in ([b'a'], [b'a' * (v.MAX_TTS_BYTES + 2)], []):
            with self.subTest(size=sum(map(len,chunks))), self.assertRaises(v.VoiceError):
                tts.return_value = FakeSpeechResponse(chunks)
                bot.speech('hello')

    def test_record_is_bounded_and_closes(self):
        audio = FakeAudio()
        devices = v.AudioDevices(v.Settings(seconds=.4), audio)
        recorded = devices.record()
        with wave.open(io.BytesIO(recorded), 'rb') as f:
            self.assertEqual(f.getnframes(), 3200)
        self.assertEqual(sum(audio.requests), 3200)
        self.assertTrue(audio.closed)

    def test_stop_early_and_overflow_close_stream(self):
        audio = FakeAudio()
        called = 0
        def stop():
            nonlocal called
            called += 1
            return called > 6
        devices = v.AudioDevices(v.Settings(seconds=2), audio)
        recorded = devices.record(stop)
        with wave.open(io.BytesIO(recorded), 'rb') as f:
            self.assertLess(f.getnframes(), 16000)
        self.assertTrue(audio.closed)
        audio2 = FakeAudio(overflow=True)
        with self.assertRaises(v.VoiceError):
            v.AudioDevices(v.Settings(), audio2).record()
        self.assertTrue(audio2.closed)

    def test_play_stream_and_bound(self):
        audio = FakeAudio()
        dev = v.AudioDevices(v.Settings(), audio)
        pcm = b'\0\0' * 9000
        dev.play(pcm)
        self.assertEqual(b''.join(audio.output), pcm)
        self.assertTrue(audio.closed)
        with self.assertRaises(v.VoiceError): dev.play(b'odd')

if __name__ == '__main__': unittest.main()

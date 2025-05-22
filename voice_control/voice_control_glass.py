# SSAFY 13 embedded proj.
# AR Glass - Voice Control Only

from PIL import Image, ImageDraw, ImageFont
import board
import digitalio
import adafruit_ssd1306
from datetime import datetime, timedelta, timezone
from gpiozero import Button
from google.cloud import speech
import pyaudio
import queue
import threading
import asyncio
import websockets

# OLED 설정
disp_width, disp_height = 64, 128
oled_reset = digitalio.DigitalInOut(board.D24)
oled_cs = digitalio.DigitalInOut(board.D23)
oled_dc = digitalio.DigitalInOut(board.D25)
TimeZone = timezone(timedelta(hours=9))  # KST

font_small = ImageFont.truetype('malgun.ttf', 15)
font_big = ImageFont.truetype('malgun.ttf', 25)

ACT_BUTTON_PIN = 16
serverURI = 'ws://192.168.137.250:7890'

# 음성 데이터 스트림 클래스
class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True
        self.frame_count = 0

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        print('mic ends')
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            data = []
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            self.frame_count += 1
            yield b''.join(data)

# Voice Mode 클래스
class VoiceMode:
    def __init__(self):
        self.screenImage = Image.new('1', (disp_width, disp_height), 0)
        self.draw = ImageDraw.Draw(self.screenImage)
        self.is_websocket_active = False
        self.lasttime_you_said = []
        self.words_to_show = []
        self.command_list = []

        self.rate = 16000
        self.chunk = int(self.rate / 10)
        self.encoding = 'LINEAR16'
        self.language_code = 'ko-KR'

        self.client = speech.SpeechClient()
        self.client_config = speech.RecognitionConfig(
            encoding=self.encoding,
            sample_rate_hertz=self.rate,
            max_alternatives=1,
            language_code=self.language_code
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.client_config,
            interim_results=True
        )

        mic_thread = threading.Thread(target=self.doVoiceRecognition)
        mic_thread.start()

    def update(self):
        self.draw.rectangle((0, 0, disp_width, disp_height), fill=0)
        text = ' '.join(self.words_to_show) + '\n...' if self.is_websocket_active else 'press\nACTION\nfor\nvoice\ninput'
        self.draw.multiline_text((0, 10), text, align='center', font=font_small, fill=1)

    def actButtonPressed(self):
        self.is_websocket_active = not self.is_websocket_active
        if self.is_websocket_active:
            self.websocket_thread = threading.Thread(target=self.doWebsocketClient)
            self.websocket_thread.start()
        else:
            self.websocket_thread.join()

    def doWebsocketClient(self):
        asyncio.run(self.websocket_client())

    async def websocket_client(self):
        try:
            async with websockets.connect(serverURI) as websocket:
                print("[DEBUG] WebSocket 연결됨")
                while True:
                    if self.command_list:
                        print(f"[DEBUG] 전송할 명령: {self.command_list}")
                        for command in self.command_list:
                            await websocket.send(command)
                            print(f'[TX] "{command}" 전송됨')
                            resp = await websocket.recv()
                            print(f'[RX] 응답 수신: {resp}')
                        self.command_list = []
                    if not self.is_websocket_active:
                        print("[INFO] WebSocket 종료")
                        break
        except Exception as e:
            print(f'[ERROR] WebSocket 오류: {e}')

    def doVoiceRecognition(self):
        with MicrophoneStream(self.rate, self.chunk) as stream:
            while not stream.closed:
                audio_generator = stream.generator()
                requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
                responses = self.client.streaming_recognize(self.streaming_config, requests)
                self.listen_print_loop(responses, stream)

    def listen_print_loop(self, responses, stream):
        for response in responses:
            if stream.frame_count > 60 * self.rate / self.chunk:
                stream.frame_count = 0
                break
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            tr = transcript.split()
            if self.lasttime_you_said == []:
                self.words_to_show = tr
            elif tr == self.lasttime_you_said:
                continue
            elif len(tr) < len(self.lasttime_you_said):
                self.words_to_show = [w for i, w in enumerate(tr) if i >= len(self.lasttime_you_said) or w != self.lasttime_you_said[i]]
            else:
                self.words_to_show = [w for i, w in enumerate(tr) if i >= len(self.lasttime_you_said) or w != self.lasttime_you_said[i]]
            self.lasttime_you_said = tr
            self.command_list = self.words_to_show
            print(f'[RECOGNIZED] {self.words_to_show}')

# 메인 루프
def main():
    spi = board.SPI()
    oled = adafruit_ssd1306.SSD1306_SPI(disp_height, disp_width, spi, oled_dc, oled_reset, oled_cs)
    oled.fill(0)
    oled.show()

    voicemode = VoiceMode()
    act_button = Button(ACT_BUTTON_PIN)
    act_button.when_pressed = voicemode.actButtonPressed

    try:
        while True:
            voicemode.update()
            flipped = voicemode.screenImage.transpose(Image.FLIP_LEFT_RIGHT)
            rotated = flipped.transpose(Image.ROTATE_90)
            oled.image(rotated)
            oled.show()
    except KeyboardInterrupt:
        print('사용자 종료')
        oled.fill(0)
        oled.show()
    except:
        print('예기치 못한 종료')
        oled.fill(0)
        oled.show()

if __name__ == '__main__':
    main()

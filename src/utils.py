from PyQt5.QtCore import QTimer
import pyttsx3
from gtts import gTTS
import os
import playsound

class TextToSpeechApp:
    def __init__(self):
        # Khởi tạo pyttsx3 (offline)
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Tốc độ nói (mặc định 200)
        self.engine.setProperty('volume', 1)  # Âm lượng (0.0 to 1.0)
        self.is_speaking = False  # Cờ kiểm tra trạng thái phát âm
        self.timer = QTimer()  # Tạo một QTimer
        self.timer.setSingleShot(True)  # Đảm bảo chỉ chạy 1 lần
        self.timer.timeout.connect(self.resume_speaking)  # Khi hết thời gian, gọi hàm resume_speaking

    def speak_offline(self, text):
        """Sử dụng pyttsx3 để phát âm (offline)"""
        if not self.is_speaking:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()  # Đợi cho đến khi phát âm hoàn tất
            self.timer.start(1)  # Đợi 2 giây trước khi cho phép phát âm tiếp

    def speak_online(self, text, lang='en'):
        """Sử dụng gTTS để phát âm (online)"""
        if not self.is_speaking:
            self.is_speaking = True
            tts = gTTS(text=text, lang=lang, slow=False)
            temp_audio_file = 'temp_audio.mp3'
            tts.save(temp_audio_file)
            playsound.playsound(temp_audio_file)
            os.remove(temp_audio_file)
            self.timer.start(2000)  # Đợi 2 giây trước khi cho phép phát âm tiếp

    def speak(self, text, use_online=True):
        """Chọn phương thức phát âm: online (gTTS) hoặc offline (pyttsx3)"""
        if use_online:
            print("Sử dụng phát âm online...")
            self.speak_online(text)
        else:
            print("Sử dụng phát âm offline...")
            self.speak_offline(text)

    def resume_speaking(self):
        """Hàm này sẽ được gọi sau khi chờ đợi 2 giây"""
        self.is_speaking = False  # Đánh dấu là không còn phát âm nữa

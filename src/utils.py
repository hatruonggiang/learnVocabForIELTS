from gtts import gTTS
import os
import pygame
import time

class TextToSpeechApp:
    def __init__(self):
        pygame.mixer.init()

    def speak_online(self, text, lang='en'):
        tts = gTTS(text=text, lang=lang, slow=False)
        temp_audio_file = 'temp_audio.mp3'
        tts.save(temp_audio_file)

        pygame.mixer.music.load(temp_audio_file)
        pygame.mixer.music.play()

        # Chờ phát xong
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Dừng hẳn, đợi một lúc trước khi xóa
        pygame.mixer.music.stop()
        pygame.mixer.quit()  # <- QUAN TRỌNG: đóng mixer để giải phóng file
        time.sleep(0.3)

        # Thử xóa nhiều lần nếu file vẫn bị lock
        for _ in range(5):
            try:
                os.remove(temp_audio_file)
                break
            except PermissionError:
                time.sleep(0.2)

        # Khởi động lại mixer cho lần sau
        pygame.mixer.init()

    def speak(self, text):
        print("Sử dụng phát âm online...")
        self.speak_online(text)

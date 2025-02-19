import cv2
import numpy as np
import win32api
import random
import threading
import time
from capture import Capture
from mouse import Mouse
from settings import Settings

class Colorbot:
    """
    Colorbot sınıfı, ekran yakalama, renk algılama ve fare kontrolü işlemlerini yönetir.
    Ekranda belirli renklere nişan almayı ve renk belirli bir bölgede olduğunda eylemleri tetiklemeyi destekler.
    """

    def __init__(self, x, y, x_fov, y_fov):
        """
        Colorbot'ı ekran yakalama parametreleri ile başlatır.

        Args:
            x (int): Yakalama başlangıç noktası için X koordinatı.
            y (int): Yakalama başlangıç noktası için Y koordinatı.
            x_fov (int): Yakalama alanının genişliği.
            y_fov (int): Yakalama alanının yüksekliği.
        """
        self.capturer = Capture(x, y, x_fov, y_fov)
        self.mouse = Mouse()
        self.settings = Settings()

        # Renk algılama ayarları (HSV)
        self.lower_color = np.array([150, 76, 123])  # Kullanıcıdan alınan değerlerle güncellenebilir
        self.upper_color = np.array([160, 197, 255])  # Kullanıcıdan alınan değerlerle güncellenebilir

        # Aimbot ayarları
        self.aim_enabled = self.settings.get_boolean('Aimbot', 'Enabled')
        self.aim_key = int(self.settings.get('Aimbot', 'toggleKey'), 16)
        self.x_speed = self.settings.get_float('Aimbot', 'xSpeed')
        self.y_speed = self.settings.get_float('Aimbot', 'ySpeed')
        self.x_fov = self.settings.get_int('Aimbot', 'xFov')
        self.y_fov = self.settings.get_int('Aimbot', 'yFov')
        self.target_offset = self.settings.get_float('Aimbot', 'targetOffset')

        # Triggerbot ayarları
        self.trigger_enabled = self.settings.get_boolean('Triggerbot', 'Enabled')
        self.trigger_key = int(self.settings.get('Triggerbot', 'toggleKey'), 16)
        self.min_delay = self.settings.get_int('Triggerbot', 'minDelay')
        self.max_delay = self.settings.get_int('Triggerbot', 'maxDelay')
        self.x_range = self.settings.get_int('Triggerbot', 'xRange')
        self.y_range = self.settings.get_int('Triggerbot', 'yRange')

        # Önceden hesaplanmış değerler
        self.kernel = np.ones((3, 3), np.uint8)
        self.screen_center = (self.x_fov // 2, self.y_fov // 2)
        self.capture_interval = 0.05  # Ekran yakalama sıklığı (50 ms)

    def listen_aimbot(self):
        """
        Aimbot tuşuna basılmasını sürekli dinler ve nişan alma işlemlerini gerçekleştirir.
        """
        while True:
            if win32api.GetAsyncKeyState(self.aim_key) < 0:
                self.process("move")
            time.sleep(0.01)  # Yüksek CPU kullanımını önlemek için küçük bir uyku

    def listen_triggerbot(self):
        """
        Triggerbot tuşuna basılmasını sürekli dinler ve tıklama işlemlerini gerçekleştirir.
        """
        while True:
            if win32api.GetAsyncKeyState(self.trigger_key) < 0:
                self.process("click")
            time.sleep(0.01)  # Yüksek CPU kullanımını önlemek için küçük bir uyku

    def listen(self):
        """
        Hem aimbot hem de triggerbot işlevsellikleri için dinleyicileri başlatır.
        """
        if self.aim_enabled:
            threading.Thread(target=self.listen_aimbot).start()
        if self.trigger_enabled:
            threading.Thread(target=self.listen_triggerbot).start()

    def process(self, action):
        """
        Yakalanan ekranı işleyerek belirtilen rengi algılar ve algılanan hedefe göre eylemler gerçekleştirir.

        Args:
            action (str): Gerçekleştirilecek eylem, "move" fareyi hareket ettirmek için veya "click" tıklama tetiklemek için.
        """
        # Yakalanan ekranı HSV renk alanına dönüştür
        hsv = cv2.cvtColor(self.capturer.get_screen(), cv2.COLOR_BGR2HSV)
        
        # Algılanan renklerin beyaz, diğer her şeyin siyah olduğu bir ikili maske oluştur
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        
        # Maskeyi genişleterek algılanan bölgeleri daha belirgin hale getir
        dilated = cv2.dilate(mask, self.kernel, iterations=5)
        
        # İkili bir görüntü elde etmek için eşikleme uygula
        thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]
        
        # İkili görüntüde konturları bul
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Algılanan konturları işle
        if contours:
            min_distance = float('inf')
            closest_center = None
            
            for contour in contours:
                # Ekranın merkezine en yakın konturu bulmak için momentleri kullan
                moments = cv2.moments(contour)
                if moments['m00'] != 0:  # Sıfıra bölmeyi önlemek için
                    center = (int(moments['m10'] / moments['m00']), int(moments['m01'] / moments['m00']))
                    distance = np.sqrt((center[0] - self.screen_center[0]) ** 2 + (center[1] - self.screen_center[1]) ** 2)

                    # Mesafe daha küçükse en yakın merkezi güncelle
                    if distance < min_distance:
                        min_distance = distance
                        closest_center = center

            if closest_center is not None:
                # En yakın merkez koordinatlarını al ve hedef ofsetini uygula
                cX, cY = closest_center
                cY -= int(self.target_offset)

                if action == "move":
                    # Ekranın merkezine ve algılanan hedefe olan farkı hesapla
                    x_diff = cX - self.screen_center[0]
                    y_diff = cY - self.screen_center[1]

                    # Fareyi hedefe doğru hareket ettir
                    self.mouse.move(self.x_speed * x_diff, self.y_speed * y_diff)

                elif action == "click":
                    # Algılanan hedefin tetikleme aralığında olup olmadığını kontrol et
                    if (abs(cX - self.screen_center[0]) <= self.x_range and
                        abs(cY - self.screen_center[1]) <= self.y_range):
                        # Tıklama tetiklenmeden önce rastgele bir gecikme uygula
                        time.sleep(random.uniform(self.min_delay / 1000.0, self.max_delay / 1000.0))
                        self.mouse.click()

    def open_color_picker(self):
        # Burada bir GUI kütüphanesi kullanarak renk seçici açabilirsiniz
        pass
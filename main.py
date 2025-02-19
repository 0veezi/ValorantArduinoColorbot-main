import pyautogui
import os
from colorbot import Colorbot
from settings import Settings

class Main:
    """
    Main sınıfı, uygulamayı başlatır, gerekli parametreleri ayarlar
    ve Colorbot'u çalıştırır.
    """

    def __init__(self):
        """
        Main sınıfını ekran parametrelerini ayarlayarak ve Colorbot örneğini oluşturarak başlatır.

        Attributes:
            settings (Settings): Konfigürasyon dosyalarını okumak için ayar örneği.
            monitor (tuple): Ekran çözünürlüğü.
            center_x (int): Ekranın merkez X koordinatı.
            center_y (int): Ekranın merkez Y koordinatı.
            x_fov (int): Yakalama alanının genişliği.
            y_fov (int): Yakalama alanının yüksekliği.
            colorbot (Colorbot): Ekran yakalama ve renk algılama için Colorbot örneği.
        """
        self.settings = Settings()

        self.monitor = pyautogui.size()
        self.center_x, self.center_y = self.monitor.width // 2, self.monitor.height // 2
        self.x_fov = self.settings.get_int('Aimbot', 'xFov')
        self.y_fov = self.settings.get_int('Aimbot', 'yFov')

        self.colorbot = Colorbot(
            self.center_x - self.x_fov // 2, 
            self.center_y - self.y_fov // 2, 
            self.x_fov, 
            self.y_fov
        )

    def run(self):
        """
        Uygulama başlığını ve renk ayarlarını yazdırır, ardından Colorbot'u başlatır.
        """
        os.system('cls')
        os.system('title github.com/iamennui/ValorantArduinoColorbot')
        print('Düşman Kontur Rengi: Mor')
        self.colorbot.listen()

if __name__ == '__main__':
    Main().run()
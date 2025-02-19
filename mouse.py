import time
import threading
import serial
import serial.tools.list_ports
from settings import Settings

class Mouse:
    """
    Mouse sınıfı, Arduino tabanlı bir fare kontrol cihazı ile bağlantıyı yönetmek
    ve hareket komutlarını bir seri port aracılığıyla göndermekle sorumludur.

    Attributes:
        settings (Settings): Konfigürasyon ayarlarını almak için Settings sınıfının bir örneği.
        serial_port (serial.Serial): Arduino ile olan seri port bağlantısı.
        remainder_x (float): X eksenindeki hareketin birikmiş kalanı.
        remainder_y (float): Y eksenindeki hareketin birikmiş kalanı.
    """
    
    def __init__(self):
        """
        Mouse sınıfını başlatır, Arduino ile seri port bağlantısını kurar
        ve kalan değerleri başlatır.
        """
        self.settings = Settings()
        self.lock = threading.Lock()
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 0
        self.serial_port.port = self.find_serial_port()
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        try:
            self.serial_port.open()
        except serial.SerialException:
            print("Colorbot zaten açık veya Arduino başka bir uygulama tarafından kullanılıyor. Lütfen bağlantıyı kontrol edin ve tekrar deneyin.\n10 saniye içinde çıkılıyor...")
            time.sleep(10)
            exit()

    def find_serial_port(self):
        """
        Konfigürasyon ayarlarına dayalı olarak Arduino'ya bağlı seri portu bulur ve döndürür.

        Returns:
            str: Bağlı seri portun cihaz adı.

        Raises:
            SystemExit: Belirtilen Arduino COM portu bulunamazsa.
        """
        com_port = self.settings.get('Settings', 'COM-Port')
        port = next((port for port in serial.tools.list_ports.comports() if com_port in port.description), None)
        if port is not None:
            return port.device
        else:
            print(f"Belirtilen Arduino'nuzu ({com_port}) tespit edilemiyor.\nLütfen bağlantısını ve settings.ini dosyasını kontrol edin, ardından tekrar deneyin.\n10 saniye içinde çıkılıyor...")
            time.sleep(10)
            exit()

    def move(self, x, y):
        """
        Arduino'ya bir fare hareket komutu gönderir, kesirli hareketleri biriktirerek yönetir.

        Args:
            x (float): X eksenindeki hareket.
            y (float): Y eksenindeki hareket.
        """
        # Önceki hesaplamadan kalan değeri ekle
        x += self.remainder_x
        y += self.remainder_y

        # x ve y'yi yuvarla ve yeni kalanı hesapla
        move_x = int(x)
        move_y = int(y)
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y

        if move_x != 0 or move_y != 0:
            with self.lock:
                self.serial_port.write(f'M{move_x},{move_y}\n'.encode())

    def click(self):
        """
        Arduino'ya bir fare tıklama komutu gönderir.
        """
        with self.lock: 
            self.serial_port.write('C\n'.encode())
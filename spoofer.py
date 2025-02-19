import os
import re
import time
import random
import requests
import zipfile
import subprocess
import win32com.client

class Spoofer:
    """
    Spoofer sınıfı, Arduino CLI'yi ayarlamak, bağlı fare cihazlarını tespit etmek,
    Arduino Leonardo kart ayarlarını yapılandırmak ve Arduino sketch'ini derleyip yüklemekle ilgilenir.
    """

    SKETCH_FILE = "arduino/arduino.ino"
    BOARDS_TXT_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt")

    def __init__(self):
        """
        Spoofer sınıfını başlatır, Arduino CLI yolunu ayarlar.
        """
        self.arduino_cli_path = os.path.join(os.getcwd(), "arduino/arduino-cli.exe")

    def download_arduino_cli(self):
        """
        Arduino CLI'yi indirmeyi ve çıkarmayı gerçekleştirir, eğer zaten mevcut değilse.
        """
        # 'arduino' dizinini oluştur, eğer yoksa
        os.makedirs("arduino", exist_ok=True)

        # Eğer Arduino CLI zaten mevcutsa indirmeyi atla
        if os.path.exists(self.arduino_cli_path):
            return

        # Arduino CLI'yi indir
        if not os.path.exists(os.path.join(os.getcwd(), "arduino/arduino-cli.zip")):
            print("Arduino CLI indiriliyor...")
            response = requests.get("https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip", stream=True)
            with open("arduino/arduino-cli.zip", "wb") as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)

        # Arduino CLI'yi çıkar
        with zipfile.ZipFile("arduino/arduino-cli.zip", 'r') as zip_ref:
            zip_ref.extractall("./arduino/")

    def update_boards(self, vendor_id, product_id):
        """
        Arduino Leonardo kartı için 'boards.txt' dosyasını güncelleyerek VID ve PID'yi değiştirir.
        
        Args:
            vendor_id (str): Hexadecimal formatında Üretici Kimliği (VID) (örneğin, '0x2341').
            product_id (str): Hexadecimal formatında Ürün Kimliği (PID) (örneğin, '0x8036').
        """
        # 'boards.txt' dosyasını oku
        with open(self.BOARDS_TXT_PATH, 'r') as boards_file:
            board_config_lines = boards_file.readlines()

        # Arduino Leonardo kartı için rastgele bir isim oluştur
        random_name = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))

        # Arduino Leonardo kartı için VID ve PID'yi güncelle
        for index, line in enumerate(board_config_lines):
            if line.startswith("leonardo.name="):
                board_config_lines[index] = f"leonardo.name={random_name}\n"
            elif line.startswith("leonardo.vid."):
                suffix = line.split("leonardo.vid.")[1].split("=")[0]
                board_config_lines[index] = f"leonardo.vid.{suffix}={vendor_id}\n"
            elif line.startswith("leonardo.pid."):
                suffix = line.split("leonardo.pid.")[1].split("=")[0]
                board_config_lines[index] = f"leonardo.pid.{suffix}={product_id}\n"
            elif line.startswith("leonardo.build.vid="):
                board_config_lines[index] = f"leonardo.build.vid={vendor_id}\n"
            elif line.startswith("leonardo.build.pid="):
                board_config_lines[index] = f"leonardo.build.pid={product_id}\n"
            elif line.startswith("leonardo.build.usb_product="):
                board_config_lines[index] = f"leonardo.build.usb_product=\"{random_name}\"\n"

        # Güncellenmiş 'boards.txt' dosyasını yaz
        with open(self.BOARDS_TXT_PATH, 'w') as boards_file:
            boards_file.writelines(board_config_lines)

    def detect_mouse_devices(self):
        """
        WMI kullanarak bağlı tüm fare cihazlarını tespit eder ve cihaz adı, VID ve PID içeren bir liste döndürür.

        Returns:
            list: Her bir tuple'ın cihaz adı, VID ve PID içerdiği bir liste.
        """
        # WMI servisine bağlan
        wmi_service = win32com.client.GetObject("winmgmts:")
        # Tüm işaretleme cihazlarını al
        mouse_devices = wmi_service.InstancesOf("Win32_PointingDevice")
        # Tespit edilen farelerin listesi
        detected_mice = []

        # Her işaretleme cihazını döngüye al
        for device in mouse_devices:
            # Cihaz adını al
            device_name = device.Name
            # PNPDeviceID'den VID ve PID'yi çıkar
            id_match = re.search(r'VID_(\w+)&PID_(\w+)', device.PNPDeviceID)
            # Cihaz adı, VID ve PID'yi listeye ekle
            vid, pid = id_match.groups() if id_match else (None, None)
            detected_mice.append((device_name, vid, pid))

        # Tespit edilen farelerin listesini döndür
        return detected_mice

    def prompt_mouse_selection(self):
        """
        Kullanıcıdan bir fare cihazı seçmesini ister ve Arduino Leonardo kart ayarlarını buna göre yapılandırır.
        """
        # Tüm bağlı fare cihazlarını tespit et
        detected_mice = self.detect_mouse_devices()

        # Eğer fare cihazı tespit edilmezse, 10 saniye sonra çık
        if not detected_mice:
            print("Hiçbir fare cihazı bulunamadı.\n10 saniye içinde çıkılıyor...")
            time.sleep(10)
            exit()

        os.system('cls')

        # Geçerli USB giriş cihazlarını filtrele ve sakla
        valid_mice = {}
        for device_name, vid, pid in detected_mice:
            if "USB Input Device" in device_name and vid and pid:
                device_key = (vid, pid)
                if device_key not in valid_mice:  # Tekrarları önle
                    valid_mice[device_key] = device_name

        # Eğer geçerli fare cihazı bulunamazsa, çık
        if not valid_mice:
            print("Geçerli USB Giriş Cihazı bulunamadı.\n10 saniye içinde çıkılıyor...")
            time.sleep(10)
            exit()

        # Tespit edilen USB giriş cihazlarını göster
        for index, ((vid, pid), device_name) in enumerate(valid_mice.items(), 1):
            print(f"{index} → {device_name}\tVID: {vid}, PID: {pid}")

        # Kullanıcıdan bir fare cihazı seçmesini iste
        selected_mouse_index = int(input("\nFare numaranızı seçin: ")) - 1
        selected_device_key = list(valid_mice.keys())[selected_mouse_index]
        selected_vid, selected_pid = selected_device_key
        # Arduino Leonardo kart ayarlarını güncelle
        self.update_boards("0x" + selected_vid, "0x" + selected_pid)

    def install_avr_core(self):
        """
        AVR çekirdek ve Mouse kütüphanesinin zaten kurulu olup olmadığını kontrol eder. Eğer değilse, Arduino CLI kullanarak kurar.
        """
        # Yüklenmiş çekirdekleri kontrol etmek için 'core list' komutunu çalıştır
        result = subprocess.run([self.arduino_cli_path, "core", "list"], capture_output=True, text=True)

        # Çıktıda 'arduino:avr' ve versiyon '1.8.6' olup olmadığını kontrol et
        if "arduino:avr" not in result.stdout and not "1.8.6" in result.stdout:
            print("AVR çekirdeği 1.8.6 kuruluyor...")
            os.system(f"{self.arduino_cli_path} core install arduino:avr@1.8.6 >NUL 2>&1")

        # Yüklenmiş kütüphaneleri kontrol etmek için 'lib list' komutunu çalıştır
        result = subprocess.run([self.arduino_cli_path, "lib", "list"], capture_output=True, text=True)

        # Çıktıda 'Mouse' olup olmadığını kontrol et
        if "Mouse" not in result.stdout:
            print("Mouse kütüphanesi kuruluyor...")
            os.system(f"{self.arduino_cli_path} lib install Mouse >NUL 2>&1")

    def compile_sketch(self):
        """
        Arduino sketch'ini Arduino CLI kullanarak derler.
        """
        os.system('cls')
        
        # Kullanıcıdan Arduino Leonardo'nun COM portunu girmesini iste
        com_port = input("Arduino Leonardo COM-Port'unuzu girin (örneğin, COM3): ")

        print("Sketch derleniyor...")

        # Sketch dosyasının var olup olmadığını kontrol et
        if not os.path.exists(self.SKETCH_FILE):
            print(f"Hata: Sketch dosyası '{self.SKETCH_FILE}' bulunamadı!")
            return
        
        os.system(f"{self.arduino_cli_path} compile --fqbn arduino:avr:leonardo {self.SKETCH_FILE} >NUL 2>&1")
        self.upload_sketch(com_port)

    def upload_sketch(self, com_port):
        """
        Derlenmiş sketch'i Arduino Leonardo kartına yükler.
        """
        # Sketch dosyasının var olup olmadığını kontrol et
        if not os.path.exists(self.SKETCH_FILE):
            print(f"Hata: Sketch dosyası '{self.SKETCH_FILE}' bulunamadı!")
            return
        
        print("Sketch Arduino'ya yükleniyor...")
        
        # Yükleme komutunu oluştur
        upload_command = f"{self.arduino_cli_path} upload -p {com_port} --fqbn arduino:avr:leonardo {self.SKETCH_FILE}"
        
        # Yükleme komutunu çalıştır ve çıktıyı yakala
        exit_code = os.system(upload_command)
        
        # Yüklemenin başarılı olup olmadığını kontrol et
        if exit_code == 0:
            print("Spoof işlemi başarıyla tamamlandı, artık colorbot'u kullanabilirsiniz!")
        else:
            # Ekstra sorun giderme bilgisi sağla
            print(f"Sketch yüklemesi başarısız oldu. Hata kodu: {exit_code}")
            print("Arduino'nun bağlı olduğundan ve COM portunun doğru olduğundan emin olun.")

    def run(self):
        """
        Arduino Leonardo'yu ayarlama ve yapılandırma sürecini yürütür.
        """
        self.download_arduino_cli()
        self.install_avr_core()
        self.prompt_mouse_selection()
        self.compile_sketch()

if __name__ == "__main__":
    os.system('cls')
    os.system("title github.com/iamennui/ValorantArduinoColorbot")
    Spoofer().run()
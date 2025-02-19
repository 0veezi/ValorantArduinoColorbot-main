import configparser

class Settings:
    """
    Settings sınıfı, 'settings.ini' dosyasından konfigürasyon değerlerini okumak ve yazmak için yöntemler sağlar.

    Attributes:
        config (ConfigParser): Konfigürasyon verilerini yönetmek için kullanılan ConfigParser örneği.
    """

    def __init__(self):
        """
        Settings sınıfını 'settings.ini' dosyasından konfigürasyonu okuyarak başlatır.
        """
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')

    def get(self, section, key):
        """
        Konfigürasyondan bir string değeri alır.

        Args:
            section (str): Konfigürasyon dosyasındaki bölüm.
            key (str): Değerin alınacağı anahtar.

        Returns:
            str: Verilen bölüm ve anahtarla ilişkili değer.
        """
        return self.config.get(section, key)

    def get_boolean(self, section, key):
        """
        Konfigürasyondan bir boolean değeri alır.

        Args:
            section (str): Konfigürasyon dosyasındaki bölüm.
            key (str): Değerin alınacağı anahtar.

        Returns:
            bool: Verilen bölüm ve anahtarla ilişkili boolean değer.
        """
        return self.config.getboolean(section, key)

    def get_float(self, section, key):
        """
        Konfigürasyondan bir float değeri alır.

        Args:
            section (str): Konfigürasyon dosyasındaki bölüm.
            key (str): Değerin alınacağı anahtar.

        Returns:
            float: Verilen bölüm ve anahtarla ilişkili float değer.
        """
        return self.config.getfloat(section, key)
    
    def get_float_list(self, section, key):
        """
        Konfigürasyondan bir float değerler listesi alır. Değerlerin
        bir liste stringi olarak saklanması beklenir (örneğin, "[1.0, 2.0, 3.0]").

        Args:
            section (str): Konfigürasyon dosyasındaki bölüm.
            key (str): Değerin alınacağı anahtar.

        Returns:
            list[float]: Verilen bölüm ve anahtarla ilişkili float değerler listesi.
        """
        string_value = self.config.get(section, key)
        values_as_strings = string_value.strip('[]').split(',')
        return [float(value) for value in values_as_strings]

    def get_int(self, section, key):
        """
        Konfigürasyondan bir integer değeri alır.

        Args:
            section (str): Konfigürasyon dosyasındaki bölüm.
            key (str): Değerin alınacağı anahtar.

        Returns:
            int: Verilen bölüm ve anahtarla ilişkili integer değer.
        """
        return self.config.getint(section, key)

    def save(self):
        """
        Mevcut konfigürasyonu 'settings.ini' dosyasına kaydeder.
        """
        with open('settings.ini', 'w') as f:
            self.config.write(f)

    def set(self, section, key, value):
        """
        Bir konfigürasyon değerini ayarlar ve konfigürasyonu 'settings.ini' dosyasına kaydeder. 
        Eğer bölüm mevcut değilse, oluşturulur.

        Args:
            section (str): Konfigürasyon dosyasındaki bölüm.
            key (str): Ayarlanacak anahtar.
            value (str): Verilen bölüm ve anahtar için ayarlanacak değer.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save()
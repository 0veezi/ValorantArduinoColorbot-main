## SORUMLULUK REDDİ

- **Hile Tespiti**: Bu proje, tespit edilmemek amacıyla tasarlanmamıştır ve asla böyle bir hedefi olmayacaktır.
- **Uyumluluk**: Bu yazılım yalnızca Arduino Leonardo kartları için tasarlanmıştır.
- **Sorumluluk**: Bu yazılım yalnızca eğitim amaçlıdır. Bu aracı kullanmaktan kaynaklanabilecek herhangi bir hesap yasaklaması, ceza veya başka sonuçlardan sorumlu değilim. Kendi riskinizle kullanın ve potansiyel sonuçların farkında olun.

## Kurulum Talimatları

1. **Gereksinimleri Yükleyin**:
   - Tüm gerekli bağımlılıkları yüklemek için aşağıdaki komutu çalıştırın:
     ```bash
     pip install -r requirements.txt
     ```
     
2. **Arduino'yu Spooflayın**:
   - Arduino Leonardo kartınızı farenizin VID ve PID'sine spooflamak için aşağıdaki komutu çalıştırın:
     ```bash
     py spoofer.py
     ```

3. **`settings.ini` Dosyasını Yapılandırın**:
   - `settings.ini` dosyasındaki ayarları tercihinize göre ayarlayın, tuş atamalarını değiştirmek isterseniz değerleri [buradan](https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes) bulabilirsiniz.

4. **Oyun İçi Ayarlar**:
   - Oyun içi hassasiyetinizi **0.5** olarak ayarlayın.
   - Düşman vurgulama rengini **Mor** olarak değiştirin.
     
5. **Colorbot'u Çalıştırın**:
   - Ana scripti çalıştırmak için aşağıdaki komutu çalıştırın:
     ```bash
     py main.py
     ```

## Profiller
- GitHub: [0veezi](https://github.com/0veezi)
- MemoryHackers: [Durmuş Karaca](https://memoryhackers.org/members/durmuk.1871708/)

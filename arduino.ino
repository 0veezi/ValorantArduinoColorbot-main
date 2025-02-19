#include <Mouse.h>

// Komut ve hareket değerlerini tutmak için global değişkenler
String command = "";  // Seri tampondan alınan komut
int deltaX = 0, deltaY = 0;  // X ve Y eksenleri için hareket değerleri

// Tıklama durumu yönetimi
bool isClicking = false;  // Şu anda bir fare tıklamasının olup olmadığını takip eder
unsigned long clickStartTime = 0;  // Tıklamanın başladığı zamanı işaretler
unsigned long clickDuration;  // Tıklamanın ne kadar süreceğini milisaniye cinsinden belirtir

void setup() {
    // 115200 baud hızında seri iletişimi başlat
    Serial.begin(115200);
    Serial.setTimeout(1);  // Seri okumalar için kısa bir zaman aşımı ayarla
    Mouse.begin();  // Fare kontrolünü başlat
    
    // Rastgele tıklama süreleri için rastgele sayı üreteci tohumla
    randomSeed(analogRead(0));  // Daha iyi rastgelelik için bağlı olmayan bir analog pini kullan
}

void loop() {
    // Seri tamponunda bekleyen herhangi bir komut olup olmadığını kontrol et
    if (Serial.available() > 0) {
        // Yeni bir komut gelene kadar gelen komutu oku
        command = Serial.readStringUntil('\n');
        command.trim();  // Herhangi bir baştaki veya sondaki boşluğu temizle

        // Eğer komut 'M' ile başlıyorsa, bu bir fare hareket komutu
        if (command.startsWith("M")) {
            int commaIndex = command.indexOf(',');  // Virgülün konumunu bul
            // Komutun doğru formatta olup olmadığını kontrol et
            if (commaIndex != -1) {
                // X ve Y eksenleri için hareket değerlerini çıkar
                deltaX = command.substring(1, commaIndex).toInt();  // X eksenindeki hareketi al
                deltaY = command.substring(commaIndex + 1).toInt();  // Y eksenindeki hareketi al

                // Fareyi ani sıçramaları önlemek için kademeli olarak hareket ettir
                while (deltaX != 0 || deltaY != 0) {
                    int moveX = constrain(deltaX, -128, 127);  // X hareketini sınırlayarak taşmayı önle
                    int moveY = constrain(deltaY, -128, 127);  // Y hareketini de benzer şekilde sınırlayarak
                    Mouse.move(moveX, moveY);  // Fare hareketini gerçekleştir
                    deltaX -= moveX;  // Kalan X hareketini azalt
                    deltaY -= moveY;  // Kalan Y hareketini azalt
                }
            }
        }
        // Eğer komut 'C' ile başlıyorsa, bu bir fare tıklama komutu
        else if (command.startsWith("C")) {
            // Tıklama süreci başlamadıysa başlat
            if (!isClicking) {
                Mouse.press(MOUSE_LEFT);  // Sol fare butonunu basılı tut
                clickStartTime = millis();  // Tıklamanın başlangıç zamanını kaydet
                clickDuration = random(40, 80);  // 40ms ile 80ms arasında rastgele bir tıklama süresi seç
                isClicking = true;  // Tıklama durumunu aktif olarak işaretle
            }
        }
    }

    // Eğer bir tıklama devam ediyorsa, butonu bırakma zamanını kontrol et
    if (isClicking) {
        // Belirtilen tıklama süresi geçtiyse butonu bırak
        if (millis() - clickStartTime >= clickDuration) {
            Mouse.release(MOUSE_LEFT);  // Sol fare butonunu bırak
            isClicking = false;  // Tıklama durumunu sıfırla
        }
    }
} 
#include <Mouse.h>

// Global variables to hold the command and movement values
String command = "";  // The command received from the serial buffer
int deltaX = 0, deltaY = 0;  // Movement values for the X and Y axes

// Click state management
bool isClicking = false;  // Tracks whether a mouse click is currently happening
unsigned long clickStartTime = 0;  // Marks the time when the click begins
unsigned long clickDuration;  // Specifies how long the click will last in milliseconds

void setup() {
    // Initialize serial communication at a baud rate of 115200
    Serial.begin(115200);
    Serial.setTimeout(1);  // Set a short timeout for serial reads
    Mouse.begin();  // Initialize mouse control
    
    // Seed the random number generator for varying click durations
    randomSeed(analogRead(0));  // Use an unconnected analog pin for better randomness
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
            // Start the click process if we're not already clicking
            if (!isClicking) {
                Mouse.press(MOUSE_LEFT);  // Press the left mouse button down
                clickStartTime = millis();  // Record the current time as the start of the click
                clickDuration = random(40, 80);  // Choose a random click duration between 40ms and 80ms
                isClicking = true;  // Mark that we're in a clicking state
            }
        }
    }

    // If a click is ongoing, check if it's time to release the button
    if (isClicking) {
        // If the specified click duration has passed, release the button
        if (millis() - clickStartTime >= clickDuration) {
            Mouse.release(MOUSE_LEFT);  // Release the left mouse button
            isClicking = false;  // Reset the clicking state
        }
    }
}
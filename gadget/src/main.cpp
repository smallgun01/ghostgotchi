#include <Arduino.h>
#include <M5Unified.h>

static const char* TAG = "ghostgotchi";

void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    M5.Lcd.setTextSize(2);
    M5.Lcd.println("Ghostgotchi");
    Serial.println("[ghostgotchi] booting...");
}

void loop() {
    M5.update();
    delay(10);
}

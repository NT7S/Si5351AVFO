// Host stand-in for the Arduino core, just enough for sh1106.cpp and ui.cpp.
#pragma once
#include <stdint.h>
#include <stddef.h>

#define HIGH 0x1
#define LOW  0x0
#define OUTPUT 0x1
#define INPUT  0x0
#define MSBFIRST 1
#define SPI_MODE0 0

// Distinct ids. The firmware only cares that the OLED pins differ.
#define PIN_PA0 0
#define PIN_PA1 1
#define PIN_PA2 2
#define PIN_PA3 3
#define PIN_PA4 4
#define PIN_PA5 5
#define PIN_PA6 6
#define PIN_PA7 7
#define PIN_PB0 8
#define PIN_PB1 9
#define PIN_PB2 10
#define PIN_PB3 11
#define PIN_PB4 12
#define PIN_PB5 13
#define PIN_PC0 16
#define PIN_PC1 17
#define PIN_PC2 18
#define PIN_PC3 19

#define A0 0

class SPISettings {
 public:
  SPISettings() {}
  SPISettings(uint32_t, uint8_t, uint8_t) {}
};

void pinMode(uint8_t pin, uint8_t mode);
void digitalWrite(uint8_t pin, uint8_t val);
int digitalRead(uint8_t pin);
void delay(unsigned long ms);
void delayMicroseconds(unsigned int us);
unsigned long millis();
char *ultoa(unsigned long value, char *buf, int radix);

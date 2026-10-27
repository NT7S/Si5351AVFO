// SH1106 command/data emulator. 132-column GDDRAM, visible window starts
// at column 2 (the panel's 128 columns). Commands match what sh1106.cpp sends.
#include "oled_port.h"
#include "mock/Arduino.h"
#include "mock/SPI.h"
#include <stdio.h>

uint8_t oled_ram[OLED_RAM_PAGES][OLED_RAM_COLS];
int oled_oob_writes = 0;

static unsigned long g_ms = 0;
static uint8_t pin_level[32];
static uint8_t cur_page = 0;
static uint8_t cur_col = 0;

void sim_set_millis(unsigned long ms) { g_ms = ms; }
unsigned long sim_millis() { return g_ms; }
unsigned long millis() { return g_ms; }

void pinMode(uint8_t, uint8_t) {}
void digitalWrite(uint8_t pin, uint8_t val) {
  if (pin < sizeof(pin_level)) pin_level[pin] = val;
}
int digitalRead(uint8_t pin) {
  return pin < sizeof(pin_level) ? pin_level[pin] : 0;
}
void delay(unsigned long) {}
void delayMicroseconds(unsigned int) {}

char *ultoa(unsigned long value, char *buf, int radix) {
  if (radix < 2 || radix > 10) radix = 10;
  char tmp[16];
  int n = 0;
  if (value == 0) tmp[n++] = '0';
  while (value) {
    tmp[n++] = (char)('0' + (value % (unsigned)radix));
    value /= (unsigned)radix;
  }
  int j = 0;
  while (n) buf[j++] = tmp[--n];
  buf[j] = 0;
  return buf;
}

SPIClass SPI;

void SPIClass::begin() {}
void SPIClass::beginTransaction(SPISettings) {}
void SPIClass::endTransaction() {}

static void command(uint8_t b) {
  if (b >= 0xB0 && b <= 0xB7) {
    cur_page = b & 7;
  } else if ((b & 0xF0) == 0x00) {
    cur_col = (uint8_t)((cur_col & 0xF0) | (b & 0x0F));
  } else if ((b & 0xF0) == 0x10) {
    cur_col = (uint8_t)((cur_col & 0x0F) | ((b & 0x0F) << 4));
  }
}

uint8_t SPIClass::transfer(uint8_t b) {
  bool cs = pin_level[4];   // PIN_OLED_CS = PIN_PA4
  bool dc = pin_level[5];   // PIN_OLED_DC = PIN_PA5
  if (cs) return 0;          // chip not selected
  if (!dc) {
    command(b);
    return 0;
  }
  if (cur_page < OLED_RAM_PAGES && cur_col < OLED_RAM_COLS) {
    oled_ram[cur_page][cur_col] = b;
  } else {
    oled_oob_writes++;
  }
  if (cur_col < 255) cur_col++;
  return 0;
}

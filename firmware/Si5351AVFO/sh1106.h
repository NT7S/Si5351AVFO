// Minimal SH1106 128x64 SPI driver for the Si5351A VFO (no frame buffer).
// Text is written straight to display RAM, one 8-pixel page at a time.
#pragma once
#include <Arduino.h>
#include <SPI.h>

#include "pins.h"
#define OLED_CS  PIN_OLED_CS
#define OLED_DC  PIN_OLED_DC
#define OLED_RES PIN_OLED_RES
#define SH1106_COL_OFFSET 2   // 132-column RAM, 128 visible

namespace sh1106 {
void begin();
void clear();
void setPos(uint8_t page, uint8_t col);
// 5x7 text on one page (6 px per char). Character index `ul` (0xFF = none)
// gets a 1 px underline in the free bottom row of the page; `inv` inverts.
void text5x7(uint8_t page, uint8_t col, const char *s, uint8_t ul = 0xFF, bool inv = false);
// 8x16 digits over two pages (8 px per char); only '0'-'9', '.', '-', ' '.
void big8x16(uint8_t page, uint8_t col, const char *s);
// Write `n` copies of the column byte `b` (used for clearing and bars).
void fill(uint8_t page, uint8_t col, uint8_t n, uint8_t b);
inline void clearPage(uint8_t page) { fill(page, 0, 128, 0); }
}

// pins.h - ATtiny3226 pin map for the Si5351A VFO (REQUIREMENTS.md §2).
// megaTinyCore PIN_Pxn names. All inputs have external 10k pull-ups and RC
// filters on the board, so no internal pull-ups are enabled. Active low.
#pragma once

// Rotary encoder (Alps EC11E18244A5, SW1)
#define PIN_ENC_A    PIN_PC0
#define PIN_ENC_B    PIN_PC1
#define PIN_ENC_SW   PIN_PC2   // encoder push

// Soft buttons, numbered left to right under the display
#define PIN_BTN_S1   PIN_PC3   // SW2, left   (main: BAND-)
#define PIN_BTN_S2   PIN_PB5   // SW3, middle (main: BAND+)
#define PIN_BTN_S3   PIN_PA7   // SW4, right  (main: MENU)

// SH1106 OLED on SPI0 (default pins): MOSI PA1, SCK PA3 (MISO PA2 unused)
#define PIN_OLED_MOSI PIN_PA1
#define PIN_OLED_SCK  PIN_PA3
#define PIN_OLED_CS   PIN_PA4
#define PIN_OLED_DC   PIN_PA5
#define PIN_OLED_RES  PIN_PA6

// Si5351A on TWI0 (default pins): SCL PB0, SDA PB1. I2C address 0x60.
#define PIN_I2C_SCL  PIN_PB0
#define PIN_I2C_SDA  PIN_PB1

// USART0 default pins to the CP2102N: TX PB2, RX PB3. PB4 is the alternate
// reset pin (fuse "UPDI on PA0, RST on PB4"), PA0 is UPDI. Not used by code.

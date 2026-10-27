// SH1106 RAM window shared by the SPI emulator and the simulator.
#pragma once
#include <stdint.h>

#define OLED_RAM_COLS 132
#define OLED_RAM_PAGES 8

extern uint8_t oled_ram[OLED_RAM_PAGES][OLED_RAM_COLS];
extern int oled_oob_writes;   // data written outside the 132-column RAM

void sim_set_millis(unsigned long ms);
unsigned long sim_millis();

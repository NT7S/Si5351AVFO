// Host SPI stand-in. Transfer goes into the SH1106 RAM emulator.
#pragma once
#include <stdint.h>
#include "Arduino.h"

class SPIClass {
 public:
  void begin();
  void beginTransaction(SPISettings);
  void endTransaction();
  uint8_t transfer(uint8_t b);
};

extern SPIClass SPI;

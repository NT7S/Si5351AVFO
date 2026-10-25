// eeprom_layout.h - byte-exact EEPROM slot image (REQUIREMENTS §7). Two
// 128 B slots (A at 0, B at 128) fill the 256 B EEPROM.
// Pure C++: pack/unpack a VfoState to/from a byte array, plus CRC8.
// settings.cpp does the actual EEPROM reads and writes.
#pragma once
#include <stdint.h>
#include "vfo_state.h"

#define EE_MAGIC0   0x56   // 'V'
#define EE_MAGIC1   0x46   // 'F'
#define EE_VERSION  2   // 2: A/B slots with sequence byte

// Byte offsets. Multi-byte values are little-endian.
enum EeOffset : uint8_t {
  EE_OFF_MAGIC     = 0,    // 2
  EE_OFF_VERSION   = 2,    // 1
  EE_OFF_FREQ      = 3,    // 4  current F
  EE_OFF_BAND      = 7,    // 1
  EE_OFF_STEP      = 8,    // 1
  EE_OFF_MODE      = 9,    // 1
  EE_OFF_CLK_EN    = 10,   // 1  bitfield
  EE_OFF_INJ       = 11,   // 1
  EE_OFF_IQ        = 12,   // 1
  EE_OFF_LIMIT     = 13,   // 1
  EE_OFF_FOVR      = 14,   // 1  bitfield
  EE_OFF_IF        = 15,   // 4
  EE_OFF_DRIVE     = 19,   // 1  2 bits per clock, CLK0 in bits 1:0
  EE_OFF_CAL       = 20,   // 4  int32 ppb
  EE_OFF_BAND_LAST = 24,   // 13 x 4
  EE_OFF_MEM       = 76,   // 10 x 5 (uint32 F + info byte)
  EE_OFF_SEQ       = 126,  // 1  slot sequence counter (newer wins, mod 256)
  EE_OFF_CRC       = 127,  // 1  CRC8 over bytes 0..126
  EE_SIZE          = 128,  // one slot
  EE_SLOTS         = 2
};

uint8_t crc8(const uint8_t *p, uint8_t n);   // poly 0x07, init 0x00

// Pack s into img[EE_SIZE] including magic, version and CRC.
void ee_pack(const VfoState &s, uint8_t *img, uint8_t seq = 0);
// Unpack img into s. Returns false (s untouched) if magic, version or CRC is
// wrong. Out-of-range fields are replaced with defaults.
bool ee_unpack(const uint8_t *img, VfoState &s);
// True if img has the right magic, version and CRC.
bool ee_valid(const uint8_t *img);
// True if sequence a is newer than b (serial-number arithmetic mod 256).
inline bool ee_newer(uint8_t a, uint8_t b) { return (int8_t)(a - b) > 0; }

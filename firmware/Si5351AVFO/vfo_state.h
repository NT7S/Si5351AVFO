// vfo_state.h - everything the VFO remembers, in one plain struct.
// Pure C++ (no Arduino headers) so it can be compiled and tested on a PC.
// RAM keeps fields unpacked; eeprom_layout.cpp packs them per REQUIREMENTS §7.
#pragma once
#include <stdint.h>

#define NUM_CLOCKS   3
#define NUM_BANDS    13
#define NUM_MEMORIES 10
#define CAL_MAX_PPB  999999L   // calibration range, +/- ppb
#define MEM_EMPTY    0xFF     // memory band/mode byte when the channel is unused

enum OutputMode : uint8_t { MODE_DIRECT = 0, MODE_SUPERHET = 1, MODE_QUAD = 2, MODE_COUNT };
enum Injection  : uint8_t { INJ_HIGH = 0, INJ_LOW = 1 };       // LO = F + IF / F - IF
enum LimitMode  : uint8_t { LIMIT_WIDE = 0, LIMIT_HAM = 1 };   // wide open / amateur only
enum Drive      : uint8_t { DRIVE_2MA = 0, DRIVE_4MA, DRIVE_6MA, DRIVE_8MA };

struct Memory {
  uint32_t freq;   // Hz
  uint8_t  info;   // high nibble: mode, low nibble: band index; MEM_EMPTY if unused
};

struct VfoState {
  uint32_t freq;               // displayed (tuned) frequency, Hz
  uint8_t  band;               // index into band table (last band selected)
  uint8_t  step_idx;           // index into tuning step table
  uint8_t  mode;               // OutputMode
  uint8_t  clk_en;             // bit n = CLKn enabled by the user
  uint8_t  injection;          // Injection (superhet)
  uint8_t  iq_order;           // 0: CLK0 = I (leads), 1: CLK1 = I
  uint8_t  limit;              // LimitMode
  uint8_t  filter_override;    // bit n = ignore the LPF warning on CLKn
  uint32_t if_freq;            // superhet IF / BFO, Hz
  uint8_t  drive[NUM_CLOCKS];  // Drive per clock
  int32_t  cal_ppb;            // Si5351 correction, parts per billion
  uint32_t band_last[NUM_BANDS];
  Memory   mem[NUM_MEMORIES];
};

// Fill `s` with factory defaults (first-use band frequencies, 8 mA, wide open).
void state_defaults(VfoState &s);

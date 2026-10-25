#include "bands.h"

// Name, low edge, high edge, first-use frequency (Hz). Sources: ITU RR Art. 5
// plus the national tables noted in REQUIREMENTS §6.4.
const Band BANDS[NUM_BANDS] = {
  {"160M",   1800000UL,   2000000UL,   1840000UL},
  {"80M",    3500000UL,   4000000UL,   3573000UL},
  {"60M",    5250000UL,   5450000UL,   5357000UL},  // outer envelope, no channels
  {"40M",    7000000UL,   7300000UL,   7074000UL},
  {"30M",   10100000UL,  10150000UL,  10136000UL},
  {"20M",   14000000UL,  14350000UL,  14074000UL},
  {"17M",   18068000UL,  18168000UL,  18100000UL},
  {"15M",   21000000UL,  21450000UL,  21074000UL},
  {"12M",   24890000UL,  24990000UL,  24915000UL},
  {"10M",   28000000UL,  29700000UL,  28074000UL},
  {"6M",    50000000UL,  54000000UL,  50313000UL},
  {"4M",    70000000UL,  70500000UL,  70154000UL},
  {"2M",   144000000UL, 148000000UL, 144174000UL},
};

uint8_t band_find(uint32_t f) {
  for (uint8_t i = 0; i < NUM_BANDS; i++)
    if (f >= BANDS[i].lo && f <= BANDS[i].hi) return i;
  return 0xFF;
}

uint8_t band_step(uint8_t band, int8_t dir) {
  if (band >= NUM_BANDS) band = 0;
  if (dir > 0) return (band + 1 == NUM_BANDS) ? 0 : band + 1;
  return band == 0 ? NUM_BANDS - 1 : band - 1;
}

uint32_t freq_clamp(uint32_t f, uint8_t limit, uint8_t band) {
  uint32_t lo = FREQ_MIN_HZ, hi = FREQ_MAX_HZ;
  if (limit == LIMIT_HAM && band < NUM_BANDS) { lo = BANDS[band].lo; hi = BANDS[band].hi; }
  return f < lo ? lo : (f > hi ? hi : f);
}

void state_defaults(VfoState &s) {
  s.band = 3;                      // 40 m
  s.freq = BANDS[3].start;
  s.step_idx = 2;                  // 1 kHz
  s.mode = MODE_DIRECT;
  s.clk_en = 0x01;                 // CLK0 on
  s.injection = INJ_HIGH;
  s.iq_order = 0;
  s.limit = LIMIT_WIDE;
  s.filter_override = 0;
  s.if_freq = 9000000UL;           // 9 MHz IF
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) s.drive[i] = DRIVE_8MA;
  s.cal_ppb = 0;
  for (uint8_t i = 0; i < NUM_BANDS; i++) s.band_last[i] = BANDS[i].start;
  for (uint8_t i = 0; i < NUM_MEMORIES; i++) { s.mem[i].freq = 0; s.mem[i].info = MEM_EMPTY; }
}

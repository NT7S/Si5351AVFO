#include "tuning.h"

const uint32_t STEPS_HZ[NUM_STEPS] = {100000UL, 10000UL, 1000UL, 500UL, 100UL, 10UL};

uint8_t step_next(uint8_t idx) { return (idx + 1 >= NUM_STEPS) ? 0 : idx + 1; }

void freq_format(uint32_t f, char *buf) {
  // Fill from the right: 3 Hz digits, '.', 3 kHz digits, '.', 3 MHz digits.
  buf[FREQ_STR_LEN] = 0;
  int8_t i = FREQ_STR_LEN - 1;
  for (uint8_t d = 0; d < 9; d++) {
    if (d == 3 || d == 6) buf[i--] = '.';
    // MHz digits beyond the first are blanked when zero (leading spaces).
    buf[i--] = (d >= 7 && f == 0) ? ' ' : (char)('0' + f % 10);
    f /= 10;
  }
}

uint8_t step_underline_pos(uint8_t step_idx) {
  // String layout: 0-2 MHz, 3 '.', 4-6 kHz, 7 '.', 8-10 Hz.
  static const uint8_t pos[NUM_STEPS] = {4, 5, 6, 7, 8, 9};
  return pos[step_idx < NUM_STEPS ? step_idx : 2];
}

uint32_t freq_tune(uint32_t f, int8_t detents, uint32_t step) {
  if (detents >= 0) return f + (uint32_t)detents * step;
  uint32_t d = (uint32_t)(-detents) * step;
  return d > f ? 0 : f - d;
}

int8_t enc_decode(uint8_t &state, uint8_t ab) {
  // Index = old AB << 2 | new AB. +1 = A leads B (clockwise on the EC11).
  static const int8_t table[16] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};
  int8_t d = table[((state & 3) << 2) | (ab & 3)];
  state = ab & 3;
  return d;
}

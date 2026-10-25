// tuning.h - tuning steps, frequency formatting, step underline position and
// the encoder quadrature decoder. Pure C++ (host-testable).
#pragma once
#include <stdint.h>

#define NUM_STEPS 6
extern const uint32_t STEPS_HZ[NUM_STEPS];   // 100k, 10k, 1k, 500, 100, 10 Hz

// Encoder push on the main screen: 100 kHz -> ... -> 10 Hz -> 100 kHz.
uint8_t step_next(uint8_t idx);

// Format f as "MMM.KKK.HHH" (11 chars + NUL, MHz right-aligned with spaces),
// e.g. 7074000 -> "  7.074.000". buf must hold FREQ_STR_LEN + 1 bytes.
#define FREQ_STR_LEN 11
void freq_format(uint32_t f, char *buf);

// Character index in the freq_format string to underline for a step.
// 100k/10k/1k/100/10 Hz -> that digit; 500 Hz -> the '.' between kHz and Hz.
uint8_t step_underline_pos(uint8_t step_idx);

// Tune f by `detents` steps, without wrapping below 0 (caller clamps range).
uint32_t freq_tune(uint32_t f, int8_t detents, uint32_t step);

// Quadrature decoder. Feed the 2-bit AB pin state; returns -1, 0 or +1
// quarter-steps. `state` holds the previous AB value. Invalid jumps (bounce)
// return 0.
int8_t enc_decode(uint8_t &state, uint8_t ab);

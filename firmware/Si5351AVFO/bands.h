// bands.h - amateur band table, 160 m to 2 m (REQUIREMENTS §6.4). Pure C++.
// Edges are the widest amateur allocation in any ITU region or significant
// national table, so "amateur only" never blocks a legal frequency anywhere.
#pragma once
#include <stdint.h>
#include "vfo_state.h"

struct Band {
  char     name[5];   // "160M"
  uint32_t lo, hi;    // edges, Hz
  uint32_t start;     // first-use frequency, Hz (FT8 calling frequency area)
};

// Wide-open tuning range (all clocks); CLK2's LPF is good to 165 MHz.
#define FREQ_MIN_HZ   8000UL
#define FREQ_MAX_HZ   160000000UL

extern const Band BANDS[NUM_BANDS];

// Index of the band containing f, or 0xFF if f is outside every band.
uint8_t band_find(uint32_t f);
// Next/previous band index with wrap (2 m -> 160 m and back). dir = +1 / -1.
uint8_t band_step(uint8_t band, int8_t dir);
// Apply the tuning limit: amateur-only clamps to `band`'s edges, wide open
// clamps to FREQ_MIN_HZ..FREQ_MAX_HZ.
uint32_t freq_clamp(uint32_t f, uint8_t limit, uint8_t band);

#include "modes.h"
#include "bands.h"

const char *const MODE_NAMES[MODE_COUNT] = {"DIR", "SH", "IQ"};

bool iq_plan(uint32_t f, uint32_t &pll, uint8_t &div) {
  if (!iq_in_range(f)) return false;
  // Highest even divider that keeps the PLL at or below 900 MHz.
  uint32_t d = PLL_MAX_HZ / f;
  if (d > IQ_MAX_DIV) d = IQ_MAX_DIV;
  d &= ~1UL;
  if (d < IQ_MIN_DIV) return false;
  uint32_t p = f * d;          // <= 900 MHz, fits in 32 bits
  if (p < PLL_MIN_HZ) return false;
  pll = p;
  div = (uint8_t)d;
  return true;
}

void plan_outputs(const VfoState &s, ClockPlan &p) {
  const uint32_t F = s.freq;
  p.flags = 0;
  p.filter_warn = 0;
  p.iq_pll = 0;
  p.iq_div = 0;
  p.on = s.clk_en & 0x07;

  switch (s.mode) {
    case MODE_SUPERHET: {
      // CLK0 = LO, CLK1 = IF/BFO, CLK2 = tuned frequency.
      uint32_t lo;
      if (s.injection == INJ_HIGH) lo = F + s.if_freq;
      else lo = (F > s.if_freq) ? F - s.if_freq : s.if_freq - F;  // low side (or mirrored)
      if (lo < FREQ_MIN_HZ || lo > FREQ_MAX_HZ) { p.flags |= PLAN_LO_RANGE; p.on &= ~0x01; }
      p.f[0] = lo;
      p.f[1] = s.if_freq;
      p.f[2] = F;
      break;
    }
    case MODE_QUAD:
      // CLK0/CLK1 = I/Q pair at F (90 degrees), CLK2 = tuned frequency.
      p.f[0] = p.f[1] = p.f[2] = F;
      if (!iq_plan(F, p.iq_pll, p.iq_div)) {
        p.flags |= (F > IQ_MAX_HZ) ? PLAN_IQ_HIGH : PLAN_IQ_LOW;
        p.on &= ~0x03;
      }
      break;
    default:  // MODE_DIRECT: every enabled clock shows the displayed frequency
      p.f[0] = p.f[1] = p.f[2] = F;
      break;
  }

  for (uint8_t i = 0; i < NUM_CLOCKS; i++) {
    uint32_t lim = (i == 2) ? LPF_CLK2_HZ : LPF_CLK01_HZ;
    if (p.f[i] > lim) {
      p.filter_warn |= 1 << i;
      if (!(s.filter_override & (1 << i)) && (p.on & (1 << i))) {
        p.on &= ~(1 << i);
        p.flags |= PLAN_FILTER;
      }
    }
  }
}

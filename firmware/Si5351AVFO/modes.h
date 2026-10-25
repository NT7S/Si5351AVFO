// modes.h - turn the VFO state into per-clock frequencies (REQUIREMENTS §6.3).
// Pure C++ (host-testable); vfo.cpp sends the plan to the Si5351.
#pragma once
#include <stdint.h>
#include "vfo_state.h"

// Low-pass filter warning thresholds (REQUIREMENTS §1): CLK0/1 60 MHz Cauer,
// CLK2 flat to ~165 MHz.
#define LPF_CLK01_HZ  60000000UL
#define LPF_CLK2_HZ  165000000UL

// Quadrature floor: integer MS divider <= 126 (phase register is 7 bits) and
// PLL >= 600 MHz, so F >= 600 MHz / 127 ~= 4.72 MHz.
#define IQ_MIN_HZ      4724410UL
#define IQ_MAX_DIV     126
#define PLL_MIN_HZ     600000000UL
#define PLL_MAX_HZ     900000000UL

// Status flags for the UI and STATUS command.
enum PlanFlags : uint8_t {
  PLAN_IQ_LOW    = 0x01,  // quadrature requested below IQ_MIN_HZ: CLK0/1 muted
  PLAN_LO_RANGE  = 0x02,  // superhet LO out of range (e.g. F - IF < 8 kHz): CLK0 muted
  PLAN_FILTER    = 0x04,  // at least one clock muted by an LPF warning
};

struct ClockPlan {
  uint32_t f[NUM_CLOCKS];   // output frequency per clock, Hz
  uint8_t  on;              // bit n = CLKn actually driven
  uint8_t  filter_warn;     // bit n = CLKn above its LPF (whether or not overridden)
  uint8_t  flags;           // PlanFlags
  // Quadrature only: shared PLLA frequency and integer divider (= phase value).
  uint32_t iq_pll;
  uint8_t  iq_div;
};

// Integer PLL plan for an I/Q pair at f. Returns false if impossible.
bool iq_plan(uint32_t f, uint32_t &pll, uint8_t &div);

// Build the full output plan from the state. A clock above its LPF is muted
// unless its filter_override bit is set (the bypass jumper may be fitted).
void plan_outputs(const VfoState &s, ClockPlan &p);

// modes.h - turn the VFO state into per-clock frequencies (REQUIREMENTS §6.3).
// Pure C++ (host-testable); vfo.cpp sends the plan to the Si5351.
#pragma once
#include <stdint.h>
#include "vfo_state.h"

// Low-pass filter warning thresholds (REQUIREMENTS §1): CLK0/1 60 MHz Cauer,
// CLK2 flat to ~165 MHz. Tuning stops at 160 MHz, so the CLK2 check is a guard
// that tuning cannot reach (REQUIREMENTS §6.4).
#define LPF_CLK01_HZ  60000000UL
#define LPF_CLK2_HZ  165000000UL

// Quadrature floor: even integer MS divider <= 126 (phase register is 7 bits)
// and PLL >= 600 MHz, so F >= ceil(600 MHz / 126) = 4 761 905 Hz (~4.76 MHz).
#define IQ_MIN_HZ      4761905UL
#define IQ_MAX_DIV     126
// Quadrature ceiling: set_phase is unreliable at MS ratio <= 8 (Si5351Arduino
// 2.4.1, Test Lab probe #6), so keep the divider >= 10: F <= 900/10 = 90 MHz.
#define IQ_MIN_DIV     10
#define IQ_MAX_HZ      90000000UL
#define PLL_MIN_HZ     600000000UL
#define PLL_MAX_HZ     900000000UL

// Status flags for the UI and STATUS command.
enum PlanFlags : uint8_t {
  PLAN_IQ_LOW    = 0x01,  // quadrature requested below IQ_MIN_HZ: CLK0/1 muted
  PLAN_LO_RANGE  = 0x02,  // superhet LO out of range (e.g. F - IF < 8 kHz): CLK0 muted
  PLAN_FILTER    = 0x04,  // at least one clock muted by an LPF warning
  PLAN_IQ_HIGH   = 0x08,  // quadrature requested above IQ_MAX_HZ: CLK0/1 muted
  PLAN_FAIL      = 0x10,  // the Si5351 library refused a clock: it is off
};

// True if F is inside the quadrature range (IQ_MIN_HZ..IQ_MAX_HZ).
inline bool iq_in_range(uint32_t f) { return f >= IQ_MIN_HZ && f <= IQ_MAX_HZ; }

struct ClockPlan {
  uint32_t f[NUM_CLOCKS];   // output frequency per clock, Hz
  uint8_t  on;              // bit n = CLKn actually driven
  uint8_t  filter_warn;     // bit n = CLKn above its LPF (whether or not overridden)
  uint8_t  flags;           // PlanFlags
  // Quadrature only: shared PLLA frequency and integer divider (= phase value).
  uint32_t iq_pll;
  uint8_t  iq_div;
};

// Short mode names "DIR", "SH", "IQ" (screen and serial).
extern const char *const MODE_NAMES[MODE_COUNT];

// Integer PLL plan for an I/Q pair at f. Returns false if impossible.
bool iq_plan(uint32_t f, uint32_t &pll, uint8_t &div);

// Build the full output plan from the state. A clock above its LPF is muted
// unless its filter_override bit is set (the bypass jumper may be fitted).
void plan_outputs(const VfoState &s, ClockPlan &p);

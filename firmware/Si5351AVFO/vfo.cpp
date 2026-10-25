#include <Arduino.h>
#include <si5351.h>
#include "vfo.h"
#include "bands.h"
#include "tuning.h"
#include "settings.h"
#include "config.h"
#include <string.h>

VfoState g_vfo;
ClockPlan g_plan;
bool g_si5351_ok;
uint8_t g_changed = 1;

static Si5351 si5351;
static uint8_t hw_mode = 0xFF;           // mode the Si5351 is currently set up for
static uint32_t hw_f[NUM_CLOCKS];        // last frequency written per clock
static uint8_t hw_drive[NUM_CLOCKS] = {0xFF, 0xFF, 0xFF};
static uint8_t hw_on = 0xFF;
static bool cal_active;

static inline si5351_clock CLK(uint8_t i) { return (si5351_clock)i; }

void vfo_changed() {
  g_changed = 1;
  settings_touch();
}

bool vfo_begin() {
  g_si5351_ok = si5351.init(SI5351_CRYSTAL_LOAD_0PF, REF_FREQ_HZ, g_vfo.cal_ppb) &&
                !si5351.get_i2c_error();
  if (g_si5351_ok) {
    hw_mode = 0xFF;   // force a full reprogram (init/reset cleared the chip)
    hw_on = 0xFF;
    for (uint8_t i = 0; i < NUM_CLOCKS; i++) hw_drive[i] = 0xFF;
    vfo_apply();
  }
  return g_si5351_ok;
}

// PLL routing (REQUIREMENTS §6.3): quadrature puts CLK0+CLK1 on PLLA as an
// integer pair and CLK2 on PLLB; otherwise CLK0 on PLLA, CLK1/CLK2 on PLLB.
static void setup_routing(uint8_t mode) {
  si5351.set_ms_source(SI5351_CLK0, SI5351_PLLA);
  si5351.set_ms_source(SI5351_CLK1, mode == MODE_QUAD ? SI5351_PLLA : SI5351_PLLB);
  si5351.set_ms_source(SI5351_CLK2, SI5351_PLLB);
  if (mode != MODE_QUAD) {
    si5351.set_phase(SI5351_CLK0, 0);
    si5351.set_phase(SI5351_CLK1, 0);
  }
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) hw_f[i] = 0;
}

void vfo_apply() {
  plan_outputs(g_vfo, g_plan);
  if (cal_active) {                    // calibration: only CLK2 at 10 MHz
    g_plan.f[2] = CAL_FREQ_HZ;
    g_plan.on = 0x04;
  }
  if (!g_si5351_ok) return;

  uint8_t mode = cal_active ? MODE_DIRECT : g_vfo.mode;
  if (mode != hw_mode) { setup_routing(mode); hw_mode = mode; }

  for (uint8_t i = 0; i < NUM_CLOCKS; i++) {
    if (g_vfo.drive[i] != hw_drive[i]) {
      si5351.drive_strength(CLK(i), (si5351_drive)g_vfo.drive[i]);
      hw_drive[i] = g_vfo.drive[i];
    }
  }

  if (mode == MODE_QUAD && (g_plan.on & 0x03) && g_plan.f[0] != hw_f[0]) {
    // Integer I/Q pair: same PLL, same divider, phase register = divider on
    // the clock that lags. A PLL reset re-aligns the phases.
    uint64_t pll = (uint64_t)g_plan.iq_pll * 100ULL;
    uint64_t f = (uint64_t)g_plan.f[0] * 100ULL;
    uint8_t e = si5351.set_freq_manual(f, pll, SI5351_CLK0);
    e |= si5351.set_freq_manual(f, pll, SI5351_CLK1);
    if (e) { g_plan.on &= ~0x03; g_plan.flags |= PLAN_FAIL; }
    si5351.set_phase(g_vfo.iq_order ? SI5351_CLK1 : SI5351_CLK0, 0);
    si5351.set_phase(g_vfo.iq_order ? SI5351_CLK0 : SI5351_CLK1, g_plan.iq_div);
    si5351.pll_reset(SI5351_PLLA);
    hw_f[0] = hw_f[1] = e ? 0 : g_plan.f[0];
    // set_freq_manual() enables both outputs; force the enable pass below so
    // a clock that is off in the plan is switched off again.
    hw_on = 0xFF;
  }
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) {
    if (mode == MODE_QUAD && i < 2) continue;          // handled above
    if (!(g_plan.on & (1 << i)) || g_plan.f[i] == hw_f[i]) continue;
    if (si5351.set_freq((uint64_t)g_plan.f[i] * 100ULL, CLK(i))) {
      g_plan.on &= ~(1 << i);          // refused (e.g. two >100 MHz on one PLL)
      g_plan.flags |= PLAN_FAIL;
      hw_f[i] = 0;
    } else hw_f[i] = g_plan.f[i];
    hw_on = 0xFF;                      // set_freq may enable the output
  }
  if (g_plan.on != hw_on) {
    for (uint8_t i = 0; i < NUM_CLOCKS; i++) si5351.output_enable(CLK(i), (g_plan.on >> i) & 1);
    hw_on = g_plan.on;
  }
}

void vfo_update() {
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) hw_f[i] = 0;
  vfo_apply();
  vfo_changed();
}

// The only place the band index changes (§6.1: any band change, by any path).
// Clock enables follow the band (§6.3): Direct/Quadrature on a band above the
// CLK0/1 filters uses CLK2 (CLK0/1 dropped unless overridden); coming back
// from such a band with only CLK2 on restores the CLK0 default.
static bool band_vhf(uint8_t b) { return b < NUM_BANDS && BANDS[b].lo > LPF_CLK01_HZ; }

// Clock-enable rule (§6.1), run on every band change and every mode change.
static void apply_enable_rule(bool was_vhf, bool vhf) {
  if (g_vfo.mode == MODE_SUPERHET) return;
  if (vhf) g_vfo.clk_en = (g_vfo.clk_en & g_vfo.filter_override & 0x03) | 0x04;
  else if (was_vhf && g_vfo.clk_en == 0x04) g_vfo.clk_en = 0x01;
}

static void set_band_index(uint8_t band) {
  if (band >= NUM_BANDS || band == g_vfo.band) return;
  apply_enable_rule(band_vhf(g_vfo.band), band_vhf(band));
  g_vfo.band = band;
}

static void set_mode_index(uint8_t mode) {
  if (mode >= MODE_COUNT || mode == g_vfo.mode) return;
  g_vfo.mode = mode;
  bool v = band_vhf(g_vfo.band);
  apply_enable_rule(v, v);
}

void vfo_set_freq(uint32_t f) {
  // Amateur only: a frequency inside another band switches to that band;
  // anything outside every band clamps to the current band's edges (§6.4).
  uint8_t b = band_find(f);
  if (g_vfo.limit == LIMIT_HAM && b != 0xFF) set_band_index(b);
  g_vfo.freq = freq_clamp(f, g_vfo.limit, g_vfo.band);
  // Keep the band index and its last-used frequency in step (§6.6). Tuning
  // off-band leaves band_last at the last in-band frequency.
  b = band_find(g_vfo.freq);
  if (b != 0xFF) { set_band_index(b); g_vfo.band_last[b] = g_vfo.freq; }
  vfo_apply();
  vfo_changed();
}

void vfo_tune(int8_t detents) {
  vfo_set_freq(freq_tune(g_vfo.freq, detents, STEPS_HZ[g_vfo.step_idx]));
}

void vfo_set_band(uint8_t band) {
  if (band >= NUM_BANDS) return;
  // band_last is kept current by vfo_set_freq, so just jump to the new band.
  set_band_index(band);
  vfo_set_freq(g_vfo.band_last[band]);
}

void vfo_set_limit(uint8_t limit) {
  g_vfo.limit = limit;
  uint32_t f = g_vfo.freq;
  if (limit == LIMIT_HAM && band_find(f) == 0xFF) {
    // Switching to amateur-only while off-band: go to the nearest band edge.
    // Table is in ascending frequency and '<' keeps the first match, so a tie
    // goes to the lower-frequency band (§6.4).
    uint32_t best = 0xFFFFFFFFUL;
    uint8_t nb = g_vfo.band;
    for (uint8_t i = 0; i < NUM_BANDS; i++) {
      uint32_t e = f < BANDS[i].lo ? BANDS[i].lo : BANDS[i].hi;
      uint32_t d = e > f ? e - f : f - e;
      if (d < best) { best = d; nb = i; }
    }
    set_band_index(nb);
  }
  vfo_set_freq(f);
}

void vfo_band_step(int8_t dir) { vfo_set_band(band_step(g_vfo.band, dir)); }

void vfo_set_mode(uint8_t mode) {
  if (mode >= MODE_COUNT) return;
  set_mode_index(mode);
  vfo_apply();
  vfo_changed();
}

void vfo_set_clock(uint8_t clk, bool on) {
  if (clk >= NUM_CLOCKS) return;
  if (on) g_vfo.clk_en |= 1 << clk; else g_vfo.clk_en &= ~(1 << clk);
  vfo_apply();
  vfo_changed();
}

void vfo_set_drive(uint8_t clk, uint8_t drive) {
  if (clk >= NUM_CLOCKS || drive > DRIVE_8MA) return;
  g_vfo.drive[clk] = drive;
  vfo_apply();
  vfo_changed();
}

void vfo_set_cal(int32_t ppb) {
  g_vfo.cal_ppb = ppb;
  if (g_si5351_ok) {
    si5351.set_correction(ppb, SI5351_PLL_INPUT_XO);
    for (uint8_t i = 0; i < NUM_CLOCKS; i++) hw_f[i] = 0;   // re-send every frequency
    vfo_apply();
  }
  vfo_changed();
}

// Calibration preview: hardware only, g_vfo and EEPROM untouched (§8).
void vfo_preview_cal(int32_t ppb) {
  if (!g_si5351_ok) return;
  si5351.set_correction(ppb, SI5351_PLL_INPUT_XO);
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) hw_f[i] = 0;
  vfo_apply();
}

void vfo_cal_mode(bool on) {
  cal_active = on;
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) hw_f[i] = 0;
  vfo_apply();
  g_changed = 1;
}

bool vfo_mem_store(uint8_t n) {
  if (n >= NUM_MEMORIES) return false;
  g_vfo.mem[n].freq = g_vfo.freq;
  g_vfo.mem[n].info = (uint8_t)((g_vfo.mode << 4) | (g_vfo.band & 0x0F));
  settings_save_now();                 // memory stores are written on confirm
  g_changed = 1;
  return true;
}

bool vfo_mem_recall(uint8_t n) {
  if (n >= NUM_MEMORIES || g_vfo.mem[n].info == MEM_EMPTY) return false;
  uint8_t mode = g_vfo.mem[n].info >> 4, band = g_vfo.mem[n].info & 0x0F;
  // The recalled mode governs the enable rule: mode first, then band (§6.1).
  set_mode_index(mode);
  set_band_index(band);
  vfo_set_freq(g_vfo.mem[n].freq);
  return true;
}

bool vfo_mem_clear(uint8_t n) {
  if (n >= NUM_MEMORIES) return false;
  g_vfo.mem[n].freq = 0;
  g_vfo.mem[n].info = MEM_EMPTY;
  settings_save_now();
  g_changed = 1;
  return true;
}

// Factory reset: everything, including calibration and memories.
void vfo_defaults() {
  state_defaults(g_vfo);
  vfo_set_cal(0);          // also re-applies every output
  settings_save_now();
}

// Reset settings: defaults, but keep calibration and memories (§6.2, §9).
void vfo_reset_settings() {
  int32_t cal = g_vfo.cal_ppb;
  Memory mem[NUM_MEMORIES];
  memcpy(mem, g_vfo.mem, sizeof(mem));
  state_defaults(g_vfo);
  memcpy(g_vfo.mem, mem, sizeof(mem));
  vfo_set_cal(cal);
  settings_save_now();
}

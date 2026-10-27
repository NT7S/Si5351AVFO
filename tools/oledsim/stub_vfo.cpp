// Hardware-free VFO. State changes match the firmware; the Si5351 is not
// programmed. plan_outputs() still fills g_plan so the status line is real.
#include "vfo.h"
#include "bands.h"
#include "settings.h"
#include "tuning.h"
#include <string.h>

VfoState g_vfo;
ClockPlan g_plan;
bool g_si5351_ok = true;
uint8_t g_changed = 1;

static void replan() {
  plan_outputs(g_vfo, g_plan);
  g_changed = 1;
}

void vfo_changed() { g_changed = 1; }
void vfo_update() { replan(); }
void vfo_apply() { replan(); }
bool vfo_begin() { replan(); return g_si5351_ok; }

void vfo_set_freq(uint32_t f) {
  uint8_t b = band_find(f);
  if (g_vfo.limit == LIMIT_HAM && b != 0xFF) g_vfo.band = b;
  g_vfo.freq = freq_clamp(f, g_vfo.limit, g_vfo.band);
  b = band_find(g_vfo.freq);
  if (b != 0xFF) {
    g_vfo.band = b;
    g_vfo.band_last[b] = g_vfo.freq;
  }
  replan();
}

void vfo_tune(int8_t detents) {
  vfo_set_freq(freq_tune(g_vfo.freq, detents, STEPS_HZ[g_vfo.step_idx]));
}

void vfo_set_band(uint8_t band) {
  if (band >= NUM_BANDS) return;
  g_vfo.band = band;
  vfo_set_freq(g_vfo.band_last[band]);
}

void vfo_band_step(int8_t dir) { vfo_set_band(band_step(g_vfo.band, dir)); }

void vfo_set_limit(uint8_t limit) {
  g_vfo.limit = limit;
  vfo_set_freq(g_vfo.freq);
}

void vfo_set_mode(uint8_t mode) {
  if (mode >= MODE_COUNT || mode == g_vfo.mode) return;
  g_vfo.mode = mode;
  replan();
}

void vfo_set_clock(uint8_t clk, bool on) {
  if (clk >= NUM_CLOCKS) return;
  if (on) g_vfo.clk_en |= (uint8_t)(1 << clk);
  else g_vfo.clk_en &= (uint8_t)~(1 << clk);
  replan();
}

void vfo_set_drive(uint8_t clk, uint8_t drive) {
  if (clk >= NUM_CLOCKS || drive > DRIVE_8MA) return;
  g_vfo.drive[clk] = drive;
  replan();
}

void vfo_set_cal(int32_t ppb) {
  g_vfo.cal_ppb = ppb;
  g_changed = 1;
}

void vfo_cal_mode(bool) { g_changed = 1; }
void vfo_preview_cal(int32_t) {}

bool vfo_mem_store(uint8_t n) {
  if (n >= NUM_MEMORIES) return false;
  g_vfo.mem[n].freq = g_vfo.freq;
  g_vfo.mem[n].info = (uint8_t)((g_vfo.mode << 4) | (g_vfo.band & 0x0F));
  settings_save_now();
  g_changed = 1;
  return true;
}

uint8_t vfo_mem_recall(uint8_t n) {
  if (n >= NUM_MEMORIES || g_vfo.mem[n].info == MEM_EMPTY) return MR_EMPTY;
  uint8_t mode = g_vfo.mem[n].info >> 4;
  if (mode == MODE_QUAD && !iq_in_range(g_vfo.mem[n].freq)) return MR_IQRANGE;
  g_vfo.mode = mode;
  g_vfo.freq = g_vfo.mem[n].freq;
  replan();
  return MR_OK;
}

bool vfo_mem_clear(uint8_t n) {
  if (n >= NUM_MEMORIES) return false;
  g_vfo.mem[n].freq = 0;
  g_vfo.mem[n].info = MEM_EMPTY;
  settings_save_now();
  g_changed = 1;
  return true;
}

void vfo_defaults() {
  state_defaults(g_vfo);
  replan();
  settings_save_now();
}

void vfo_reset_settings() {
  int32_t cal = g_vfo.cal_ppb;
  Memory mem[NUM_MEMORIES];
  memcpy(mem, g_vfo.mem, sizeof(mem));
  state_defaults(g_vfo);
  memcpy(g_vfo.mem, mem, sizeof(mem));
  g_vfo.cal_ppb = cal;
  replan();
  settings_save_now();
}

bool settings_load() {
  state_defaults(g_vfo);
  return true;
}
void settings_touch() {}
void settings_poll() {}
void settings_save_now() {}

// serialcmd.cpp - executes parsed commands against the VFO. Parsing itself is
// in cmd_parser.cpp (host-testable). Replies are "OK", "ERR <reason>" or data.
#include <Arduino.h>
#include "serialcmd.h"
#include "cmd_parser.h"
#include "vfo.h"
#include "bands.h"
#include "tuning.h"
#include "settings.h"
#include "config.h"

#if ENABLE_SERIAL

static char line_buf[CMD_MAX_LINE + 1];
static uint8_t line_len;
static bool line_overflow;


static void ok() { Serial.println(F("OK")); }
static void err(const __FlashStringHelper *why) { Serial.print(F("ERR ")); Serial.println(why); }

#define streq cmd_streq

// Clock argument "0".."2" (also accepts "CLK0".."CLK2").
static bool arg_clk(const char *s, uint8_t &clk) {
  if (!s) return false;
  if (s[0] == 'C' && s[1] == 'L' && s[2] == 'K') s += 3;
  if (s[0] < '0' || s[0] > '2' || s[1]) return false;
  clk = s[0] - '0';
  return true;
}

static void print_status() {
  const VfoState &s = g_vfo;
  uint8_t b = band_find(s.freq);
  Serial.print(F("F=")); Serial.print(s.freq);
  Serial.print(F(" BAND=")); Serial.print(b == 0xFF ? "--" : BANDS[b].name);
  Serial.print(F(" STEP=")); Serial.print(STEPS_HZ[s.step_idx]);
  Serial.print(F(" MODE=")); Serial.print(MODE_NAMES[s.mode]);
  Serial.print(F(" EN=")); Serial.print(s.clk_en, BIN);
  Serial.print(F(" OUT="));
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) {
    if (i) Serial.print(',');
    if (g_plan.on & (1 << i)) Serial.print(g_plan.f[i]); else Serial.print(F("OFF"));
  }
  Serial.print(F(" IF=")); Serial.print(s.if_freq);
  Serial.print(F(" INJ=")); Serial.print(s.injection == INJ_HIGH ? F("HI") : F("LO"));
  Serial.print(F(" IQ=")); Serial.print(s.iq_order);
  Serial.print(F(" LIMIT=")); Serial.print(s.limit == LIMIT_HAM ? F("HAM") : F("WIDE"));
  Serial.print(F(" DRIVE="));
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) { if (i) Serial.print(','); Serial.print(2 + 2 * s.drive[i]); }
  Serial.print(F(" FOVR=")); Serial.print(s.filter_override, BIN);
  Serial.print(F(" CAL=")); Serial.print(s.cal_ppb);
  Serial.print(F(" FLAGS=")); Serial.print(g_plan.flags);
  Serial.print(F(" SI5351=")); Serial.println(g_si5351_ok ? F("OK") : F("ERR"));
}

// Argument count per command (index = CmdId) when setting, and which commands
// accept a '?' query (which then takes no arguments). REQUIREMENTS §9.
static const uint8_t ARGC[CMD_COUNT] = {
  0, 1, 1, 1,             // -, F, STEP, BAND
  1, 1, 1, 2, 1, 1, 1,    // MODE ON OFF DRIVE IF INJ IQ
  1, 2,                   // LIMIT FOVR
  1, 1, 1, 0,             // MS MR MC M?
  1,                      // CAL
  0, 0, 0, 0, 0, 1, 1,    // SAVE DEFAULTS STATUS VER HELP AUTO RESET [ALL]
};
static bool can_query(uint8_t id) {
  return id == CMD_F || id == CMD_STEP || id == CMD_BAND || id == CMD_MODE ||
         id == CMD_IF || id == CMD_CAL || id == CMD_MLIST;
}

static void execute(Cmd &c) {
  if (c.id == CMD_NONE) return;
  if (c.id >= CMD_COUNT) return err(F("CMD"));
  if (c.query && !can_query(c.id)) return err(F("CMD"));
  uint8_t want = c.query ? 0 : ARGC[c.id];
  if (c.id == CMD_RESET && c.argc == 0) want = 0;    // RESET or RESET ALL
  if (c.extra || c.argc != want) return err(F("ARG"));

  uint32_t u;
  int32_t i;
  uint8_t clk;
  const char *a0 = c.argc > 0 ? c.argv[0] : nullptr;
  const char *a1 = c.argc > 1 ? c.argv[1] : nullptr;

  switch (c.id) {
    case CMD_NONE: return;
    case CMD_F:
      if (c.query) { Serial.println(g_vfo.freq); return; }
      if (!arg_u32(a0, u)) return err(F("ARG"));
      vfo_set_freq(u); return ok();
    case CMD_STEP:
      if (c.query) { Serial.println(STEPS_HZ[g_vfo.step_idx]); return; }
      if (!arg_u32(a0, u)) return err(F("ARG"));
      for (uint8_t k = 0; k < NUM_STEPS; k++)
        if (STEPS_HZ[k] == u) { g_vfo.step_idx = k; vfo_changed(); return ok(); }
      return err(F("STEP"));
    case CMD_BAND:
      if (c.query) { uint8_t b = band_find(g_vfo.freq); Serial.println(b == 0xFF ? "--" : BANDS[b].name); return; }
      if (!a0) return err(F("ARG"));
      if (streq(a0, "+")) { vfo_band_step(1); return ok(); }
      if (streq(a0, "-")) { vfo_band_step(-1); return ok(); }
      for (uint8_t b = 0; b < NUM_BANDS; b++) {
        // "40M" or the metres shorthand "40".
        const char *n = BANDS[b].name; uint8_t k = 0;
        while (a0[k] && a0[k] == n[k]) k++;
        if (!a0[k] && (!n[k] || (n[k] == 'M' && !n[k + 1]))) { vfo_set_band(b); return ok(); }
      }
      return err(F("BAND"));
    case CMD_MODE:
      if (c.query) { Serial.println(MODE_NAMES[g_vfo.mode]); return; }
      for (uint8_t m = 0; a0 && m < MODE_COUNT; m++)
        if (streq(a0, MODE_NAMES[m])) {
          if (m == MODE_QUAD && !iq_in_range(g_vfo.freq)) return err(F("IQRANGE"));
          vfo_set_mode(m); return ok();
        }
      return err(F("ARG"));
    case CMD_ON:
    case CMD_OFF:
      if (!arg_clk(a0, clk)) return err(F("ARG"));
      vfo_set_clock(clk, c.id == CMD_ON); return ok();
    case CMD_DRIVE:
      if (!arg_clk(a0, clk) || !arg_u32(a1, u) || u < 2 || u > 8 || (u & 1)) return err(F("ARG"));
      vfo_set_drive(clk, (uint8_t)(u / 2 - 1)); return ok();
    case CMD_IF:
      if (c.query) { Serial.println(g_vfo.if_freq); return; }
      if (!arg_u32(a0, u) || u < FREQ_MIN_HZ || u > FREQ_MAX_HZ) return err(F("ARG"));
      g_vfo.if_freq = u; vfo_update(); return ok();
    case CMD_INJ:
      if (a0 && streq(a0, "HI")) g_vfo.injection = INJ_HIGH;
      else if (a0 && streq(a0, "LO")) g_vfo.injection = INJ_LOW;
      else return err(F("ARG"));
      vfo_update(); return ok();
    case CMD_IQ:
      if (!arg_u32(a0, u) || u > 1) return err(F("ARG"));
      g_vfo.iq_order = (uint8_t)u; vfo_update(); return ok();
    case CMD_LIMIT:
      if (streq(a0, "HAM")) vfo_set_limit(LIMIT_HAM);
      else if (streq(a0, "WIDE")) vfo_set_limit(LIMIT_WIDE);
      else return err(F("ARG"));
      return ok();
    case CMD_FOVR:
      if (!arg_clk(a0, clk) || !arg_u32(a1, u) || u > 1) return err(F("ARG"));
      if (u) g_vfo.filter_override |= 1 << clk; else g_vfo.filter_override &= ~(1 << clk);
      vfo_update(); return ok();
    case CMD_MS:
    case CMD_MR:
    case CMD_MC: {
      if (!arg_u32(a0, u) || u >= NUM_MEMORIES) return err(F("ARG"));
      if (c.id == CMD_MR) {
        uint8_t r = vfo_mem_recall(u);
        if (r == MR_IQRANGE) return err(F("IQRANGE"));
        return r == MR_OK ? ok() : err(F("EMPTY"));
      }
      bool r = c.id == CMD_MS ? vfo_mem_store(u) : vfo_mem_clear(u);
      return r ? ok() : err(F("EMPTY"));
    }
    case CMD_MLIST:
      for (uint8_t m = 0; m < NUM_MEMORIES; m++) {
        Serial.print('M'); Serial.print(m); Serial.print(' ');
        const Memory &mem = g_vfo.mem[m];
        if (mem.info == MEM_EMPTY) { Serial.println(F("--")); continue; }
        Serial.print(mem.freq); Serial.print(' ');
        Serial.print((mem.info >> 4) < MODE_COUNT ? MODE_NAMES[mem.info >> 4] : "?");
        Serial.print(' ');
        Serial.println((mem.info & 15) < NUM_BANDS ? BANDS[mem.info & 15].name : "?");
      }
      return;
    case CMD_CAL:
      if (c.query) { Serial.println(g_vfo.cal_ppb); return; }
      if (!arg_i32(a0, i) || i < -CAL_MAX_PPB || i > CAL_MAX_PPB) return err(F("ARG"));
      vfo_set_cal(i); settings_save_now(); return ok();
    case CMD_SAVE: settings_save_now(); return ok();
    case CMD_DEFAULTS: vfo_defaults(); return ok();     // = RESET ALL (kept for compatibility)
    case CMD_RESET:
      if (!a0) { vfo_reset_settings(); return ok(); }  // keeps cal + memories
      if (streq(a0, "ALL")) { vfo_defaults(); return ok(); }
      return err(F("ARG"));
    case CMD_STATUS: print_status(); return;
    case CMD_VER: Serial.println(F(FW_NAME " " FW_VERSION)); return;
    case CMD_HELP:
      for (uint8_t k = 1; k < CMD_COUNT; k++) { Serial.print(cmd_name(k)); Serial.print(k == CMD_MLIST ? "? " : " "); }
      Serial.println();
      return;
    case CMD_AUTO:
      return err(F("NOTIMPL"));   // TODO: unsolicited status line on change
    default:
      return err(F("CMD"));
  }
}

void serialcmd_begin() { Serial.begin(SERIAL_BAUD); }

void serialcmd_poll() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\r' || ch == '\n') {
      if (line_overflow) err(F("LONG"));
      else if (line_len) {
        line_buf[line_len] = 0;
        Cmd c;
        cmd_parse(line_buf, c);
        execute(c);
      }
      line_len = 0;
      line_overflow = false;
    } else if (line_len < CMD_MAX_LINE) {
      line_buf[line_len++] = ch;
    } else {
      line_overflow = true;
    }
  }
}

#else
void serialcmd_begin() {}
void serialcmd_poll() {}
#endif

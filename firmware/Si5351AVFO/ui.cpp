// ui.cpp - display and button handling.
//
// Page map (8 px pages on the 128x64 SH1106):
//   0      status line: mode, band, tuning limit, enabled clocks
//   2-3    frequency in 8x16 digits "MMM.KKK.HHH"
//   4      2 px step underline under the digit the step changes
//   5      step size
//   6      warnings / mode info / messages
//   7      soft-key labels centred over SW2, SW3, SW4
//
// Controls:
//   main  : encoder tunes, push cycles step, SW2 BAND-, SW3 BAND+, SW4 MENU
//   menu  : encoder scrolls, push enters, SW2/SW3 page up/down, SW4 back
//   edit  : encoder changes value, SW2/SW3 move digit cursor left/right,
//           push saves, SW4 cancels
#include <Arduino.h>
#include <stdlib.h>
#include <string.h>
#include "ui.h"
#include "input.h"
#include "sh1106.h"
#include "vfo.h"
#include "bands.h"
#include "tuning.h"
#include "settings.h"
#include "config.h"

enum Screen : uint8_t { SCR_MAIN, SCR_MENU, SCR_EDIT };
static uint8_t screen = SCR_MAIN;
static bool redraw = true;               // full redraw of the current screen
static const char *msg;                  // transient message, nullptr if none
static uint32_t msg_ms;

// ---------------------------------------------------------------- menu table
enum ItemKind : uint8_t { K_CHOICE, K_NUM };
enum ItemId : uint8_t {
  I_MODE, I_CLK0, I_CLK1, I_CLK2, I_IF, I_INJ, I_IQ, I_LIMIT,
  I_DRV0, I_DRV1, I_DRV2, I_FOV0, I_FOV1, I_FOV2,
  I_MSTORE, I_MRECALL, I_MCLEAR, I_CAL, I_RESET, I_FACTORY, I_ABOUT, I_COUNT
};
struct MenuItem {
  const char *label;
  uint8_t kind;      // ItemKind
  uint8_t n;         // K_CHOICE: number of options; K_NUM: number of digits
  const char *opts;  // K_CHOICE: options separated by '|' (nullptr = generated)
};
static const MenuItem ITEMS[I_COUNT] = {
  {"OUTPUT MODE",  K_CHOICE, 3, "DIRECT|SUPERHET|QUADRATURE"},
  {"CLK0 OUTPUT",  K_CHOICE, 2, "OFF|ON"},
  {"CLK1 OUTPUT",  K_CHOICE, 2, "OFF|ON"},
  {"CLK2 OUTPUT",  K_CHOICE, 2, "OFF|ON"},
  {"IF FREQ",      K_NUM,    9, nullptr},
  {"LO INJECTION", K_CHOICE, 2, "HIGH F+IF|LOW F-IF"},
  {"IQ ORDER",     K_CHOICE, 2, "CLK0 = I|CLK1 = I"},
  {"TUNING LIMIT", K_CHOICE, 2, "WIDE OPEN|HAM BANDS"},
  {"CLK0 DRIVE",   K_CHOICE, 4, "2 MA|4 MA|6 MA|8 MA"},
  {"CLK1 DRIVE",   K_CHOICE, 4, "2 MA|4 MA|6 MA|8 MA"},
  {"CLK2 DRIVE",   K_CHOICE, 4, "2 MA|4 MA|6 MA|8 MA"},
  {"CLK0 FILT OVR", K_CHOICE, 2, "OFF|ON"},
  {"CLK1 FILT OVR", K_CHOICE, 2, "OFF|ON"},
  {"CLK2 FILT OVR", K_CHOICE, 2, "OFF|ON"},
  {"MEM STORE",    K_CHOICE, NUM_MEMORIES, nullptr},
  {"MEM RECALL",   K_CHOICE, NUM_MEMORIES, nullptr},
  {"MEM CLEAR",    K_CHOICE, NUM_MEMORIES, nullptr},
  {"CALIBRATE PPB", K_NUM,   6, nullptr},
  {"RESET SETTINGS", K_CHOICE, 2, "NO|YES"},             // keeps cal + memories
  {"FACTORY RESET", K_CHOICE, 2, "NO|YES, ERASE ALL"},   // erases cal + memories
  {"ABOUT",        K_CHOICE, 1, FW_NAME " " FW_VERSION},
};
#define MENU_ROWS 6                      // list rows on pages 1-6

static uint8_t menu_sel, menu_top;       // selected item, first visible item
static int32_t edit_val;                 // working copy while editing
static int32_t edit_orig;                // value when the editor opened (cancel)
static uint8_t edit_cursor;              // K_NUM: digit index from the right

// Current value of an item, read from g_vfo.
static int32_t item_get(uint8_t id) {
  const VfoState &s = g_vfo;
  switch (id) {
    case I_MODE:  return s.mode;
    case I_CLK0: case I_CLK1: case I_CLK2: return (s.clk_en >> (id - I_CLK0)) & 1;
    case I_IF:    return (int32_t)s.if_freq;
    case I_INJ:   return s.injection;
    case I_IQ:    return s.iq_order;
    case I_LIMIT: return s.limit;
    case I_DRV0: case I_DRV1: case I_DRV2: return s.drive[id - I_DRV0];
    case I_FOV0: case I_FOV1: case I_FOV2: return (s.filter_override >> (id - I_FOV0)) & 1;
    case I_CAL:   return s.cal_ppb;
    default:      return 0;
  }
}

// Store an edited value. Returns a message to show, or nullptr.
static const char *item_set(uint8_t id, int32_t v) {
  VfoState &s = g_vfo;
  switch (id) {
    case I_MODE:  vfo_set_mode((uint8_t)v); break;
    case I_CLK0: case I_CLK1: case I_CLK2: vfo_set_clock(id - I_CLK0, v); break;
    case I_IF:    s.if_freq = (uint32_t)v; vfo_update(); break;
    case I_INJ:   s.injection = (uint8_t)v; vfo_update(); break;
    case I_IQ:    s.iq_order = (uint8_t)v; vfo_update(); break;
    case I_LIMIT: vfo_set_limit((uint8_t)v); break;
    case I_DRV0: case I_DRV1: case I_DRV2: vfo_set_drive(id - I_DRV0, (uint8_t)v); break;
    case I_FOV0: case I_FOV1: case I_FOV2: {
      uint8_t bit = 1 << (id - I_FOV0);
      if (v) s.filter_override |= bit; else s.filter_override &= ~bit;
      vfo_update();
      break;
    }
    case I_MSTORE:  vfo_mem_store((uint8_t)v); return "MEMORY STORED";
    case I_MRECALL: return vfo_mem_recall((uint8_t)v) ? "MEMORY RECALLED" : "MEMORY EMPTY";
    case I_MCLEAR:  vfo_mem_clear((uint8_t)v); return "MEMORY CLEARED";
    case I_CAL:     vfo_set_cal(v); settings_save_now(); return "CAL SAVED";
    case I_RESET:   if (v) { vfo_reset_settings(); return "SETTINGS RESET"; } break;
    case I_FACTORY: if (v) { vfo_defaults(); return "FACTORY RESET DONE"; } break;
  }
  return nullptr;
}

// Append s at d, return the new end (tiny stand-in for the printf family,
// which would pull ~1.5 KB into the build).
static char *cat(char *d, const char *s) {
  while ((*d = *s++)) d++;
  return d;
}

// Text for option v of a choice item into buf (max 21 chars).
static void option_text(uint8_t id, uint8_t v, char *buf) {
  const MenuItem &it = ITEMS[id];
  if (!it.opts) {                        // memory channels: "M3 14.074.000" or "M3 --"
    const Memory &m = g_vfo.mem[v];
    buf[0] = 'M'; buf[1] = '0' + v; buf[2] = ' ';
    if (m.info == MEM_EMPTY) cat(buf + 3, "--");
    else freq_format(m.freq, buf + 3);
    return;
  }
  const char *p = it.opts;
  while (v && *p) { if (*p++ == '|') v--; }
  uint8_t i = 0;
  while (*p && *p != '|' && i < 21) buf[i++] = *p++;
  buf[i] = 0;
}

// --------------------------------------------------------------- drawing
// Draw a 5x7 line and blank the rest of the page, so nothing flickers.
static void line(uint8_t page, uint8_t col, const char *s, uint8_t ul = 0xFF, bool inv = false) {
  uint8_t len = strlen(s);
  if (col) sh1106::fill(page, 0, col, inv ? 0xFF : 0);
  sh1106::text5x7(page, col, s, ul, inv);
  uint8_t end = col + len * 6;
  if (end < 128) sh1106::fill(page, end, 128 - end, inv ? 0xFF : 0);
}

static void labels(const char *a, const char *b, const char *c) {
  sh1106::clearPage(7);
  const char *t[3] = {a, b, c};
  const uint8_t x[3] = {LABEL_X0, LABEL_X1, LABEL_X2};
  for (uint8_t i = 0; i < 3; i++) {
    int16_t col = x[i] - (int16_t)strlen(t[i]) * 3;   // centre (6 px per char)
    if (col < 0) col = 0;
    sh1106::text5x7(7, (uint8_t)col, t[i]);
  }
}

// Big 8x16 number at pages 2-3 with a 2 px bar on page 4 under character `ul`.
#define BIG_COL 20
static void big_number(const char *s, uint8_t ul) {
  sh1106::big8x16(2, BIG_COL, s);
  sh1106::clearPage(4);
  if (ul != 0xFF) sh1106::fill(4, BIG_COL + ul * 8, 7, 0x03);
}


static void draw_main() {
  char buf[24];
  const VfoState &s = g_vfo;
  if (redraw) labels("BAND-", "BAND+", "MENU");

  // Status: "DIR 40M WIDE C0--"
  uint8_t b = band_find(s.freq);
  char clk[4];
  for (uint8_t i = 0; i < 3; i++) clk[i] = (g_plan.on >> i) & 1 ? '0' + i : '-';
  clk[3] = 0;
  char *p = cat(buf, MODE_NAMES[s.mode]);
  p = cat(p, " "); p = cat(p, b == 0xFF ? "--" : BANDS[b].name);
  p = cat(p, s.limit == LIMIT_HAM ? " HAM C" : " WIDE C");
  cat(p, clk);
  line(0, 0, buf);

  char f[FREQ_STR_LEN + 1];
  freq_format(s.freq, f);
  big_number(f, step_underline_pos(s.step_idx));

  uint32_t st = STEPS_HZ[s.step_idx];
  p = cat(buf, "STEP ");
  ultoa(st >= 1000 ? st / 1000 : st, p, 10);
  cat(p + strlen(p), st >= 1000 ? " KHZ" : " HZ");
  line(5, 0, buf);

  // Info line: message, then warnings, then mode details.
  if (msg) line(6, 0, msg);
  else if (!g_si5351_ok) line(6, 0, "SI5351 NOT FOUND");
  else if (g_plan.flags & PLAN_FAIL) line(6, 0, "CLK NOT POSSIBLE: OFF");
  else if (g_plan.flags & PLAN_IQ_LOW) line(6, 0, "IQ NEEDS >4.76 MHZ");
  else if (g_plan.flags & PLAN_IQ_HIGH) line(6, 0, "IQ ONLY TO 90 MHZ");
  else if (g_plan.flags & PLAN_LO_RANGE) line(6, 0, "LO OUT OF RANGE");
  else if (g_plan.flags & PLAN_FILTER) line(6, 0, "ABOVE LPF: CLK MUTED");
  else if (s.mode == MODE_SUPERHET) {
    freq_format(s.if_freq, f);
    p = cat(buf, "IF"); p = cat(p, f);
    cat(p, s.injection == INJ_HIGH ? " HI" : " LO");
    line(6, 0, buf);
  } else line(6, 0, "");
}

static void draw_menu() {
  char buf[24];
  if (redraw) { labels("PG UP", "PG DN", "BACK"); line(0, 0, "MENU"); }
  for (uint8_t r = 0; r < MENU_ROWS; r++) {
    uint8_t id = menu_top + r;
    if (id >= I_COUNT) { sh1106::clearPage(1 + r); continue; }
    buf[0] = ' ';
    cat(buf + 1, ITEMS[id].label);
    line(1 + r, 0, buf, 0xFF, id == menu_sel);   // selected row inverted
  }
}

// Format a K_NUM edit value; returns the char index of digit `cursor`.
static uint8_t format_num(uint8_t id, int32_t v, char *buf, uint8_t cursor) {
  if (id == I_IF) {                      // "MMM.KKK.HHH" like the main screen
    freq_format((uint32_t)v, buf);
    return 10 - cursor - (cursor >= 3) - (cursor >= 6);
  }
  // Calibration: sign + 6 digits, e.g. "-001250"
  uint32_t u = v < 0 ? -v : v;
  buf[0] = v < 0 ? '-' : ' ';
  for (int8_t i = 6; i >= 1; i--) { buf[i] = '0' + u % 10; u /= 10; }
  buf[7] = 0;
  return 6 - cursor;
}

static void draw_edit() {
  char buf[24];
  const MenuItem &it = ITEMS[menu_sel];
  if (redraw) {
    sh1106::clear();
    line(0, 0, it.label);
    if (it.kind == K_NUM) labels("<", ">", "CANCEL");
    else labels("", "", "CANCEL");
  }
  if (it.kind == K_NUM) {
    uint8_t ul = format_num(menu_sel, edit_val, buf, edit_cursor);
    big_number(buf, ul);
    if (menu_sel == I_CAL) line(6, 0, "CLK2 = 10.000000 MHZ");
  } else {
    option_text(menu_sel, (uint8_t)edit_val, buf);
    line(3, 12, buf);
  }
}

// --------------------------------------------------------------- events
static void enter_screen(uint8_t s) {
  screen = s;
  redraw = true;
  sh1106::clear();
}

static void edit_begin() {
  if (menu_sel == I_ABOUT) { ui_message(FW_NAME " " FW_VERSION); return; }
  edit_val = edit_orig = item_get(menu_sel);
  edit_cursor = 0;
  if (menu_sel == I_CAL) vfo_cal_mode(true);
  enter_screen(SCR_EDIT);
}

static void edit_end(bool save) {
  const char *m = nullptr;
  if (menu_sel == I_CAL) {
    if (!save) vfo_preview_cal(edit_orig);     // undo the preview (hardware only)
    vfo_cal_mode(false);
  }
  if (save) m = item_set(menu_sel, edit_val);
  enter_screen(SCR_MENU);
  if (m) ui_message(m);
}

static void edit_turn(int8_t d) {
  const MenuItem &it = ITEMS[menu_sel];
  if (it.kind == K_CHOICE) {             // wrap through the options
    int8_t step = d < 0 ? -1 : 1;
    for (int8_t k = d; k; k -= step) {
      int16_t v = edit_val + step;
      if (v < 0) v = it.n - 1;
      if (v >= it.n) v = 0;
      edit_val = v;
      // Quadrature is greyed out (skipped) outside its range (§6.3).
      if (menu_sel == I_MODE && v == MODE_QUAD && !iq_in_range(g_vfo.freq)) k += step;
    }
    return;
  }
  if (d > 9) d = 9;                      // keeps d * p inside int32 (S7)
  if (d < -9) d = -9;
  int32_t p = 1;
  for (uint8_t i = 0; i < edit_cursor; i++) p *= 10;
  int32_t v = edit_val + (int32_t)d * p;
  int32_t lo = (menu_sel == I_CAL) ? -CAL_MAX_PPB : (int32_t)FREQ_MIN_HZ;
  int32_t hi = (menu_sel == I_CAL) ? CAL_MAX_PPB : (int32_t)FREQ_MAX_HZ;
  edit_val = v < lo ? lo : (v > hi ? hi : v);
  if (menu_sel == I_CAL) vfo_preview_cal(edit_val);   // live preview on CLK2, not saved
}

void ui_event(uint8_t ev, int8_t d) {
  if (ev == EV_NONE) return;
  g_changed = 1;
  switch (screen) {
    case SCR_MAIN:
      if (ev == EV_ENC) vfo_tune(d);
      else if (ev == EV_PUSH) { g_vfo.step_idx = step_next(g_vfo.step_idx); vfo_changed(); }
      else if (ev == EV_SW2) vfo_band_step(-1);
      else if (ev == EV_SW3) vfo_band_step(+1);
      else if (ev == EV_SW4) enter_screen(SCR_MENU);
      break;

    case SCR_MENU: {
      int16_t sel = menu_sel;
      if (ev == EV_ENC) sel += d;
      else if (ev == EV_SW2) sel -= MENU_ROWS;
      else if (ev == EV_SW3) sel += MENU_ROWS;
      else if (ev == EV_SW4) { enter_screen(SCR_MAIN); break; }
      else if (ev == EV_PUSH) { edit_begin(); break; }
      menu_sel = sel < 0 ? 0 : (sel >= I_COUNT ? I_COUNT - 1 : sel);
      if (menu_sel < menu_top) menu_top = menu_sel;
      if (menu_sel >= menu_top + MENU_ROWS) menu_top = menu_sel - MENU_ROWS + 1;
      break;
    }

    case SCR_EDIT:
      if (ev == EV_ENC) edit_turn(d);
      else if (ev == EV_PUSH) edit_end(true);
      else if (ev == EV_SW4) edit_end(false);
      else if (ITEMS[menu_sel].kind == K_NUM) {
        uint8_t n = ITEMS[menu_sel].n;
        if (ev == EV_SW2 && edit_cursor + 1 < n) edit_cursor++;   // cursor left
        if (ev == EV_SW3 && edit_cursor > 0) edit_cursor--;       // cursor right
      }
      break;
  }
}

void ui_message(const char *m) {
  msg = m;
  msg_ms = millis();
  g_changed = 1;
}

void ui_begin() {
  sh1106::begin();
  enter_screen(SCR_MAIN);
}

void ui_refresh() {
  if (msg && millis() - msg_ms >= MSG_HOLD_MS) { msg = nullptr; g_changed = 1; }
  if (!g_changed && !redraw) return;
  g_changed = 0;
  if (screen == SCR_MAIN) draw_main();
  else if (screen == SCR_MENU) {
    draw_menu();
    if (msg) line(0, 0, msg); else line(0, 0, "MENU");
  } else draw_edit();
  redraw = false;
}

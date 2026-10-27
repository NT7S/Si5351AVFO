// Drive the real ui.cpp against the SH1106 RAM emulator and dump PBM frames.
//
//   oledsim <outdir>
//
// Frames are 128x64, the visible window (RAM columns 2..129).
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "ui.h"
#include "input.h"
#include "vfo.h"
#include "bands.h"
#include "modes.h"
#include "config.h"
#include "sh1106.h"
#include "oled_port.h"

static char g_dir[512];
static int g_fails = 0;

static void frame_path(char *out, size_t n, const char *name) {
  snprintf(out, n, "%s/%s.pbm", g_dir, name);
}

static void write_frame(const char *name) {
  char path[640];
  frame_path(path, sizeof(path), name);
  FILE *f = fopen(path, "w");
  if (!f) {
    perror(path);
    g_fails++;
    return;
  }
  fprintf(f, "P1\n128 64\n");
  for (int y = 0; y < 64; y++) {
    int page = y / 8;
    int bit = y % 8;
    for (int x = 0; x < 128; x++) {
      int on = (oled_ram[page][x + SH1106_COL_OFFSET] >> bit) & 1;
      fputc(on ? '1' : '0', f);
      fputc(x == 127 ? '\n' : ' ', f);
    }
  }
  fclose(f);

  // The panel never shows RAM columns 0, 1, 130 or 131. Anything lit there
  // means a write missed the 2-column offset or ran past the visible 128.
  for (int p = 0; p < OLED_RAM_PAGES; p++) {
    for (int c = 0; c < OLED_RAM_COLS; c++) {
      bool hidden = c < SH1106_COL_OFFSET || c >= SH1106_COL_OFFSET + 128;
      if (hidden && oled_ram[p][c]) {
        fprintf(stderr, "%s: pixel in hidden RAM column %d page %d\n", name, c, p);
        g_fails++;
        return;
      }
    }
  }
  if (oled_oob_writes) {
    fprintf(stderr, "%s: %d writes outside 132-column RAM\n", name, oled_oob_writes);
    g_fails++;
  }
}

static void boot() {
  memset(oled_ram, 0, sizeof(oled_ram));
  oled_oob_writes = 0;
  state_defaults(g_vfo);
  g_si5351_ok = true;
  plan_outputs(g_vfo, g_plan);
  g_changed = 1;
  sim_set_millis(10000);
  ui_begin();
  ui_refresh();
  // Drop a confirmation left over from the previous scenario.
  sim_set_millis(sim_millis() + MSG_HOLD_MS + 1);
  ui_refresh();
}

static void act(uint8_t ev, int8_t d) {
  ui_event(ev, d);
  ui_refresh();
}

// menu_sel survives ui_begin(), so clamp to the top and then step.
static void open_item(uint8_t index) {
  boot();
  act(EV_SW4, 0);
  act(EV_ENC, (int8_t)-120);
  if (index) act(EV_ENC, (int8_t)index);
}

static void save_item(uint8_t index, int8_t turn) {
  open_item(index);
  act(EV_PUSH, 0);
  if (turn) act(EV_ENC, turn);
  act(EV_PUSH, 0);
}

static void superhet_main() {
  save_item(0, +1);             // OUTPUT MODE -> SUPERHET, confirmation up
  act(EV_SW4, 0);               // back to the main screen, message still held
  sim_set_millis(sim_millis() + MSG_HOLD_MS + 1);
  ui_refresh();                 // steady superhet screen
}

int main(int argc, char **argv) {
  if (argc < 2) {
    fprintf(stderr, "usage: oledsim <outdir>\n");
    return 2;
  }
  snprintf(g_dir, sizeof(g_dir), "%s", argv[1]);

  boot();
  write_frame("main_normal");

  superhet_main();
  write_frame("main_superhet");

  open_item(0);
  write_frame("menu_top");
  // One detent at a time so scrolling can be checked across all 21 items.
  for (uint8_t i = 1; i <= 20; i++) {
    act(EV_ENC, +1);
    char name[32];
    snprintf(name, sizeof(name), "menu_pos_%02u", i);
    write_frame(name);
  }
  write_frame("menu_bottom");

  // Page keys move by a window, then stop at the ends.
  open_item(0);
  act(EV_SW3, 0);
  write_frame("menu_page_down");
  act(EV_SW2, 0);
  write_frame("menu_page_up");

  // Editors. turn is the encoder motion inside the editor before push-to-save.
  struct Save {
    const char *name;
    uint8_t index;
    int8_t turn;
  };
  const Save saves[] = {
    {"save_mode", 0, +1},       // OUTPUT MODE -> SUPERHET
    {"save_clk", 1, +1},        // CLK0 OUTPUT -> OFF
    {"save_drive", 8, -1},      // CLK0 DRIVE -> 6 mA
    {"save_limit", 7, +1},      // TUNING LIMIT -> HAM BANDS
    {"save_filter", 11, +1},    // CLK0 FILT OVR -> ON
    {"save_if", 4, 0},          // IF FREQ, unchanged value still saved
    {"save_inject", 5, +1},     // LO INJECTION -> LOW
    {"save_iq", 6, +1},         // IQ ORDER
    {"save_memory", 14, 0},     // MEM STORE (already confirmed before this change)
    {"save_cal", 17, 0},        // CALIBRATE PPB
  };
  for (uint8_t i = 0; i < sizeof(saves) / sizeof(saves[0]); i++) {
    save_item(saves[i].index, saves[i].turn);
    write_frame(saves[i].name);
  }

  // Soft-key labels on the editor. CANCEL is centred on SW4 and its cell
  // runs through the last visible column.
  open_item(0);
  act(EV_PUSH, 0);
  write_frame("edit_choice");
  open_item(4);
  act(EV_PUSH, 0);
  write_frame("edit_if");

  if (g_fails) {
    fprintf(stderr, "%d frame checks failed\n", g_fails);
    return 1;
  }
  return 0;
}

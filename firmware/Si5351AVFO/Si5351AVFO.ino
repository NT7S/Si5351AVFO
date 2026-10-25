// Si5351A VFO firmware - NT7S/Si5351AVFO (Si5351 Field Manual ch. 6)
// Target: ATtiny3226, megaTinyCore 2.6.11, "ATtiny3226 w/Optiboot",
// 8 MHz internal, reset "UPDI on PA0, RST on PB4". See ../README.md.
// MIT License, see ../LICENSE.
#include <Arduino.h>
#include "config.h"
#include "vfo.h"
#include "input.h"
#include "ui.h"
#include "settings.h"
#include "serialcmd.h"

static uint32_t retry_ms;

void setup() {
  settings_load();          // defaults if the EEPROM is blank or corrupt
  input_begin();
  ui_begin();               // OLED reset + init (REQUIREMENTS §4 step 2)
  vfo_begin();              // Si5351 init, restores mode/frequencies/outputs
  serialcmd_begin();
}

void loop() {
  int8_t detents = 0;
  uint8_t ev = input_poll(&detents);
  ui_event(ev, detents);
  serialcmd_poll();
  settings_poll();

  // Si5351 missing: retry once a second (REQUIREMENTS §4 step 4).
  if (!g_si5351_ok && millis() - retry_ms >= 1000) {
    retry_ms = millis();
    if (vfo_begin()) g_changed = 1;
  }
  ui_refresh();
}

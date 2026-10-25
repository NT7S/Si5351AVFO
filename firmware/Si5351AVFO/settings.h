// settings.h - load/save g_vfo in EEPROM with a delayed write (REQUIREMENTS §7).
#pragma once
#include <stdint.h>

bool settings_load();      // false if EEPROM was blank/corrupt (defaults loaded)
void settings_touch();     // something changed: save SAVE_DELAY_MS after the last change
void settings_poll();      // call from loop(); performs the delayed save
void settings_save_now();  // write immediately (memories, calibration, SAVE command)

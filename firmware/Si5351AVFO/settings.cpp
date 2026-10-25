#include <Arduino.h>
#include <EEPROM.h>
#include "settings.h"
#include "eeprom_layout.h"
#include "vfo.h"
#include "config.h"

static bool dirty;
static uint32_t dirty_ms;

bool settings_load() {
  uint8_t img[EE_SIZE];
  for (uint8_t i = 0; i < EE_SIZE; i++) img[i] = EEPROM.read(i);
  if (ee_unpack(img, g_vfo)) return true;
  state_defaults(g_vfo);
  return false;
}

void settings_touch() {
  dirty = true;
  dirty_ms = millis();
}

void settings_save_now() {
  uint8_t img[EE_SIZE];
  ee_pack(g_vfo, img);
  // EEPROM.update only writes bytes that differ, which keeps wear down.
  for (uint8_t i = 0; i < EE_SIZE; i++) EEPROM.update(i, img[i]);
  dirty = false;
}

void settings_poll() {
  if (dirty && millis() - dirty_ms >= SAVE_DELAY_MS) settings_save_now();
}

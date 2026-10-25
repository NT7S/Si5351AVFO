#include <Arduino.h>
#include <EEPROM.h>
#include "settings.h"
#include "eeprom_layout.h"
#include "vfo.h"
#include "config.h"

static bool dirty;
static uint32_t dirty_ms;

// Two slots (A at 0, B at EE_SIZE). Each save goes to the older slot with
// seq + 1, so a write interrupted by power loss leaves the other slot intact.
static uint8_t cur_slot, cur_seq;

bool settings_load() {
  uint8_t img[EE_SIZE];
  bool found = false;
  for (uint8_t k = 0; k < EE_SLOTS; k++) {
    for (uint8_t i = 0; i < EE_SIZE; i++) img[i] = EEPROM.read(k * EE_SIZE + i);
    if (!ee_valid(img)) continue;
    if (found && !ee_newer(img[EE_OFF_SEQ], cur_seq)) continue;
    found = true; cur_slot = k; cur_seq = img[EE_OFF_SEQ];
  }
  if (found) {
    for (uint8_t i = 0; i < EE_SIZE; i++) img[i] = EEPROM.read(cur_slot * EE_SIZE + i);
    ee_unpack(img, g_vfo);
    return true;
  }
  state_defaults(g_vfo);
  cur_slot = EE_SLOTS - 1;             // first save goes to slot A, seq 1
  cur_seq = 0;
  return false;
}

void settings_touch() {
  dirty = true;
  dirty_ms = millis();
}

void settings_save_now() {
  uint8_t img[EE_SIZE];
  cur_slot ^= 1;
  ee_pack(g_vfo, img, ++cur_seq);
  // EEPROM.update only writes bytes that differ, which keeps wear down.
  for (uint8_t i = 0; i < EE_SIZE; i++) EEPROM.update(cur_slot * EE_SIZE + i, img[i]);
  dirty = false;
}

void settings_poll() {
  if (dirty && millis() - dirty_ms >= SAVE_DELAY_MS) settings_save_now();
}

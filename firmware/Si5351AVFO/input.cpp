#include <Arduino.h>
#include "input.h"
#include "pins.h"
#include "tuning.h"
#include "config.h"

static volatile int16_t enc_quarters;   // accumulated quarter-steps (ISR)
static uint8_t enc_state;

static void enc_isr() {
  uint8_t ab = (digitalReadFast(PIN_ENC_A) ? 2 : 0) | (digitalReadFast(PIN_ENC_B) ? 1 : 0);
  enc_quarters += enc_decode(enc_state, ab);
}

// Buttons in event order: push, SW2, SW3, SW4.
static const uint8_t BTN_PINS[4] = {PIN_ENC_SW, PIN_BTN_S1, PIN_BTN_S2, PIN_BTN_S3};
static uint8_t btn_stable = 0x0F;       // bit = 1: released (active low)
static uint8_t btn_raw = 0x0F;
static uint32_t btn_changed_ms[4];

void input_begin() {
  pinMode(PIN_ENC_A, INPUT);            // external 10k pull-ups on the board
  pinMode(PIN_ENC_B, INPUT);
  for (uint8_t i = 0; i < 4; i++) pinMode(BTN_PINS[i], INPUT);
  enc_state = (digitalRead(PIN_ENC_A) ? 2 : 0) | (digitalRead(PIN_ENC_B) ? 1 : 0);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), enc_isr, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_B), enc_isr, CHANGE);
}

uint8_t input_poll(int8_t *detents) {
  // Encoder: hand out whole detents, keep the remainder.
  noInterrupts();
  int16_t q = enc_quarters;
  int8_t d = q / ENC_QUARTERS_PER_DETENT;
  enc_quarters = q - d * ENC_QUARTERS_PER_DETENT;
  interrupts();
  if (d) {
    *detents = ENC_REVERSE ? -d : d;
    return EV_ENC;
  }

  // Buttons: a level must hold for BTN_DEBOUNCE_MS; event on the press edge.
  uint32_t now = millis();
  for (uint8_t i = 0; i < 4; i++) {
    uint8_t bit = 1 << i;
    uint8_t level = digitalRead(BTN_PINS[i]) ? bit : 0;
    if (level != (btn_raw & bit)) { btn_raw ^= bit; btn_changed_ms[i] = now; continue; }
    if (level != (btn_stable & bit) && now - btn_changed_ms[i] >= BTN_DEBOUNCE_MS) {
      btn_stable ^= bit;
      if (!level) return EV_PUSH + i;   // pressed (went low)
    }
  }
  return EV_NONE;
}

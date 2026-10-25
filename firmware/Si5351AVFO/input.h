// input.h - rotary encoder and the four push buttons, turned into events.
// The encoder is read in a pin-change interrupt so no steps are lost while
// the display is being redrawn; buttons are polled and debounced in software
// on top of the board's ~1-2 ms RC filters.
#pragma once
#include <stdint.h>

enum InputEvent : uint8_t {
  EV_NONE = 0,
  EV_ENC,       // encoder turned; detents in input_detents()
  EV_PUSH,      // encoder push (SW1)
  EV_SW2,       // left soft button  (BTN_S1, PC3)
  EV_SW3,       // middle soft button (BTN_S2, PB5)
  EV_SW4,       // right soft button (BTN_S3, PA7)
};

void input_begin();
// Return the next event, or EV_NONE. For EV_ENC, *detents gets the signed
// number of detents turned since the last call (+ = clockwise).
uint8_t input_poll(int8_t *detents);

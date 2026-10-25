// ui.h - screens: main tuning screen, menu list and value editor
// (REQUIREMENTS §5, §6.1, §6.2).
#pragma once
#include <stdint.h>

void ui_begin();
void ui_event(uint8_t ev, int8_t detents);   // InputEvent from input_poll()
void ui_refresh();                           // redraw if anything changed
void ui_message(const char *msg);            // show on the info line for MSG_HOLD_MS

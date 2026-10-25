// vfo.h - the running VFO: owns the state, drives the Si5351 and tracks
// changes. The UI and the serial interface both act through these calls so
// the display always follows serial changes and vice versa.
#pragma once
#include <stdint.h>
#include "vfo_state.h"
#include "modes.h"

extern VfoState g_vfo;        // current state (saved to EEPROM by settings.cpp)
extern ClockPlan g_plan;      // what is actually on the outputs
extern bool g_si5351_ok;      // false if the Si5351 did not answer on I2C
extern uint8_t g_changed;     // set non-zero whenever the state changes (UI redraw)

bool vfo_begin();                       // init Si5351 and apply g_vfo; false if not found
void vfo_apply();                       // re-plan and program every output
void vfo_set_freq(uint32_t f);          // clamp per tuning limit, keep band index
void vfo_tune(int8_t detents);          // tune by the current step
void vfo_band_step(int8_t dir);         // BAND+/BAND- with per-band memory
void vfo_set_band(uint8_t band);
void vfo_set_limit(uint8_t limit);     // off-band F moves to the nearest band edge
void vfo_set_mode(uint8_t mode);
void vfo_set_clock(uint8_t clk, bool on);
void vfo_set_drive(uint8_t clk, uint8_t drive);
void vfo_set_cal(int32_t ppb);          // apply correction live
void vfo_cal_mode(bool on);             // CLK2 = 10 MHz for calibration
bool vfo_mem_store(uint8_t n);
bool vfo_mem_recall(uint8_t n);
bool vfo_mem_clear(uint8_t n);
void vfo_defaults();
void vfo_changed();
void vfo_update();                      // after editing g_vfo fields directly: reprogram all + save                     // mark state changed: redraw + delayed save

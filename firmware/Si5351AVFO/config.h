// config.h - build-time constants for the Si5351A VFO firmware.
#pragma once

#define FW_VERSION       "0.1.0"
#define FW_NAME          "SI5351A VFO"

#define REF_FREQ_HZ      25000000UL   // X1 25.000 MHz TCXO into XA
#define SERIAL_BAUD      115200
#define SAVE_DELAY_MS    5000UL        // write EEPROM 5 s after the last change
#define CAL_FREQ_HZ      10000000UL    // calibration output on CLK2
#define MSG_HOLD_MS      2000UL        // how long a status message stays up

// Encoder: quarter-steps (AB transitions) per mechanical detent.
// EC11E18244A5: 18 pulses / 36 detents -> 2. VERIFY ON HARDWARE.
#define ENC_QUARTERS_PER_DETENT 2
// Set to 1 if the encoder tunes backwards on the real board.
#define ENC_REVERSE      0

#define BTN_DEBOUNCE_MS  20

// Soft-key label centres in px (button centres 5.0/17.7/30.4 mm on the 35.4 mm
// module). VERIFY ON A SAMPLE MODULE.
#define LABEL_X0  18
#define LABEL_X1  64
#define LABEL_X2  110

// Compile-time switch to drop the serial interface (flash emergencies only).
#ifndef ENABLE_SERIAL
#define ENABLE_SERIAL 1
#endif

#include "eeprom_layout.h"
#include "bands.h"
#include "tuning.h"

static void put32(uint8_t *p, uint32_t v) {
  for (uint8_t i = 0; i < 4; i++) { p[i] = (uint8_t)v; v >>= 8; }
}
static uint32_t get32(const uint8_t *p) {
  return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

uint8_t crc8(const uint8_t *p, uint8_t n) {
  uint8_t c = 0;
  while (n--) {
    c ^= *p++;
    for (uint8_t b = 0; b < 8; b++) c = (c & 0x80) ? (uint8_t)((c << 1) ^ 0x07) : (uint8_t)(c << 1);
  }
  return c;
}

void ee_pack(const VfoState &s, uint8_t *img) {
  img[EE_OFF_MAGIC] = EE_MAGIC0;
  img[EE_OFF_MAGIC + 1] = EE_MAGIC1;
  img[EE_OFF_VERSION] = EE_VERSION;
  put32(img + EE_OFF_FREQ, s.freq);
  img[EE_OFF_BAND] = s.band;
  img[EE_OFF_STEP] = s.step_idx;
  img[EE_OFF_MODE] = s.mode;
  img[EE_OFF_CLK_EN] = s.clk_en;
  img[EE_OFF_INJ] = s.injection;
  img[EE_OFF_IQ] = s.iq_order;
  img[EE_OFF_LIMIT] = s.limit;
  img[EE_OFF_FOVR] = s.filter_override;
  put32(img + EE_OFF_IF, s.if_freq);
  img[EE_OFF_DRIVE] = (s.drive[0] & 3) | ((s.drive[1] & 3) << 2) | ((s.drive[2] & 3) << 4);
  put32(img + EE_OFF_CAL, (uint32_t)s.cal_ppb);
  for (uint8_t i = 0; i < NUM_BANDS; i++) put32(img + EE_OFF_BAND_LAST + 4 * i, s.band_last[i]);
  for (uint8_t i = 0; i < NUM_MEMORIES; i++) {
    put32(img + EE_OFF_MEM + 5 * i, s.mem[i].freq);
    img[EE_OFF_MEM + 5 * i + 4] = s.mem[i].info;
  }
  img[EE_OFF_CRC] = crc8(img, EE_OFF_CRC);
}

bool ee_unpack(const uint8_t *img, VfoState &s) {
  if (img[EE_OFF_MAGIC] != EE_MAGIC0 || img[EE_OFF_MAGIC + 1] != EE_MAGIC1) return false;
  if (img[EE_OFF_VERSION] != EE_VERSION) return false;
  if (crc8(img, EE_OFF_CRC) != img[EE_OFF_CRC]) return false;

  VfoState d;            // defaults, used for any out-of-range field
  state_defaults(d);
  s = d;
  uint32_t f = get32(img + EE_OFF_FREQ);
  if (f >= FREQ_MIN_HZ && f <= FREQ_MAX_HZ) s.freq = f;
  if (img[EE_OFF_BAND] < NUM_BANDS) s.band = img[EE_OFF_BAND];
  if (img[EE_OFF_STEP] < NUM_STEPS) s.step_idx = img[EE_OFF_STEP];
  if (img[EE_OFF_MODE] < MODE_COUNT) s.mode = img[EE_OFF_MODE];
  s.clk_en = img[EE_OFF_CLK_EN] & 0x07;
  s.injection = img[EE_OFF_INJ] ? INJ_LOW : INJ_HIGH;
  s.iq_order = img[EE_OFF_IQ] ? 1 : 0;
  s.limit = img[EE_OFF_LIMIT] ? LIMIT_HAM : LIMIT_WIDE;
  s.filter_override = img[EE_OFF_FOVR] & 0x07;
  f = get32(img + EE_OFF_IF);
  if (f <= FREQ_MAX_HZ) s.if_freq = f;
  for (uint8_t i = 0; i < NUM_CLOCKS; i++) s.drive[i] = (img[EE_OFF_DRIVE] >> (2 * i)) & 3;
  s.cal_ppb = (int32_t)get32(img + EE_OFF_CAL);
  for (uint8_t i = 0; i < NUM_BANDS; i++) {
    f = get32(img + EE_OFF_BAND_LAST + 4 * i);
    if (f >= FREQ_MIN_HZ && f <= FREQ_MAX_HZ) s.band_last[i] = f;
  }
  for (uint8_t i = 0; i < NUM_MEMORIES; i++) {
    s.mem[i].freq = get32(img + EE_OFF_MEM + 5 * i);
    s.mem[i].info = img[EE_OFF_MEM + 5 * i + 4];
  }
  return true;
}

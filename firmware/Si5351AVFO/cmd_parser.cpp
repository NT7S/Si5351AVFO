#include "cmd_parser.h"

// Indexed by CmdId (1..CMD_COUNT-1). "M?" is stored as "M" + query.
static const char *const NAMES[CMD_COUNT] = {
  "", "F", "STEP", "BAND",
  "MODE", "ON", "OFF", "DRIVE", "IF", "INJ", "IQ",
  "LIMIT", "FOVR",
  "MS", "MR", "MC", "M",
  "CAL",
  "SAVE", "DEFAULTS", "STATUS", "VER", "HELP", "AUTO",
};

const char *cmd_name(uint8_t id) { return (id > 0 && id < CMD_COUNT) ? NAMES[id] : nullptr; }

static bool streq(const char *a, const char *b) {
  while (*a && *a == *b) { a++; b++; }
  return *a == *b;
}

static char *skip_space(char *p) { while (*p == ' ' || *p == '\t') p++; return p; }

uint8_t cmd_parse(char *line, Cmd &c) {
  c.id = CMD_NONE; c.query = false; c.extra = false; c.argc = 0;
  for (char *p = line; *p; p++) if (*p >= 'a' && *p <= 'z') *p -= 32;

  char *p = skip_space(line);
  if (!*p) return c.id;
  char *verb = p;
  while (*p && *p != ' ' && *p != '\t') p++;
  if (*p) *p++ = 0;
  // Trailing '?' on the verb marks a query ("F?", "M?").
  char *e = verb; while (*e) e++;
  if (e > verb && e[-1] == '?') { c.query = true; *--e = 0; }

  for (;;) {
    p = skip_space(p);
    if (!*p) break;
    if (c.argc == CMD_MAX_ARGS) { c.extra = true; break; }   // too many args
    c.argv[c.argc++] = p;
    while (*p && *p != ' ' && *p != '\t') p++;
    if (*p) *p++ = 0;
  }

  // "F ?" (query mark as the only argument) is the same as "F?".
  if (!c.query && c.argc == 1 && c.argv[0][0] == '?' && !c.argv[0][1]) { c.query = true; c.argc = 0; }

  c.id = CMD_UNKNOWN;
  for (uint8_t i = 1; i < CMD_COUNT; i++)
    if (streq(verb, NAMES[i])) { c.id = i; break; }
  // A bare "M" is only valid as the "M?" list query.
  if (c.id == CMD_MLIST && !c.query) c.id = CMD_UNKNOWN;
  return c.id;
}

bool arg_u32(const char *s, uint32_t &v) {
  if (!s || !*s) return false;
  uint32_t r = 0;
  for (; *s; s++) {
    if (*s < '0' || *s > '9') return false;
    uint8_t d = *s - '0';
    if (r > (0xFFFFFFFFUL - d) / 10) return false;
    r = r * 10 + d;
  }
  v = r;
  return true;
}

bool arg_i32(const char *s, int32_t &v) {
  if (!s) return false;
  bool neg = (*s == '-');
  if (*s == '-' || *s == '+') s++;
  uint32_t u;
  if (!arg_u32(s, u) || u > 0x7FFFFFFFUL) return false;
  v = neg ? -(int32_t)u : (int32_t)u;
  return true;
}

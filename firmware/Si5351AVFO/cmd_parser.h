// cmd_parser.h - USB serial command line parser (REQUIREMENTS §9). Pure C++.
// Splits a line into a command id and up to two arguments. serialcmd.cpp
// executes the command against the running VFO.
#pragma once
#include <stdint.h>

enum CmdId : uint8_t {
  CMD_NONE = 0,   // empty line
  CMD_F, CMD_STEP, CMD_BAND,
  CMD_MODE, CMD_ON, CMD_OFF, CMD_DRIVE, CMD_IF, CMD_INJ, CMD_IQ,
  CMD_LIMIT, CMD_FOVR,
  CMD_MS, CMD_MR, CMD_MC, CMD_MLIST,
  CMD_CAL,
  CMD_SAVE, CMD_DEFAULTS, CMD_STATUS, CMD_VER, CMD_HELP, CMD_AUTO, CMD_RESET,
  CMD_COUNT,
  CMD_UNKNOWN = 0xFF
};

#define CMD_MAX_LINE 32   // longer lines are rejected with "ERR LONG"
#define CMD_MAX_ARGS 2

struct Cmd {
  uint8_t id;              // CmdId
  bool    query;           // "F?" or "F ?"
  bool    extra;           // more than CMD_MAX_ARGS arguments (reply ERR ARG)
  uint8_t argc;
  const char *argv[CMD_MAX_ARGS];   // point into the (modified) line buffer
};

// Parse `line` in place (it is upper-cased and split with NULs).
// Returns the command id (also stored in c.id).
uint8_t cmd_parse(char *line, Cmd &c);

// String equality (shared with serialcmd.cpp).
bool cmd_streq(const char *a, const char *b);

// Name of a command for HELP, or nullptr.
const char *cmd_name(uint8_t id);

// Argument helpers. Return false on bad syntax or overflow.
bool arg_u32(const char *s, uint32_t &v);
bool arg_i32(const char *s, int32_t &v);

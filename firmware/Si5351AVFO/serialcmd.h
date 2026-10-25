// serialcmd.h - USB serial command interface (REQUIREMENTS §9).
#pragma once
void serialcmd_begin();
void serialcmd_poll();     // call from loop(): read chars, execute complete lines

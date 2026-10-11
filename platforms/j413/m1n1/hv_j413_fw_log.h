/* SPDX-License-Identifier: MIT */
#ifndef HV_J413_FW_LOG_H
#define HV_J413_FW_LOG_H
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#define HV_J413_GOP_TAKEOVER "J413_GOP_CONSOLE_TAKEOVER"
struct hv_j413_fw_log { char line[256]; size_t length; bool taken; };
typedef void (*hv_j413_fw_line_fn)(const char *, bool, void *);
static inline void hv_j413_fw_log_feed(struct hv_j413_fw_log *log, unsigned char c,
                                      hv_j413_fw_line_fn emit, void *opaque)
{
    if (c == '\r') return;
    if (c != '\n' && (c < 0x20 || c > 0x7e)) c = '?';
    if (c != '\n') log->line[log->length++] = (char)c;
    if (c == '\n' || log->length == sizeof(log->line) - 1) {
        log->line[log->length] = 0;
        if (!strcmp(log->line, HV_J413_GOP_TAKEOVER)) log->taken = true;
        emit(log->line, log->taken, opaque);
        log->length = 0;
    }
}
#endif

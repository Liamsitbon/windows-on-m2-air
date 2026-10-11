/* SPDX-License-Identifier: MIT
 * Adapted from Apple RTKit IPC library, Copyright (C) The Asahi Linux Contributors.
 */
#ifndef APPLE_RTKIT_MANAGEMENT_H
#define APPLE_RTKIT_MANAGEMENT_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define RTKIT_MAX_REPLIES 7
struct rtkit_message { uint8_t endpoint; uint64_t word; };
struct rtkit_management {
    uint32_t endpoints[8];
    uint16_t version, iop_power, ap_power;
    bool hello, epmap_complete, crashed;
};
struct rtkit_plan {
    struct rtkit_management next;
    struct rtkit_message replies[RTKIT_MAX_REPLIES];
    size_t count;
};
enum rtkit_status {
    RTKIT_OK, RTKIT_INVALID, RTKIT_NOT_MANAGEMENT, RTKIT_UNKNOWN_MESSAGE,
    RTKIT_VERSION_MISMATCH, RTKIT_SEQUENCE_ERROR, RTKIT_NOT_READY
};

/* Pure message planning: no MMIO, DMA, allocation, locks or blocking waits.
 * The caller serializes input and must commit next ONLY after all replies have
 * been accepted by its transport. A partial send failure requires recovery,
 * not blind replay. Initialize/reset state only while the coprocessor is reset.
 * Input state and output plan must not overlap. */
enum rtkit_status rtkit_plan_management(const struct rtkit_management *state,
                                       struct rtkit_message message,
                                       struct rtkit_plan *plan);
bool rtkit_has_endpoint(const struct rtkit_management *state, uint8_t endpoint);
bool rtkit_management_running(const struct rtkit_management *state);
enum rtkit_status rtkit_plan_start_endpoint(const struct rtkit_management *state,
                                           uint8_t endpoint, struct rtkit_plan *plan);
#endif

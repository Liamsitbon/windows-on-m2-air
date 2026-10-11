/* SPDX-License-Identifier: MIT
 * Adapted from drivers/soc/apple/rtkit.c in Asahi Linux:
 * Copyright (C) The Asahi Linux Contributors
 * See ../README.md for the pinned source, selected license and adapter contract.
 */
#include "rtkit_management.h"

enum { HELLO = 1, HELLO_REPLY = 2, START_EP = 5, IOP_ACK = 7,
       EPMAP = 8, AP_ACK = 11, MIN_VERSION = 11, MAX_VERSION = 12 };

static uint64_t management_word(unsigned type, uint64_t payload)
{
    return ((uint64_t)type << 52) | payload;
}

static void begin_plan(const struct rtkit_management *state, struct rtkit_plan *plan)
{
    struct rtkit_plan empty = {0};
    *plan = empty;
    plan->next = *state;
}

static void append(struct rtkit_plan *plan, uint64_t word)
{
    plan->replies[plan->count].endpoint = 0;
    plan->replies[plan->count++].word = word;
}

bool rtkit_has_endpoint(const struct rtkit_management *state, uint8_t endpoint)
{
    return state && (state->endpoints[endpoint / 32] & (UINT32_C(1) << (endpoint % 32)));
}

bool rtkit_management_running(const struct rtkit_management *state)
{
    return state && state->hello && state->epmap_complete && !state->crashed &&
           (state->iop_power & 0xff) == 0x20 && (state->ap_power & 0xff) == 0x20;
}

enum rtkit_status rtkit_plan_management(const struct rtkit_management *state,
                                       struct rtkit_message message,
                                       struct rtkit_plan *plan)
{
    if (!state || !plan)
        return RTKIT_INVALID;
    begin_plan(state, plan);
    if (message.endpoint != 0)
        return RTKIT_NOT_MANAGEMENT;
    if (state->crashed)
        return RTKIT_NOT_READY;
    unsigned type = (unsigned)((message.word >> 52) & 0xff);
    uint64_t payload = message.word;
    switch (type) {
    case HELLO: {
        unsigned minimum = (unsigned)(payload & 0xffff);
        unsigned maximum = (unsigned)((payload >> 16) & 0xffff);
        if (minimum > maximum)
            return RTKIT_INVALID;
        if (minimum > MAX_VERSION || maximum < MIN_VERSION)
            return RTKIT_VERSION_MISMATCH;
        if (state->hello)
            return RTKIT_SEQUENCE_ERROR;
        unsigned version = maximum < MAX_VERSION ? maximum : MAX_VERSION;
        plan->next.version = (uint16_t)version;
        plan->next.hello = true;
        append(plan, management_word(HELLO_REPLY, version | ((uint64_t)version << 16)));
        return RTKIT_OK;
    }
    case EPMAP: {
        if (!state->hello || state->epmap_complete)
            return RTKIT_SEQUENCE_ERROR;
        unsigned base = (unsigned)((payload >> 32) & 7);
        bool last = (payload & (UINT64_C(1) << 51)) != 0;
        plan->next.endpoints[base] |= (uint32_t)payload;
        append(plan, management_word(EPMAP, ((uint64_t)base << 32) |
                                     (last ? UINT64_C(1) << 51 : UINT64_C(1))));
        if (last) {
            /* Asahi starts these advertised system endpoints before boot can
             * complete. Their buffer/log handlers remain the adapter's job. */
            static const uint8_t system_endpoints[] = {1, 2, 3, 4, 8, 10};
            for (size_t i = 0; i < sizeof(system_endpoints); ++i) {
                uint8_t ep = system_endpoints[i];
                if (rtkit_has_endpoint(&plan->next, ep))
                    append(plan, management_word(START_EP, ((uint64_t)ep << 32) | 2));
            }
            plan->next.epmap_complete = true;
        }
        return RTKIT_OK;
    }
    case IOP_ACK:
        plan->next.iop_power = (uint16_t)payload;
        return RTKIT_OK;
    case AP_ACK:
        plan->next.ap_power = (uint16_t)payload;
        return RTKIT_OK;
    default:
        return RTKIT_UNKNOWN_MESSAGE;
    }
}

enum rtkit_status rtkit_plan_start_endpoint(const struct rtkit_management *state,
                                           uint8_t endpoint, struct rtkit_plan *plan)
{
    if (!state || !plan)
        return RTKIT_INVALID;
    begin_plan(state, plan);
    if (!rtkit_has_endpoint(state, endpoint))
        return RTKIT_INVALID;
    if (!state->hello || !state->epmap_complete || state->crashed ||
        (endpoint >= 32 && !rtkit_management_running(state)))
        return RTKIT_NOT_READY;
    /* Endpoint 0 is already started, never start management recursively. */
    if (!endpoint)
        return RTKIT_INVALID;
    append(plan, management_word(START_EP, ((uint64_t)endpoint << 32) | 2));
    return RTKIT_OK;
}

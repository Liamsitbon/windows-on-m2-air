/* SPDX-License-Identifier: MIT */
#include "hid_stream.h"
enum dchid_status dchid_stream_reset(struct dchid_stream *s, uint8_t *buffer, size_t capacity)
{
    if (!s || !buffer || capacity < 20) return DCHID_INVALID;
    s->buffer = buffer; s->capacity = capacity; s->used = 0; s->expected = 8; s->fault = DCHID_OK;
    return DCHID_OK;
}
enum dchid_status dchid_stream_feed(struct dchid_stream *s, const uint8_t *data,
                                    size_t size, size_t *consumed, struct dchid_packet *view)
{
    if (!consumed || !view) return DCHID_INVALID;
    *consumed = 0; struct dchid_packet empty = {0}; *view = empty;
    if (!s || !s->buffer || (!data && size) || s->expected < 8 ||
        s->expected > s->capacity || s->used > s->expected) return DCHID_INVALID;
    if (s->fault != DCHID_OK) return s->fault;
    for (;;) {
        while (s->used < s->expected && *consumed < size)
            s->buffer[s->used++] = data[(*consumed)++];
        if (s->used < s->expected) return DCHID_INCOMPLETE;
        if (s->expected == 8) {
            const uint8_t *h = s->buffer;
            size_t body = h[2] | (size_t)h[3] << 8;
            if (h[0] != 8 || h[5] >= 16 || body < 8 || body % 4 ||
                (h[1] != DCHID_COMMAND_CHANNEL && h[1] != DCHID_REPORT_CHANNEL))
                return s->fault = DCHID_BAD_HEADER;
            if (body + 12 > s->capacity) return s->fault = DCHID_NO_SPACE;
            s->expected = body + 12;
            continue;
        }
        enum dchid_status status = dchid_parse_packet(s->buffer, s->used, view);
        if (status != DCHID_OK) s->fault = status;
        return status;
    }
}

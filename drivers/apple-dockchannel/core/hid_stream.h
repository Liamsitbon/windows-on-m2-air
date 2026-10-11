/* SPDX-License-Identifier: MIT */
#ifndef APPLE_DCHID_STREAM_H
#define APPLE_DCHID_STREAM_H
#include "hid_packet.h"
struct dchid_stream { uint8_t *buffer; size_t capacity, used, expected; enum dchid_status fault; };
/* Serialize calls. Caller owns disjoint storage and input. Complete-frame views
 * survive until reset. A malformed frame latches a fault: never scan arbitrary
 * payload bytes for a new header. Reset only after transport recovery/discard. */
enum dchid_status dchid_stream_reset(struct dchid_stream *s, uint8_t *buffer, size_t capacity);
enum dchid_status dchid_stream_feed(struct dchid_stream *s, const uint8_t *data,
                                    size_t size, size_t *consumed, struct dchid_packet *view);
#endif

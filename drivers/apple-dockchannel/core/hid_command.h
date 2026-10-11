/* SPDX-License-Identifier: MIT
 * Protocol adaptation: Copyright The Asahi Linux Contributors
 */
#ifndef APPLE_DCHID_COMMAND_H
#define APPLE_DCHID_COMMAND_H
#include "hid_packet.h"
struct dchid_command {
    uint8_t next_sequence, sequence, interface_id, flags, report_id, active;
};
enum dchid_reply_status { DCHID_REPLY_OK, DCHID_REPLY_INVALID,
    DCHID_REPLY_UNEXPECTED, DCHID_REPLY_REMOTE_ERROR, DCHID_REPLY_NO_SPACE };
/* Zero-initialize once while the transport is quiescent. Serialize all calls
 * and RX; begin sets active before the adapter transmits. On any TX failure,
 * timeout or cancellation, cancel once and recover a partially sent frame.
 * No send, polling, allocation or implicit retry. Disjoint buffers required. */
enum dchid_status dchid_command_begin(struct dchid_command *command,
    uint8_t interface_id, uint8_t flags, const uint8_t *payload, size_t size,
    uint8_t *wire, size_t capacity, size_t *written);
/* Input must be a view from successful dchid_parse_packet. Response excludes
 * report ID. Exact length and remote code are returned; insufficient capacity
 * preserves the outstanding command and writes no response bytes. */
enum dchid_reply_status dchid_command_complete(struct dchid_command *command,
    const struct dchid_packet *packet, uint8_t *response, size_t capacity,
    size_t *response_size, uint32_t *return_code);
void dchid_command_cancel(struct dchid_command *command);
#endif

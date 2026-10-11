/* SPDX-License-Identifier: MIT
 * Protocol adaptation: Copyright The Asahi Linux Contributors
 * Pinned source and license selection: ../README.md.
 */
#include "hid_command.h"
void dchid_command_cancel(struct dchid_command *command)
{
    if (command && command->active) {
        command->active = 0;
        command->next_sequence = (uint8_t)(command->sequence + 1);
    }
}
enum dchid_status dchid_command_begin(struct dchid_command *command,
    uint8_t interface_id, uint8_t flags, const uint8_t *payload, size_t size,
    uint8_t *wire, size_t capacity, size_t *written)
{
    if (!written) return DCHID_INVALID;
    *written = 0;
    /* HID_INPUT_REPORT=1 (GET only), OUTPUT=2, FEATURE=3; SET=0, GET=1. */
    if (!command || command->active || !payload || !size ||
        (flags >> 6) == 0 || (flags & 0x3f) > 1 ||
        ((flags >> 6) == 1 && (flags & 0x3f) != 1))
        return DCHID_INVALID;
    enum dchid_status status = dchid_encode_command(interface_id, command->next_sequence,
        flags, payload, size, wire, capacity, written);
    if (status != DCHID_OK) return status;
    command->sequence = command->next_sequence;
    command->interface_id = interface_id;
    command->flags = flags;
    command->report_id = payload[0];
    command->active = 1;
    return DCHID_OK;
}
enum dchid_reply_status dchid_command_complete(struct dchid_command *command,
    const struct dchid_packet *packet, uint8_t *response, size_t capacity,
    size_t *response_size, uint32_t *return_code)
{
    if (!response_size || !return_code) return DCHID_REPLY_INVALID;
    *response_size = 0; *return_code = 0;
    if (!command || !packet || !packet->payload || !packet->payload_size ||
        (!response && capacity)) return DCHID_REPLY_INVALID;
    if (!command->active || packet->channel != DCHID_COMMAND_CHANNEL ||
        packet->interface_id != command->interface_id || packet->sequence != command->sequence ||
        packet->flags != command->flags || packet->payload[0] != command->report_id)
        return DCHID_REPLY_UNEXPECTED;
    *return_code = packet->return_code;
    *response_size = packet->payload_size - 1;
    if (packet->return_code) {
        dchid_command_cancel(command);
        return DCHID_REPLY_REMOTE_ERROR;
    }
    if (*response_size > capacity) return DCHID_REPLY_NO_SPACE;
    for (size_t i = 0; i < *response_size; ++i) response[i] = packet->payload[i + 1];
    dchid_command_cancel(command);
    return DCHID_REPLY_OK;
}

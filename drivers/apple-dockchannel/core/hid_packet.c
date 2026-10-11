/* SPDX-License-Identifier: MIT
 * Protocol adaptation from Asahi Linux dockchannel-hid.c:
 * Copyright The Asahi Linux Contributors
 * See ../README.md for pinned source, MIT license and Windows adapter limits.
 */
#include "hid_packet.h"

static uint16_t read16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | (uint16_t)p[1] << 8);
}
static uint32_t read32(const uint8_t *p)
{
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
           (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}
static void write16(uint8_t *p, uint16_t value)
{
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8);
}
static void write32(uint8_t *p, uint32_t value)
{
    for (unsigned i = 0; i < 4; ++i)
        p[i] = (uint8_t)(value >> (8 * i));
}
static uint32_t checksum(const uint8_t *p, size_t length)
{
    uint32_t sum = 0;
    for (size_t i = 0; i < length; i += 4)
        sum += read32(p + i);
    return sum;
}

enum dchid_status dchid_parse_packet(const uint8_t *bytes, size_t available,
                                     struct dchid_packet *view)
{
    if (!view)
        return DCHID_INVALID;
    struct dchid_packet empty = {0};
    *view = empty;
    if (!bytes)
        return DCHID_INVALID;
    if (available < 8)
        return DCHID_INCOMPLETE;
    if (bytes[0] != 8 || bytes[5] >= 16 ||
        (bytes[1] != DCHID_COMMAND_CHANNEL && bytes[1] != DCHID_REPORT_CHANNEL))
        return DCHID_BAD_HEADER;
    size_t body_size = read16(bytes + 2);
    if (body_size < 8 || body_size % 4)
        return DCHID_BAD_HEADER;
    size_t packet_size = body_size + 12;
    if (available < packet_size)
        return DCHID_INCOMPLETE;
    if (checksum(bytes, packet_size) != UINT32_MAX)
        return DCHID_BAD_CHECKSUM;
    size_t payload_size = read16(bytes + 10);
    if (payload_size > body_size - 8)
        return DCHID_BAD_HEADER;
    view->payload = bytes + 16;
    view->payload_size = payload_size;
    view->consumed = packet_size;
    view->return_code = read32(bytes + 12);
    view->channel = bytes[1];
    view->sequence = bytes[4];
    view->interface_id = bytes[5];
    view->flags = bytes[8];
    return DCHID_OK;
}

enum dchid_status dchid_encode_command(uint8_t interface_id, uint8_t sequence,
                                       uint8_t flags, const uint8_t *payload,
                                       size_t payload_size, uint8_t *output,
                                       size_t capacity, size_t *written)
{
    if (!written)
        return DCHID_INVALID;
    *written = 0;
    if (!output || (!payload && payload_size) || interface_id >= 16 ||
        payload_size > DCHID_MAX_PAYLOAD)
        return DCHID_INVALID;
    size_t padded = (payload_size + 3) & ~(size_t)3;
    size_t total = padded + 20;
    if (capacity < total)
        return DCHID_NO_SPACE;
    for (size_t i = 0; i < total; ++i)
        output[i] = 0;
    output[0] = 8;
    output[1] = DCHID_COMMAND_CHANNEL;
    write16(output + 2, (uint16_t)(padded + 8));
    output[4] = sequence;
    output[5] = interface_id;
    output[8] = flags;
    write16(output + 10, (uint16_t)payload_size);
    for (size_t i = 0; i < payload_size; ++i)
        output[16 + i] = payload[i];
    write32(output + total - 4, UINT32_MAX - checksum(output, total - 4));
    *written = total;
    return DCHID_OK;
}

/* SPDX-License-Identifier: MIT
 * Protocol adaptation: Copyright The Asahi Linux Contributors
 * Source/license review: ../README.md. No Linux scheduling or allocation.
 */
#include "hid_discovery.h"
static uint16_t le16(const uint8_t *p) { return (uint16_t)(p[0] | (uint16_t)p[1] << 8); }
static int copy_name(char *out, const uint8_t *in, size_t limit)
{
    size_t i = 0;
    while (i < limit && in[i]) { out[i] = (char)in[i]; ++i; }
    out[i] = 0;
    return i != 0; /* Fixed-width upstream names may occupy the entire field. */
}
enum dchid_status dchid_parse_discovery(const uint8_t *data, size_t size,
                                        struct dchid_discovery *output)
{
    if (!output) return DCHID_INVALID;
    struct dchid_discovery next = {0};
    *output = next;
    if (!data) return DCHID_INVALID;
    if (size < 22) return DCHID_INCOMPLETE;
    if (data[0] != 0xf0 || data[3] >= 16 || data[20] > 1 ||
        !copy_name(next.name, data + 4, 16)) return DCHID_BAD_HEADER;
    next.interface_id = data[3]; next.more_packets = data[20];
    size_t offset = 22;
    int have_gpio = 0, have_product = 0, have_descriptor = 0;
    while (offset < size) {
        if (size - offset < 4) return DCHID_BAD_HEADER;
        uint16_t type = le16(data + offset), length = le16(data + offset + 2);
        offset += 4;
        if (length > size - offset) return DCHID_BAD_HEADER;
        const uint8_t *block = data + offset;
        switch (type) {
        case 0:
            if (have_descriptor || !length) return DCHID_BAD_HEADER;
            have_descriptor = 1;
            next.descriptor = block; next.descriptor_size = length;
            break;
        case 1:
            if (have_gpio || length < 36 || !copy_name(next.gpio_name, block + 4, 32))
                return DCHID_BAD_HEADER;
            have_gpio = 1; next.gpio_id = le16(block + 2);
            break;
        case 2:
            /* Upstream stops at this block; do not interpret any trailing bytes. */
            *output = next; return DCHID_OK;
        case 7:
            if (have_product || !length || block[length - 1]) return DCHID_BAD_HEADER;
            have_product = 1; next.product = block; next.product_size = length;
            break;
        default: break;
        }
        offset += length;
    }
    *output = next;
    return DCHID_OK;
}

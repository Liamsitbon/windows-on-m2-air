/* SPDX-License-Identifier: MIT
 * Protocol adaptation: Copyright The Asahi Linux Contributors
 */
#ifndef APPLE_DCHID_DISCOVERY_H
#define APPLE_DCHID_DISCOVERY_H
#include "hid_packet.h"
struct dchid_discovery {
    uint8_t interface_id, more_packets;
    char name[17], gpio_name[33];
    uint16_t gpio_id;
    const uint8_t *descriptor, *product;
    size_t descriptor_size, product_size;
};
/* Parse one INIT event payload, not an outer transport frame. Borrowed views
 * remain valid only while the immutable input snapshot lives. No device state
 * is modified; caller must accumulate multi-packet discovery separately.
 * Output must not overlap input. Unknown blocks are skipped by their length. */
enum dchid_status dchid_parse_discovery(const uint8_t *data, size_t size,
                                        struct dchid_discovery *output);
#endif

/* SPDX-License-Identifier: MIT
 * Protocol adaptation: Copyright The Asahi Linux Contributors
 */
#ifndef APPLE_DCHID_FIRMWARE_H
#define APPLE_DCHID_FIRMWARE_H
#include "hid_packet.h"
/* Validate an HIDF v1 archive, copy its declared data into disjoint caller
 * storage, and patch the interface byte only at a nonzero declared offset.
 * Invalid/no-space calls write no output and set written=0. Not signature or
 * device-compatibility verification; does not allocate/map/send firmware. */
enum dchid_status dchid_prepare_firmware(const uint8_t *archive, size_t size,
    uint8_t interface_id, uint8_t *output, size_t capacity, size_t *written);
#endif

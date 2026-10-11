/* SPDX-License-Identifier: MIT
 * Protocol adaptation: Copyright The Asahi Linux Contributors
 * Pinned source and license selection: ../README.md.
 */
#include "hid_firmware.h"
static uint32_t le32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1]<<8 | (uint32_t)p[2]<<16 | (uint32_t)p[3]<<24;
}
enum dchid_status dchid_prepare_firmware(const uint8_t *archive, size_t size,
    uint8_t interface_id, uint8_t *output, size_t capacity, size_t *written)
{
    if (!written) return DCHID_INVALID;
    *written = 0;
    if (!archive || !output || interface_id >= 16) return DCHID_INVALID;
    if (size < 20) return DCHID_INCOMPLETE;
    uint32_t header = le32(archive + 8), length = le32(archive + 12), offset = le32(archive + 16);
    if (le32(archive) != UINT32_C(0x46444948) || le32(archive + 4) != 1 ||
        header < 20 || header > size || length > size - header || offset >= length)
        return DCHID_BAD_HEADER;
    if (length > capacity) return DCHID_NO_SPACE;
    for (size_t i = 0; i < length; ++i) output[i] = archive[header + i];
    if (offset) output[offset] = interface_id;
    *written = length;
    return DCHID_OK;
}

/* SPDX-License-Identifier: MIT
 * Original portable implementation of the inspected DockChannel FIFO contract.
 * See documentation/reverse-engineering/DOCKCHANNEL.md for sources and limits.
 */
#include "dockchannel.h"

enum { TX8 = 0x04, TX32 = 0x10, TX_FREE = 0x14,
       RX8 = 0x1c, RX32 = 0x28, RX_COUNT = 0x2c };

static struct dc_result result(enum dc_status status, size_t transferred)
{
    struct dc_result r = {status, transferred};
    return r;
}

static size_t transfer_size(size_t count, size_t budget, uint32_t capacity)
{
    size_t n = count < budget ? count : budget;
    return n < capacity ? n : capacity;
}

static struct dc_result completed(size_t transferred, size_t requested)
{
    return result(transferred == requested ? DC_COMPLETE :
                  transferred ? DC_PARTIAL : DC_WOULD_BLOCK, transferred);
}

struct dc_result dc_try_send(const struct dc_io *io, const uint8_t *buffer,
                             size_t count, size_t budget)
{
    if (!count)
        return result(DC_COMPLETE, 0);
    if (!io || !buffer || !io->read32 || !io->write32 || !io->write8 || !io->fifo_size)
        return result(DC_INVALID, 0);
    if (!budget)
        return result(DC_WOULD_BLOCK, 0);
    uint32_t capacity = io->read32(io->context, TX_FREE);
    if (capacity > io->fifo_size)
        return result(DC_BAD_CAPACITY, 0);
    size_t n = transfer_size(count, budget, capacity), pos = 0;
    for (; n - pos >= 4; pos += 4) {
        uint32_t word = (uint32_t)buffer[pos] | ((uint32_t)buffer[pos+1] << 8) |
                        ((uint32_t)buffer[pos+2] << 16) | ((uint32_t)buffer[pos+3] << 24);
        io->write32(io->context, TX32, word);
    }
    for (; pos < n; ++pos)
        io->write8(io->context, TX8, buffer[pos]);
    return completed(n, count);
}

struct dc_result dc_try_receive(const struct dc_io *io, uint8_t *buffer,
                                size_t count, size_t budget)
{
    if (!count)
        return result(DC_COMPLETE, 0);
    if (!io || !buffer || !io->read32 || !io->fifo_size)
        return result(DC_INVALID, 0);
    if (!budget)
        return result(DC_WOULD_BLOCK, 0);
    uint32_t capacity = io->read32(io->context, RX_COUNT);
    if (capacity > io->fifo_size)
        return result(DC_BAD_CAPACITY, 0);
    size_t n = transfer_size(count, budget, capacity), pos = 0;
    for (; n - pos >= 4; pos += 4) {
        uint32_t word = io->read32(io->context, RX32);
        for (size_t byte = 0; byte < 4; ++byte)
            buffer[pos+byte] = (uint8_t)(word >> (8*byte));
    }
    for (; pos < n; ++pos)
        buffer[pos] = (uint8_t)(io->read32(io->context, RX8) >> 8);
    return completed(n, count);
}

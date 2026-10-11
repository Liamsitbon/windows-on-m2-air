/* SPDX-License-Identifier: MIT */
#include "hv_j413_boot_data.h"

int hv_j413_cpu_index(uint32_t adt_reg)
{
    if (adt_reg < 4)
        return (int)adt_reg;
    if (adt_reg >= 0x100 && adt_reg <= 0x103)
        return (int)(adt_reg - 0x100 + 4);
    return -1;
}

static bool next(uint64_t base, uint64_t size, uint64_t *out)
{
    if (size > UINT64_MAX - base)
        return false;
    uint64_t end = base + size;
    if (end > UINT64_MAX - (HV_ASSISTED_ALIGNMENT - 1))
        return false;
    *out = (end + HV_ASSISTED_ALIGNMENT - 1) & ~(HV_ASSISTED_ALIGNMENT - 1);
    return true;
}

bool hv_j413_range_inside(uint64_t base, uint64_t size,
                          uint64_t start, uint64_t end)
{
    return start <= end && base >= start && base <= end && size <= end - base;
}

bool hv_j413_ranges_disjoint(uint64_t a, uint64_t a_size,
                             uint64_t b, uint64_t b_size)
{
    if (a_size > UINT64_MAX - a || b_size > UINT64_MAX - b)
        return false;
    return !a_size || !b_size || a + a_size <= b || b + b_size <= a;
}

bool hv_j413_boot_data_plan(const struct hv_j413_boot_slots *s,
                           uint64_t adt, uint64_t tc, uint64_t fw,
                           uint64_t sep, uint64_t log,
                           struct hv_assisted_layout *out)
{
    struct hv_assisted_layout p = {0};
    uint64_t end;
    if (!s || !out || !adt || !fw || adt > s->adt_max || fw > s->firmware_max ||
        s->adt >= s->firmware || s->firmware >= s->boot_args ||
        s->boot_args >= s->data_limit ||
        ((s->adt | s->firmware | s->boot_args) & (HV_ASSISTED_ALIGNMENT - 1)))
        return false;
    p.adt_base = s->adt;
    p.firmware_base = s->firmware;
    p.boot_args_base = s->boot_args;
    if (!next(s->adt, adt, &p.trust_cache_base) ||
        !next(p.trust_cache_base, tc, &end) || end > s->firmware ||
        /* Mu reserves PcdFdSize, even if its output file omits unused tail
         * blocks. SEP/log must start after that full reservation. */
        !next(s->firmware, s->firmware_max, &p.sepfw_base) ||
        !next(p.sepfw_base, sep, &p.preoslog_base) ||
        !next(p.preoslog_base, log, &end) || end > s->boot_args ||
        !next(s->boot_args, HV_ASSISTED_BOOTARGS_SIZE, &p.top_of_kernel_data) ||
        p.top_of_kernel_data > s->data_limit)
        return false;
    *out = p;
    return true;
}

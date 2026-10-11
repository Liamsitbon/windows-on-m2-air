/* SPDX-License-Identifier: MIT */
#ifndef HV_J413_BOOT_DATA_H
#define HV_J413_BOOT_DATA_H
#include <stdbool.h>
#include <stdint.h>
#include "hv_assisted_layout.h"

struct hv_j413_boot_slots {
    uint64_t adt, firmware, boot_args, data_limit;
    uint64_t firmware_max, adt_max;
};

/* Pure planning: output is unchanged on failure. Fixed Mu pointers are never
 * moved to accommodate larger live Apple data. All intervals are half open. */
bool hv_j413_boot_data_plan(const struct hv_j413_boot_slots *slots,
                           uint64_t adt, uint64_t tc, uint64_t firmware,
                           uint64_t sep, uint64_t log,
                           struct hv_assisted_layout *out);
bool hv_j413_range_inside(uint64_t base, uint64_t size,
                          uint64_t start, uint64_t end);
bool hv_j413_ranges_disjoint(uint64_t a, uint64_t a_size,
                             uint64_t b, uint64_t b_size);
/* Apple ADT CPU reg encodes cluster/core as 0x100..103; it is not
 * architectural MPIDR_EL1 (the P cores use 0x10100..10103 there). */
int hv_j413_cpu_index(uint32_t adt_reg);
#endif

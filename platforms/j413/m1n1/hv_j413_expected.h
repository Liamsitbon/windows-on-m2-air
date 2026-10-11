/* SPDX-License-Identifier: MIT */
#ifndef HV_J413_EXPECTED_H
#define HV_J413_EXPECTED_H
#include "hv_launch_preflight.h"
#define HV_J413_TARGET 0x3331344aU
/* A source-derived experiment contract, NOT a measured assisted-launch golden. */
bool hv_j413_expected_init(struct hv_contract_snapshot *out, uint64_t ram_end,
                          uint64_t adt_size, uint64_t firmware_size);
#endif

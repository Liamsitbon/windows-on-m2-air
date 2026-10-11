/* SPDX-License-Identifier: MIT */
#ifndef HV_AUTONOMOUS_TARGET_H
#define HV_AUTONOMOUS_TARGET_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
static inline bool hv_autonomous_target_matches(uint32_t chip, const char *target, size_t size)
{
#ifdef M1N1_J413
    const char expected[] = "J413";
    const uint32_t expected_chip = 0x8112;
#else
    const char expected[] = "J313";
    const uint32_t expected_chip = 0x8103;
#endif
    if (chip != expected_chip || !target || size != sizeof(expected))
        return false;
    for (size_t i = 0; i < sizeof(expected); i++)
        if (target[i] != expected[i])
            return false;
    return true;
}
#endif

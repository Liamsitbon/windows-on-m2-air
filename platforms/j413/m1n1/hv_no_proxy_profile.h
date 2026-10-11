/* SPDX-License-Identifier: MIT */
#ifndef HV_NO_PROXY_PROFILE_H
#define HV_NO_PROXY_PROFILE_H
#include "hv_autonomous_profile.h"

/* A local physical framebuffer is the only consumer in this image. */
static inline bool hv_no_proxy_profile_allowed(const struct hv_autonomous_profile *profile)
{
    return profile && profile->physical_display && !profile->virtual_display &&
           !profile->debug_host && !profile->monitor && !profile->telemetry &&
           !profile->proxy_takeover;
}
static inline bool hv_no_proxy_flags_allowed(uint32_t flags)
{
    struct hv_autonomous_profile profile;
    return hv_autonomous_profile_decode(flags, &profile) &&
           hv_no_proxy_profile_allowed(&profile);
}
#endif

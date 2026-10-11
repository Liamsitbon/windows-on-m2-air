/* SPDX-License-Identifier: BSD-2-Clause-Patent */
#ifndef J413_BOOT_MEMORY_H
#define J413_BOOT_MEMORY_H
#include <stdint.h>
#include <stdbool.h>

struct j413_boot_reservations {
  uint64_t before_fd_base, after_fd_base;
  uint32_t before_fd_size, after_fd_size;
};

/* FD is already split off by MemoryPeim. Reserve both adjacent boot-data
 * intervals independently, because a resource HOB cannot straddle the FD. */
static inline bool j413_boot_reservations_plan(
  uint64_t ram, uint64_t ram_size, uint64_t adt, uint64_t fd, uint64_t fd_size,
  uint64_t ba, uint64_t ba_size, uint64_t top, uint64_t limit,
  struct j413_boot_reservations *out)
{
  struct j413_boot_reservations p;
  if (!out || !ram_size || ram_size > UINT64_MAX-ram || !fd_size ||
      fd_size > UINT64_MAX-fd || !ba_size || ba_size > UINT64_MAX-ba ||
      ((adt | fd | fd_size | ba | ba_size | top | limit) & 0xfff) ||
      adt < ram || adt >= fd || fd+fd_size > ba || ba+ba_size > top ||
      top > limit || limit > ram+ram_size ||
      fd-adt > UINT32_MAX || top-(fd+fd_size) > UINT32_MAX)
    return false;
  p.before_fd_base=adt; p.before_fd_size=(uint32_t)(fd-adt);
  p.after_fd_base=fd+fd_size; p.after_fd_size=(uint32_t)(top-p.after_fd_base);
  *out=p;
  return true;
}
#endif

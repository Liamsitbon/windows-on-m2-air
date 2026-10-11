/* SPDX-License-Identifier: MIT */
#ifndef J413_USB_DART_READY_H
#define J413_USB_DART_READY_H
#include <Uefi.h>
/* Published only after both USB1 DART banks have flushed and entered bypass.
 * A firmware dependency, not an OS IOMMU protocol or general DMA permission. */
typedef struct { UINT32 ControllerMask; } J413_USB_DART_READY;
extern EFI_GUID gJ413UsbDartReadyProtocolGuid;
#endif

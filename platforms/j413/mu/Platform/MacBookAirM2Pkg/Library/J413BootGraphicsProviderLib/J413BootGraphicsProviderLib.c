/** J413 boot mark; generated in firmware, no external bitmap dependency.
 * SPDX-License-Identifier: BSD-2-Clause-Patent
 */
#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/BootGraphicsProviderLib.h>
#include <Library/DxeServicesLib.h>
#include <Library/PcdLib.h>

EFI_STATUS EFIAPI GetBootGraphic(BOOT_GRAPHIC Graphic, UINTN *ImageSize, UINT8 **ImageData)
{
  if (ImageSize == NULL || ImageData == NULL) return EFI_INVALID_PARAMETER;
  if (Graphic != BG_SYSTEM_LOGO) {
    EFI_GUID *Guid;
    if (Graphic == BG_CRITICAL_OVER_TEMP) Guid = PcdGetPtr(PcdThermalFile);
    else if (Graphic == BG_CRITICAL_LOW_BATTERY) Guid = PcdGetPtr(PcdLowBatteryFile);
    else return EFI_UNSUPPORTED;
    return GetSectionFromAnyFv(Guid, EFI_SECTION_RAW, 0, (VOID **)ImageData, ImageSize);
  }
  *ImageData = NULL; *ImageSize = 0;
  return EFI_UNSUPPORTED;
}

UINT32 EFIAPI GetBackgroundColor(VOID) { return 0; }

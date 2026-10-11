/** J413 boot mark; generated in firmware, no external bitmap dependency.
 * SPDX-License-Identifier: BSD-2-Clause-Patent
 */
#include <Uefi.h>
#include <Library/BaseMemoryLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/BootGraphicsProviderLib.h>
#include <Library/DxeServicesLib.h>
#include <Library/PcdLib.h>

STATIC VOID Put16(UINT8 *P, UINT16 V) { P[0] = (UINT8)V; P[1] = (UINT8)(V >> 8); }
STATIC VOID Put32(UINT8 *P, UINT32 V) { Put16(P, (UINT16)V); Put16(P + 2, (UINT16)(V >> 16)); }

EFI_STATUS EFIAPI GetBootGraphic(BOOT_GRAPHIC Graphic, UINTN *ImageSize, UINT8 **ImageData)
{
  UINT8 *Image;
  UINTN X, Y, Offset;
  CONST UINT32 Width = 192, Height = 192, Row = 576;
  CONST UINT32 Size = 54 + 192 * 576;
  if (ImageSize == NULL || ImageData == NULL) return EFI_INVALID_PARAMETER;
  if (Graphic != BG_SYSTEM_LOGO) {
    EFI_GUID *Guid;
    if (Graphic == BG_CRITICAL_OVER_TEMP) Guid = PcdGetPtr(PcdThermalFile);
    else if (Graphic == BG_CRITICAL_LOW_BATTERY) Guid = PcdGetPtr(PcdLowBatteryFile);
    else return EFI_UNSUPPORTED;
    return GetSectionFromAnyFv(Guid, EFI_SECTION_RAW, 0, (VOID **)ImageData, ImageSize);
  }
  Image = AllocateZeroPool(Size);
  if (Image == NULL) return EFI_OUT_OF_RESOURCES;
  Image[0] = 'B'; Image[1] = 'M'; Put32(Image + 2, Size); Put32(Image + 10, 54);
  Put32(Image + 14, 40); Put32(Image + 18, Width); Put32(Image + 22, Height);
  Put16(Image + 26, 1); Put16(Image + 28, 24); Put32(Image + 34, Row * Height);
  for (Y = 16; Y < 176; Y++) for (X = 16; X < 176; X++) {
    if ((X >= 92 && X < 100) || (Y >= 92 && Y < 100)) continue;
    Offset = 54 + (Height - 1 - Y) * Row + X * 3;
    Image[Offset] = 0xd4; Image[Offset + 1] = 0x78; Image[Offset + 2] = 0x00;
  }
  *ImageData = Image; *ImageSize = Size;
  return EFI_SUCCESS;
}

UINT32 EFIAPI GetBackgroundColor(VOID) { return 0; }

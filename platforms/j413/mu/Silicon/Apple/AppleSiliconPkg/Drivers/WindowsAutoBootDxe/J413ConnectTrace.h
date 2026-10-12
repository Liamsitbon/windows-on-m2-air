/** @file J413 console diagnostics for the UefiBootManagerLib ConnectAll algorithm.
  Derived from MdeModulePkg/Library/UefiBootManagerLib/BmConnect.c.
  Copyright (c) 2011 - 2018, Intel Corporation. All rights reserved.
  SPDX-License-Identifier: BSD-2-Clause-Patent
**/
#ifndef J413_CONNECT_TRACE_H
#define J413_CONNECT_TRACE_H
#include <Library/DxeServicesTableLib.h>

STATIC VOID J413ConnectAll(VOID)
{
  EFI_STATUS Status;
  UINTN Pass = 0;
  Print(L"UEFI CONNECT: initial consoles entered\r\n");
  EfiBootManagerConnectAllDefaultConsoles();
  Print(L"UEFI CONNECT: initial consoles returned\r\n");
  do {
    EFI_HANDLE *Handles = NULL;
    UINTN Count = 0;
    Status = gBS->LocateHandleBuffer(AllHandles, NULL, NULL, &Count, &Handles);
    Print(L"UEFI CONNECT: pass %u enumeration %r; handles %u\r\n", Pass, Status, Count);
    if (EFI_ERROR(Status)) {
      if (Handles != NULL) FreePool(Handles);
      return;
    }
    for (UINTN Index = 0; Index < Count; Index++) {
      EFI_DEVICE_PATH_PROTOCOL *Path = DevicePathFromHandle(Handles[Index]);
      CHAR16 *Text = Path == NULL ? NULL : ConvertDevicePathToText(Path, FALSE, FALSE);
      Print(L"UEFI CONNECT: pass %u controller %u/%u handle %p entered\r\n",
            Pass, Index + 1, Count, Handles[Index]);
      if (Text != NULL) {
        Print(L"UEFI CONNECT: path %s\r\n", Text);
        FreePool(Text);
      }
      Status = gBS->ConnectController(Handles[Index], NULL, NULL, TRUE);
      Print(L"UEFI CONNECT: controller %u returned %r\r\n", Index + 1, Status);
    }
    if (Handles != NULL) FreePool(Handles);
    Print(L"UEFI CONNECT: DXE dispatch entered\r\n");
    Status = gDS->Dispatch();
    Print(L"UEFI CONNECT: DXE dispatch returned %r\r\n", Status);
    Pass++;
  } while (!EFI_ERROR(Status));
  Print(L"UEFI CONNECT: final consoles entered\r\n");
  EfiBootManagerConnectAllDefaultConsoles();
  Print(L"UEFI CONNECT: final consoles returned\r\n");
}
#endif

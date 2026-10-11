/** @file Application-level J413 Setup selection. SPDX-License-Identifier: BSD-2-Clause-Patent */
#ifndef J413_WINDOWS_SETUP_H
#define J413_WINDOWS_SETUP_H
#include <Uefi.h>
#include <Library/UefiBootManagerLib.h>
extern EFI_GUID gJ413WindowsSetupProtocolGuid;
typedef EFI_STATUS (EFIAPI *J413_GET_SETUP_OPTION)(OUT EFI_BOOT_MANAGER_LOAD_OPTION *Option);
typedef struct { J413_GET_SETUP_OPTION GetOption; } J413_WINDOWS_SETUP;
#endif

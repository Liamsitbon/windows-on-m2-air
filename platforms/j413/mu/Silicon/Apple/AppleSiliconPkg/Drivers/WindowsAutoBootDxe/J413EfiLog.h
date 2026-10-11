/** @file Bounded application-level phase log. SPDX-License-Identifier: BSD-2-Clause-Patent */
#ifndef J413_EFI_LOG_H
#define J413_EFI_LOG_H
#include <Library/PrintLib.h>
#include <Library/BaseMemoryLib.h>
#define J413_LOG_CAPACITY 16384
STATIC CHAR8 mJ413Log[J413_LOG_CAPACITY];
STATIC UINTN mJ413LogUsed;

STATIC VOID J413LogStatus(CONST CHAR8 *Label, EFI_STATUS Status)
{
  UINTN Available = sizeof(mJ413Log) - mJ413LogUsed;
  UINTN Written;
  if (Available <= 1) return;
  Written = AsciiSPrint(mJ413Log + mJ413LogUsed, Available, "%a: %r\r\n", Label, Status);
  if (Written >= Available) Written = Available - 1;
  mJ413LogUsed += Written;
}

STATIC VOID J413LogCount(CONST CHAR8 *Label, UINTN Value)
{
  CHAR8 Line[96];
  AsciiSPrint(Line, sizeof(Line), "%a = %Lu", Label, (UINT64)Value);
  J413LogStatus(Line, EFI_SUCCESS);
}

STATIC BOOLEAN J413IsNvmeFs(EFI_HANDLE Handle)
{
  EFI_DEVICE_PATH_PROTOCOL *Path = DevicePathFromHandle(Handle);
  if (Path == NULL) return FALSE;
  // Device paths returned by firmware protocols must themselves be valid.
  while (!IsDevicePathEnd(Path)) {
    if (DevicePathType(Path) == MESSAGING_DEVICE_PATH &&
        DevicePathSubType(Path) == MSG_NVME_NAMESPACE_DP) return TRUE;
    Path = NextDevicePathNode(Path);
  }
  return FALSE;
}

STATIC EFI_STATUS J413SaveLog(VOID)
{
  EFI_HANDLE *Handles = NULL;
  UINTN Count = 0;
  EFI_STATUS Result = EFI_NOT_FOUND;
  EFI_STATUS Status = gBS->LocateHandleBuffer(ByProtocol, &gEfiSimpleFileSystemProtocolGuid,
                                             NULL, &Count, &Handles);
  if (EFI_ERROR(Status)) return Status;
  for (UINTN Index = 0; Index < Count; Index++) {
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *Fs = NULL;
    EFI_BLOCK_IO_PROTOCOL *BlockIo = NULL;
    EFI_FILE_PROTOCOL *Root = NULL, *Anchor = NULL, *Log = NULL;
    UINTN Bytes = sizeof(mJ413Log);
    if (!J413IsNvmeFs(Handles[Index])) continue;
    Status = gBS->HandleProtocol(Handles[Index], &gEfiBlockIoProtocolGuid, (VOID **)&BlockIo);
    if (EFI_ERROR(Status) || BlockIo == NULL || BlockIo->Media == NULL ||
        !BlockIo->Media->MediaPresent || BlockIo->Media->ReadOnly) continue;
    Status = gBS->HandleProtocol(Handles[Index], &gEfiSimpleFileSystemProtocolGuid, (VOID **)&Fs);
    if (EFI_ERROR(Status) || Fs == NULL) continue;
    Status = Fs->OpenVolume(Fs, &Root);
    if (EFI_ERROR(Status)) continue;
    Status = Root->Open(Root, &Anchor, L"\\m1n1\\boot.bin", EFI_FILE_MODE_READ, 0);
    if (EFI_ERROR(Status)) { Root->Close(Root); continue; }
    Anchor->Close(Anchor);
    Status = Root->Open(Root, &Log, L"\\m1n1\\j413uefi.log",
                       EFI_FILE_MODE_READ | EFI_FILE_MODE_WRITE | EFI_FILE_MODE_CREATE, 0);
    if (!EFI_ERROR(Status)) {
      Status = Log->SetPosition(Log, 0);
      if (!EFI_ERROR(Status)) Status = Log->Write(Log, &Bytes, mJ413Log);
      if (!EFI_ERROR(Status) && Bytes != sizeof(mJ413Log)) Status = EFI_DEVICE_ERROR;
      if (!EFI_ERROR(Status)) Status = Log->Flush(Log);
      Log->Close(Log);
    }
    Root->Close(Root);
    Result = Status;
    // Never select a second anchored internal filesystem after a write attempt.
    break;
  }
  FreePool(Handles);
  return Result;
}

STATIC VOID J413Checkpoint(CONST CHAR8 *Label, EFI_STATUS Status)
{
  EFI_STATUS Saved;
  J413LogStatus(Label, Status);
  Saved = J413SaveLog();
  if (gST->ConOut != NULL) {
    if (EFI_ERROR(Saved)) Print(L"UEFI BOOT: phase log not saved: %r\r\n", Saved);
    else Print(L"UEFI BOOT: phase log saved to internal ESP \\m1n1\\j413uefi.log\r\n");
  }
}
#endif

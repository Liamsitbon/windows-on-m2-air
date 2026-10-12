/** @file Recursive, filesystem-independent ARM64 EFI application discovery.
    SPDX-License-Identifier: BSD-2-Clause-Patent **/
#ifndef J413_EFI_CANDIDATES_H
#define J413_EFI_CANDIDATES_H
#define J413_EFI_MAX_PATH 1024
#define J413_EFI_MAX_DEPTH 32
#define J413_EFI_MAX_ENTRIES 100000
#define J413_EFI_MAX_CANDIDATES 256

typedef struct J413_EFI_CANDIDATE {
  struct J413_EFI_CANDIDATE *Next;
  EFI_HANDLE Handle;
  CHAR16 Path[J413_EFI_MAX_PATH];
} J413_EFI_CANDIDATE;
STATIC J413_EFI_CANDIDATE *mEfiHead, *mEfiTail;
STATIC UINTN mEfiCount;
STATIC BOOLEAN mEfiScanned;
STATIC EFI_HANDLE mEfiAlreadyAttemptedHandle;

STATIC CHAR16 J413EfiFold(CHAR16 C) { return C >= L'A' && C <= L'Z' ? C + (L'a' - L'A') : C; }
STATIC BOOLEAN J413EfiSamePath(CONST CHAR16 *A, CONST CHAR16 *B) {
  while (*A && J413EfiFold(*A) == J413EfiFold(*B)) { A++; B++; }
  return J413EfiFold(*A) == J413EfiFold(*B);
}
STATIC UINT32 J413EfiLe32(CONST UINT8 *P) {
  return (UINT32)P[0] | ((UINT32)P[1] << 8) | ((UINT32)P[2] << 16) | ((UINT32)P[3] << 24);
}
STATIC UINT16 J413EfiLe16(CONST UINT8 *P) { return (UINT16)(P[0] | ((UINT16)P[1] << 8)); }

// Header preflight only. Standard BDS LoadImage still owns complete validation/security.
STATIC BOOLEAN J413EfiApplication(EFI_FILE_PROTOCOL *Root, CHAR16 *Path) {
  EFI_FILE_PROTOCOL *File = NULL;
  UINT8 Dos[64], Pe[94];
  UINTN Size = sizeof(Dos);
  BOOLEAN Valid = FALSE;
  EFI_STATUS Status = Root->Open(Root, &File, Path, EFI_FILE_MODE_READ, 0);
  if (EFI_ERROR(Status) || File == NULL) return FALSE;
  Status = File->Read(File, &Size, Dos);
  if (!EFI_ERROR(Status) && Size == sizeof(Dos) && Dos[0] == 'M' && Dos[1] == 'Z') {
    UINT32 Offset = J413EfiLe32(Dos + 60);
    if (Offset >= sizeof(Dos) && Offset <= 0x1000000) {
      Status = File->SetPosition(File, Offset);
      Size = sizeof(Pe);
      if (!EFI_ERROR(Status)) Status = File->Read(File, &Size, Pe);
      if (!EFI_ERROR(Status) && Size == sizeof(Pe)) {
        Valid = J413EfiLe32(Pe) == 0x4550 && J413EfiLe16(Pe + 4) == 0xaa64 &&
                J413EfiLe16(Pe + 20) >= 70 && J413EfiLe16(Pe + 24) == 0x20b &&
                J413EfiLe16(Pe + 92) == 10;
      }
    }
  }
  File->Close(File);
  return Valid;
}

STATIC VOID J413EfiQueue(EFI_HANDLE Handle, EFI_FILE_PROTOCOL *Root, CHAR16 *Path) {
  J413_EFI_CANDIDATE *Item;
  if (Handle == mEfiAlreadyAttemptedHandle && J413EfiSamePath(Path, L"\\EFI\\BOOT\\BOOTAA64.EFI")) return;
  if (mEfiCount >= J413_EFI_MAX_CANDIDATES || StrLen(Path) >= J413_EFI_MAX_PATH) return;
  for (Item = mEfiHead; Item != NULL; Item = Item->Next) {
    if (Item->Handle == Handle && J413EfiSamePath(Item->Path, Path)) return;
  }
  if (!J413EfiApplication(Root, Path)) return;
  Item = AllocateZeroPool(sizeof(*Item));
  if (Item == NULL) { Print(L"UEFI EFI: candidate allocation failed\r\n"); return; }
  Item->Handle = Handle;
  CopyMem(Item->Path, Path, (StrLen(Path) + 1) * sizeof(CHAR16));
  if (mEfiTail != NULL) mEfiTail->Next = Item; else mEfiHead = Item;
  mEfiTail = Item;
  mEfiCount++;
  Print(L"UEFI EFI: found %s\r\n", Path);
}

STATIC VOID J413EfiWalk(EFI_HANDLE Handle, EFI_FILE_PROTOCOL *Root,
  EFI_FILE_PROTOCOL *Directory, CONST CHAR16 *Parent, UINTN Depth, UINTN *Visited) {
  EFI_FILE_INFO *Info;
  UINTN Capacity = 4096;
  if (Depth >= J413_EFI_MAX_DEPTH) { Print(L"UEFI EFI: directory depth limit at %s\r\n", Parent); return; }
  Info = AllocatePool(Capacity);
  if (Info == NULL) return;
  while (*Visited < J413_EFI_MAX_ENTRIES && mEfiCount < J413_EFI_MAX_CANDIDATES) {
    UINTN Size = Capacity, NameLength = 0, ParentLength;
    EFI_STATUS Status = Directory->Read(Directory, &Size, Info);
    CHAR16 *Path;
    if (Status == EFI_BUFFER_TOO_SMALL && Size > Capacity && Size <= 65536) {
      EFI_FILE_INFO *Larger = AllocatePool(Size);
      if (Larger == NULL) break;
      FreePool(Info); Info = Larger; Capacity = Size; continue;
    }
    if (EFI_ERROR(Status) || Size == 0) break;
    (*Visited)++;
    if (Size > Capacity || Size < OFFSET_OF(EFI_FILE_INFO, FileName) + sizeof(CHAR16) ||
        Info->Size > Size || Info->Size < OFFSET_OF(EFI_FILE_INFO, FileName) + sizeof(CHAR16)) break;
    UINTN NameCapacity = (UINTN)(Info->Size - OFFSET_OF(EFI_FILE_INFO, FileName)) / sizeof(CHAR16);
    while (NameLength < NameCapacity && Info->FileName[NameLength] != 0) NameLength++;
    if (NameLength == 0 || NameLength == NameCapacity) continue;
    if (J413EfiSamePath(Info->FileName, L".") || J413EfiSamePath(Info->FileName, L"..")) continue;
    BOOLEAN BadName = FALSE;
    for (UINTN Index = 0; Index < NameLength; Index++) {
      if (Info->FileName[Index] == L'\\' || Info->FileName[Index] == L'/') BadName = TRUE;
    }
    if (BadName) continue;
    ParentLength = StrLen(Parent);
    if (ParentLength + NameLength + 2 > J413_EFI_MAX_PATH) continue;
    Path = AllocatePool((ParentLength + NameLength + 2) * sizeof(CHAR16));
    if (Path == NULL) break;
    CopyMem(Path, Parent, ParentLength * sizeof(CHAR16));
    Path[ParentLength] = L'\\';
    CopyMem(Path + ParentLength + 1, Info->FileName, (NameLength + 1) * sizeof(CHAR16));
    if ((Info->Attribute & EFI_FILE_DIRECTORY) != 0) {
      EFI_FILE_PROTOCOL *Child = NULL;
      Status = Root->Open(Root, &Child, Path, EFI_FILE_MODE_READ, 0);
      if (!EFI_ERROR(Status) && Child != NULL) {
        J413EfiWalk(Handle, Root, Child, Path, Depth + 1, Visited);
        Child->Close(Child);
      }
    } else if (NameLength >= 4 && J413EfiSamePath(Info->FileName + NameLength - 4, L".efi")) {
      J413EfiQueue(Handle, Root, Path);
    }
    FreePool(Path);
  }
  FreePool(Info);
}

STATIC EFI_STATUS J413NextEfiOption(EFI_BOOT_MANAGER_LOAD_OPTION *Option) {
  EFI_STATUS Status;
  if (!mEfiScanned) {
    EFI_HANDLE *Handles = NULL;
    UINTN Count = 0;
    mEfiScanned = TRUE;
    Status = gBS->LocateHandleBuffer(ByProtocol, &gEfiSimpleFileSystemProtocolGuid, NULL, &Count, &Handles);
    if (EFI_ERROR(Status)) { if (Handles != NULL) FreePool(Handles); return Status; }
    // All readable filesystems: no partition, volume-name, vendor or BlockIo requirement.
    for (UINTN Pass = 0; Pass < 2; Pass++) {
      for (UINTN Index = 0; Index < Count; Index++) {
        EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *Fs = NULL;
        EFI_FILE_PROTOCOL *Root = NULL;
        Status = gBS->HandleProtocol(Handles[Index], &gEfiSimpleFileSystemProtocolGuid, (VOID **)&Fs);
        if (EFI_ERROR(Status) || Fs == NULL) continue;
        Status = Fs->OpenVolume(Fs, &Root);
        if (EFI_ERROR(Status) || Root == NULL) continue;
        if (Pass == 0) {
          J413EfiQueue(Handles[Index], Root, L"\\EFI\\BOOT\\BOOTAA64.EFI");
          J413EfiQueue(Handles[Index], Root, L"\\EFI\\Microsoft\\Boot\\bootmgfw.efi");
        } else {
          UINTN Visited = 0;
          J413EfiWalk(Handles[Index], Root, Root, L"", 0, &Visited);
          if (Visited >= J413_EFI_MAX_ENTRIES) Print(L"UEFI EFI: filesystem entry limit reached\r\n");
        }
        Root->Close(Root);
      }
    }
    if (Handles != NULL) FreePool(Handles);
    if (mEfiCount >= J413_EFI_MAX_CANDIDATES) Print(L"UEFI EFI: candidate limit reached\r\n");
    Print(L"UEFI EFI: discovered %u ARM64 application candidates\r\n", mEfiCount);
  }
  while (mEfiHead != NULL) {
    J413_EFI_CANDIDATE *Item = mEfiHead;
    EFI_DEVICE_PATH_PROTOCOL *Path;
    mEfiHead = Item->Next;
    if (mEfiHead == NULL) mEfiTail = NULL;
    Path = FileDevicePath(Item->Handle, Item->Path);
    Status = Path == NULL ? EFI_OUT_OF_RESOURCES :
      EfiBootManagerInitializeLoadOption(Option, LoadOptionNumberUnassigned,
        LoadOptionTypeBoot, LOAD_OPTION_ACTIVE, Item->Path, Path, NULL, 0);
    if (Path != NULL) FreePool(Path);
    if (!EFI_ERROR(Status)) Print(L"UEFI EFI: selected %s\r\n", Item->Path);
    FreePool(Item);
    if (!EFI_ERROR(Status)) return Status;
    Print(L"UEFI EFI: option creation failed: %r\r\n", Status);
  }
  return EFI_NOT_FOUND;
}
#endif

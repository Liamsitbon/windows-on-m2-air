/* SPDX-License-Identifier: MIT */

#include "hv_j413_expected.h"
#include "hv_j413_layout.generated.h"
#include "hv_guest_cpu_state.h"

/* MPIDRs from the J413/T8112 DTS; checked against the live CPU ADT before launch. */
static const uint64_t j413_mpidrs[HV_CONTRACT_MAX_CPUS] = {
    0x0, 0x1, 0x2, 0x3, 0x10100, 0x10101, 0x10102, 0x10103,
};

static void fill_cpu(struct hv_contract_cpu *cpu, uint64_t mpidr, bool initialized)
{
    struct hv_guest_cpu_state s = hv_guest_cpu_state_prepare(0, 0);
    *cpu = (struct hv_contract_cpu){
        .mpidr = mpidr,
        .hacr = initialized ? s.hacr : 0,
        .mdcr = initialized ? s.mdcr : 0,
        .mdscr = initialized ? s.mdscr : 0,
        .amx_config = initialized ? s.amx_config : 0,
        .apvmkeylo = initialized ? s.apvmkeylo : 0,
        .apvmkeyhi = initialized ? s.apvmkeyhi : 0,
        .apsts = initialized ? s.apsts : 0,
        .actlr = initialized ? s.actlr : 0,
    };
}

static void fill_common(struct hv_contract_snapshot *snapshot, uint32_t checkpoint,
                        uint64_t ram_end, uint64_t adt_size)
{
    snapshot->identity = (struct hv_contract_identity){
        .target = HV_J413_TARGET,
        .schema_revision = 1,
    };
    snapshot->boot = (struct hv_contract_boot){
        .ram_base = 0x850000000ULL,
        .ram_size = (ram_end - 0x850000000ULL),
        .guest_entry = 0x8510b4000ULL,
        .args = {0x8533e8000ULL, 0, 0, 0},
    };
    snapshot->adt_size = adt_size;
    snapshot->regions[0] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_GUEST_RAM, .base = 0x850000000ULL, .size = (ram_end - 0x850000000ULL)};
    snapshot->regions[1] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_HEAP, .base = 0x850000000ULL, .size = 0x1000000ULL};
    snapshot->regions[2] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_FIRMWARE, .base = 0x8510b4000ULL, .size = J413_AUTONOMOUS_LAYOUT.firmware_max_size};
    snapshot->regions[3] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_ADT, .base = 0x851000000ULL, .size = ((adt_size + 0x3fff) & ~0x3fffULL)};
    snapshot->regions[4] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_BOOT_ARGS, .base = 0x8533e8000ULL, .size = 0x4000ULL};
    snapshot->regions[5] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_FRAMEBUFFER, .base = 0x85e000000ULL, .size = 0x1040000ULL};
    snapshot->regions[6] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_LOW_MEMORY, .base = 0x8a0100000ULL, .size = 0x3ff00000ULL};
    snapshot->regions[7] = (struct hv_contract_region){
        .kind = HV_CONTRACT_REGION_DART_TABLES, .flags = 1, .base = 0x850000000ULL};
    snapshot->region_count = 8;

    snapshot->cpu_count = HV_CONTRACT_MAX_CPUS;
    for (uint32_t i = 0; i < HV_CONTRACT_MAX_CPUS; i++)
        fill_cpu(&snapshot->cpus[i], j413_mpidrs[i], checkpoint != HV_CONTRACT_PRE_HV_INIT);

    snapshot->irq_routes[0] = (struct hv_contract_irq_route){
        .physical_irq = 1112, .vintid = 857, .flags = HV_CONTRACT_IRQ_LEVEL};
    snapshot->irq_route_count = 1;
    snapshot->devices = (struct hv_contract_devices){
        .pci_ecam_base = 0x690000000ULL,
        .xhci_base = 0x502280000ULL,
        .dart_base = 0x502f00000ULL,
        .vuart_base = 0x235200000ULL,
        .display_base = 0x85e000000ULL,
        .display_width = 2560,
        .display_height = 1664,
        .display_stride = 10240,
    };
}

bool hv_j413_expected_init(
    struct hv_contract_snapshot out[HV_LAUNCH_PREFLIGHT_BLOCKING_CHECKPOINTS],
    uint64_t ram_end, uint64_t adt_size, uint64_t firmware_size)
{
    if (!out || ram_end <= J413_AUTONOMOUS_LAYOUT.phys_base ||
        adt_size > J413_AUTONOMOUS_LAYOUT.adt_max_size ||
        firmware_size > J413_AUTONOMOUS_LAYOUT.firmware_max_size)
        return false;
    for (uint32_t i = 0; i < HV_LAUNCH_PREFLIGHT_BLOCKING_CHECKPOINTS; i++)
        out[i] = (struct hv_contract_snapshot){0};
    for (uint32_t i = 0; i < HV_LAUNCH_PREFLIGHT_BLOCKING_CHECKPOINTS; i++) {
        out[i].header.magic = HV_CONTRACT_MAGIC;
        out[i].header.version = HV_CONTRACT_VERSION;
        out[i].header.checkpoint = i;
        out[i].header.sequence = i + 1;
        fill_common(&out[i], i, ram_end, adt_size);
        if (!hv_contract_finalize(&out[i]))
            return false;
    }
    return true;
}

/*
 * Isolated Win32 fixture for the exact 61-byte FUN_00442FA0 slice.
 * This executes transplanted original machine code, not the original game.
 */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define PAGE 4096u
#define CODE_LEN 0x3du
#define MAX_CAP 4001u
#define CANARY 16u

typedef int (__cdecl *allocator_fn)(void);

static const uint8_t expected[CODE_LEN] = {
  0x53,0x56,0x57,0x33,0xdb,0x33,0xc0,0xbf,0x01,0x00,0x00,0x00,
  0xb9,0x2a,0x9a,0x89,0x00,0x66,0x83,0xb9,0xa0,0xf6,0xff,0xff,
  0x00,0x75,0x12,0x66,0x8b,0x31,0x0f,0xbf,0xd6,0x3b,0xd3,0x7c,
  0x04,0x8b,0xda,0x8b,0xc7,0x46,0x66,0x89,0x31,0x83,0xc1,0x02,
  0x47,0x81,0xf9,0x88,0xa3,0x89,0x00,0x7c,0xd8,0x5f,0x5e,0x5b,
  0xc3
};

typedef struct {
  uint8_t *mapping;
  uint8_t *data;
  SIZE_T bytes;
} guarded_region;

static void fail(const char *why) {
  fprintf(stderr, "FAIL %s\n", why);
  ExitProcess(2);
}

static guarded_region guarded_alloc(SIZE_T bytes) {
  SIZE_T pages = (bytes + 2u * CANARY + PAGE - 1u) / PAGE;
  SIZE_T total = (pages + 2u) * PAGE;
  uint8_t *mapping = (uint8_t *)VirtualAlloc(NULL, total, MEM_RESERVE, PAGE_NOACCESS);
  guarded_region region;
  if (!mapping) fail("guarded reserve failed");
  if (!VirtualAlloc(mapping + PAGE, pages * PAGE, MEM_COMMIT, PAGE_READWRITE))
    fail("guarded commit failed");
  region.mapping = mapping;
  region.data = mapping + PAGE + CANARY;
  region.bytes = bytes;
  memset(region.data - CANARY, 0xa5, CANARY);
  memset(region.data + bytes, 0x5a, CANARY);
  return region;
}

static void guarded_check(const guarded_region *region) {
  unsigned i;
  for (i = 0; i < CANARY; ++i) {
    if ((region->data - CANARY)[i] != 0xa5 ||
        region->data[region->bytes + i] != 0x5a)
      fail("guarded array canary changed");
  }
}

static void guarded_free(guarded_region *region) {
  VirtualFree(region->mapping, 0, MEM_RELEASE);
}

static void read_original(const char *path, uint8_t *out) {
  FILE *file = fopen(path, "rb");
  size_t got;
  if (!file || fseek(file, 0x42fa0L, SEEK_SET) != 0)
    fail("original read/seek failed");
  got = fread(out, 1, CODE_LEN, file);
  fclose(file);
  if (got != CODE_LEN || memcmp(out, expected, CODE_LEN) != 0)
    fail("original allocator bytes mismatch");
}

/* Independent expected model: caller owns occupancy; allocator only ages free slots. */
static unsigned expected_selector(uint16_t *exist, uint16_t *age, unsigned cap) {
  int best_age = 0;
  unsigned result = 0;
  unsigned i;
  for (i = 1; i < cap; ++i) {
    if (exist[i] == 0) {
      int age_value = (int)(int16_t)age[i];
      if (best_age <= age_value) {
        best_age = age_value;
        result = i;
      }
      age[i] = (uint16_t)(age[i] + 1u);
    }
  }
  return result;
}

static int run_case(const uint8_t *original, const char *name, unsigned cap,
                    const uint16_t *initial_exist, const uint16_t *initial_age,
                    uint16_t *result_exist, uint16_t *result_age,
                    unsigned *result_index) {
  guarded_region exist_region = guarded_alloc((SIZE_T)cap * 2u);
  guarded_region age_region = guarded_alloc((SIZE_T)cap * 2u);
  uint16_t *exist = (uint16_t *)exist_region.data;
  uint16_t *age = (uint16_t *)age_region.data;
  uint16_t expected_exist[MAX_CAP], expected_age[MAX_CAP];
  uint8_t *code;
  uintptr_t age_base, exist_base, start, end;
  uint32_t displacement;
  unsigned expected_result;
  unsigned i;
  int actual_result;
  DWORD old_protection;

  if (cap > MAX_CAP) fail("capacity exceeds fixture bound");
  memcpy(exist, initial_exist, cap * 2u);
  memcpy(age, initial_age, cap * 2u);
  memcpy(expected_exist, initial_exist, cap * 2u);
  memcpy(expected_age, initial_age, cap * 2u);
  expected_result = expected_selector(expected_exist, expected_age, cap);

  age_base = (uintptr_t)age;
  exist_base = (uintptr_t)exist;
  start = age_base + 2u;
  end = age_base + (uintptr_t)cap * 2u;
  /* The original uses signed JL for the end check; reject wrap/sign crossing. */
  if (start >= 0x80000000u || end >= 0x80000000u || end <= start)
    fail("dynamic address crosses signed-jl boundary");
  displacement = (uint32_t)(exist_base - age_base);

  code = (uint8_t *)VirtualAlloc(NULL, PAGE, MEM_COMMIT, PAGE_READWRITE);
  if (!code) fail("dynamic code allocation failed");
  memcpy(code, original, CODE_LEN);
  memcpy(code + 0x0d, &start, 4);
  memcpy(code + 0x14, &displacement, 4);
  memcpy(code + 0x33, &end, 4);
  for (i = 0; i < CODE_LEN; ++i) {
    if ((i < 0x0d || i > 0x10) && (i < 0x14 || i > 0x17) &&
        (i < 0x33 || i > 0x36) && code[i] != original[i])
      fail("non-fixup machine byte changed");
  }
  if (!VirtualProtect(code, PAGE, PAGE_EXECUTE_READ, &old_protection))
    fail("code RX transition failed");
  if (!FlushInstructionCache(GetCurrentProcess(), code, PAGE))
    fail("instruction cache flush failed");

  actual_result = ((allocator_fn)code)();
  if ((unsigned)actual_result != expected_result)
    fail(name);
  if (memcmp(exist, expected_exist, cap * 2u) != 0 ||
      memcmp(age, expected_age, cap * 2u) != 0)
    fail("full state differs from independent model");
  guarded_check(&exist_region);
  guarded_check(&age_region);
  if (result_exist) memcpy(result_exist, exist, cap * 2u);
  if (result_age) memcpy(result_age, age, cap * 2u);
  if (result_index) *result_index = (unsigned)actual_result;
  VirtualFree(code, 0, MEM_RELEASE);
  guarded_free(&exist_region);
  guarded_free(&age_region);
  return 0;
}

static void clear_state(uint16_t *exist, uint16_t *age, unsigned cap) {
  unsigned i;
  for (i = 0; i < cap; ++i) {
    exist[i] = 0;
    age[i] = 0;
  }
}

int main(int argc, char **argv) {
  uint8_t bytes[CODE_LEN], bulk_sentinel[16], bulk_after[16];
  uint16_t exist[MAX_CAP], age[MAX_CAP];
  uint16_t common1200_exist[1200], common1200_age[1200];
  uint16_t common1201_exist[1201], common1201_age[1201];
  uint16_t common4001_exist[4001], common4001_age[4001];
  uint16_t pair_exist[1200], pair_age[1200];
  unsigned result;
  unsigned i;
  if (argc != 2) fail("usage: fixture original.exe");
  read_original(argv[1], bytes);
  memset(bulk_sentinel, 0xa5, sizeof(bulk_sentinel));

  /* Empty: all free ages tie, so the later slot wins; slot0 is untouched. */
  clear_state(exist, age, 1200u);
  exist[0] = 1;
  age[0] = 0x4321;
  run_case(bytes, "empty case failed", 1200u, exist, age, NULL, NULL, &result);
  if (result != 1199u) fail("empty selector expectation failed");

  /* Single free and occupied preservation. */
  for (i = 1; i < 1200u; ++i) age[i] = (uint16_t)(100u + i);
  for (i = 1; i < 1200u; ++i) exist[i] = 1;
  exist[77] = 0;
  age[77] = 5;
  run_case(bytes, "single-free case failed", 1200u, exist, age, NULL, NULL, &result);
  if (result != 77u) fail("single-free selector expectation failed");

  /* Multiple free, equal age: later equal slot must win. */
  clear_state(exist, age, 1200u);
  exist[0] = 1;
  for (i = 1; i < 1200u; ++i) exist[i] = 1;
  exist[10] = 0; age[10] = 7;
  exist[11] = 0; age[11] = 7;
  exist[12] = 0; age[12] = 6;
  run_case(bytes, "multiple-free case failed", 1200u, exist, age, NULL, NULL, &result);
  if (result != 11u) fail("equal-age tie expectation failed");

  /* Signed boundary, wrap, and all-negative no-eligible behavior. */
  clear_state(exist, age, 1200u);
  exist[0] = 1;
  for (i = 1; i < 1200u; ++i) exist[i] = 1;
  exist[10] = 0; exist[11] = 0; exist[12] = 0; exist[13] = 0;
  age[10] = 0x7fffu; age[11] = 0x7fffu; age[12] = 0xffffu; age[13] = 0x8000u;
  run_case(bytes, "signed-age case failed", 1200u, exist, age, NULL, NULL, &result);
  if (result != 11u) fail("signed-age selector expectation failed");
  if (age[10] != 0x7fffu || age[11] != 0x7fffu)
    fail("input age unexpectedly changed");

  clear_state(exist, age, 1200u);
  exist[0] = 1;
  for (i = 1; i < 1200u; ++i) exist[i] = 1;
  exist[10] = 0; exist[11] = 0;
  age[10] = 0xffffu; age[11] = 0xfffeu;
  run_case(bytes, "negative-age case failed", 1200u, exist, age, NULL, NULL, &result);
  if (result != 0u) fail("all-negative no-eligible expectation failed");

  /* Paired common state: 1200 reference and 1201 copy with slot1200 occupied. */
  clear_state(exist, age, 1200u);
  exist[0] = 1; exist[1] = 1; exist[1199] = 0; age[1199] = 21;
  memcpy(pair_exist, exist, sizeof(pair_exist));
  memcpy(pair_age, age, sizeof(pair_age));
  run_case(bytes, "common1200 failed", 1200u, exist, age,
           common1200_exist, common1200_age, &result);
  clear_state(exist, age, 1201u);
  memcpy(exist, pair_exist, sizeof(pair_exist));
  memcpy(age, pair_age, sizeof(pair_age));
  exist[1200] = 1; age[1200] = 99;
  run_case(bytes, "common1201 failed", 1201u, exist, age,
           common1201_exist, common1201_age, &result);
  if (memcmp(common1200_exist, common1201_exist, 1200u * 2u) != 0 ||
      memcmp(common1200_age, common1201_age, 1200u * 2u) != 0 ||
      common1201_exist[1200] != 1 || common1201_age[1200] != 99)
    fail("paired common state mismatch");
  clear_state(exist, age, 4001u);
  memcpy(exist, pair_exist, sizeof(pair_exist));
  memcpy(age, pair_age, sizeof(pair_age));
  for (i = 1200u; i < 4001u; ++i) {
    exist[i] = 1;
    age[i] = (uint16_t)(0x2200u + (i % 17u));
  }
  run_case(bytes, "common4001 failed", 4001u, exist, age,
           common4001_exist, common4001_age, &result);
  if (memcmp(common1200_exist, common4001_exist, 1200u * 2u) != 0 ||
      memcmp(common1200_age, common4001_age, 1200u * 2u) != 0)
    fail("paired 4001 common state mismatch");

  /* Boundary and exhaustion capacities. */
  clear_state(exist, age, 1201u);
  for (i = 1; i < 1200u; ++i) exist[i] = 1;
  age[1200] = 9;
  run_case(bytes, "1200-to-1201 boundary failed", 1201u, exist, age, NULL, NULL, &result);
  if (result != 1200u) fail("1200-to-1201 selector expectation failed");
  for (i = 1; i < 1201u; ++i) exist[i] = 1;
  run_case(bytes, "1201 exhaustion failed", 1201u, exist, age, NULL, NULL, &result);
  if (result != 0u) fail("1201 exhaustion expectation failed");

  clear_state(exist, age, 4001u);
  for (i = 1; i < 4000u; ++i) exist[i] = 1;
  age[4000] = 9;
  run_case(bytes, "3999-to-4000 boundary failed", 4001u, exist, age, NULL, NULL, &result);
  if (result != 4000u) fail("3999-to-4000 selector expectation failed");
  for (i = 1; i < 4001u; ++i) exist[i] = 1;
  run_case(bytes, "4001 exhaustion failed", 4001u, exist, age, NULL, NULL, &result);
  if (result != 0u) fail("4001 exhaustion expectation failed");

  memcpy(bulk_after, bulk_sentinel, sizeof(bulk_after));
  if (memcmp(bulk_sentinel, bulk_after, sizeof(bulk_sentinel)) != 0)
    fail("standalone bulk sentinel changed");
  printf("{\"status\":\"PASS\",\"execution\":\"transplanted_original_machine_code\",\"cases\":12,\"case_names\":[\"empty\",\"single_free\",\"multiple_equal_tie\",\"signed_wrap\",\"all_negative_no_eligible\",\"common1200\",\"common1201\",\"common4001\",\"boundary1201\",\"exhaustion1201\",\"boundary4001\",\"exhaustion4001\"],\"capacities\":[1200,1201,4001],\"full_state_model\":true,\"caller_occupancy_only\":true,\"bulk_sentinel\":\"standalone_only_not_game_bulk_proof\",\"activation\":\"NO-GO\"}\n");
  return 0;
}

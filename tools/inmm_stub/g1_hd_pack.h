#ifndef G1_HD_PACK_H
#define G1_HD_PACK_H

#include <stddef.h>
#include <stdint.h>

#define G1_HD_PACK_KEY 0xFEu

/* Pointer-free pack file name: <prefix><digest8>_<w>x<h>.idx8 (lowercase hex,
 * decimal size).  A general A/B writer frame is h<digest8>: the digest is the
 * same FNV-1a over the first 128 source bytes that the ledger key uses, so
 * tools/g1_hd_convert.py can compute it offline from the original file.  A
 * whole-screen raw picture (H-HDF0) is f<digest8> over every source byte. */
static inline int g1_hd_pack_format_name(char *output, size_t output_size, char prefix,
                                         uint32_t digest, uint32_t width,
                                         uint32_t height)
{
    static const char hex[] = "0123456789abcdef";
    size_t cursor = 0u, nibble;
    uint32_t value[2];
    size_t field;
    if (!output || output_size < 32u || !width || !height ||
        width > 800u || height > 600u) return 0;
    output[cursor++] = prefix;
    for (nibble = 0u; nibble < 8u; ++nibble)
        output[cursor++] = hex[(digest >> (28u - (unsigned)nibble * 4u)) & 15u];
    value[0] = width;
    value[1] = height;
    for (field = 0u; field < 2u; ++field) {
        char digits[10];
        size_t count = 0u;
        uint32_t number = value[field];
        output[cursor++] = field ? 'x' : '_';
        do { digits[count++] = (char)('0' + number % 10u); number /= 10u; } while (number);
        while (count) output[cursor++] = digits[--count];
    }
    output[cursor++] = '.'; output[cursor++] = 'i'; output[cursor++] = 'd';
    output[cursor++] = 'x'; output[cursor++] = '8'; output[cursor] = '\0';
    return 1;
}

/* H-HDPAL: a pack frame is quantised to one screen palette, so frames live in <pack>\<pal8>\<name>.  pal8 is the
 * lowercase-hex FNV-1a of the 768 R,G,B bytes of the renderer's 256 PALETTEENTRYs (tools/g1_hd_convert.py computes the
 * same value from a .pal file).  A pack root has no frames of its own, so a picture can never meet a foreign palette. */
static inline int g1_hd_pack_format_pal(char *output, size_t output_size, uint32_t pal)
{
    static const char hex[] = "0123456789abcdef";
    size_t nibble;
    if (!output || output_size < 9u) return 0;
    for (nibble = 0u; nibble < 8u; ++nibble)
        output[nibble] = hex[(pal >> (28u - (unsigned)nibble * 4u)) & 15u];
    output[8] = '\0';
    return 1;
}

static inline int g1_hd_pack_name(char *output, size_t output_size,
                                  uint32_t digest, uint32_t width,
                                  uint32_t height)
{
    return g1_hd_pack_format_name(output, output_size, 'h', digest, width, height);
}

/* H-HDN0: two different pictures can share the first 128 stream bytes, hence one h<digest8>_<w>x<h> name.  The pack then
 * writes no file under that name; it writes the marker h<digest8>_<w>x<h>.amb (4 bytes little endian: prefix length L)
 * and one frame per picture as h<digest8>_<w>x<h>_<L>_<p8>.idx8, p8 = FNV-1a of the first L source bytes. */
#define G1_HD_PACK_EXT_MIN 129u
#define G1_HD_PACK_EXT_MAX 65536u

/* no-tree-loop-distribute-patterns: the DLL links without the CRT, so the length loop must not become a strlen call */
static inline __attribute__((optimize("no-tree-loop-distribute-patterns"))) size_t g1_hd_pack_stem(char *output, size_t output_size, uint32_t digest, uint32_t width, uint32_t height)
{
    size_t length = 0u;
    if (!g1_hd_pack_format_name(output, output_size, 'h', digest, width, height)) return 0u;
    while (output[length]) ++length;
    return length - 5u;                                  /* without ".idx8" */
}

static inline int g1_hd_pack_marker_name(char *output, size_t output_size, uint32_t digest, uint32_t width,
                                         uint32_t height)
{
    size_t stem = g1_hd_pack_stem(output, output_size, digest, width, height);
    if (!stem || stem + 5u > output_size) return 0;
    output[stem] = '.'; output[stem + 1u] = 'a'; output[stem + 2u] = 'm'; output[stem + 3u] = 'b';
    output[stem + 4u] = '\0';
    return 1;
}

static inline int g1_hd_pack_ext_name(char *output, size_t output_size, uint32_t digest, uint32_t width,
                                      uint32_t height, uint32_t length, uint32_t prefix_hash)
{
    static const char hex[] = "0123456789abcdef";
    size_t cursor = g1_hd_pack_stem(output, output_size, digest, width, height), count = 0u, nibble;
    char digits[10];
    if (!cursor || length < G1_HD_PACK_EXT_MIN || length > G1_HD_PACK_EXT_MAX || cursor + 28u > output_size) return 0;
    output[cursor++] = '_';
    do { digits[count++] = (char)('0' + length % 10u); length /= 10u; } while (length);
    while (count) output[cursor++] = digits[--count];
    output[cursor++] = '_';
    for (nibble = 0u; nibble < 8u; ++nibble)
        output[cursor++] = hex[(prefix_hash >> (28u - (unsigned)nibble * 4u)) & 15u];
    output[cursor++] = '.'; output[cursor++] = 'i'; output[cursor++] = 'd';
    output[cursor++] = 'x'; output[cursor++] = '8'; output[cursor] = '\0';
    return 1;
}

static inline int g1_hd_pack_fullscreen_name(char *output, size_t output_size,
                                             uint32_t digest, uint32_t width,
                                             uint32_t height)
{
    return g1_hd_pack_format_name(output, output_size, 'f', digest, width, height);
}

/* A pack frame is 2w x 2h bytes, row-major.  Every 2x2 block of a pixel the
 * original writer produced (written != 0) must be fully opaque; every block of
 * a pixel it did not produce must be entirely the key.  That keeps the
 * silhouette identical to the original primitive's, so a pack can only
 * recolour, never reshape. */
static inline int g1_hd_pack_valid(const uint8_t *written, size_t written_stride,
                                   size_t width, size_t height,
                                   const uint8_t *pack, size_t pack_bytes)
{
    size_t x, y;
    if (!written || !pack || !width || !height || written_stride < width ||
        width > (size_t)-1 / height / 4u || pack_bytes != width * height * 4u)
        return 0;
    for (y = 0u; y < height; ++y) {
        for (x = 0u; x < width; ++x) {
            size_t top = y * 2u * width * 2u + x * 2u;
            size_t bottom = top + width * 2u;
            int keyed = pack[top] == G1_HD_PACK_KEY &&
                        pack[top + 1u] == G1_HD_PACK_KEY &&
                        pack[bottom] == G1_HD_PACK_KEY &&
                        pack[bottom + 1u] == G1_HD_PACK_KEY;
            int opaque = pack[top] != G1_HD_PACK_KEY &&
                         pack[top + 1u] != G1_HD_PACK_KEY &&
                         pack[bottom] != G1_HD_PACK_KEY &&
                         pack[bottom + 1u] != G1_HD_PACK_KEY;
            if (written[y * written_stride + x] ? !opaque : !keyed) return 0;
        }
    }
    return 1;
}

#endif /* G1_HD_PACK_H */

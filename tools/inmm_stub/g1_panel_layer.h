#ifndef G1_PANEL_LAYER_H
#define G1_PANEL_LAYER_H

#include <stddef.h>
#include <stdint.h>

#define G1_PANEL_KEY 0xFEu

/* Panel pack keys carry no runtime pointer (it varies per run): writer, source
 * digest and size name the file, like g1_hd_pack_name for the general ledger. */
static inline uint32_t g1_panel_source_digest(const uint8_t *source,
                                              size_t source_bytes)
{
    uint32_t hash = 2166136261u;
    size_t index;
    if (!source || source_bytes < 128u) return 0u;
    for (index = 0u; index < 128u; ++index) {
        hash ^= source[index];
        hash *= 16777619u;
    }
    return hash;
}

static inline int g1_panel_asset_key(char *output, size_t output_size,
                                    uint32_t writer, uint32_t width,
                                    uint32_t height, uint32_t source_digest)
{
    static const char hex[] = "0123456789abcdef";
    uint32_t fields[2] = {writer, source_digest};
    size_t cursor = 0u, field, nibble;
    if (!output || output_size < 48u || width != 831u ||
        !height || height > 203u) return 0;
    /* Emit fixed-width lowercase fields without depending on CRT formatting. */
    output[cursor++] = 'w';
    for (field = 0u; field < 2u; ++field) {
        uint32_t number = fields[field];
        if (field) output[cursor++] = '_';
        if (field == 1u) output[cursor++] = 'h';
        for (nibble = 0u; nibble < 8u; ++nibble)
            output[cursor++] = hex[(number >> (28u - (unsigned)nibble * 4u)) & 15u];
    }
    output[cursor++] = '_';
    /* Width and height are bounded panel dimensions and fit decimal digits. */
    {
        char digits[10]; size_t count = 0u;
        do { digits[count++] = (char)('0' + width % 10u); width /= 10u; } while (width);
        while (count) output[cursor++] = digits[--count];
        output[cursor++] = 'x'; count = 0u;
        do { digits[count++] = (char)('0' + height % 10u); height /= 10u; } while (height);
        while (count) output[cursor++] = digits[--count];
    }
    output[cursor++] = '.'; output[cursor++] = 'i'; output[cursor++] = 'd';
    output[cursor++] = 'x'; output[cursor++] = '8'; output[cursor] = '\0';
    return 1;
}

static inline int g1_panel_hd_pack_valid(const uint8_t *source,
                                         size_t source_stride,
                                         size_t width, size_t height,
                                         const uint8_t *pack,
                                         size_t pack_bytes)
{
    size_t x, y;
    if (!source || !pack || !width || !height || source_stride < width ||
        width > (size_t)-1 / height / 4u || pack_bytes != width * height * 4u)
        return 0;
    for (y = 0u; y < height; ++y) {
        for (x = 0u; x < width; ++x) {
            size_t index = y * 2u * width * 2u + x * 2u;
            size_t subpixels[4] = {index, index + 1u,
                                   index + width * 2u,
                                   index + width * 2u + 1u};
            size_t sub;
            if (source[y * source_stride + x] == G1_PANEL_KEY) {
                for (sub = 0u; sub < 4u; ++sub)
                    if (pack[subpixels[sub]] != G1_PANEL_KEY) return 0;
            } else {
                for (sub = 0u; sub < 4u; ++sub)
                    if (pack[subpixels[sub]] == G1_PANEL_KEY) return 0;
            }
        }
    }
    return 1;
}

static inline int g1_panel_writer_return(uint32_t address)
{
    return address == 0x0041B78Cu || address == 0x0041C5A5u ||
           address == 0x0042496Au || address == 0x00441538u;
}

static inline int g1_panel_binding_matches(uintptr_t expected_buffer,
                                            size_t expected_pitch,
                                            uintptr_t actual_buffer,
                                            size_t actual_pitch)
{
    return expected_buffer != 0u && actual_buffer == expected_buffer &&
           actual_pitch == expected_pitch;
}

typedef struct {
    size_t copied;
    size_t key_preserved;
    size_t mismatch_cleared;
    size_t uncovered;
} G1PanelTransferStats;

typedef struct {
    uint32_t state[8];
    uint64_t total_bits;
    uint8_t block[64];
    size_t used;
} G1PanelSha256;

static inline uint32_t g1_panel_rotr32(uint32_t value, unsigned int count)
{ return (value >> count) | (value << (32u - count)); }

static inline void g1_panel_sha256_transform(G1PanelSha256 *ctx,
                                             const uint8_t block[64])
{
    static const uint32_t k[64] = {
        0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
        0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
        0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
        0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
        0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
        0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
        0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
        0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u
    };
    uint32_t w[64], a,b,c,d,e,f,g,h;
    unsigned int i;
    for (i = 0u; i < 16u; ++i)
        w[i] = ((uint32_t)block[i*4u] << 24) | ((uint32_t)block[i*4u+1u] << 16) |
               ((uint32_t)block[i*4u+2u] << 8) | block[i*4u+3u];
    for (i = 16u; i < 64u; ++i) {
        uint32_t s0 = g1_panel_rotr32(w[i-15u],7u) ^ g1_panel_rotr32(w[i-15u],18u) ^ (w[i-15u] >> 3);
        uint32_t s1 = g1_panel_rotr32(w[i-2u],17u) ^ g1_panel_rotr32(w[i-2u],19u) ^ (w[i-2u] >> 10);
        w[i] = w[i-16u] + s0 + w[i-7u] + s1;
    }
    a=ctx->state[0]; b=ctx->state[1]; c=ctx->state[2]; d=ctx->state[3];
    e=ctx->state[4]; f=ctx->state[5]; g=ctx->state[6]; h=ctx->state[7];
    for (i = 0u; i < 64u; ++i) {
        uint32_t s1 = g1_panel_rotr32(e,6u) ^ g1_panel_rotr32(e,11u) ^ g1_panel_rotr32(e,25u);
        uint32_t ch = (e & f) ^ (~e & g);
        uint32_t t1 = h + s1 + ch + k[i] + w[i];
        uint32_t s0 = g1_panel_rotr32(a,2u) ^ g1_panel_rotr32(a,13u) ^ g1_panel_rotr32(a,22u);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        uint32_t t2 = s0 + maj;
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    ctx->state[0]+=a; ctx->state[1]+=b; ctx->state[2]+=c; ctx->state[3]+=d;
    ctx->state[4]+=e; ctx->state[5]+=f; ctx->state[6]+=g; ctx->state[7]+=h;
}

static inline void g1_panel_sha256_init(G1PanelSha256 *ctx)
{
    static const uint32_t initial[8] = {0x6a09e667u,0xbb67ae85u,0x3c6ef372u,0xa54ff53au,
        0x510e527fu,0x9b05688cu,0x1f83d9abu,0x5be0cd19u};
    unsigned int i;
    for (i=0u;i<8u;++i) ctx->state[i]=initial[i];
    ctx->total_bits=0u; ctx->used=0u;
}

static inline void g1_panel_sha256_update(G1PanelSha256 *ctx,
                                           const uint8_t *data, size_t length)
{
    size_t take;
    while (length) {
        take = 64u - ctx->used;
        if (take > length) take = length;
        { size_t i; volatile uint8_t *block = ctx->block;
          for (i=0u;i<take;++i) block[ctx->used+i]=data[i]; }
        ctx->used += take; data += take; length -= take;
        if (ctx->used == 64u) {
            g1_panel_sha256_transform(ctx, ctx->block);
            ctx->total_bits += 512u; ctx->used = 0u;
        }
    }
}

static inline void g1_panel_sha256_final(G1PanelSha256 *ctx, uint8_t digest[32])
{
    unsigned int i;
    ctx->total_bits += (uint64_t)ctx->used * 8u;
    ctx->block[ctx->used++] = 0x80u;
    if (ctx->used > 56u) {
        while (ctx->used < 64u) ctx->block[ctx->used++] = 0u;
        g1_panel_sha256_transform(ctx, ctx->block); ctx->used = 0u;
    }
    while (ctx->used < 56u) ctx->block[ctx->used++] = 0u;
    for (i=0u;i<8u;++i) ctx->block[56u+i]=(uint8_t)(ctx->total_bits >> (56u-i*8u));
    g1_panel_sha256_transform(ctx, ctx->block);
    for (i=0u;i<8u;++i) {
        digest[i*4u]=(uint8_t)(ctx->state[i]>>24);
        digest[i*4u+1u]=(uint8_t)(ctx->state[i]>>16);
        digest[i*4u+2u]=(uint8_t)(ctx->state[i]>>8);
        digest[i*4u+3u]=(uint8_t)ctx->state[i];
    }
}

static inline int g1_panel_sha256_rows(const uint8_t *source, size_t stride,
                                       size_t width, size_t height, char output[65])
{
    static const char hex[] = "0123456789abcdef";
    G1PanelSha256 ctx;
    uint8_t digest[32];
    size_t y, i;
    if (!source || !output || stride < width || !width || !height) return 0;
    g1_panel_sha256_init(&ctx);
    for (y=0u;y<height;++y) g1_panel_sha256_update(&ctx, source+y*stride, width);
    g1_panel_sha256_final(&ctx, digest);
    for (i=0u;i<32u;++i) { output[i*2u]=hex[digest[i]>>4]; output[i*2u+1u]=hex[digest[i]&15u]; }
    output[64]='\0';
    return 1;
}

/* Decode the panel's byte RLE.  0xFE,count emits count key pixels. */
static inline int g1_panel_decode_rows(const uint8_t *source, size_t source_bytes,
                                       size_t width, size_t height,
                                       size_t destination_stride,
                                       uint8_t *destination)
{
    size_t cursor = 0u, y, x;
    if (!source || !destination || !width || !height ||
        destination_stride < width) return 0;
    for (y = 0u; y < height; ++y) {
        uint8_t *row = destination + y * destination_stride;
        for (x = 0u; x < width;) {
            uint8_t value;
            size_t count;
            if (cursor >= source_bytes) return 0;
            value = source[cursor++];
            count = 1u;
            if (value == G1_PANEL_KEY) {
                if (cursor >= source_bytes) return 0;
                count = source[cursor++];
                if (!count) return 0;
                value = G1_PANEL_KEY;
            }
            if (count > width - x) return 0;
            while (count--) row[x++] = value;
        }
    }
    return cursor == source_bytes;
}

/* The original writer uses pitch 800 while consuming 831 source columns. */
static inline int g1_panel_fold_frame(const uint8_t *source,
                                      size_t source_stride,
                                      uint8_t *destination,
                                      size_t destination_stride,
                                      size_t width, size_t height)
{
    size_t y, x;
    if (!source || !destination || !width || !height ||
        source_stride < width || destination_stride < width) return 0;
    for (y = 0u; y < height; ++y)
        for (x = 0u; x < width; ++x)
            destination[y * destination_stride + x] =
                source[y * source_stride + x];
    return 1;
}

static inline int g1_panel_frame_equal(const uint8_t *left, size_t left_stride,
                                       const uint8_t *right, size_t right_stride,
                                       size_t width, size_t height)
{
    size_t y, x;
    if (!left || !right || left_stride < width || right_stride < width) return 0;
    for (y = 0u; y < height; ++y)
        for (x = 0u; x < width; ++x)
            if (left[y * left_stride + x] != right[y * right_stride + x]) return 0;
    return 1;
}

static inline int g1_panel_build_scale2x(const uint8_t *source, size_t source_stride,
                                         size_t width, size_t height,
                                         uint8_t *destination,
                                         size_t destination_stride)
{
    size_t x, y;
    if (!source || !destination || !width || !height || source_stride < width ||
        destination_stride < width * 2u) return 0;
    for (y = 0u; y < height; ++y) {
        size_t top = y ? y - 1u : y;
        size_t bottom = y + 1u < height ? y + 1u : y;
        for (x = 0u; x < width; ++x) {
            size_t left = x ? x - 1u : x;
            size_t right = x + 1u < width ? x + 1u : x;
            uint8_t e = source[y * source_stride + x];
            uint8_t b = source[top * source_stride + x];
            uint8_t d = source[y * source_stride + left];
            uint8_t f = source[y * source_stride + right];
            uint8_t h = source[bottom * source_stride + x];
            uint8_t p0 = e, p1 = e, p2 = e, p3 = e;
            if (b != h && d != f) {
                p0 = d == b ? d : e;
                p1 = b == f ? f : e;
                p2 = d == h ? d : e;
                p3 = h == f ? f : e;
            }
            if (e != G1_PANEL_KEY) {
                if (p0 == G1_PANEL_KEY) p0 = e;
                if (p1 == G1_PANEL_KEY) p1 = e;
                if (p2 == G1_PANEL_KEY) p2 = e;
                if (p3 == G1_PANEL_KEY) p3 = e;
            }
            {
                uint8_t *row = destination + y * 2u * destination_stride + x * 2u;
                row[0] = p0; row[1] = p1;
                row[destination_stride] = p2;
                row[destination_stride + 1u] = p3;
            }
        }
    }
    return 1;
}

static inline size_t g1_panel_key_subpixels(const uint8_t *source,
                                             size_t source_stride,
                                             size_t width, size_t height,
                                             const uint8_t *hd,
                                             size_t hd_stride)
{
    size_t count = 0u, x, y;
    if (!source || !hd || source_stride < width || hd_stride < width * 2u)
        return (size_t)-1;
    for (y = 0u; y < height; ++y)
        for (x = 0u; x < width; ++x)
            if (source[y * source_stride + x] != G1_PANEL_KEY) {
                const uint8_t *pixel = hd + y * 2u * hd_stride + x * 2u;
                count += (pixel[0] == G1_PANEL_KEY) +
                         (pixel[1] == G1_PANEL_KEY) +
                         (pixel[hd_stride] == G1_PANEL_KEY) +
                         (pixel[hd_stride + 1u] == G1_PANEL_KEY);
            }
    return count;
}

static inline int g1_panel_apply_transfer(
    const uint8_t *panel_expected, const uint8_t *panel_covered,
    const uint8_t *panel_hd, size_t panel_stride, size_t panel_hd_stride,
    const uint8_t *actual, size_t actual_stride,
    size_t source_x, size_t source_y, size_t destination_x, size_t destination_y,
    size_t width, size_t height, uint8_t *screen_expected,
    uint8_t *screen_covered, uint8_t *screen_hd,
    size_t screen_stride, size_t screen_hd_stride,
    size_t screen_width, size_t screen_height, G1PanelTransferStats *stats)
{
    size_t x, y;
    G1PanelTransferStats result = {0u, 0u, 0u, 0u};
    if (!panel_expected || !panel_covered || !panel_hd || !actual ||
        !screen_expected || !screen_covered || !screen_hd || !stats ||
        panel_stride < source_x + width || actual_stride < source_x + width ||
        screen_stride < screen_width || panel_hd_stride < panel_stride * 2u ||
        screen_hd_stride < screen_stride * 2u || source_y + height > 203u ||
        destination_x + width > screen_width || destination_y + height > screen_height)
        return 0;
    for (y = 0u; y < height; ++y) {
        for (x = 0u; x < width; ++x) {
            size_t panel = (source_y + y) * panel_stride + source_x + x;
            size_t screen = (destination_y + y) * screen_stride + destination_x + x;
            uint8_t value = actual[(source_y + y) * actual_stride + source_x + x];
            if (value == G1_PANEL_KEY) {
                ++result.key_preserved;
            } else if (panel_covered[panel] && panel_expected[panel] == value) {
                size_t src = (source_y + y) * 2u * panel_hd_stride + (source_x + x) * 2u;
                size_t dst = (destination_y + y) * 2u * screen_hd_stride + (destination_x + x) * 2u;
                screen_expected[screen] = value;
                screen_covered[screen] = 1u;
                screen_hd[dst] = panel_hd[src];
                screen_hd[dst + 1u] = panel_hd[src + 1u];
                screen_hd[dst + screen_hd_stride] = panel_hd[src + panel_hd_stride];
                screen_hd[dst + screen_hd_stride + 1u] = panel_hd[src + panel_hd_stride + 1u];
                ++result.copied;
            } else {
                screen_covered[screen] = 0u;
                ++result.mismatch_cleared;
            }
        }
    }
    stats->copied = result.copied;
    stats->key_preserved = result.key_preserved;
    stats->mismatch_cleared = result.mismatch_cleared;
    stats->uncovered = result.uncovered;
    return 1;
}

#endif

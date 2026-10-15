#ifndef G1_SHA256_H
#define G1_SHA256_H

#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t state[8];
    uint64_t bytes;
    uint8_t block[64];
    size_t used;
} G1Sha256;

static const uint32_t g1_sha256_k[64] = {
    0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
    0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
    0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
    0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
    0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
    0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
    0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
    0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u
};

static uint32_t g1_sha256_rotr(uint32_t x, unsigned n) { return (x >> n) | (x << (32u - n)); }

static void g1_sha256_transform(G1Sha256 *ctx, const uint8_t block[64])
{
    uint32_t w[64], a,b,c,d,e,f,g,h,t1,t2;
    unsigned i;
    for (i = 0; i < 16u; ++i)
        w[i] = ((uint32_t)block[i*4u] << 24) | ((uint32_t)block[i*4u+1u] << 16) |
               ((uint32_t)block[i*4u+2u] << 8) | block[i*4u+3u];
    for (; i < 64u; ++i) {
        uint32_t s0 = g1_sha256_rotr(w[i-15u],7u) ^ g1_sha256_rotr(w[i-15u],18u) ^ (w[i-15u] >> 3);
        uint32_t s1 = g1_sha256_rotr(w[i-2u],17u) ^ g1_sha256_rotr(w[i-2u],19u) ^ (w[i-2u] >> 10);
        w[i] = w[i-16u] + s0 + w[i-7u] + s1;
    }
    a=ctx->state[0]; b=ctx->state[1]; c=ctx->state[2]; d=ctx->state[3];
    e=ctx->state[4]; f=ctx->state[5]; g=ctx->state[6]; h=ctx->state[7];
    for (i = 0; i < 64u; ++i) {
        uint32_t s1 = g1_sha256_rotr(e,6u) ^ g1_sha256_rotr(e,11u) ^ g1_sha256_rotr(e,25u);
        uint32_t ch = (e & f) ^ (~e & g);
        uint32_t s0 = g1_sha256_rotr(a,2u) ^ g1_sha256_rotr(a,13u) ^ g1_sha256_rotr(a,22u);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        t1 = h + s1 + ch + g1_sha256_k[i] + w[i]; t2 = s0 + maj;
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    ctx->state[0]+=a; ctx->state[1]+=b; ctx->state[2]+=c; ctx->state[3]+=d;
    ctx->state[4]+=e; ctx->state[5]+=f; ctx->state[6]+=g; ctx->state[7]+=h;
}

static void g1_sha256_init(G1Sha256 *ctx)
{
    static const uint32_t initial[8] = {0x6a09e667u,0xbb67ae85u,0x3c6ef372u,0xa54ff53au,
        0x510e527fu,0x9b05688cu,0x1f83d9abu,0x5be0cd19u};
    unsigned i;
    for (i=0;i<8u;++i) ctx->state[i]=initial[i];
    ctx->bytes=0; ctx->used=0;
}

static void g1_sha256_update(G1Sha256 *ctx, const void *data, size_t length)
{
    const uint8_t *input = (const uint8_t *)data;
    ctx->bytes += length;
    while (length) {
        size_t take = 64u - ctx->used;
        if (take > length) take = length;
        { size_t i; volatile uint8_t *out = ctx->block + ctx->used;
          for (i=0;i<take;++i) out[i]=input[i]; }
        ctx->used += take; input += take; length -= take;
        if (ctx->used == 64u) { g1_sha256_transform(ctx, ctx->block); ctx->used=0; }
    }
}

static void g1_sha256_final(G1Sha256 *ctx, uint8_t digest[32])
{
    uint64_t bits = ctx->bytes * 8u;
    unsigned i;
    ctx->block[ctx->used++] = 0x80u;
    if (ctx->used > 56u) {
        while (ctx->used < 64u) ctx->block[ctx->used++]=0;
        g1_sha256_transform(ctx, ctx->block); ctx->used=0;
    }
    while (ctx->used < 56u) ctx->block[ctx->used++]=0;
    for (i=0;i<8u;++i) ctx->block[56u+i]=(uint8_t)(bits >> (56u-8u*i));
    g1_sha256_transform(ctx, ctx->block);
    for (i=0;i<8u;++i) {
        digest[i*4u]=(uint8_t)(ctx->state[i]>>24); digest[i*4u+1u]=(uint8_t)(ctx->state[i]>>16);
        digest[i*4u+2u]=(uint8_t)(ctx->state[i]>>8); digest[i*4u+3u]=(uint8_t)ctx->state[i];
    }
}

#endif

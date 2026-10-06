#ifndef G1_CENSUS_RESIDUAL_H
#define G1_CENSUS_RESIDUAL_H

/* Opt-in shadow comparison for the writer census (SYW2_G1_CENSUS_RESIDUAL=1).
 * The shadow holds the buffer as it was right after the last hooked writer;
 * pixels that differ at present were written by something no hook saw.  Pure
 * and platform independent so host tests can compile it; no CRT calls. */
#define G1_RESIDUAL_WIDTH 800u
#define G1_RESIDUAL_HEIGHT 600u

typedef struct {
    unsigned long pixels;
    int min_x, min_y, max_x, max_y;
    unsigned long histogram[256];
} G1CensusResidual;

/* Copy buffer rectangle (x,y,width,height) into the compact 800-wide shadow.
 * Returns 0 and leaves the shadow untouched for an out-of-range rectangle. */
static inline int g1_census_residual_sync(unsigned char *shadow,
                                          const unsigned char *buffer,
                                          unsigned long pitch, unsigned x,
                                          unsigned y, unsigned width,
                                          unsigned height)
{
    unsigned row, col;
    if (!shadow || !buffer || pitch < G1_RESIDUAL_WIDTH || width == 0u ||
        height == 0u || x > G1_RESIDUAL_WIDTH || width > G1_RESIDUAL_WIDTH - x ||
        y > G1_RESIDUAL_HEIGHT || height > G1_RESIDUAL_HEIGHT - y) return 0;
    for (row = 0; row < height; ++row)
        for (col = 0; col < width; ++col)
            shadow[(y + row) * G1_RESIDUAL_WIDTH + x + col] =
                buffer[(unsigned long)(y + row) * pitch + x + col];
    return 1;
}

/* Count screen pixels where buffer != shadow; optionally mark them in mask. */
static inline void g1_census_residual_compare(const unsigned char *shadow,
                                              const unsigned char *buffer,
                                              unsigned long pitch,
                                              G1CensusResidual *out,
                                              unsigned char *mask)
{
    unsigned x, y;
    for (x = 0; x < 256u; ++x) out->histogram[x] = 0u;
    out->pixels = 0u;
    out->min_x = out->min_y = out->max_x = out->max_y = -1;
    if (!shadow || !buffer || pitch < G1_RESIDUAL_WIDTH) return;
    for (y = 0; y < G1_RESIDUAL_HEIGHT; ++y)
        for (x = 0; x < G1_RESIDUAL_WIDTH; ++x) {
            unsigned char now = buffer[(unsigned long)y * pitch + x];
            if (now == shadow[y * G1_RESIDUAL_WIDTH + x]) continue;
            ++out->pixels;
            ++out->histogram[now];
            if (mask) mask[y * G1_RESIDUAL_WIDTH + x] = 1u;
            if (out->min_x < 0 || (int)x < out->min_x) out->min_x = (int)x;
            if (out->min_y < 0 || (int)y < out->min_y) out->min_y = (int)y;
            if ((int)x > out->max_x) out->max_x = (int)x;
            if ((int)y > out->max_y) out->max_y = (int)y;
        }
}

#endif

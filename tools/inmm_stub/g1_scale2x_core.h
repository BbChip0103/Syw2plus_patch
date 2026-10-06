#ifndef G1_SCALE2X_CORE_H
#define G1_SCALE2X_CORE_H

#include <stddef.h>
#include <stdint.h>

/* Portable kernel shared by the Windows bridge and host-gcc regression test. */
static inline int g1_scale2x_build_masked(
    const uint8_t *source, size_t source_stride,
    const uint8_t *written, size_t written_stride,
    size_t width, size_t height,
    uint8_t *destination, size_t destination_stride)
{
    size_t x, y;
    if (!source || !written || !destination || !width || !height ||
        source_stride < width || written_stride < width ||
        destination_stride < width * 2u) return 0;

    for (y = 0; y < height; ++y) {
        for (x = 0; x < width; ++x) {
            const size_t left_x = x ? x - 1u : x;
            const size_t right_x = x + 1u < width ? x + 1u : x;
            const size_t top_y = y ? y - 1u : y;
            const size_t bottom_y = y + 1u < height ? y + 1u : y;
            const size_t center_offset = y * source_stride + x;
            const uint8_t e = source[center_offset];
            uint8_t p0 = e, p1 = e, p2 = e, p3 = e;
            if (written[y * written_stride + x]) {
                const uint8_t b = written[top_y * written_stride + x]
                    ? source[top_y * source_stride + x] : e;
                const uint8_t d = written[y * written_stride + left_x]
                    ? source[y * source_stride + left_x] : e;
                const uint8_t f = written[y * written_stride + right_x]
                    ? source[y * source_stride + right_x] : e;
                const uint8_t h = written[bottom_y * written_stride + x]
                    ? source[bottom_y * source_stride + x] : e;
                if (b != h && d != f) {
                    p0 = d == b ? d : e;
                    p1 = b == f ? f : e;
                    p2 = d == h ? d : e;
                    p3 = h == f ? f : e;
                }
            }
            {
                uint8_t *row = destination + (y * 2u) * destination_stride + x * 2u;
                row[0] = p0;
                row[1] = p1;
                row[destination_stride] = p2;
                row[destination_stride + 1u] = p3;
            }
        }
    }
    return 1;
}

#endif

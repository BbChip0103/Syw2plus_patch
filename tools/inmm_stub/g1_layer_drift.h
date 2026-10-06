#ifndef G1_LAYER_DRIFT_H
#define G1_LAYER_DRIFT_H

/* lap1015 H-S2d: opt-in (SYW2_G1_LAYER_DRIFT=1, mirror candidate only)
 * diagnostic for the 1x terrain-cache layer drift.  A pixel is "drifted" when
 * the candidate layer is covered but the live cache byte differs from the
 * value composed into g_layer_expected.  Pure helpers so host tests can
 * compile them; no CRT calls.  Geometry is the three save000 stale
 * components found in lap1010/lap1012 (cache coordinates, pitch 832). */
#define G1_LAYER_DRIFT_RECTS 3u
#define G1_LAYER_DRIFT_CACHE_PITCH 832u
#define G1_LAYER_DRIFT_SCREEN_WIDTH 800u

/* Call-level outcomes of one cache-target mirror_reinvoke (rect overlap
 * counted per call), then the per-pixel results of compose_cache_layer. */
#define G1_DRIFT_RET_ARGS 0u
#define G1_DRIFT_RET_BUFFER 1u
#define G1_DRIFT_RET_PANEL_FOREIGN 2u
#define G1_DRIFT_RET_RANGE 3u
#define G1_DRIFT_NOT_READY 4u
#define G1_DRIFT_COMPOSE_BOUNDS 5u
#define G1_DRIFT_COMPOSE_RAN 6u
#define G1_DRIFT_CALL_REASONS 7u
#define G1_DRIFT_PX_A_NE_B 0u
#define G1_DRIFT_PX_UNWRITTEN 1u
#define G1_DRIFT_PX_LOOKUP_MISS 2u
#define G1_DRIFT_PX_COMPOSED 3u
#define G1_DRIFT_PX_RESULTS 4u
/* Last-event result code of a sample point: call reasons 0..6, pixels 16+. */
#define G1_DRIFT_EVENT_PIXEL_BASE 16u

typedef struct {
    unsigned x0, y0, x1, y1; /* half-open */
} G1LayerDriftRect;

typedef struct {
    unsigned stale;          /* layer covered && cache != layer_expected */
    unsigned uncovered;      /* layer not covered */
    unsigned screen_ne_cache;/* present source pixel != cache byte */
    unsigned snap_ne_layer;  /* screen covered && snapshot != layer_expected */
} G1LayerDriftCounts;

static inline G1LayerDriftRect g1_layer_drift_rect(unsigned index)
{
    static const G1LayerDriftRect rects[G1_LAYER_DRIFT_RECTS] = {
        {38u, 64u, 187u, 169u},   /* A x38..186 y64..168 */
        {371u, 427u, 503u, 492u}, /* B x371..502 y427..491 */
        {259u, 0u, 338u, 26u},    /* C x259..337 y0..25 */
    };
    G1LayerDriftRect empty = {0u, 0u, 0u, 0u};
    return index < G1_LAYER_DRIFT_RECTS ? rects[index] : empty;
}

/* Sample points, default inside rect[index]: A (112,126), B (437,463), C (302,9).
 * SYW2_G1_DRIFT_SAMPLES=x,y;x,y;x,y (g1_layer_drift_samples_parse) replaces them
 * for diagnostics; every translation unit owns and parses its own copy. */
#define G1_LAYER_DRIFT_SAMPLE_WIDTH 800u
#define G1_LAYER_DRIFT_SAMPLE_HEIGHT 600u
static unsigned g1_layer_drift_points[G1_LAYER_DRIFT_RECTS][2] = {
    {112u, 126u}, {437u, 463u}, {302u, 9u},
};

static inline void g1_layer_drift_sample(unsigned index, unsigned *x, unsigned *y)
{
    *x = index < G1_LAYER_DRIFT_RECTS ? g1_layer_drift_points[index][0] : 0u;
    *y = index < G1_LAYER_DRIFT_RECTS ? g1_layer_drift_points[index][1] : 0u;
}

/* Exactly three "x,y" points joined by ';', each coordinate 1..4 digits inside
 * the 800x600 screen.  Returns 0 for anything else and keeps the points. */
static inline int g1_layer_drift_samples_parse(const char *text, unsigned long length)
{
    unsigned parsed[G1_LAYER_DRIFT_RECTS][2];
    unsigned long i = 0ul;
    unsigned point, axis, digits, value;
    if (!text) return 0;
    for (point = 0u; point < G1_LAYER_DRIFT_RECTS; ++point) {
        for (axis = 0u; axis < 2u; ++axis) {
            digits = 0u;
            value = 0u;
            while (i < length && text[i] >= '0' && text[i] <= '9') {
                if (++digits > 4u) return 0;
                value = value * 10u + (unsigned)(text[i] - '0');
                ++i;
            }
            if (digits == 0u) return 0;
            if (value >= (axis == 0u ? G1_LAYER_DRIFT_SAMPLE_WIDTH : G1_LAYER_DRIFT_SAMPLE_HEIGHT)) return 0;
            parsed[point][axis] = value;
            if (axis == 0u) {
                if (i >= length || text[i] != ',') return 0;
                ++i;
            }
        }
        if (point + 1u < G1_LAYER_DRIFT_RECTS) {
            if (i >= length || text[i] != ';') return 0;
            ++i;
        }
    }
    if (i != length) return 0;
    for (point = 0u; point < G1_LAYER_DRIFT_RECTS; ++point) {
        g1_layer_drift_points[point][0] = parsed[point][0];
        g1_layer_drift_points[point][1] = parsed[point][1];
    }
    return 1;
}

static inline int g1_layer_drift_contains(unsigned index, long x, long y)
{
    G1LayerDriftRect r = g1_layer_drift_rect(index);
    return x >= (long)r.x0 && x < (long)r.x1 && y >= (long)r.y0 && y < (long)r.y1;
}

/* Pixels of the width x height region at (ox, oy) that fall inside rect[index]. */
static inline unsigned g1_layer_drift_overlap(unsigned index, long ox, long oy,
                                              unsigned width, unsigned height)
{
    G1LayerDriftRect r = g1_layer_drift_rect(index);
    long left = ox > (long)r.x0 ? ox : (long)r.x0;
    long top = oy > (long)r.y0 ? oy : (long)r.y0;
    long right = ox + (long)width < (long)r.x1 ? ox + (long)width : (long)r.x1;
    long bottom = oy + (long)height < (long)r.y1 ? oy + (long)height : (long)r.y1;
    if (right <= left || bottom <= top) return 0u;
    return (unsigned)(right - left) * (unsigned)(bottom - top);
}

/* Count the four drift classes over rect[index].  cache is the live 1x cache
 * (pitch 832), layer_* the candidate layer (pitch 832), screen the present
 * source surface, snapshot/covered the 800x600 candidate screen state. */
static inline void g1_layer_drift_count(unsigned index, const unsigned char *cache,
                                        const unsigned char *layer_expected,
                                        const unsigned char *layer_covered,
                                        const unsigned char *screen,
                                        unsigned screen_pitch,
                                        const unsigned char *snapshot,
                                        const unsigned char *covered,
                                        G1LayerDriftCounts *out)
{
    G1LayerDriftRect r = g1_layer_drift_rect(index);
    unsigned x, y;
    out->stale = out->uncovered = out->screen_ne_cache = out->snap_ne_layer = 0u;
    for (y = r.y0; y < r.y1; ++y) {
        for (x = r.x0; x < r.x1; ++x) {
            unsigned layer_index = y * G1_LAYER_DRIFT_CACHE_PITCH + x;
            unsigned screen_index = y * G1_LAYER_DRIFT_SCREEN_WIDTH + x;
            unsigned char live = cache[layer_index];
            if (layer_covered[layer_index]) {
                if (live != layer_expected[layer_index]) ++out->stale;
            } else {
                ++out->uncovered;
            }
            if (screen[y * screen_pitch + x] != live) ++out->screen_ne_cache;
            if (covered[screen_index] &&
                snapshot[screen_index] != layer_expected[layer_index])
                ++out->snap_ne_layer;
        }
    }
}

#endif

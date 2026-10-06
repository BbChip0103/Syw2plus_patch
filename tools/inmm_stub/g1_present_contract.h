#ifndef G1_PRESENT_CONTRACT_H
#define G1_PRESENT_CONTRACT_H

/*
 * Surface-role eligibility for W60.  This header is intentionally free of
 * Win32/DirectDraw types so the exact production gate can be compiled by a
 * host-side regression fixture as well as by the PE32 bridge.
 */

#define G1_PRESENT_CAPS_PRIMARYSURFACE 0x00000200u
#define G1_PRESENT_CAPS_BACKBUFFER     0x00000004u

enum {
    G1_PRESENT_REJECT_NONE = 0,
    G1_PRESENT_REJECT_MISSING_DESCRIPTOR = 1,
    G1_PRESENT_REJECT_NOT_PRIMARY = 2,
    G1_PRESENT_REJECT_DESTINATION_SIZE = 3,
    G1_PRESENT_REJECT_SOURCE_MISSING = 4,
    G1_PRESENT_REJECT_SAME_SURFACE = 5,
    G1_PRESENT_REJECT_OFFSCREEN_SHAPE = 6,
    G1_PRESENT_REJECT_MENU_ROLE = 7,
    G1_PRESENT_REJECT_RECT = 8
};

enum {
    G1_PRESENT_VARIANT_NONE = 0,
    G1_PRESENT_VARIANT_OFFSCREEN_800 = 1,
    G1_PRESENT_VARIANT_MENU_BACKBUFFER = 2
};

#if defined(__GNUC__) || defined(__clang__)
#define G1_PRESENT_UNUSED __attribute__((unused))
#else
#define G1_PRESENT_UNUSED
#endif

typedef struct {
    unsigned int destination_identity;
    unsigned int source_identity;
    unsigned int destination_caps;
    unsigned int source_caps;
    unsigned int destination_width;
    unsigned int destination_height;
    unsigned int source_width;
    unsigned int source_height;
    int destination_descriptor_known;
    int source_descriptor_known;
    unsigned int x;
    unsigned int y;
    int source_rect_present;
    int source_left;
    int source_top;
    int source_right;
    int source_bottom;
} G1PresentGateInput;

typedef struct {
    int eligible;
    unsigned int variant;
    unsigned int reject_reason;
    int source_left;
    int source_top;
    int source_right;
    int source_bottom;
    int destination_left;
    int destination_top;
    int destination_right;
    int destination_bottom;
} G1PresentGateDecision;

static int g1_present_gate_rect_valid(const G1PresentGateInput *input,
                                      const G1PresentGateDecision *decision)
{
    int width = decision->source_right - decision->source_left;
    int height = decision->source_bottom - decision->source_top;
    return input->x <= 800u && input->y <= 600u &&
           input->x + (unsigned int)width <= 800u &&
           input->y + (unsigned int)height <= 600u;
}

static G1_PRESENT_UNUSED G1PresentGateDecision g1_present_gate_decide(const G1PresentGateInput *input)
{
    G1PresentGateDecision decision;
    int offscreen_shape;
    int menu_shape;

    decision.eligible = 0;
    decision.variant = G1_PRESENT_VARIANT_NONE;
    decision.reject_reason = G1_PRESENT_REJECT_MISSING_DESCRIPTOR;
    decision.source_left = 0;
    decision.source_top = 0;
    decision.source_right = 0;
    decision.source_bottom = 0;
    decision.destination_left = 0;
    decision.destination_top = 0;
    decision.destination_right = 0;
    decision.destination_bottom = 0;
    if (!input || !input->destination_descriptor_known ||
        !input->source_descriptor_known) return decision;
    if (!(input->destination_caps & G1_PRESENT_CAPS_PRIMARYSURFACE)) {
        decision.reject_reason = G1_PRESENT_REJECT_NOT_PRIMARY;
        return decision;
    }
    if (input->destination_width != 1600u || input->destination_height != 1200u) {
        decision.reject_reason = G1_PRESENT_REJECT_DESTINATION_SIZE;
        return decision;
    }
    if (input->source_identity == 0u) {
        decision.reject_reason = G1_PRESENT_REJECT_SOURCE_MISSING;
        return decision;
    }
    if (input->source_identity == input->destination_identity) {
        decision.reject_reason = G1_PRESENT_REJECT_SAME_SURFACE;
        return decision;
    }

    offscreen_shape = input->source_width >= 800u && input->source_height == 600u;
    menu_shape = input->source_width == 1600u && input->source_height == 1200u &&
        (input->source_caps & G1_PRESENT_CAPS_BACKBUFFER) != 0u &&
        (input->source_caps & G1_PRESENT_CAPS_PRIMARYSURFACE) == 0u &&
        input->x == 0u && input->y == 0u && !input->source_rect_present;
    if (menu_shape) {
        decision.variant = G1_PRESENT_VARIANT_MENU_BACKBUFFER;
        decision.source_right = 800;
        decision.source_bottom = 600;
    } else if (offscreen_shape) {
        decision.variant = G1_PRESENT_VARIANT_OFFSCREEN_800;
        if (input->source_rect_present) {
            decision.source_left = input->source_left;
            decision.source_top = input->source_top;
            decision.source_right = input->source_right;
            decision.source_bottom = input->source_bottom;
        } else {
            decision.source_right = 800;
            decision.source_bottom = 600;
        }
    } else {
        decision.reject_reason = input->source_width == 1600u &&
            input->source_height == 1200u
            ? G1_PRESENT_REJECT_MENU_ROLE : G1_PRESENT_REJECT_OFFSCREEN_SHAPE;
        return decision;
    }
    if (decision.source_left < 0 || decision.source_top < 0 ||
        decision.source_right <= decision.source_left ||
        decision.source_bottom <= decision.source_top ||
        decision.source_right - decision.source_left != 800 ||
        decision.source_bottom - decision.source_top != 600 ||
        !g1_present_gate_rect_valid(input, &decision)) {
        decision.variant = G1_PRESENT_VARIANT_NONE;
        decision.reject_reason = G1_PRESENT_REJECT_RECT;
        return decision;
    }
    decision.destination_right = (int)(input->x * 2u) + 1600;
    decision.destination_bottom = (int)(input->y * 2u) + 1200;
    if (decision.destination_right > 1600 || decision.destination_bottom > 1200) {
        decision.variant = G1_PRESENT_VARIANT_NONE;
        decision.reject_reason = G1_PRESENT_REJECT_RECT;
        return decision;
    }
    decision.destination_left = (int)(input->x * 2u);
    decision.destination_top = (int)(input->y * 2u);
    decision.eligible = 1;
    decision.reject_reason = G1_PRESENT_REJECT_NONE;
    return decision;
}

static G1_PRESENT_UNUSED const char *g1_present_reject_name(unsigned int reason)
{
    switch (reason) {
    case G1_PRESENT_REJECT_NONE: return "none";
    case G1_PRESENT_REJECT_MISSING_DESCRIPTOR: return "missing_descriptor";
    case G1_PRESENT_REJECT_NOT_PRIMARY: return "not_primary";
    case G1_PRESENT_REJECT_DESTINATION_SIZE: return "destination_size";
    case G1_PRESENT_REJECT_SOURCE_MISSING: return "source_missing";
    case G1_PRESENT_REJECT_SAME_SURFACE: return "same_surface";
    case G1_PRESENT_REJECT_OFFSCREEN_SHAPE: return "offscreen_shape";
    case G1_PRESENT_REJECT_MENU_ROLE: return "menu_role";
    case G1_PRESENT_REJECT_RECT: return "rect";
    default: return "unknown";
    }
}

#undef G1_PRESENT_UNUSED

#endif /* G1_PRESENT_CONTRACT_H */

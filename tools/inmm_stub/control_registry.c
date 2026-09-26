/* control_registry.c — goal → state 매핑 테이블 (Win32 전용, CRT 없음) */

#include <windows.h>
#include "control_registry.h"

#define BP_SIH  { BRIDGE_PRIO_STATE, BRIDGE_PRIO_INPUT, BRIDGE_PRIO_HANDLER }
#define BP_SI   { BRIDGE_PRIO_STATE, BRIDGE_PRIO_INPUT, -1 }
#define BP_SH   { BRIDGE_PRIO_STATE, BRIDGE_PRIO_HANDLER, -1 }

#define DOWNGRADE_WINDOW  "[0x66976C]==0"

static const goal_entry_t s_registry[] = {
    { "enter_title",           8,  9,  5000, TRUE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SI,
      { 0, 40, 180, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_scenario_select", 14, 15, 5000, TRUE,
      BRIDGE_OK,      BRIDGE_UNKNOWN,
      500, TRUE, BP_SI,
      { 9, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_custom_game",     6,  7,  5000, TRUE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SI,
      { 9, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_scenario_ingame", 1,  3,  8000, FALSE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      800, TRUE, BP_SIH,
      { 20, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    /* R4 추가 (06 플랜 §6 필수 범위) */

    { "enter_briefing",        16, 20, 6000, TRUE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SIH,
      { 15, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_lobby",           4,  5,  5000, TRUE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SI,
      { 9, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_load_game",       35, 35, 5000, TRUE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SH,
      { 9, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_victory",         24, 25, 5000, FALSE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SH,
      { 3, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_defeat",          26, 27, 5000, FALSE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SH,
      { 3, -1, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },

    { "enter_battle_report",   28, 29, 5000, FALSE,
      BRIDGE_UNKNOWN, BRIDGE_UNKNOWN,
      500, TRUE, BP_SH,
      { 24, 26, -1, -1, -1, -1 }, DOWNGRADE_WINDOW },
};

#define REGISTRY_SIZE ((int)(sizeof(s_registry) / sizeof(s_registry[0])))

const goal_entry_t *control_registry_lookup(const char *goal)
{
    if (!goal) return NULL;
    for (int i = 0; i < REGISTRY_SIZE; ++i) {
        if (lstrcmpA(s_registry[i].goal, goal) == 0)
            return &s_registry[i];
    }
    return NULL;
}

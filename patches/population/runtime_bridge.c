/* Private diagnostic only. Evidence: population_runtime_bridge_0910.md. */
#include <windows.h>
#include "control_input_bridge.h"

#define REQUEST "C:\\supply_probe_request.txt"
#define RESULT "C:\\supply_probe_result.json"
#define RESULT_TMP "C:\\supply_probe_result.tmp"
#define LOG "C:\\supply_probe_log.jsonl"
#define U32(a) (*(volatile DWORD *)(ULONG_PTR)(a))
#define U16(a) (*(volatile USHORT *)(ULONG_PTR)(a))
#define S16(a) (*(volatile SHORT *)(ULONG_PTR)(a))
#define U8(a) (*(volatile BYTE *)(ULONG_PTR)(a))

static LONG busy;
static DWORD last_id;
static DWORD last_poll;
static BOOL fixture_failed;

static BOOL same_bytes(DWORD va, const BYTE *expected, DWORD length)
{
    DWORD i;
    for (i = 0; i < length; ++i)
        if (U8(va + i) != expected[i]) return FALSE;
    return TRUE;
}

static BOOL profile_matches(void)
{
    static const BYTE train[] = {0x53,0x66,0x8b,0x5c,0x24,0x0c,0x56,0x57};
    static const BYTE save[] = {0x8b,0x4c,0x24,0x04,0x81,0xec,0x00,0x01};
    static const BYTE load[] = {0x8b,0x4c,0x24,0x04,0x81,0xec,0x04,0x01};
    static const BYTE rice[] = {0x8b,0x44,0x24,0x04,0x89,0x41,0x14,0x50};
    static const BYTE wood[] = {0x8b,0x44,0x24,0x04,0x89,0x41,0x18,0x50};
    static const BYTE spawn[] = {0x55,0x8b,0x6c,0x24,0x08,0x0f,0xbf,0xc5};
    static const BYTE placement[] = {0x83,0xec,0x18,0x53,0x55,0x56,0x8b,0x74};
    static const BYTE gate[] = {0x66,0x83,0x7c,0x24,0x08,0x01};
    return (ULONG_PTR)GetModuleHandleA(NULL) == 0x400000u &&
           same_bytes(0x4af5e0,train,sizeof(train)) &&
           same_bytes(0x440c20,save,sizeof(save)) &&
           same_bytes(0x440ff0,load,sizeof(load)) &&
           same_bytes(0x43ed60,rice,sizeof(rice)) &&
           same_bytes(0x43ed80,wood,sizeof(wood)) &&
           same_bytes(0x443190,spawn,sizeof(spawn)) &&
           same_bytes(0x42ecb0,placement,sizeof(placement)) &&
           same_bytes(0x43eda0,gate,sizeof(gate)) &&
           U8(0x42334a) == 0xff && U8(0x42334b) == 0xd6;
}

static BOOL read_request(DWORD values[8])
{
    char text[256];
    DWORD count = 0, i, position = 0;
    HANDLE h = CreateFileA(REQUEST, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE |
                          FILE_SHARE_DELETE, NULL, OPEN_EXISTING, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return FALSE;
    if (!ReadFile(h,text,sizeof(text)-1,&count,NULL)) count = 0;
    CloseHandle(h);
    if (!count || count == sizeof(text)-1) return FALSE;
    text[count] = 0;
    for (i = 0; i < 8; ++i) {
        DWORD value = 0;
        while (position < count && (text[position] == ' ' || text[position] == '\n' ||
               text[position] == '\r' || text[position] == '\t')) ++position;
        if (text[position] < '0' || text[position] > '9') return FALSE;
        while (position < count && text[position] >= '0' && text[position] <= '9') {
            DWORD digit = (DWORD)(text[position++] - '0');
            if (value > (0xffffffffu-digit)/10u) return FALSE;
            value = value * 10u + digit;
        }
        values[i] = value;
    }
    while (position < count) {
        char c = text[position++];
        if (c != ' ' && c != '\n' && c != '\r' && c != '\t') return FALSE;
    }
    return values[0] != 0;
}

static void write_file(const char *path, const char *data, BOOL append)
{
    DWORD written;
    HANDLE h = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                          append ? OPEN_ALWAYS : CREATE_ALWAYS, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return;
    if (append) SetFilePointer(h,0,NULL,FILE_END);
    WriteFile(h,data,(DWORD)lstrlenA(data),&written,NULL);
    FlushFileBuffers(h);
    CloseHandle(h);
}

static void ledger(char *out, DWORD owner)
{
    DWORD p = 0x956770u + owner * 0x3abcu, live = 0, slot;
    for (slot = 1; slot < 1200; ++slot) {
        DWORD unit = 0x66b790u + slot * 0x758u;
        if (U16(0x8990c8u + slot*2u) && U8(unit+0x8e) == owner &&
            (LONG)U32(unit+0xb4) > 0) ++live;
    }
    wsprintfA(out,"{\"rice\":%u,\"wood\":%u,\"reserved\":%d,\"used\":%d,"
              "\"cap\":%d,\"count\":%d,\"live\":%u}",
              U32(p+0x14),U32(p+0x18),(LONG)U32(p+0x1c),
              (int)S16(p+0x200c),(int)S16(p+0x2012),(int)S16(p+0x200a),live);
}

/* Called only by the copied _imeGetTime export, passing its ORIGINAL caller. */
void supply_probe_poll(void *caller)
{
    DWORD request[8], owner, slot, type, op, raw = 0, p, tick_before, pid = 0;
    DWORD now, window_thread;
    DWORD fixture_added=0, fixture_attempts=0;
    HWND hwnd;
    char enabled[8], before[192], after[192], producer[160], extra[800], result[2048];
    const char *reason = "executed";
    BOOL ok = TRUE;
    if ((ULONG_PTR)caller != 0x42334cu) return;
    if (GetEnvironmentVariableA("SYW2_SUPPLY_PROBE",enabled,sizeof(enabled)) != 1 ||
        enabled[0] != '1') return;
    if (InterlockedCompareExchange(&busy,1,0) != 0) return;
    now = GetTickCount();
    if ((DWORD)(now-last_poll) < 25u) goto done;
    last_poll = now;
    hwnd = cib_get_hwnd();
    window_thread = hwnd ? GetWindowThreadProcessId(hwnd,&pid) : 0;
    if (!window_thread || pid != GetCurrentProcessId() ||
        window_thread != GetCurrentThreadId()) goto done;
    if (!read_request(request) || request[0] <= last_id) goto done;
    last_id = request[0];
    op=request[1]; owner=request[2]; slot=request[3]; type=request[4];
    tick_before = U32(0x8924b8);
    lstrcpyA(before,"null"); lstrcpyA(after,"null"); lstrcpyA(producer,"null");
    lstrcpyA(extra,"null");
    if (!profile_matches()) { ok=FALSE; reason="profile_mismatch"; }
    else if (U16(0x4ed818) != 3) { ok=FALSE; reason="requires_ingame_ps3"; }
    else if (owner >= 8 || op > 9) { ok=FALSE; reason="bad_owner_or_operation"; }
    else {
        p = 0x956770u + owner * 0x3abcu;
        ledger(before,owner);
        if (op == 1) {
            DWORD unit = 0x66b790u + slot*0x758u;
            if (slot < 1 || slot >= 1200 || type >= 200) {
                ok=FALSE; reason="bad_unit_or_type";
            } else if (!U16(0x8990c8u+slot*2u) || U8(unit+0x8e) != owner ||
                       (LONG)U32(unit+0xb4) <= 0) {
                ok=FALSE; reason="producer_not_alive_or_owned";
            } else {
                typedef DWORD (__cdecl *Train)(DWORD,SHORT,DWORD);
                raw=((Train)0x4af5e0u)(U32(unit+0x29c),(SHORT)type,1);
            }
        } else if (op == 2 || op == 3) {
            if (slot >= 100) { ok=FALSE; reason="bad_save_slot"; }
            else {
                typedef DWORD (__cdecl *SaveLoad)(DWORD);
                raw=((SaveLoad)(ULONG_PTR)(op==2 ? 0x440c20u : 0x440ff0u))(slot);
            }
        } else if (op == 4) {
            if (request[5]>1000000 || request[6]>1000000 || request[7]>5000) {
                ok=FALSE; reason="fixture_out_of_range";
            } else {
                typedef void (__attribute__((thiscall)) *SetResource)(void*,DWORD);
                ((SetResource)0x43ed60u)((void*)(ULONG_PTR)p,request[5]);
                ((SetResource)0x43ed80u)((void*)(ULONG_PTR)p,request[6]);
                U16(p+0x200c)=(USHORT)request[7];
                raw=1;
            }
        } else if (op == 7) {
            /* Resource-only fixture for production-path probes.  Unlike op=4,
             * this never writes used/reserved/count or any unit record. */
            if (request[5]>1000000 || request[6]>1000000) {
                ok=FALSE; reason="resource_fixture_out_of_range";
            } else {
                typedef void (__attribute__((thiscall)) *SetResource)(void*,DWORD);
                ((SetResource)0x43ed60u)((void*)(ULONG_PTR)p,request[5]);
                ((SetResource)0x43ed80u)((void*)(ULONG_PTR)p,request[6]);
                raw=1;
            }
        } else if (op == 5 || op == 6) {
            /* Bounded engine-seeded roster, NOT production or resource spending.
             * fixture_type is the caller-supplied type (request[4]) restricted to an
             * explicit allow-list. W24 Step A (type_table_inventory) found type 46
             * (cost20/width3/height3/flags0) gate-legal alongside the original 5/7,
             * so the allow-list is widened from {5,7} to {5,7,46}; the width/height/
             * flags guards below and the Place->Gate->Spawn + per-entity accounting
             * check are unchanged (card LAP461 section 6-1).
             * lap526 strategy K1/§83 + lap527 W36 §1: bit 0x4 전투 타입 type 2 추가(N182·N184).
             * lap692 work: G2 전비10000 실측을 위해 cost40 후보(pinned
             * type_costs.json: type28/29=40)를 진단용으로 추가한다. 개인 개체
             * 상한(250)은 그대로 두고 250*40=10000으로 정확히 맞춰, 브리지 확장 vs
             * 개인상한 조정 중 브리지 확장을 택한다(analysis/memory_maps/
             * g2_supply10000_cap_bump_20260926.md 산술 근거). width/height/flags
             * 게이트는 원본 type 테이블이 그대로 판정하며(28/29/108은 flags로
             * 거부됨을 이 lap이 실측), 104(cost40, gate-legal)도 추가한다.
             * 실측 결과 원본 Gate(0x43eda0)가 owner당 실제 개체수 약242에서
             * 거부해 cost40*242=9680<10000이라 cost40만으로는 부족함이
             * 드러나, cost65 type103(gate-legal)도 진단 후보에 추가한다
             * (154기*65=10010, 실측 ~242 한계에 안전 여유). */
            DWORD fixture_type = type;
            DWORD type_offset = fixture_type*0x394u, unit, candidate, cells;
            SHORT fixture_cost = S16(0x9b5238u+type_offset);
            DWORD wanted=request[7] ? request[7] : 1;
            SHORT map_width=S16(0xb3de34u), map_height=S16(0xb3de36u);
            SHORT width=S16(0x9b523eu+type_offset), height=S16(0x9b5240u+type_offset);
            typedef DWORD (__attribute__((thiscall)) *Place)(void*,SHORT,SHORT,SHORT,SHORT,
                                                            SHORT,SHORT,SHORT,SHORT);
            typedef SHORT (__attribute__((thiscall)) *Gate)(void*,DWORD,SHORT);
            typedef DWORD (__cdecl *Spawn)(DWORD,DWORD,DWORD,DWORD,DWORD,DWORD,DWORD);
            slot=0;
            if (fixture_failed) {
                ok=FALSE; reason="fixture_locked_after_accounting_failure";
            } else if ((fixture_type != 5u && fixture_type != 7u && fixture_type != 46u && fixture_type != 2u &&
                        fixture_type != 28u && fixture_type != 29u && fixture_type != 104u && fixture_type != 108u &&
                        fixture_type != 103u) ||
                (U32(0x9b524cu+type_offset)&14u) != 0 ||
                width<1 || width>8 || height<1 || height>8) {
                ok=FALSE; reason="unsupported_army_fixture_type";
            } else if (map_width<1 || map_width>180 || map_height<1 || map_height>180 ||
                       request[5]>=(DWORD)map_width || request[6]>=(DWORD)map_height || wanted>200) {
                ok=FALSE; reason="invalid_fixture_coordinates";
            } else {
                cells=(DWORD)map_width*(DWORD)map_height;
                candidate=request[6]*(DWORD)map_width+request[5];
                while (fixture_added<wanted && fixture_attempts<10000 && fixture_attempts<cells) {
                    DWORD x=candidate%(DWORD)map_width, y=candidate/(DWORD)map_width;
                    SHORT allocated, old_used=S16(p+0x200c), old_count=S16(p+0x200a);
                    ++fixture_attempts;
                    candidate=(candidate+1u)%cells;
                    if ((LONG)old_used+(LONG)U32(p+0x1c)+(LONG)fixture_cost>S16(p+0x2012)) {
                        ok=FALSE; reason="fixture_exceeds_unreserved_supply"; break;
                    }
                    if (((Place)0x42ecb0u)((void*)0xb3dda8u,(SHORT)x,(SHORT)y,
                                         width,height,-1,-1,0,0)!=1) continue;
                    allocated=((Gate)0x43eda0u)((void*)(ULONG_PTR)p,type,0);
                    if (allocated<1 || allocated>=1200) {
                        ok=FALSE; reason="fixture_original_gate_rejected"; break;
                    }
                    slot=(DWORD)allocated;
                    raw=((Spawn)0x443190u)(type,slot,x,y,1,100,owner);
                    unit=0x66b790u+slot*0x758u;
                    if (raw!=1 || !U16(0x8990c8u+slot*2u) || U8(unit+0x8e)!=owner ||
                        U8(unit+0x8d)!=type || S16(p+0x200a)!=old_count+1 ||
                        S16(p+0x200c)!=old_used+fixture_cost) {
                        ok=FALSE; reason="spawn_accounting_mismatch";
                        fixture_failed=TRUE;
                        break;
                    }
                    ++fixture_added;
                }
                if (ok && fixture_added!=wanted) {
                    ok=FALSE; reason="fixture_placement_budget_exhausted";
                }
            }
        } else if (op == 8) {
            /* G2 S0 (lap523 card): issue one original target-order via the
             * unmodified issuer FUN_00415480. Read-only diagnostic -- this
             * branch writes no unit record or ledger field itself; only the
             * original engine call (if admitted below) mutates state. The
             * side/hostility byte (PlayerStruct+5) is deliberately NOT
             * checked here -- the original function decides admission and
             * raw_return plus the reported player-side bytes let a later
             * reviewer tell NF-a (rejected, same side) from acceptance. */
            static const BYTE issuer_sig[] = {0x53,0x56,0x8B,0xF1,0x57,0x8A,
                                               0x86,0x1C,0x03,0x00,0x00,0x84};
            DWORD src_slot = slot, tgt_slot = type;
            DWORD src_unit = 0x66b790u + src_slot*0x758u;
            DWORD tgt_unit = 0x66b790u + tgt_slot*0x758u;
            if (!same_bytes(0x415480u, issuer_sig, sizeof(issuer_sig))) {
                ok=FALSE; reason="issuer_signature_mismatch";
            } else if (src_slot < 1 || src_slot >= 1200 || tgt_slot < 1 || tgt_slot >= 1200) {
                ok=FALSE; reason="bad_order_slot";
            } else if (!U16(0x8990c8u+src_slot*2u) || !U16(0x8990c8u+tgt_slot*2u)) {
                ok=FALSE; reason="order_slot_not_alive";
            } else if ((LONG)U32(src_unit+0xb4) <= 0 || (LONG)U32(tgt_unit+0xb4) <= 0 ||
                       U8(src_unit+0x31c) == 0 || U8(tgt_unit+0x31c) == 0) {
                ok=FALSE; reason="order_slot_dead_or_uninitialized";
            } else if (U8(src_unit+0x8e) != owner || U8(tgt_unit+0x8e) == owner ||
                       U8(src_unit+0x8e) >= 8 || U8(tgt_unit+0x8e) >= 8) {
                ok=FALSE; reason="order_owner_mismatch";
            } else if ((U32(tgt_unit+0x29c) & 0xffffu) != tgt_slot) {
                ok=FALSE; reason="target_uid_slot_mismatch";
            } else {
                typedef int (__attribute__((thiscall)) *Issue)(void*,DWORD,DWORD,DWORD);
                DWORD tgt_uid = U32(tgt_unit+0x29c);
                DWORD tgt_x = (DWORD)U16(tgt_unit+0x2a2);
                DWORD tgt_y = (DWORD)U16(tgt_unit+0x2a4);
                DWORD pending_before = U32(src_unit+0x384);
                DWORD po, poff = 0;
                char players[400];
                raw = (DWORD)((Issue)0x415480u)((void*)(ULONG_PTR)src_unit, tgt_x, tgt_y, tgt_uid);
                for (po = 0; po < 8; ++po) {
                    DWORD pp = 0x956770u + po*0x3abcu;
                    char one[72];
                    wsprintfA(one,"%s{\"owner\":%u,\"b0\":%u,\"b2\":%u,\"b5\":%u}",
                              po?",":"", po, (unsigned)U8(pp+0x00), (unsigned)U8(pp+0x02),
                              (unsigned)U8(pp+0x05));
                    lstrcpyA(players+poff, one);
                    poff += lstrlenA(one);
                }
                wsprintfA(extra,
                    "{\"raw_return\":%u,\"src_slot\":%u,\"tgt_slot\":%u,"
                    "\"src_cmd\":%d,\"src_0x294\":%d,\"src_0x634\":%u,\"src_0x390\":%d,"
                    "\"src_0x1d8\":%u,\"src_0x1d4\":%u,"
                    "\"src_0x384_before\":%u,\"src_0x384_after\":%u,\"src_0x388\":%u,\"src_0x38c\":%u,"
                    "\"tgt_0x1bc\":%u,\"tgt_type\":%u,\"tgt_owner\":%u,\"tgt_hp\":%d,"
                    "\"players\":[%s]}",
                    raw, src_slot, tgt_slot,
                    (int)S16(src_unit+0x290), (int)S16(src_unit+0x294), U32(src_unit+0x634),
                    (int)U16(src_unit+0x390), U32(src_unit+0x1d8), U32(src_unit+0x1d4),
                    pending_before, U32(src_unit+0x384), U32(src_unit+0x388), U32(src_unit+0x38c),
                    (unsigned)U8(tgt_unit+0x1bc), (unsigned)U8(tgt_unit+0x8d),
                    (unsigned)U8(tgt_unit+0x8e), (LONG)U32(tgt_unit+0xb4), players);
            }
        } else if (op == 9) {
            /* G2 (라) diagnostic (lap548 card section 2): issue one original
             * move order via the unmodified issuer FUN_004AEDE0 (cdecl,
             * N203). Read-only diagnostic except for the one original engine
             * call -- this branch writes no unit record or ledger field
             * itself. request[4] carries dest_x (reusing "type" above),
             * request[5] carries dest_y (reusing "rice"); wood/used unused. */
            static const BYTE move_sig[] = {0x8B,0x44,0x24,0x10,0x8B,0x0D,0x78,0x5C,
                                             0x9E,0x00,0x8B,0x54};
            DWORD src_slot = slot, dest_x = type, dest_y = request[5];
            DWORD src_unit = 0x66b790u + src_slot*0x758u;
            SHORT move_map_w = S16(0xb3de34u), move_map_h = S16(0xb3de36u);
            if (!same_bytes(0x4aede0u, move_sig, sizeof(move_sig))) {
                ok=FALSE; reason="move_issuer_signature_mismatch";
            } else if (src_slot < 1 || src_slot >= 1200) {
                ok=FALSE; reason="bad_move_slot";
            } else if (!U16(0x8990c8u+src_slot*2u)) {
                ok=FALSE; reason="move_slot_not_alive";
            } else if ((LONG)U32(src_unit+0xb4) <= 0 || U8(src_unit+0x31c) == 0) {
                ok=FALSE; reason="move_slot_dead_or_uninitialized";
            } else if (U8(src_unit+0x8e) != owner) {
                ok=FALSE; reason="move_owner_mismatch";
            } else if (dest_x >= (DWORD)move_map_w || dest_y < 1 || dest_y >= (DWORD)move_map_h) {
                ok=FALSE; reason="bad_move_destination";
            } else {
                typedef int (__cdecl *Move)(DWORD,DWORD,DWORD,DWORD);
                DWORD src_uid = U32(src_unit+0x29c);
                SHORT pre_290 = S16(src_unit+0x290);
                USHORT pre_2a2 = U16(src_unit+0x2a2), pre_2a4 = U16(src_unit+0x2a4);
                SHORT pre_682 = S16(src_unit+0x682), pre_692 = S16(src_unit+0x692);
                USHORT pre_390 = U16(src_unit+0x390), pre_394 = U16(src_unit+0x394);
                raw = (DWORD)((Move)0x4aede0u)(src_uid, dest_x, dest_y, 1);
                wsprintfA(extra,
                    "{\"raw_return\":%u,\"src_slot\":%u,\"dest_x\":%u,\"dest_y\":%u,"
                    "\"src_pre_0x290\":%d,\"src_pre_0x2a2\":%u,\"src_pre_0x2a4\":%u,"
                    "\"src_pre_0x682\":%d,\"src_pre_0x692\":%d,"
                    "\"src_pre_0x390\":%u,\"src_pre_0x394\":%u,"
                    "\"src_post_0x290\":%d,\"src_post_0x2a2\":%u,\"src_post_0x2a4\":%u,"
                    "\"src_post_0x682\":%d,\"src_post_0x692\":%d,"
                    "\"src_post_0x390\":%u,\"src_post_0x394\":%u}",
                    raw, src_slot, dest_x, dest_y,
                    (int)pre_290, (unsigned)pre_2a2, (unsigned)pre_2a4,
                    (int)pre_682, (int)pre_692, (unsigned)pre_390, (unsigned)pre_394,
                    (int)S16(src_unit+0x290), (unsigned)U16(src_unit+0x2a2),
                    (unsigned)U16(src_unit+0x2a4), (int)S16(src_unit+0x682),
                    (int)S16(src_unit+0x692), (unsigned)U16(src_unit+0x390),
                    (unsigned)U16(src_unit+0x394));
            }
        }
        ledger(after,owner);
        if (slot > 0 && slot < 1200 && (op == 0 || op == 1 || op == 5 || op == 6)) {
            DWORD unit=0x66b790u+slot*0x758u;
            wsprintfA(producer,"{\"slot\":%u,\"id\":%u,\"type\":%u,\"owner\":%u,"
                      "\"command\":%d,\"progress\":%u,\"production_type\":%u}",
                      slot,U32(unit+0x29c),(unsigned)U8(unit+0x8d),
                      (unsigned)U8(unit+0x8e),(int)S16(unit+0x290),
                      U32(unit+0x1f8),U32(unit+0x320));
        }
    }
    wsprintfA(result,"{\"id\":%u,\"op\":%u,\"owner\":%u,\"ok\":%s,"
              "\"reason\":\"%s\",\"raw_return\":%u,\"tick_before\":%u,\"tick_after\":%u,"
              "\"thread\":%u,\"ps\":%u,\"before\":%s,\"after\":%s,\"producer\":%s,"
              "\"fixture_added\":%u,\"fixture_attempts\":%u}\n",
              request[0],op,owner,ok?"true":"false",reason,raw,tick_before,
              U32(0x8924b8),GetCurrentThreadId(),(unsigned)U16(0x4ed818),before,after,producer,
              fixture_added,fixture_attempts);
    if ((op == 8 || op == 9) && ok) {
        /* Splice via lstrcatA, never via a single wsprintfA call: wsprintfA's
         * formatted output must stay well under 1024 bytes per call (both
         * calls above independently do), but the spliced total can exceed
         * that safely since lstrcatA has no such formatting-length limit. */
        DWORD rl = lstrlenA(result);
        if (rl >= 2 && result[rl-1] == '\n' && result[rl-2] == '}') {
            result[rl-2] = 0;
            lstrcatA(result, op == 8 ? ",\"op8\":" : ",\"op9\":");
            lstrcatA(result, extra);
            lstrcatA(result, "}\n");
        }
    }
    write_file(RESULT_TMP,result,FALSE);
    MoveFileExA(RESULT_TMP,RESULT,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH);
    write_file(LOG,result,TRUE);
done:
    InterlockedExchange(&busy,0);
}

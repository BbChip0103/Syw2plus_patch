# 2026-10-07 | lap1081 | G1 H-L2 (`0x467E60` diff 미러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 승인·수용 판정은 하지 않는다(독립 검수는 다음 middle).
- 가설: lap1080 §5 H-L2 — 미후킹 `0x467E60`(클립 없는 좌우 반전 반투명 RLE, ret 0x1c, 7 인자)이 화면 버퍼에 직접 쓰는 유닛 스프라이트가 throttle(40:30) 재현 stale ord 171..182의 원인이며, `mirror_blend_flip7`류 diff 미러(원본 1회 호출·전후 diff)로 해소된다.
- 예상 PASS / FAIL: lap1080 §5 (a) ld7 옵션 2회 ord 171..182 합 0/0·다른 ord 증가 없음 / (b) 정상 속도 save006 LEFT,RIGHT edge hold 0 + 계수로 H-pos 판별 / (c) UP/DOWN edge·save000 키 hold·save006 고정 비회귀·E-0·p95·안전 7종 0·cleanup·source_unchanged. 안전 위반·크래시 = FAIL.
- 변경 파일 / source 해시 접두 / 커밋: uncommitted. `tools/inmm_stub/g1_mirror2x.c` `fd66ba27…`(hook `mirror_flip_blend7`·계수 `g_flip_blend7_*`·install/restore/reset·`G1_FLIP_BLEND7 0x467E60`), `tools/inmm_stub/g1_mirror2x.h` `6788f63f…`(accessor 8), `tools/inmm_stub/direct_draw_trace.c` `8f404782…`(`blend_467E60_*` 8개 + `mirror_details[9216→9728]`), `tests/test_g1_rect_fill.py` `61f30193…`(새 테스트 2 + 9216 단언 갱신). 하네스 불변.
- 원본 SHA / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` MATCH(읽기만, 모든 run `source_unchanged` true·cleanup ok·game 사본 삭제). 비합성 save006(`--p4b-s-snapshot`)·save000(`--scene-actions none`), scale2x HD, load 2.5~5.1(≤8), run마다 대기 0 s 후 순차. 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1081_work_hl2`(`run_hl.sh` `794dfd43`·`analyze_hl.py` `28366b3b`), 로그 `logs/gates/lap1081_hl_hl{1..6}.{log,exit}`.

## L2-0 테스트 먼저 (RED→GREEN)

- 원본 objdump(`0x467E60`..`0x467FC6`, 읽기만)를 직접 재확인: 5 B 경계 `83 EC 08 55 56`, 인자 x·y·w·h 모두 `movsx` 16비트, rle `[esp+0x2c]`·remap·level, `0x467F93 mov [eax+esi-1],bl`에서 `eax = w − k` → 쓰기 열 **x+w−1−k**, 목적지 읽기 `mov dl,[esi+ebp]` = 열 **x+k**, `0xFE n` = k += n(넘침 허용)·RLE 인덱스 행 간 유지, 클립(+0x4D0..) 접근 없음, `ret 0x1c`. 호출처 `0x41A9FF`·`0x41A887`.
- RED: `test_flip_blend7_hook_table_and_wrapper_contract` 실패(`G1_FLIP_BLEND7` 부재), `test_flip_blend7_original_write_model_stays_inside_screen_region`(C 모델 20,000 무작위: 쓰기 열 ⊆ [x,x+w)·읽기 열 ⊆ [x,x+w)·화면 안 쓰기 ⊆ `g1_flip_rle_region` 영역)은 모델이라 처음부터 PASS.
- GREEN 직전 일시 FAIL 1건: `test_mirror_details_builder_holds_worst_case_concatenation` 최악 길이 9,471 > 9,216(새 블록 8계수) → `mirror_details` 9,216→**9,728**(`trace_event_raw` `line[10240]`에 prefix+details 최악 ≈9.8k로 들어감), 9216을 단언하던 `test_shade_flip_hook…`·주석 갱신. 최종 `tests/test_g1_rect_fill.py`+`test_g1_panel_layer.py` 32 passed, `make lint`·`make typecheck` PASS.

## L2-1 구현

- `mirror_flip_blend7`: `mirror_flip_blend`(0x467FD0, 클립 없는 좌우 반전)의 7 인자 형제. 인자는 `(int16_t)` 부호 확장, 영역 = `g1_flip_rle_region`(사각형∩화면, 스트라이드 넘침 행은 미러 안 함), 화면 전체까지 커질 수 있어 `g_flip_blend7_before[800×600]`+`g_flip_blend7_tile`로 `g1_overlay_blt_apply_tiled`(≤320×160 타일), 대상 검사(renderer `0xE5BF18`, 캐시·panel 제외, 스트라이드·높이)·guard·`layer_drift_write_*` 기존과 동일. 원본은 정확히 1회(행 안 읽기-쓰기 의존), 7 인자 그대로 전달. 계수 `blend_467E60_{invocations,mirrored_calls,mirrored_pixels,changed_calls,reject_target,reject_bounds,reject_size,reject_guard}`.

## 실행 결과 (순차 6 run, 게임 6회 launch)

| run | pair | 옵션 | hold 창 합 / ≥100 px present | 계수 `blend_467E60` | 비고 |
|---|---|---|---|---|---|
| hl3 `3dbcf93d5d56` | PASS | save006 LEFT,RIGHT edge 정상 속도 | **0 / 0**, 마지막40 0 | invocations **0** | E-0 24칸 왕복·(158,101)·p50 50/p95 gap 53(고정 52)·elapsed p95 7(6)·tps 20.0 |
| hl1 `6159fcc42d84` | HOLD(기대) | 동일 + `--candidate-throttle 40:30` | **640 / 3** (ord 123 199·140 257·191 184), **ord 171..182 = 0** | 11/11/8,833 px/11, reject 0 | candidate 17칸(lane parity HOLD, ld7과 동일), p50 70, throttle stop 120회·4,845 ms |
| hl2 `6d00bd7d4a3f` | HOLD(기대) | 동일 | **199 / 1** (ord 123만), **ord 171..182 = 0** | 12/12/9,802 px/12, reject 0 | p50 70, stop 120회·4,832 ms, 최종 상태 R |
| hl4 `6e8fe1978834` | PASS | save006 UP,DOWN edge | **0 / 0**, 마지막40 0 | 0 | UP/DOWN 24칸 왕복·gate 전부 PASS·p95 gap 53(53)·elapsed 7(7) |
| hl5 `36606480b76f` | HOLD(기존) | save000 DOWN,UP 키 hold | **0 / 0**, 마지막40 0 | 0 | DOWN/UP 24칸·최종 (39,53)·gate = lap1077 lb5와 동일 HOLD(`input_effect`·`terrain_scroll`, v2 계열 BLOCKED) |
| hl6 `b856388b47e9` | PASS | save006 고정 | 300..848 합 **0**·마지막40 0 | 0 | 총합 291,382·6..299 합 183,290 = lap1077 lb6과 동일 |

- (a) hl1·hl2 모두 **ord 171..182 → 0**(기준 ld7 746~974 px ×12). 남은 ≥100 px = ord 123(199 px, x0..31·y285..303, 기준 ld7·ld8·ld10과 같은 값)·ord 140(257 px, hl1만, 마스크 bbox x0..427 안 x400..427 y310..328 부분)·ord 191(184 px, hl1만, 기준 ld10에도 있음). 모두 lap1080 정정 2·3의 별도 잔여이며 기준 값을 넘지 않는다.
- (b) 정상 속도 hl3: hold 0, `blend_467E60_invocations` **0**(run 전체 구간에서 한 번도 호출되지 않음; throttle run은 11~12회, 모두 mirrored·reject 0). 사전등록 판정 규칙(invocations=0 → H-pos **판별 불가**)대로 기록. 간접 사실: 이 함수는 throttle 때 정지한 카메라 (141,118) 구간에서만 호출됐고, 정상 속도 lane의 24칸 이동 경로(최종 (134,125))에서는 0이다. H-pos 확정은 아니다.
- (c) 비회귀: hl4·hl5·hl6 hold 0·고정 300..848 0, 안전 7종 최대 0(hl1~hl6), 두 lane `game_removed`·`source_unchanged` true, 정상 속도 E-0 24칸 왕복, p95 present elapsed ≤ 고정+1.
- 미러 폭주 없음: hl1·hl2 `mirrored_pixels` 8,833/9,802(호출당 약 800), reject_* 전부 0.

## 판정 / 한계

- **H-L2 PASS(partial, work 판정)** — 사전등록 PASS 조건 (a) 2/2·(b)(c) 모두 충족. 수용은 middle이 한다.
- 한계: ① 재현은 candidate만 인위적으로 느리게 한 조건이고(사용자 환경 부하 동일성 UNKNOWN) 정상 속도에서는 이 함수가 호출조차 되지 않아(invocations 0) 정상 속도 개선은 입증되지 않는다. ② 타일 경로(>320×160)는 정적 계약·`g1_overlay_blt_apply_tiled` 기존 테스트로만 검증했고 런타임 호출은 모두 소형(호출당 ≈800 px)이다. ③ 남은 throttle 전용 소잔여 ord 123/140/191은 별개 writer UNKNOWN(귀속 안 함). ④ hl1 ord 191은 이번에 ≥100 px로 나타남(ld7·ld8에는 <100, ld10에는 184) — run 간 변동 UNKNOWN. ⑤ 디스크 여유 15→7.4 GiB로 감소: game 사본은 지웠으나 `local/runtime/lap1081_hl_*`(prefix 등, 1.2~1.4 GiB ×6)는 provenance 규칙상 삭제하지 않았다(archive/restore 검증 뒤에만 회수 가능). 다음 세션이 `make check` 전에 여유를 확인해야 한다.

## 검사

- `make lint`·`make typecheck` PASS. 기록·인계 freeze 뒤 `make check`·`checks/safety.sh check` 결과는 STATUS 검증 상태에만 보강한다.

## 다음 한 가지

middle(Opus) H-L2 독립 검수(`loop/ESCALATE_SOL`). 수용 시 후보: 모서리(대각) 스크롤, 남은 throttle 전용 소잔여 ord 123·140·191 귀속, HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비.

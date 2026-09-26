# 2026-09-20 | lap 410 | 목표 G2 (P1 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5 / high / middle(중간계획·컨펌).
  loop/PROMPT.md ①~⑥, AGENTS.md, INBOX 2026-09-20 21:58 지시(같은 source 전체 게이트 반복 금지)를 따른다.
  게임 코드 hands-on 수정 없음. 이 lap의 산출물은 판정 + 다음 work 카드다.
- 가설 / 검수 대상: lap409(work, Sonnet5/high)가 남긴 P1 원시 증거
  (`p1_summary.json`, `seed_receipts.json`, `save090.dat`, presave/postload snapshot, `trace.jsonl`)가
  "marked compat 후보가 near-4000 live에서 save/load 왕복 무손실"을 실제로 뒷받침하는지 독립 확인한다.
- 변경 파일: `docs/STATUS.md`, `docs/feedback/INBOX.md`, 본 기록,
  신규 카드 `docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md`. 제품/게임/패치 모듈 무변경.

## 검사 범위 (INBOX 21:58 반영)

전체 784 `make check`를 재실행하지 않았다. 직전 동일 source의 full gate가 PASS이고 이번 lap은
source를 바꾸지 않았다. 대신 **원시 산출물 재계산 + 표적 테스트 + 원본/안전 검사**만 수행했다.

## 독립 확인한 것 (재계산, lap409 서술을 그대로 믿지 않음)

1. **원본 불변**: `Syw2plus_re/Syw2plus/syw2plus_original.exe`
   = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재해시 일치.
   후보 빌드 실행 후 재해시해도 동일(빌드가 원본을 건드리지 않음).
2. **후보 재현성**: `g2_full_capacity_persistence_compat_v1.build_candidate(original, 4001)`을
   이 세션에서 다시 실행 → `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
   `runtime_driver.SUPPORTED_EXECUTABLES` 핀과 일치하고, 실행에 쓰인
   `local/runtime/20260920_215245_1236080_0/game/syw2plus_original.exe`와 **바이트 동일**.
3. **저장 파일**: `save090.dat` 재해시 `814e7f05…a88460`, 크기 9,272,322 B 일치.
   마커 `S2P1N4K1`이 파일 전체에서 **정확히 1회, 오프셋 `0x38`**에 존재(직접 바이트 판독).
   legacy 폴백이 아니라 신규 마킹 헤더가 실제로 기록됐다.
4. **스냅샷 대조(직접 재계산)**: presave 3,991 / postload 3,996 유닛.
   소실 슬롯 **0**, 공통 슬롯의 `internal_id` 불일치 **0**, `type`/`owner` 불일치 **0**.
   신규 슬롯은 5건(5,6,7,8,9). 슬롯 범위 10~4000, **slot≥1200이 2,801건**이며 presave/postload 동수.
5. **시딩이 gate-legal이었음**: `seed_receipts.json` 24건 = executed 23 + `fixture_exceeds_unreserved_supply` 1
   (owner0 cap 도달, 예상된 정지). producer 슬롯 16/24가 ≥1200(최대 3779) ⇒ 엔진 allocator가
   실제로 1200 이상 슬롯을 반환하고 브리지가 그 슬롯을 검증했다. 시딩 종료 시 live 합계 3,985로
   `trace.jsonl` tick 687의 3,985와 일치.
6. **리더 주소 정합**: `runtime_driver.POOL_PROFILE_LAYOUTS['g2_full_capacity_v1_n4001_persistence_compat']`
   = `(4001, 0x0108C000, 0x017B8658)`이고 `tail_relocation_storage_layout_v1.layout(4001)` 산출값과 일치.
   스냅샷은 브리지와 무관한 process_vm_readv 경로다.
7. **브리지가 진짜 N=4001 빌드였음**: `/tmp/p1_bridge4001/`이 남아 있어 직접 확인.
   `runtime_bridge.c`의 세 앵커가 모두 치환됨(`0x0108c000u`, `0x017b8658u`, 경계 `4001`,
   `allocated>=4001`). 빌드 산출 DLL SHA `f642d033…de57`이 매니페스트 및 게임 폴더에 배포된
   `_inmm.dll`과 **동일**. 배포 시각 21:57:46 → 2차 프로세스 기동 21:57:56이라 실제 로드분이 맞다.
8. **표적 테스트**: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py -q`
   → **5 passed** (lap409 신규 W7 앵커 `test_compat_wrappers_are_contained_in_rsrc_cave_without_overlap` 포함).
9. **안전**: `checks/safety.sh check` → `SAFETY_PASS`. display `:300` 잔류 프로세스 0
   (현재 남은 Xvfb는 전부 다른 저장소 `Syw2plus_re_loop` 및 `:77/:78/:103/:186/:187`로 이 lap 대상 아님 —
   AGENTS.md에 따라 건드리지 않음).

## lap409가 제시하지 않았던 **더 강한** 증거 (이번에 발굴)

`trace.jsonl`에 **엔진 tick의 역행**이 기록돼 있다: idx329 `tick=2328` → idx330 `tick=1567`.
이것은 op=3 로드가 실제로 엔진 상태를 교체했다는 직접 증거다. 이 증거가 없으면
"소실 0·불일치 0"은 *로드가 아무 일도 하지 않았어도* 똑같이 나오므로 왕복 검증으로 성립하지 않는다.
lap409 기록은 이 구분을 하지 않았다. 역행 tick이 있으므로 왕복 주장은 성립한다.

## 정정 1 — 대조 기준선이 저장 시점이 아니다 (판정 자체는 유지)

`trace.jsonl` 재구성 결과 실제 순서는 다음과 같다.

| 사건 | tick | live 합계 |
|---|---|---|
| presave 스냅샷 | ~1023 | 3,991 |
| 자연 생산 | 1157 / 1190 / 1324 | 3,992 / 3,994 / 3,995 |
| **save090.dat 기록**(mtime 대응) | ~1558 | **3,995** |
| 로드 직후(tick 역행) | 1567 | **3,995** |
| 로드 후 생산 | 1601 | 3,996 |
| postload 스냅샷 | ~1868 | 3,996 |

⇒ presave 스냅샷은 저장 시점보다 **약 535 tick 앞선다**. 따라서
- lap409의 서술 "저장 후 로드 사이 320 tick 동안 생산이 계속되어 5기 순증"은 **사실과 다르다.**
  신규 슬롯 5건 중 **4건은 저장 이전**에 생산되어 세이브에 포함됐고, **로드 이후 생산은 1건**뿐이다.
- 카운트 기준으로는 오히려 **정확한 왕복**이다: 저장 3,995 → 로드 3,995(증감 0).
- 다만 **id 단위로 검증된 것은 세이브의 3,995기 중 3,991기**다. 스냅샷과 저장 사이에 생긴 4기는
  카운트로만 확인됐고 `internal_id` 대조가 없다.

판정에 미치는 영향: **결론은 뒤집히지 않는다**(소실 0, 카운트 정확 일치). 그러나 STATUS/INBOX/lap409의
"3,991 저장 → 3,996 로드, 5기는 로드 후 생산" 서술은 정정이 필요하며, 4기 미검증 구간을 명시해야 한다.
다음 회차는 **저장 직전에 스냅샷을 찍어** 이 구간을 없앤다(카드 §3 필수 항목).

## 정정 2 — 신규 결함: 배포 진단 DLL에 stock 주소가 남아 있다 (읽기 전용, 관측 실명)

`build_runtime_bridge.py`는 `runtime_bridge.c` **한 파일만** 재배치 주소로 치환한다. 그러나 같은 DLL에
함께 컴파일되는 다른 stub 모듈들이 **stock 유닛 존재배열 `0x008990C8`과 1200 경계를 하드코딩**한다:

- `tools/inmm_stub/inmm_stub.c:331` `UD_EXISTS_VA` (+ `UD_ARRAY_VA 0x0066B790`, `UD_COUNT 1200`)
- `tools/inmm_stub/ai_shadow.c:30` `UNIT_EXISTS_VA`
- `tools/inmm_stub/sfx_hook.c:158` `PROBE_UD_EXISTS_VA`
- `tools/inmm_stub/control_executor.c:1576, 2538` `UA_EXISTS_VA` / `US_EXISTS_VA`

배포된 `_inmm.dll`을 바이트 검색하면 `0x008990C8`이 12회, 4바이트 리터럴 1200이 9회 남아 있고
재배치 주소는 0회다(재배치 주소는 `runtime_bridge.c` 쪽 코드가 다른 형태로 인코딩됨 — 소스와
매니페스트로 확인 완료, 7번 항목).

**실제로 이번 실행에서 발현했다.** 프리픽스의 `C:\inmm_unit_ticks.jsonl`이 21:58에 **생성됐으나 0바이트**다.
즉 3,991기가 살아 있는 동안 `dump_units_at_tick`이 stock 주소를 훑어 **유닛 0기를 관측**했다.
- 위험도: 모든 접근이 `volatile SHORT*` **읽기**라 원본/상태 손상 위험은 없다(코드 확인).
- 그러나 재배치 후보에서 이 관측 채널들(`inmm_unit_ticks.jsonl`, ai_shadow, sfx_hook,
  control_executor의 유닛 스캔)은 **조용히 빈 세계를 보고한다.** 향후 lap이 이 산출물을 근거로
  "유닛이 없다/전멸했다"를 결론내면 오판한다. lap409의 1차 프로세스를 날린 것과 **같은 계열의 결함**이다.
- 이번 lap의 판정에는 영향 없음: P1 증거는 전부 `runtime_driver` 외부 리더와 `runtime_bridge.c`
  경로에서 나왔고 위 채널을 쓰지 않았다.

## 측정값 / 판정

**ACCEPT (정정 2건 포함).** lap409 P1의 핵심 주장 — marked compat 후보가 near-4000 live 규모에서
gate-legal 생산 시딩 → 마킹 저장 → 마킹 로드 왕복을 무손실로 통과한다 — 은 원시 산출물 재계산으로
독립 확인됐고, 로드가 실제로 일어났다는 tick 역행 증거까지 확보했다. 기존 "compat는 382-unit만 통과"
갭은 닫힌 것으로 인정한다.

단, **제품 완료가 아니다.** 이것은 1회 왕복이며 장시간 안정성·원본 생산 경로·사망/슬롯재사용 대규모
관측·LAN이 모두 미검증이다.

## fixture

재검수는 기존 산출물만 읽었다(새 게임 실행 없음).
`temp/Syw2plus_patch/g2_capacity/20260920_lap409_p1_compat_near4000/`,
`local/runtime/20260920_215245_1236080_0/`(게임 사본·prefix·save090.dat),
`/tmp/p1_bridge4001/`(브리지 소스·DLL·매니페스트 — **아직 남아 있음. 다음 lap 전에 삭제되면
`build_runtime_bridge --unit-pool-capacity 4001` 재실행으로 재현**).

## 회귀 / 남은 위험

1. 정정 1의 4기 id-미검증 구간(다음 카드에서 제거).
2. 정정 2의 stock 주소 잔존(다음 카드 §4, bounded).
3. compat 후보 자체의 장시간 soak 없음 — non-compat 후보의 soak PASS(자칭 lap412)는 **미검수**이며
   다른 바이너리라 승계하지 않는다.
4. 시딩이 여전히 진단 브리지의 gate-legal 경로이고 원본 UI/명령 생산 경로 전체가 아니다(P2, 기존 갭).
5. strict cap(N19/되물음, P3)과 F4 전비 장부 랩은 사용자 답변 대기로 이 lap이 다루지 않았다.
6. 커밋 없음(LOOP_ALLOW_COMMITS 기본 0). 목표·범위·승인 변경 없음.

## 다음 한 가지

work 회차(Sonnet5/high)가 신규 카드
`docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md`를 실행한다 — marked compat 후보의 **장시간 soak**
(8인 cap5000, near-4000 유지, 저장 직전 스냅샷 포함, 사망/슬롯 재사용 관측, 메모리/시간 수치).
P2(원본 생산 명령 경로 대체)는 soak PASS 뒤로 미룬다: soak이 G2 "안정성" 본문에 더 직접 닿고
실제 런타임 증거를 늘리는 쪽이기 때문이다.

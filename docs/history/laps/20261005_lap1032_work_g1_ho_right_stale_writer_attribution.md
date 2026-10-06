# 2026-10-05 | lap1032 | G1 work — H-O 우측 잔여 stale 표본 writer 귀속(진단, 제품 동작 불변)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work 1 lap. 커밋 0.
- 목표·가설: lap1031 §5 사전등록. 남은 save000 우측(x≥686) stale 표본 3점 A(695,468 고정)·B(766,139 이동)·C(799,315 가장자리)의 writer를 귀속하고 FEASIBLE/NOT_FEASIBLE/BLOCKED를 판정한다.
- 변경 파일: `tools/inmm_stub/direct_draw_trace.c` 1줄(`rect_solid_details[340]`→`[360]`, lap1031 허용 부수 수리, 이 버퍼는 지역 스택 문자열 — 제품 동작 불변·계약 테스트 없음). 하네스·gate 변경 0(기존 `--drift-samples`/`--screen-watch`/`--stale-mask`).
- 원본·후보 SHA: 원본 EXE `b56986e0…8ac`(objdump 대상, read-only). 수정 후 `direct_draw_trace.c` `d7b33b84…`(= run bridge 사본 일치). save000 `1c703551…`(index 1) 비합성.
- 실행: 공유 temp `20261005_lap1032_work_ho/run_o.sh`(SHA `0198dfbe…`) — save000 pair 2회 순차(load 2.95/3.02), `--fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch --drift-samples "695,468;766,139;799,315" --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`. exit 2·status HOLD = 기존 pair HOLD(V2s). 분석 `analyze_o.py` `d36a3872…` → `analysis_o.json` `1f223710…`. 로그 `logs/gates/lap1032_ho_s0_r{1,2}.log`. game 사본 잔존 0.
- fixture: save000 pair, scene_state_equal true, 활성8인 부하 증명 아님.

## 결과

| 항목 | r1 / r2 |
|---|---|
| O-0 selftest·무장 | PASS(hit 1) · 52라운드 fail 0 · 주소 `0x08B1BA00`+stride 832 · match 7 · JSONL 손상 0 |
| O-0 마지막40 stale 중앙값 | 246.5 / 246.5 (사전등록 246.5±5% 이내 — watch 영향 없음) |
| O-0 안전·cleanup | 안전 7종 0, cleanup·source_unchanged true, scene_state_equal true |
| 성능(참고) | candidate p95 11/11 ms — watch 온 진단 run이며 lap1028 M-2 watch run(10/12)과 동급, gate 아님 |
| O-1 `u` 귀속 | A 33/33·B 37/37·C 50/50 = 100%(≥90%), 두 run 동일 |
| 표본 stale present | A 78 · B 21 · C 22(두 run 동일) |

### O-2 stale present 마지막 writer(EIP, 값 일치 기준, r1=r2)

| 표본 | writer | stale present 중 | 분류 |
|---|---|---|---|
| A (695,468) | `0x467ABA`(호출처 `0x41A9A4`) | **77/78**(1 = `0x46884E`) | (ii) 미후킹 EXE 함수 — 아래 `0x4678C0` |
| B (766,139) | `0x4680F5`(호출처 `0x41A0D2`) | **17/21**(4 = `0x466BB3`) | (ii) 미후킹 `0x467FD0` |
| C (799,315) | `0x466BB3`(호출처 `0x419F55`) | **21/22**(1 = `0x467CCF` 기후킹) | (i) 기후킹 `0x466B50`(H-F3) |

- **A = `0x4678C0`**(objdump, read-only 원본): `ret 0x1c`(`0x467AFC`), 7 스택 인자·thiscall(ecx=renderer `0xE5BF18`), 인자 x/y/w/h 16비트 movsx, 클립 `[ecx+0x4D0/0x4D4]`, 팔레트 룩업 가중 혼합(0x467B00 H-B4 가족). 쓰기 `0x467AB7 mov [edi+esi],dl`(EIP `0x467ABA`). 시작 5바이트 `83 EC 18 33 C0`(명령 경계 3+2). 호출 2곳(`0x41A827`·`0x41A99F`).
- **B = `0x467FD0`**: `ret 0x14`(`0x468131`), 5 스택 인자·thiscall, 16비트 movsx, 클립 비교 없음, RLE 0xFE 스킵 + 룩업 쓰기 `0x4680F3 mov [edi],dl`(EIP `0x4680F5`). 시작 5바이트 `83 EC 08 53 56`(3+1+1). 호출 2곳(`0x41A0CD`·`0x41AC95`).
- **C = `0x466B50` 기후킹, 그런데 stale**: `flip_rle_466B50_*` = invocations 777·mirrored 702·**reject_size 75**·reject_target 0·reject_guard 0. 표본 C·B 일부 stale = 이 75 reject(사각형이 `g1_overlay_blt_accepts`/가장자리 조건 탈락, 호출 인자 미기록 — lap1011 "save000 신규 76"과 일치). 이번 lap은 거부된 사각형 크기를 알 수 없다(UNKNOWN).

## 판정

- **O-0 PASS · O-1 PASS(100%) · O-2 = FEASIBLE**: 표본 A는 stale present의 98.7%가 단일 미후킹 함수 `0x4678C0`(hook 가능), 표본 B는 81%가 단일 미후킹 `0x467FD0`(hook 가능)이다. 사전등록 기준(≥80% 단일 미후킹·hook 가능) 충족.
- 표본 C는 (i) 기후킹 `0x466B50`의 reject_size 75 → 수리 경로 = 거부 사각형 크기 계측 후 한도(폭·높이·화면 밖) 조정.
- 한계: 표본 3점뿐(이동 스프라이트 전부를 덮지 못함, lap1031 위험 유지). A 1건 `0x46884E`·B/C 소수는 별도 writer(미조사).
- 제품 동작 변경 0이므로 save006 env-off 비회귀 pair는 생략(DLL 변경 = 지역 버퍼 크기 1줄, bridge 사본 SHA 일치).

## 다음 한 가지(lap1033 middle 검수 후 work)

- middle: 위 귀속·objdump를 새 스크립트로 재계산 검수, `0x4678C0`·`0x467FD0` hook 순서(표본 A 우선) 확정 → work H-P: `0x4678C0` diff 미러(`mirror_blend_clip` 동형, 16비트 인자·클립 `[ecx+0x4D0/0x4D4]` 교집합, 7인자·`ret 0x1c`)와 reject 계측을 같은 lap에 구현하고 save000 pair + save006 비회귀로 표본 A stale 78→0·마지막40 중앙값 감소를 측정.
- backlog: `0x467FD0`(B), `0x466B50` reject_size 75 원인, `0x46884E`.

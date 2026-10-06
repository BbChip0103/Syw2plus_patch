# G2 ESL2608 점검 보고서 — 2026-09-30 / lap 806

## 범위와 입력

대상은 `../260921_temp/`의 두 ESL2608 후보와 각 비패치 baseline이다. 후보 SHA는
normal `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`,
fixed-start `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`이다.
비교 baseline SHA는 각각 `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`,
`f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973`이다.

모든 runtime probe는 private Wine win32 prefix/Xvfb와 ESL2608 Data overlay에서 수행했으며,
원본·후보 EXE와 `../260921_temp/`의 기존 파일은 수정하지 않았다. normal/fixed-start ×
baseline/candidate 4-way가 필요한 항목은 같은 fixture와 입력 계약으로 paired 했다.

## 체크리스트 판정

| 항목 | 판정 | 근거와 제한 |
|---|---|---|
| A. 주소·선택 계약 | PASS/parity | Phase A 4-way에서 100 active fixture, 선택 `1→19→20`, Ctrl+1 호출, 21번째 거부 `20→20`, 제거·재추가가 모두 baseline과 동일했다. ESL2608 candidate 주소는 pool `0x0112E000`, existence `0x018849F8`, stride `0x758`로 고정됐다. `docs/history/laps/20260930_lap790_work_g2_esl2608_phase_a_address_repair_pass.md` |
| B. 선택·일반 명령 | PASS/parity | 이동·공격·정지·홀드·순찰을 4-way로 측정했다. 명령별 선택 유닛 `20/20`, 비선택 sentinel 변화 없음, crash 0, source 불변이었다. 사용자 신고인 Shift+클릭 단일 추가도 같은 Phase A 계약에서 `1→2`, 제거 `2→1`, 20에서 추가 거부 parity로 재현되지 않았다. |
| C. 생산·집결지·창모드 | PASS/parity + UNKNOWN + BLOCKED | worker 생산과 충분히 떨어진 좌표의 UI 집결지 지정은 4-way에서 rally `(94,57)→(94,52)`, worker `2→3`으로 PASS했다. hero/장수 생산은 prereq fixture가 성립하지 않아 runtime `UNKNOWN`; 관련 writer와 candidate diff는 `ORIGINAL_PARITY` 정적 판정이다. DxWnd는 같은 bundle에서 notepad는 실행됐지만 Syw2plus target child가 5회 모두 생성되지 않아 `BLOCKED(env: DxWnd game target launch)`이며 창모드 스크롤 수치는 측정하지 않았다. |
| D. 저장·로드·UI·고슬롯 | PASS/parity | 자체 save/load와 보호된 구 save fallback은 4/4 PASS, crash/timeout 0, prefix residue 0이었다. 고슬롯 초상화는 normal/fixed-start × baseline/candidate 4/4 PASS; candidate synthetic producer pointer `4092`, camera focus 변화 확인. 자연 장수 초상화와 24k/144k 부하는 이 보고서의 완료 근거가 아니다. |
| E. 멀티·전달 | BLOCKED(env) | 이번 회차의 짧은 환경 재확인에서 Wine `9.0 (Ubuntu 9.0~repack-4build3)`, builtin `dpwsockx.dll` SHA `3b4f6a9d355114fb78f1e2a3961f48324b654c7e246a1bcd0925f3cdbe7986c9`가 그대로였다. 보존된 native IPX 재현 로그는 서비스 공급자 로드 실패 → `DPERR_UNAVAILABLE` → null page fault를 기록한다. 2인 동기화·패킷 와이어 증거는 만들지 못했으며, 제품 FAIL이나 멀티 지원 완료로 해석하지 않는다. |
| F. 장기·부하 | UNKNOWN | 이번 점검 범위에서 24k/144k, 장기 tick, 지원 멀티는 수행하지 않았다. 기존 단일 런타임 PASS를 이 항목의 완료로 승격하지 않는다. |

## 사용자 신고 3건

1. **Shift+클릭 단일 추가:** ESL2608 stock 선택 상한20 조건에서 baseline/candidate 간 차이를 재현하지 못했다. `1→2`, 제거 `2→1`, 20에서 21번째 거부가 parity다. 이는 G5 선택 상한50 후보의 승격 근거가 아니며, 20기 계약의 점검 결과다.
2. **창모드 스크롤:** EXE 바이트 결함으로 판정하지 않는다. DxWnd가 동일 bundle의 notepad는 띄웠지만 새 Syw2plus target은 child/window/tick을 만들지 못했다. 배포 DxWnd 프로필의 파일명이 `[ESL]Syw2plus 2603.exe`에 고정돼 새 G2 파일명에 적용되지 않는 정적 위험도 함께 기록한다.
3. **장수 집결:** 일반 worker 집결지는 실제 UI 입력과 도착이 4-way parity다. hero/장수 자체는 prereq/생산 acceptance fixture가 성립하지 않아 `UNKNOWN(fixture contract)`이며, candidate 변경으로 인한 불일치는 발견되지 않았다. `ORIGINAL_PARITY`는 runtime PASS와 다르다.

## Phase E 짧은 재확인

실행한 read-only 확인은 `wine --version`, `sha256sum`(Wine `dpwsockx.dll`/`dplayx.dll` 및 배포 native DLL),
`strings`의 `DPWSCB_*` callback/stub 확인이다. 새 2인 게임을 다시 만들지 않은 이유는 lap742에서 같은 native
IPXWrapper 경로가 방 생성 시 2/2 재현됐고, builtin 대조군은 조용히 provider 화면으로 복귀했기 때문이다.
재확인 결과는 환경 변경 없음이며, 상세 raw는 다음을 사용한다.

- `temp/Syw2plus_patch/g5_multiplayer_lobby/20260928_lap742_crash_repro/result.json`
  SHA `c0cb357431662e65693e5ad170dea43a6d31d38bf9031399c2541752c0fb876a`
- `temp/Syw2plus_patch/g5_multiplayer_lobby/20260928_lap742_crash_backtrace/orchestrator.log`
  SHA `5e0df2c1a1e263982007ddfecf7e7e15a27f55e35ededab491b049ff0d04bf46`

## 결론과 다음 경계

G2 ESL2608 두 후보에서 이번 체크리스트의 측정 가능한 A/B/D 및 worker 집결지는 baseline parity로
확인됐다. hero runtime, DxWnd runtime, 부하·멀티, middle 독립 검수, 사용자 승인은 남아 있다.
제품 EXE 결함을 재현하지 않았으므로 이번 회차에는 EXE를 새로 만들지 않는다. 기존 EXE는 덮어쓰지
않았고, DxWnd 프로필 안내만 새 파일로 전달한다. 이 보고서는 G2 활성8인×전비10000 완료 또는
마일스톤 승인 문서가 아니다.

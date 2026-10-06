# 2026-09-30 | lap 802 | G2 ESL2608 Phase-C hero static parity

- 날짜/lap/목표: 2026-09-30 / 802 / G2 ESL2608 hero 집결지 정적 판정.
- 가설: hero 생성·집결지 적용 경로가 G2 후보 변경 범위에 포함되면 후보별 별도 runtime 검증/수리가 필요하고, 포함되지 않으면 원본 parity로 닫을 수 있다.
- 변경파일: `analysis/memory_maps/g2_esl2608_phase_c_hero_static_lap802.md`, `docs/STATUS.md`, `docs/feedback/INBOX.md`, 이 lap 기록. 제품 EXE·원본·probe 코드는 변경하지 않음.
- 원본SHA/후보SHA: normal baseline `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`; normal candidate `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`; fixed candidate `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`.
- 실행명령: `sha256sum`; baseline `objdump -Mintel -d` 전체 xref/집중 disassembly; read-only baseline↔두 candidate byte comparison.
- 정적 수치/근거: HQ writer `0x412540`가 선택 객체 `+0x654/+0x656`만 기록; new-unit init `0x411B85/0x411B8C`는 0으로 초기화; `0x48B12F/0x48B136`은 특정 type flag에서 자기 좌표+3을 기록. hero eligibility `0x43E7F0` 호출자는 `0x406B68`, `0x48D1B7`; hero counter gate는 `[ecx+0x980]`. 관련 candidate diff는 `0x412540`, `0x43E7F0`, `0x48B080`, `0x48D180`, `0x4AF400`, `0x4AF5E0` 각 0 byte.
- 판정: **`HERO_RALLY_STATIC=ORIGINAL_PARITY/RUNTIME_UNKNOWN`**. lap800의 prereq cache 미성립으로 hero runtime은 검증하지 않았고 제품 FAIL로 승격하지 않음. DxWnd는 lap801의 `BLOCKED(env: DxWnd game target launch)` 유지.
- fixture/환경: runtime 없음; 보호 baseline·기존 후보 EXE read-only, source SHA 확인. 기존 lap800 fixture는 재실행하지 않음.
- 다음행동: Phase D의 미니맵 gate parity·실교전·고슬롯 초상화 4-way로 진행. 새 middle이 hero 정적 근거와 G2 diff 범위를 독립 검수해야 하며, 최종 수정판/배포/사용자 승인은 미완료.

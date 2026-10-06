# 2026-10-07 | lap 1090 | 목표 G7 (사용자 FAIL 재작업 계획)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌). 게임 실행·source·하네스·테스트 변경 0, commit 0.
- 가설 / 사용자 관찰: 사용자(2026-10-06 19:31 KST, 일반판 `fb7c2131…`·시작자리고정판 `58b9b22a…`) G6 PASS, G7 FAIL — ↑/↓로 1P 아닌 자리에서 저장 → 타이틀·게임 중 로드 둘 다 seat 0(컴퓨터) 유닛으로 로드.
  가설: R4b는 저장된 로비 스냅샷 `0x632F7C`에서 own id 첫 일치로 local을 다시 계산하는데, 사용자 실경로 세이브의 스냅샷은 실제 자리와 어긋나 local이 0이 된다. 게임 중 로드 FAIL은 원래 local을 건드리지 않던 인게임 로드를 R4b가 회귀시킨 것.
- 이번 lap 정적 근거(원본 `b56986e0…a8ac`·이식판 normal `0e28ef57…d257`/fixed_start `703deaf4…6ea0` 직접 sha256 MATCH, 공유 temp `temp/Syw2plus_patch/20261007_lap1090_middle_review/`):
  - local `[0xB63FC4]` 쓰기 = 직접 `0x41CA85` 하나 + `0x43AF40` 호출 5곳뿐(`scan_lobby_controls.json` `633d64e3…`). 사용자 게임 중 local=k는 그때 live 표의 own id 첫 일치 결과.
  - 대기실 ↑/↓ 처리기 미발견(LISTBOX/COMBOBOX 문자열 0, `0x439520`은 비솔로 분기 `0x4B7F97` 전용). 정적 조사는 여기서 멈춘다(구현 우선).
  - G5SC 저장 `0x18A7800`·로드 `0x18A7880` 모두 끝이 fclose 꼬리 `jmp 0x4DA97C`(`0x18A7832` `E9 45 31 C3 FE`, `0x18A78D6` `E9 A1 30 C3 FE`), 두 이식판 동일·`.g5code` +0x8DA 뒤 0(`r5_site_bytes.json` `88b8b16b…`). 로드 체인 `0x44130B call 0x10910D0`(G2 PSN2) → `0x18A7880`.
  - 사용자 세이브 파일은 없다(공유 `260921_temp/save/` 비어 있음, 2026-10-06 19:44 생성).
- 판정: **H-G7x/R4b(cand67 `fb7c2131…`·`58b9b22a…`)는 사용자 실경로 FAIL → G7 현행 후보에서 철회**(기술 기록은 보존). 수리 경로 **R5 채택**: 저장 때 local·live 표 `0x632C9C`(0x170)를 G5SC 뒤 `'G7LS'` 꼬리로 기록, 로드 때 태그·solo 게이트가 맞으면 그대로 복원, 아니면 무변화(R4b hook 미적용). 설계·사전등록 W-0~W-3: `docs/work/active/G7_MIDDLE_LAP1090_USER_FAIL_R5_SAVE_TRAILER_HANDOFF.md`.
- 예상 PASS / FAIL 조건: 위 카드 §4(S-1~S-8). 진단 W-1(스냅샷 덮어쓰기 주입으로 R4b 사용자 증상 재현 여부)은 제품 근거 아님.
- 변경 파일: 새 카드 1, 이 기록, `docs/history/laps/20261007_lap1090_preserved_lap1089_escalate_sol_g1_huld.txt`(lap1089 ESCALATE_SOL byte 일치 원문, SHA256 `e58eeed0…6003`), STATUS·INBOX(처리 메모)·APPROVALS(사용자 세이브 요청)·`analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`(lap1090 절). `loop/ESCALATE_SOL` 삭제(원문 보존).
- G1 처리: lap1089 H-ULd 독립 재계산·H-W330 확정은 **보류**(사용자 G7 최우선). G7 R5 work 뒤 middle 큐로 STATUS에 남긴다. 근거·원문은 위 보존 파일.
- 회귀 / 남은 위험: 실제 ↑/↓ 경로 재현 BLOCKED 유지(W-3 시간 상자 재시도). R5도 사용자 재시험이 최종 판정. 멀티 비검증.
- 다음 한 가지: work(Sonnet) H-G7s — R5 구현·W-0~W-3 실행.

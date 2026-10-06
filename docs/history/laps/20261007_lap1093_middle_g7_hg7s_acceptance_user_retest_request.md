# 2026-10-07 | lap 1093 | 목표 G7 (H-G7s R5 독립 재계산·수용 → 사용자 재시험 요청)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 중간 계획·컨펌(middle) 1 lap. 게임 실행·source/하네스/테스트 변경·commit 0.
- 입력: lap1091 work 기록 `20261007_lap1091_work_g7_r5_save_trailer_hg7s.md`, lap1092 work ESCALATE_SOL(원문 byte 일치 보존
  `20261007_lap1093_preserved_lap1092_escalate_sol.txt`, SHA256 `dfb44392…c9ad542`), 카드 `docs/work/active/G7_MIDDLE_LAP1090_USER_FAIL_R5_SAVE_TRAILER_HANDOFF.md` §4.
- 가설 / 사용자 관찰: 사용자(2026-10-06 19:31) R4b FAIL. R5 = 저장 시점 local·live 표를 세이브 꼬리에 넣고 로드 때 그대로 복원하면 자리 결정 경로와 무관하게 복원된다.
- 예상 PASS / FAIL 조건: 카드 §4 W-1·S-1~S-8·fixed_start를 work 스크립트 없이 새 스크립트로 raw에서 다시 유도해 판정 불일치 0이면 수용.
- 변경 파일 / source fingerprint / 커밋: 문서만(이 기록·STATUS·APPROVALS·INBOX 메모·ESCALATE_SOL). source는 lap1091 그대로
  (`g7_save_trailer_local_restore.py` `c0ae1c5e…`·테스트 `d6ef4fed…`·`g7_save_load_probe.py` `0baa9990…`·`g6_shift_click_probe.py` `59b90726…` 직접 sha256 MATCH). uncommitted.
- 원본 SHA / 후보 SHA / fixture: 입력 이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…6ea0`(직접 MATCH). 혼자하기 기본 지도, 자리 2는 `lobby-snapshot` 우회(실제 ↑/↓ 아님).
- 실행 명령 / 산출물(공유 temp `temp/Syw2plus_patch/20261007_lap1093_middle_review/`):
  `PYTHONPATH=. .venv/bin/python -I recalc_lap1093.py <repo> <lap1091_dir> recalc_lap1093.json` — 스크립트 `42b9229c…86ee6`, 결과 `30168f39…155f`, failures [].
  focused `pytest` (R5·G6 패치 테스트·g7/g6 probe 테스트) **62 passed/4.13s**.
- 측정값 / 판정:
  1. **재조립 4/4 일치**: 이식판 + (G6 모듈) + 직접 바이트 쓰기(hook `jmp` rel 직접 계산·cave 바이트)로 normal+G6 `b582fb19…2dfd`·fixed+G6 `acf5bd3d…f1a4`·R5만 `4de640e6…4d43`·`7426e555…62c9`, 모듈 출력과도 같음. 바뀐 바이트 268(G6 포함)/238. restore exact, R4b 자리 `0x441310` 원바이트, cave 0 범위·G6 cave(+0xC00, 23 B)와 비중첩, scratch `0x18A6E00..0x18A6F80` ⊂ `.g5bss`(`0x18A6000`+0x1000, raw 0 = 실행 시 0 초기화).
  2. **cave capstone 명령 단위 일치**: save = pushad/pushfd → 헤더 16 B(`'G7LS'`·1·`[0xB63FC4]`·`movzx word [0x4ED848]`) → `fwrite 0x4DA39F`(buf,0x10,1,`[esp+0x28]`) → 표 `0x632C9C` 0x170 → popfd/popad → `jmp 0x4DA97C`. load = solo·`[0x18A68D0]=='G5SC'` 게이트 → `fread 0x4DA4A9` 헤더 eax==1 → 태그·v1·저장 solo 1·local<8 → 표 fread eax==1 → `rep movsd` 0x5C dword → `[0xB63FC4]`=저장 local. 조건 점프 8개 전부 공통 출구(popfd `0x18A7E96`). FILE* = 원래 `[esp+4]`(G5SC 블록이 `pop ebp` 뒤 `jmp fclose` tail call; pushad+pushfd 0x24 → `[esp+0x28]`), fwrite/fread 주소 = G5SC 블록 자신이 부르는 주소와 같음.
  3. **세이브 raw 꼬리 6/6**: cand-r5 세이브 5개(r5_s0/s2/s2r·fixed_s0/s2) 끝 0x180 = `'G7LS'`·v1·local(0/2/2/0/2 = 저장 시 live local)·solo 1, 꼬리 표 = 저장 시 live 표 0x170 byte 일치, G5SC 태그가 끝에서 592 B(=4+0xCC+0x180) = 꼬리가 G5SC 바로 뒤. R4b 세이브는 꼬리 없음·208 B(=4+0xCC), 크기 차 0x180.
  4. **판정 재유도(raw local·locals_seen·ps_seen·selected_owners) 불일치 0**: W-1 진단 R4b 인게임·타이틀 local 0·ps `[3,27,29]`(덮어쓰기 전 표 ≠ 이동 전 표) = 사용자 증상 재현 / S-1 타이틀 S2r(로드 전 local 0) → 2·`[3]`·owner `[2]` / S-2 인게임 S2r 2 / S-3 S2 둘 다 2 / S-4 S0 둘 다 0 / S-5 자리2 게임→S0 = 0, 1P 게임→S2r = 2, x12 타이틀 복귀 S2 2·S0 0 / S-6 꼬리 없는 old S2: 자리 2 게임 인게임 2 유지, 1P 게임 인게임 0·`[3,27,29]`, 새 프로세스 타이틀 0·`[3,27,29]`(원래 결함 유지 = 예상) / S-7 이식판(`0e28ef57…`)이 S2r 타이틀 로드 COMPLETE·local 0 / S-8 G6 `[2,3,4,5,6]`·1→3·3→2(victim 제거)·drag 50·추가 거부 50·60초 local 2 / fixed_start S2 2·S0 0(인게임·타이틀) / 로드 뒤 표 = 저장 표(cand-r5 10/10 byte 일치, R4b는 불일치) / EXE provenance 15/15·cleanup 15/15(game 삭제·prefix 프로세스 0).
  5. **정정 1(기록만)**: lap1091 W-3 "패널 변화 0"은 f2/f3/f6 첫 ↓ 단계에서 309/1,085 px가 있다(직전 캡처가 포커스 클릭 전이라 클릭 자체의 표시 변화). 키 상태 word 0·표 불변·local 0은 7/7 그대로 → W-3 BLOCKED 판정 불변.
  6. 관찰(위험 아님, 기록): 1P(자리 0) 게임의 live 표 id는 `[1×8]`로 own id 0이 없다(첫 일치 없음). R5는 local을 직접 저장하므로 영향 없고, 로드 후 `0x43AF40`가 다시 불려도 복원 표 = 저장 시 표라 저장 당시 결과와 같다.
- **판정: H-G7s PASS(partial, 기술) 수용, R5(G6+R5 normal `b582fb19…`·fixed `acf5bd3d…`)가 G7 현행 후보.** 사용자 합격 아님.
- 사용자 시험판 스테이징(공유 temp, `260921_temp` 배치는 root/사용자 몫): `20261007_lap1093_middle_review/user_test_staging/` — 일반판 `b582fb19…2dfd`·시작자리고정판 `acf5bd3d…f1a4`(파일명 `…_G5_선택50_G6G7_세이브자리수정R5_시험용.exe`, `xb` 신규 생성·재해시 MATCH)·안내문 `3f5622c9…0d7a`.
- 회귀 / 남은 위험: (a) 실제 ↑/↓ 경로 동일성 UNKNOWN(W-3 BLOCKED, 사용자 재시험이 판정) (b) 이전 판·원본 세이브는 꼬리가 없어 타이틀 로드 결함 유지(안내문 공개) (c) 자리 2 외·LAN 멀티 미검증 (d) S-7 선택 상한 50 미측정(이식판 바이트 불변) (e) 사용자 세이브 파일 요청(lap1090) 유지.
- 다음 한 가지: root가 시험판 전달·사용자 재시험 요청(ESCALATE_SOL). 사용자 판단은 비차단이므로 루프 다음은 middle(Opus) 보류 G1 H-ULd 검수(`20261007_lap1089_work_g1_huld_diag_ct_control.md`, lap1089 ESCALATE_SOL 원문 `20261007_lap1090_preserved_lap1089_escalate_sol_g1_huld.txt`).

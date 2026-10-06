# 2026-10-05 | lap 975 | G1 middle — lap974 H-W 독립 검수 · 다음 가설 H-F(`0x466070` diff 미러) 정의

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). `loop/.lap_counter` 975 읽기만. lap974 work의 `loop/ESCALATE_SOL`(요지: raw 재계산, 두 함수 경계 확인, H-T 방식 다음 가설·사전등록)을 입력으로 처리하고 삭제했다.
- 가설 / 사용자 관찰: 검수 대상 = lap974 H-W(census 창 서수 301~364 지연 + watch로 HP 바·유닛 덩어리 writer 확정). 새 사용자 관찰 없음.
- 예상 PASS / FAIL 조건: lap973 카드 §4 H-W PASS(hook 밖 같은 EIP ≥50%, mirror 미대상)·반증 (i)~(iii). 제품 helper 없이 재계산 불일치 0이고 EXE 경계가 기록과 맞으면 검수 PASS.
- 변경 파일 / source fingerprint / 커밋: 문서만 — 이 기록, 카드 `docs/work/active/G1_MIDDLE_W70_HW_ACCEPTANCE_RECT_FILL_DIFF_MIRROR_HANDOFF_LAP975.md`, `analysis/memory_maps/g1_unhooked_writers_466070_466b50_lap974.md` §3 정정(전사 오류), STATUS, `loop/ESCALATE_SOL` 삭제. 제품·하네스 source 불변(lap974 uncommitted 4파일 fingerprint 기록과 일치). 커밋 0.
- 원본 SHA / 환경 / fixture: 게임 실행 0. 보호 원본 EXE SHA256 `b56986e0…08a8ac` 직접 재계산 MATCH(읽기만). 입력 raw는 lap974 hp/unit(공유 temp 읽기만). 활성8인 부하증명 아님.
- 실행 명령 / 산출 해시(공유 temp `20261005_lap975_middle_review/`): `python3 recalc_lap975.py`(`29e5f581…3e1b`) → `recalc_lap975.json`(`1942385b…dbc4`); `.venv/bin/python disasm_lap975.py 466070:186 466B50:135`(`0054c36e…6e75`) → `disasm_lap975.txt`(`d28b5132…70b4`); `xref_lap975.py`(`f1c89b78…1852`) → `xref_lap975.txt`(`8e3066bf…bcc6`).
- 측정값 / 판정:
  - 재계산 불일치 0: 두 raw SHA 일치, present_skip 300→301·armed 301·selftest PASS, hit 126(present 302~364 각 2, 순서 hook 안→밖), hook 밖 `0x466114`(HP, 값 68)·`0x466BB3`(유닛, 값 66) 각 63/126, overflow 0. 스택 첫 값 `0x479044`(=`0x47903F` call 복귀)·`0x41A4FF`(=`0x41A4FA` call 복귀).
  - EXE: `0x466070` `ret 0x14`·5인자·prologue 5바이트 경계 정확·호출 8곳 — 기록 일치. **`0x466B50`은 `ret 0x18`(6인자: x·y·w·h·RLE·LUT, 클립 없음, 오른쪽→왼쪽)** — lap974의 `ret 0x1c`·7인자는 앞 함수 끝(`0x466B4A`)을 옮긴 전사 오류 → 주소 문서만 정정(raw·결론 불변). prologue 8바이트는 `rle_tinted_clip`과 동일, 호출 2곳. 두 함수 모두 mirror hook 대상 밖.
  - **H-W PASS(partial) 수용.** 다음 가설 **H-F:** `0x466070` exact-5-byte hook, 화면 frame 대상만 호출 전후 사각형 비교 → 바뀐 픽셀만 Scale2x 미러(`g1_overlay_blt_apply` 재사용). FEASIBLE. 사전등록 F-1 HP 바 423→≤42·F-2 영역 밖 신규 stale 0·F-3 hook/계수·F-4 안전/성능, 반증 (i)~(iii)은 카드 §4.
- 회귀 / 남은 위험 / 독립 검수·승인: lap974 결과는 이번 독립 검수로 기술 수용(진단 하네스). 사용자 마일스톤 승인 아님. V2s raw HOLD는 APPROVALS 사용자 판단 대기 그대로. 픽셀 1개씩 표본 한계·유닛 애니메이션 변형 writer 가능성 유지. 이번 lap은 문서만이며 직전 lap974는 실제 실행이 있었으므로 연속 1회다.
- 다음 한 가지: Sonnet work 1 lap — 카드 §4 H-F(회귀 테스트 RED→GREEN, `0x466070` hook + diff 미러, fresh save006 scale2x pair 2회), 사전등록 PASS/FAIL 그대로.

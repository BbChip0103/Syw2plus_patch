# 2026-10-05 | lap 978 | 목표 G6 (H-G6a 검수, G1 보류)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(독립 검수·중간계획). 게임 실행·source 변경·commit 0.
- 가설 / 사용자 관찰: lap977 work `loop/ESCALATE_SOL` 처리. lap977 H-G6a(이식판 `0x41DD82` 루프를 선택 개수로 한정)의 런타임 수치와 slot0 emulation 타당성을 독립 검수하고, 디스크를 회수하고, 다음 work를 정한다.
- 예상 PASS / FAIL 조건: probe-result 5개 재계산 불일치 0, 후보 바이트가 카드 lap976 §2와 일치하면 수용. emulation이 DESIGN G6 합격 문구("1P가 아닌 자리에서 재현")를 충족하는지 별도 판정.
- 변경 파일 / source fingerprint / 커밋: 문서만 — `docs/work/active/G6_MIDDLE_LAP978_HG6A_ACCEPTANCE_REAL_SEAT_HANDOFF.md`(신규), 이 기록,
  `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`(lap978 절 추가), `docs/feedback/APPROVALS.md`(비차단 질문 1줄), `docs/STATUS.md`. `loop/ESCALATE_SOL` 삭제.
  ignored 유지보수: `local/maintenance/20261005_lap978_g6_prefix_archive/`(archive.py·plan/report/restore_verification·tar.zst·inventory). uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(read-only 역어셈블),
  이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…6ea0`(배포 파일 직접 해시), 후보 normal `b50af2a615354fc90d5438137a374c909850bf8d308761c9b5b4750b426b2f4f`·fixed_start
  `7c891658a58d3f837a47e7dc8fc74dbd0bb3739030182f04b7f13091f97f64b5`(메모리 재빌드, 파일 쓰기 0). 런타임 fixture는 lap977 그대로(합성 op5, owner 0, 활성 78~96).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 temp/Syw2plus_patch/20261005_lap978_middle_review/recalc_lap978.py`(stdlib만) → `recalc_lap978.json` SHA256 `e1fcd193f04873ba7553bfc110c563e81549d088c538610766b0e2fe11854c46`.
  - `.venv/bin/python …/verify_bytes.py`(capstone 5.0.7, pefile) → `verify_bytes.json`. 정적 스캔 `xref_scan.py`·`gaks_scan.py`·`vk_scan.py`·`vk_switch_scan.py`·`vk_mem_scan.py`·`port_vk_scan.py`.
  - lap977 lobby 캡처 연속 diff(mtime 순): `.venv/bin/python …/seat_panel_diff.py` → `seat_panel_diff.json` SHA256 `23f92baf196899dd953e78b7bbe5847c48ee38d08201746122a669c62cdefb83`.
    ps7(확인 전) 방향키 4회·번호칸 클릭 뒤 방향키 4회 모두 좌측 패널 bbox None. r2/click run은 확인 뒤 입력이라 화면 전환 diff만 있다.
  - 디스크: `python3 local/maintenance/20261005_lap978_g6_prefix_archive/archive.py`(1차 시도는 가드가 호출 셸 명령줄의 스크립트 문자열에 자기매치해 계획 단계에서 중단, 삭제 0 — `archive_attempt1_selfmatch.log`).
- 측정값 / 판정:
  - 재계산 불일치 0: G6-1 orig@1·port@1 `[1,1,1,1,1,1]`(클릭 slot 합류 0/5), cand@1 `[1..6]`(5/5), port@0·cand@0 `[1..6]`. G6-2 모두 1→3(쌍 합류·외부 0),
    G6-3 모두 3→2(희생만 제거), G6-4 port/cand 50→50(추가 slot 미포함·집합 불변). 스냅샷 count==len 전부, cap 초과 0, 중복 0, slot0 poke readback 1, cleanup 프로세스 0.
  - 바이트: diff 30바이트(hook 8 + cave 22, 1바이트는 원래 0), hook/cave 역어셈블이 카드와 같고 cave 절대 참조 0, rollback byte-identical, 두 lane 동일 구조.
  - **H-G6a PASS(partial) 수용**(결함 분기 재현·제거, 비회귀). **DESIGN G6 합격 아님**: slot0 emulation은 local 0 유지라 실제 non-1P 자리가 아니다. G7도 실제 local≠0이 전제.
  - 자리 이동 BLOCKED 확인: 방향키·번호칸 클릭 뒤 방향키에서 자리 패널 변화 0(채팅 커서만 변함). 로비 local 갱신 경로 `0x4B7700`(`[0xC0D0F4]` → `0x632E0C` 복사 → `0x43AF40`) 확인.
    방향키 `GetAsyncKeyState`는 인게임 스크롤 `0x41D09F`뿐, 대기실 처리기 UNKNOWN.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 실제 자리 입력 경로 미확정. emulation이 놓치는 경로(시작 유닛 owner·AI 배정·DPID)는 미실행. fixed_start 런타임·세이브/로드·사람 플레이 미실행.
  사용자 확인 요청은 APPROVALS 비차단 큐. G6 사용자 마일스톤 승인 없음. G1 uncommitted 변경·H-F handoff 보존.
- 다음 한 가지: Sonnet work 1 lap — H-G6s(카드 §5): 하네스 `--seat-method keys-held`(A, S-1)와 `lobby-snapshot`(B, S-2)으로 실제 local=k를 만들고, 성공하면 같은 lap에 G6-1~G6-5를 O·P·C@k로 다시 실행. 둘 다 BLOCKED면 G6은 PASS(partial)로 두고 사용자 답을 기다린다.

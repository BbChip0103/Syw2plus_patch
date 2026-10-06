# 2026-10-05 | lap 976 | 목표 G6·G7 (G1 보류)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌). 게임 실행·source 변경·commit 0.
- 가설 / 사용자 관찰: 사용자 지시(INBOX 2026-10-05 03:01 KST) G6·G7 최우선. root `loop/ESCALATE_SOL`(03:07)을 받아 처리·삭제.
  G6 = Shift+클릭 두 번째 루프가 선택 개수가 아닌 칸 수 전체를 돌아 빈 칸(id 0)의 owner를 local과 비교 → local≥1이면 추가 중단.
- 예상 PASS / FAIL 조건: 카드 `docs/work/active/G6_MIDDLE_LAP976_SHIFT_CLICK_COUNT_BOUND_HANDOFF.md` §4·§5(G6-1~G6-5, 반증 (i)~(iii)).
- 변경 파일 / source fingerprint / 커밋: 문서만 — 위 카드(신규), `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`(lap976 재확인 절 추가),
  이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL` 삭제. uncommitted.
- 원본 SHA / 후보 SHA / 환경: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`Syw2plus/syw2plus_original.exe`, read-only),
  배포 이식판 normal `0e28ef57f8eb1f674df544ef84889bd2c51224720a09d0a18122e55f8399d257`(`260921_temp/…G5_선택50_시험용.exe`, test pin·읽어주세요와 일치),
  fixed_start `703deaf4c07b44975417f6835c569d65fa03adc2272ff6c75866da4723cd6ea0`(배포 파일 직접 재계산 = test pin). 후보 없음. 활성 플레이어/지도/fixture: 해당 없음(정적).
- 실행 명령 / 로그: capstone 5.0.7 역어셈블 `temp/Syw2plus_patch/20261005_lap976_middle_review/disasm.py`·`xref_local.py`,
  출력 `orig_41DC40.txt`·`orig_41DD10.txt`·`port_41DC40.txt`·`orig_local_writers.txt`·`orig_local_callers.txt`·`orig_xref_b63fc4.txt`(390 read xref).
- 측정값 / 판정:
  - 스택 배열 0 초기화 `0x41DC64`(0x14/0x32칸), 압축 복사 `0x41DD48`, 전체 칸 루프 `0x41DD82..0x41DDE7`, 중단 `0x41DE40`, 드래그 루프 빈 칸 skip `0x41DF59` — 분석 문서와 불일치 0.
  - 이식판 함수 diff = 스택 크기·칸 수·배열 주소·owner 테이블 재배치뿐.
  - `[0xB63FC4]` 직접 쓰기 `0x41CA85` 하나, `0x43AF40(&local)` 호출 5곳.
  - **G6 FEASIBLE**(첫 work H-G6a 사전등록), **G7 = 관측 먼저**(H-G7o, H-G6a 수용 뒤).
- 회귀 / 남은 위험: 런타임 미확정 — 방향키 자리 이동 하네스 미검증(실패 시 BLOCKED 처리 규정), 유닛 0 owner 값 런타임 미측정,
  cave 영역 미참조는 work가 증명해야 함. G7 복원 대상 파생 상태 미결. 독립 검수: H-G6a 결과는 다음 middle. 사용자 승인: 해당 없음.
- 다음 한 가지: Sonnet work 1 lap — H-G6a(카드 §2~§5): 이식판 위 `0x41DD82` 개수 한정 cave 패치 + 회귀 테스트, 방향키 자리 이동 하네스로
  O/P/C @local≥1 및 C@1P 런타임 측정.

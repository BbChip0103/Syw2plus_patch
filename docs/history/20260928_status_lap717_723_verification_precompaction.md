# STATUS 검증 상태 압축 보존 (lap717~723, 원문 50줄)

lap724 압축 시점의 `docs/STATUS.md` "## 검증 상태" 절 원문 50줄, SHA256
`e6facd6ead26c5496d270a4e4acabed8f336925d6a6b7812d1f6c9cc00d25f63`. 아래 그대로 보존한다.

---

## 검증 상태

lap717(work, 자체 raw 관측): 원본20/v4후보50 정지·홀드·순찰 paired **50/50 PASS**(v3는 20/50
FAIL). 16:45 운영자 후속 지시로 회귀 추가 실행 — **이동 50/50 PASS**(`converged_at_s=0.15`),
**부대지정+저장/로드 `PASS_UI_ROUNDTRIP`**(checks 7/7 True), **공격 단일측정**
`ever_command4_count=30/49`(v3 lap688 N=5 분포 27~49·중앙값32 안에 위치, N=5 반복은 예산상 생략).
`make check` **1101 passed(890.28s)** 전부 PASS, `SAFETY_PASS`, 신규 테스트 4개(v4 결정론+cave여유+
본체동일성+게이트구조), 원본 SHA 불변(모든 실행), cleanup 매회 프로세스 잔류 0, EXE/원본 미변경.
**추가로 `tools/g5_command_coverage_probe.py`(direct session이 15:49 FAIL을 낸 바로 그 도구, 원문
무수정·monkeypatch로 v4 연결) 1회 전체 재실행 — 정지/홀드/순찰 버튼·단축키 8항목 전부 50/50,
ALT/Ctrl/Shift/일반 드래그 전부 50/50, 미니맵은 원본도 무반응(회귀 아님).** gdb hook-site 실측(①)은
4회 재시도 모두 `post_marker_hits=0`으로 **BLOCKED**(lap681의 동일 현상 재확인·확장) — 상세는
`docs/history/laps/20260927_lap717_work_g5_v4_stop_hold_patrol_inverted_gate_pass.md`.

lap718(work, 독립 추가측정, middle 미회부): lap717이 예산상 생략한 공격 N=5(middle 요청 (d))를
같은 monkeypatch 방식(제품 코드 0 변경)으로 채움 — v4(50선택) `ever_command4` 중앙값
**61%**(24~65% 범위, run1=30·2=31·3=28·4=24·5=32, `/49`), 원본(20선택) lap688 중앙값58%보다
낮지 않고 v3(50선택) lap688 중앙값65%와 같은 변동폭. `attack_pass` 5회 중 2회True(표본잡음, v3와
동일 패턴). 크래시0, `source_unchanged` 4회 전부true, `candidate_sha256` 결정론 일치. 상세
`docs/history/laps/20260927_lap718_work_g5_v4_attack_n5.md`.

lap719(middle, Opus): lap717/718 독립 검수 → **v4 2단 CONDITIONAL PASS(단일플레이, 측정 명령 한정)**.
v4 원본 재빌드 `0e472792…` 일치, 대상 pytest 9 passed, 모든 후보 raw `private_exe_sha256`=v4. (a) v4 코드=lap676
문서 집합이나 문서 자체가 raw와 다름(`0x19b/0x19d~0x19f`는 어느 호출부에도 없음, `0x41F0A4`는 비명령이 아니라
런타임 `word [0x892ffe]` 명령 발행 호출부) — 안전 위험 아님, 범위 누락 위험만. (b) 즉치 21곳은 v3·원본과 동일
동작, `0x4AE550` 포인터 참조 0 → 안전. (c) 유효. (d) lap689 인정 지표(t=0 `pending==0x1000004`)로 재판정: v4 2/5회
49/49, v3·원본도 2/5 — 추가 N 불요. 잔여 R1: 50→21~49 **선택 축소 후 명령**이 미측정(청크가 꼬리 칸을 항상 넘김).
상세 `docs/history/laps/20260927_lap719_middle_g5_v4_independent_review_conditional_pass.md`.

lap721(middle, Opus): lap720 raw 3개 SHA 일치·독립 재계산 일치(누출0·누락0, 꼬리 칸 전부0), v4 재빌드
`0e472792…` 일치, v4 pytest 4 passed, `SAFETY_PASS`. 원본 제거 루틴 `0x412E9F`가 칸을 **제자리 0화**(압축 없음)
하고 명령 본문 `0x4AE587`이 고정20칸+`0x416F70` 유효성 검사임을 disasm으로 확인 → **R1 확정 FALSIFIED**.
그러나 같은 사실에서 **R3**: 선택 배열이 구멍 있는 집합이라 50선택 후 사망 등으로 count≤20이 되면 래퍼가
`entries[0:20]`만 쓰는 원본 본문으로 가서 인덱스≥20 생존 유닛이 명령을 못 받는다(v3·v4 공통, 원본 대비 회귀,
정적 PLAUSIBLE·런타임 미측정). v4는 CONDITIONAL PASS 유지(확정 승격 불가). 원본/후보 run scene 불일치(10,49 vs
93,56) 기록 누락도 지적. 상세 `docs/history/laps/20260927_lap721_middle_g5_v4_r1_confirmed_falsified_r3_sparse_gap.md`.

lap723(work, 자체 raw 관측): 신규 진단 op(원본 사망처리 함수 `FUN_00409C70` 직접 호출, 공유
`runtime_bridge.c`/G2 pin 무영향 별도 파일 `g5_r3_death_bridge.c`)로 v4에서 50선택→인덱스0~29 30기
실제 사망→count=20·생존20기(인덱스30~49) 상태를 만들어 STOP·MOVE 측정 — **생존 20/20 전부 미수신
(R3 CONFIRMED, raw)**. 같은 절차를 v5(`check_count`를 "count>20 또는 entries[20:50] 살아있는 칸"으로
확장)에 적용 — **생존 20/20 전부 수신(PASS)**. 원본 대조(20선택→10제거→생존10, 인덱스10~19)도 10/10
PASS(방법론 자체 유효 확인). v5 STOP/HOLD/PATROL 50/50 회귀 PASS. v5는 pytest로 check_count 외 v4와
byte-identical 확정(cave여유·게이트opcode구조·스파스스캔범위·청크본체 modulo relocation 5개 테스트).
`make check` **1106 passed(898.62s)** 전부 PASS, `SAFETY_PASS`. 미완결: ALT/Ctrl/Shift 드래그·공격·
부대저장로드는 `g5_command_coverage_probe.py` 자체 목적지 캘리브레이션이 이번 지형(world 93,56)에서
2회 연속 실패해 v5로 직접 재측정 못함(도구 자체의 기존 취약점으로 판단, v5 변경과 무관 — 그 도구의
로비 단계에서 실패해 v5 게이트에 도달하기도 전임). 상세
`docs/history/laps/20260928_lap723_work_g5_r3_live_confirmed_v5_fix_pass.md`.

# 2026-09-27 | lap 721 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, 중간(middle, 진단·계획·확인). 게임 코드·도구 무변경(문서만).
- 가설 / 사용자 관찰: lap720 work가 R1(선택 축소 후 청크 꼬리 칸의 잔존 핸들 누출)을 FALSIFIED로
  보고하고 middle 독립 검수를 요청(STATUS 다음 한 가지, APPROVALS lap720 항목). 검수 질문: ① raw가 주장과
  일치하는가, ② 원본 재선택이 완전분리였던 대조의 유효성, ③ 버퍼 zero-fill 근거가 R1 반증에 충분한가,
  ④ v4 lap719 CONDITIONAL PASS를 확정으로 올릴 수 있는가.
- 예상 PASS / FAIL 조건: raw 재계산이 leaked=∅·missed=∅·deselected=initial−partial과 일치하고, 선택 배열
  쓰기 경로 전체에서 "count 뒤 잔존 핸들"이 생길 수 없으면 R1 확정 FALSIFIED. 확정 PASS로 올리려면 청크
  게이트와 선택 배열 구조 사이에 다른 미측정 누락/누출 경로가 없어야 한다.
- 변경 파일 / source fingerprint / 커밋: 이 기록, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`,
  `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`(lap721 절 추가). 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경: 보호 원본 `b56986e0…c9c08a8ac` 재해시 일치. v4를 원본에서 메모리 재빌드 →
  `0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb`(lap717~720 일치). 파일 SHA 재확인:
  `tools/g5_selection_shrink_leak_probe.py` `3a5b6207…`, `patches/selection/g5_selection_cap50_v4.py` `8982da56…`(lap720 기록 일치).
- 실행 명령 / 로그: lap720 `probe-result.json` 3개 SHA256 재계산(`8c387f64…`/`b56aef77…`/`cee5fbef…` 전부 일치) 후
  독립 파이썬으로 집합 재계산. `objdump -d -M intel` 원본 `0x4AE550..0x4AE640`, `0x412D90..0x412F10`, `call 0x412d90`
  호출부 11곳(`/tmp/lap721_orig.asm`, 보존 안 함·재생성 가능). `pytest patches/selection/test_g5_selection_cap50_v4.py` 4 passed, `checks/safety.sh check` `SAFETY_PASS`.
  게임 실행 없음.

## 측정값 / 판정

1. **raw 재계산 — lap720 주장과 일치.** 원본: initial20·partial15·겹침0·deselected20, STOP 수신 15 = partial,
   누출 0. 후보 50→47: 겹침41·deselected9, 수신47, 누출0. 후보 50→27: 겹침21·deselected29, 수신27, 누출0.
   관측 56기 중 partial 밖 수신 0(3회 모두). 버퍼 꼬리 `slots_all[count:]` 원본5·후보3·후보23칸 전부 `0x0`.
   cleanup 잔류 0, `source_unchanged` 3/3, 후보 raw `private_exe_sha256`=v4.
2. **대조 유효성:** 원본 run은 world(10,49)·worker type21, 후보 두 run은 world(93,56)(얕은 run worker type7)로
   **paired가 같은 scene이 아니다**(lap720 기록은 이를 적지 않음). 누출 판정은 각 run 내부 자기완결(선택/비선택 대비)이라
   판정은 유지되지만 "paired 대조"라는 표현은 부정확 — 방법론 오탐 없음 확인 용도로만 인정.
3. **R1 확정 FALSIFIED(정적 근거 추가).** 원본 선택 제거 루틴 `0x412E9F..0x412EFC`는 일치 칸을 **제자리 0화**
   (`mov word [ecx*4+0x899028],di` / `+0x89902a`) 후 count−1, 추가 루틴 `0x412E3C..0x412E6E`는 첫 빈칸(0,0)에
   기록. 드래그 재선택은 배열 전체를 지우고 다시 채움(lap720 raw). ⇒ count 뒤에 "이전 핸들"이 남는 쓰기 경로가
   없다. 명령 본문 `0x4AE587..0x4AE623`은 count와 무관하게 **고정 20칸**을 복사하고 `0x416F70` 유효성 검사를
   통과한 칸만 패킹 → 0칸은 원본에서도 매번 건너뛴다(청크3 zero-pad·축소 후 0칸 모두 원본 동작 범위).
4. **새 잔여 위험 R3(미측정, v3·v4 공통) — 희소 선택 명령 누락.** 위 3의 결과로 선택 배열은 **구멍 있는 집합**이며
   count는 "마지막 칸 인덱스"가 아니다. 그런데 v3/v4 래퍼 `check_count`는 `movzx eax, word [SELECTION_BASE]`;
   `cmp eax,20`; `jle original_body`이고 original_body는 `entries[0:20]`만 복사한다. 따라서 **50 선택 후 제거
   이벤트로 count≤20이 되었는데 살아 있는 칸이 인덱스 20 이상에 남으면**, 그 유닛들은 명령을 받지 못한다.
   제거 경로 후보: `cmp byte [unit],1`(선택 플래그) 뒤 같은 인자 2개를 push하고 `call 0x412D90` 하는 호출부 7곳
   (`0x409C8E 0x409FB9 0x412A1E 0x476EDC 0x48E7E0`=push 0,0; `0x44302D`=push ebx×2; `0x48E209`=push ebp×2 —
   사망/소멸/탑승 등 추정, 개별 분류·레지스터 값 미확인). `0x407192`·`0x47B5B9`는 push 0,1(다른 인자). 예: 50기 부대 전투에서
   30기 사망 → 생존 20기 중 인덱스≥20 칸은 정지/이동/공격 무반응. 원본(용량20)에서는 불가능한 상태라 **원본 대비
   회귀 가능성**. 인과 사슬은 정적으로 닫혔으나 런타임 미측정이라 `PLAUSIBLE`로 둔다.
   (count>20인 희소 상태는 청크가 용량 전체 50칸을 덮으므로 안전 — 이것이 R1 반증과 같은 이유.)
5. **판정:** R1 = **CONFIRMED FALSIFIED**. v4 2단은 **CONDITIONAL PASS 유지(확정 승격 불가)** — 조건이 R1에서
   R3로 바뀜. R2(미측정 명령 버튼 opcode) 후순위 유지. 멀티 `UNKNOWN`. 사용자 milestone(v3→v4 교체·G1 재개)은
   R3 결과 전에는 요청하지 않는 것이 맞다 — 승인된 v3도 같은 게이트를 가져 R3가 v3 승인 범위에도 걸린다.

## work tier handoff (다음 한 가지, 구현 우선)

1. **R3 probe(FEASIBLE):** v4에서 드래그 50 선택 → **실제 입력/게임 이벤트로** 인덱스 0..29 쪽 유닛 30기를 선택에서
   제거(우선: Shift+클릭 해제 또는 선택 패널 초상화 해제가 `0x412D90(0,0)`을 타는지 1회 확인; 불가하면 fixture 유닛
   사망 — 적 공격/HP 조작, 어느 쪽인지 명시) → count≤20·생존 칸 인덱스≥20 확인(전체 버퍼 덤프) → STOP 버튼 →
   `unit+0x384` `0x1000002` 수신 수. PASS=생존 전원 수신, FAIL(R3 CONFIRMED)=인덱스≥20 칸 미수신.
   원본 대조: 원본은 이 상태가 성립 불가함을 기록(원본20 → 10 제거 → 10/10 수신)만.
2. **FAIL이면 같은 lap에서 v5:** `check_count`를 "count>20"이 아니라 "`entries[20:50]`에 0이 아닌 칸이 하나라도 있으면
   청크"로 바꾼다(청크 창·본문·zero-pad는 v4와 동일, 최소 변경). 재측정: R3 probe, `g5_command_coverage_probe.py`
   정지·홀드·순찰·이동 50/50, lap720 축소 probe 1회, 부대지정/저장로드, `make check`. 후보 SHA 기록.
3. 이후 새 middle 검수 → 사용자 milestone(v3→v4/v5 교체·G1 재개) 요청.

- 회귀 / 남은 위험: 이번 lap 제품 변경 0. R3(PLAUSIBLE, 우선), R2(후순위), 멀티 UNKNOWN, 원본/후보 scene 불일치 기록 누락.
- 다음 한 가지: work tier R3 probe(위 1), FAIL이면 v5(위 2).

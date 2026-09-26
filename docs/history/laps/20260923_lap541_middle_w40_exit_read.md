# 2026-09-23 | lap541 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 middle(진단·계획·확인). 게임 코드 hands-on 수정 없음.
  사양 `docs/work/active/G2_STRATEGY_W40_STOP_ISSUER_LAP538.md`(SHA `542f45fa…04ef9`, 재확인 일치) §3 2행·K2 E2.
- 가설 / 사용자 관찰: A·B를 멈춘 `FUN_00471AF0` 0 반환 출구 1개를 원시/정적 근거로 특정할 수 있다. 그 출구의 **주소·비교 필드·뒤집는 fixture 값**이 나오면 E2 조건이 충족된다.
- 예상 PASS / FAIL 조건(실행 전 고정): 출구 주소·비교 필드·fixture 값 세 가지가 모두 특정되면 `E2_MET` ⇒ work 1회(H7' + fixture).
  하나라도 못 하면 `E2_NOT_MET` ⇒ S1 `BLOCKED`, 사용자 보고(§4).
- 이전 바퀴 검수(lap540): lap540 도구 4개·산출 3개와 W40 원시 `triggers.jsonl` `bd8836f1…`·`trace.jsonl` `24e871e6…`, `original.bin` `b56986e0…`·`candidate.bin` `a10024de…`의 SHA가 lap540 기록과 같다.
  원본 exe `b56986e0…` 불변. lap540 판독(값4 case `0x48e815`, 게이트 `0x471600` 스텁·`0x471af0`)을 디스어셈블로 다시 확인했다.
- 변경 파일 / source fingerprint / 커밋: repo 비문서 변경 0. 문서만: 이 파일,
  `analysis/memory_maps/g2_attack_tick_zero_exits_00471af0_lap541_20260923.md`(신규), `docs/STATUS.md`, `docs/feedback/INBOX.md`(처리 추기), `loop/ESCALATE_SOL` §95. 커밋 0(uncommitted).
  도구·산출(temp) `temp/Syw2plus_patch/g2_capacity/20260923_lap541_middle_w40_exit/`: `pe_text.py` `2c2a6639…`(lap540 복사), `fun_471af0.dis` `78d13c7d…`,
  `fun_40b810_tail.dis` `1782ec3d…`, `type_chase_limit.py` `cd7108d5…`, `type_chase_limit.json` `9cf118a8…`, `type_chase_limit.txt` `bd1854e7…`, `neighborhood.py` `337c73d7…`, `neighborhood.txt` `c9594fca…`.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기만), 후보 `a10024de…`. 게임 실행 0. fixture는 W40 그대로다(재실행 없음).
  타입 행 값은 lap527 정적 추출 `lap527_rows.json` `e29d3339…`에서 읽었다.
- 실행 명령: `python3 type_chase_limit.py`, `python3 neighborhood.py`, capstone 디스어셈블(`pe_text.dis`).
- 측정값 / 판정:
  - **출구 후보 좁힘(정적):** type 2가 적 유닛을 표적으로 할 때 도달 가능한 0 출구는 두 계열뿐이다.
    (V) `0x471c18`/`0x471ebd`/`0x471f90`: `FUN_00415880`==0(자기 `+0x31c`==0 ∨ 표적 사망 ∨ 자기 자신 ∨ 자기 `+0x1d4`==1), `+0x708`=1을 남긴다.
    (C) **`0x472042`**: `+0x216` > `+0x218`(추격 포기).
    나머지(`+0x634` 경로, `+0x1d8` bit `0x1000000` 경로, 위치 표적, 같은 편)는 배제했다. 근거는 memory map 표.
  - **비교 필드 값:** `+0x218` = 타입 행 `+0x4A`(생성 시 `0x411eda` 한 곳). type 2 = **1**, K3 후보 6종 모두 1, **W35에서 교전한 type 110도 1**, 공격 가능 62행 중 56행이 1이다.
    ⇒ 상한 값은 교전 여부를 가르지 않는다. 타입 교체나 값 변경으로 뒤집는 fixture 값이 없다.
  - `+0x216` 의미: 하위상태 4/5에서 셀 경계(`+0x692`==0)이고 이동 스텝 반환 >0(도착·경유점·제자리 경로·이동 불가)이면 +1, 칸 이동 중이면 0이 된다. ⇒ 상한 1이면 경계에서 진척 없는 틱이 연속 2번이면 포기한다.
    이것을 뒤집는 변수는 **접근 경로가 트였는지(배치 기하)**다. 단일 필드 값이 아니다.
  - **A·B가 실제로 탄 출구: UNKNOWN.** 스택 idx0~25는 모두 CmdStop 사슬 프레임이다(`FUN_00471AF0` 잔여 없음). trace에는 `+0x1f0`·`+0x216`·`+0x708`·`+0x31c`·`+0x1d4`가 없다.
    정황: B는 북쪽이 자기 owner3 유닛 줄(y=16, x=52~64)로 막혀 표적 반대 방향으로 우회했고 162틱 뒤 정지했다(C와 맞는다). A는 15틱 만에 정지했고 판별 근거가 없다.
  - 부수 확정: 복귀 모드 writer = op8 `FUN_00415480` 자신(`0x415535` → `FUN_00415940(3, …, 출발 xy)`). 공격 뒤 출발점 복귀는 원본 설계다.
  - **판정 `E2_NOT_MET`**: 주소·비교 필드는 유력 후보로 특정했다(`0x472042`, `+0x216`>`+0x218`). 그러나 (1) A·B의 실제 출구가 미확정이고 (2) 뒤집는 fixture **값**이 존재하지 않는다(상한은 원본 전 전투 타입 공통 1).
    ⇒ 카드 §3 2행 규칙대로 **S1 교전 입력 경로 `BLOCKED`**, 사용자 보고 대상.
- 충돌·주의(승격 사유): lap532가 미리 고정해 둔 "밀집 블록이 길을 막으면 전열 배치(6~10칸 빈 띠)" 분기는 lap535에서 "원시 불지지"로 보류됐다.
  이번 정적 판독은 "경로 진척 없음 → 추격 포기"라는 기전과 B의 자기 편 벽을 새로 보였다. `BLOCKED` 보고의 §4 선택지 (가)/(나)/(다)에 **(라) 전열 배치 재개**를 넣을지는 middle 권한 밖이다(lap535 보류의 재판정) ⇒ strategy 회부(`ESCALATE_SOL` §95).
- 회귀 / 남은 위험 / 독립 검수: 게임 실행 0, source 변경 0, 커밋 0. `checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS 검증 상태에 적는다. source가 바뀌지 않아 `make check`는 생략했다(N22).
  위험: (C) 귀속은 정황이다. (V)의 `+0x31c`/`+0x1d4` 의미는 미판독이다. t0 배치는 시딩 직후 값이고 지형이 없다.
  문서 회차 streak: lap540·541 연속 2회다. PROMPT ③에 따라 **세 번째 문서 회차 전에 strategy가 계속/중단을 판정해야 한다.**
- 다음 한 가지: **strategy(Opus5.5)** — §95 판정. (a) S1 `BLOCKED` 사용자 보고를 §4 (가)/(나)/(다)로 확정할지, (b) 전열 배치 (라)를 추가하거나 fixture 범위 안 work 1회로 재개할지 정한다.
  (b)를 고르면 `+0x708`·`+0x1f0`·`+0x216`·x,y를 기록 필드에 추가해 출구를 런타임으로 확정하는 것이 최소 비용이다(E2 밖 probe라 strategy 허가가 필요하다).

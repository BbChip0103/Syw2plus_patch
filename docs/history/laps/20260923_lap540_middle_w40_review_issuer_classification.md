# 2026-09-23 | lap540 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 지정 역할 middle(진단·계획·확인).
  사양 `docs/work/active/G2_STRATEGY_W40_STOP_ISSUER_LAP538.md`(SHA `542f45fa…04ef9`, 재확인 일치) §2 분류·§3 분기.
- 가설 / 사용자 관찰: (1) lap539 자기 라벨 `ISSUER_FOUND`와 I_A·I_B site `0x48e83c`, R_B site `0x48bba3`이 원시로 재현되는가.
  (2) `0x48e83c`의 `ISSUER_FN`과 호출자 1단을 한 번 읽어 `OWNER_AI`/`UNIT_OTHER`/`UNCLASSIFIED`를 정한다(문서 1회, 60분).
- 예상 PASS / FAIL 조건: (1) `triggers.jsonl`만으로 CmdStop 127·CmdMove 44 `call+5` 집합을 새로 만들고, op8 뒤 첫 `new`==2의
  esp 최근접 일치가 lap539와 같으면 일치. (2) 카드 정의: owner 인덱스 AI 상태를 읽거나 owner 루프에서 불리면 `OWNER_AI`,
  유닛 필드·지형·목표 조건만 보면 `UNIT_OTHER`, 60분 안에 못 가르면 `UNCLASSIFIED`.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): repo 비문서 변경 0. 문서만: 이 파일,
  `analysis/memory_maps/g2_unit_attack_cmd4_stop_issuer_0048ddd0_lap540_20260923.md`(신규), `docs/STATUS.md`,
  `docs/feedback/INBOX.md`(처리 한 줄), `loop/ESCALATE_SOL` §94. 커밋 0(uncommitted).
  재계산 도구는 temp에만: `temp/Syw2plus_patch/g2_capacity/20260923_lap540_middle_w40_review/`
  (`pe_text.py` `2c2a6639…`, `recompute_w40.py` `2b24d7b2…`, `recompute_w40.json` `d0287c38…`, `diff_windows_w40.py` `39f38d16…`,
  `diff_windows_w40.json` `73989d59…`, `decode_diffs_w40.py` `251bf96b…`, `decode_diffs_w40.json` `f2427a53…`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `Syw2plus_re/Syw2plus/syw2plus_original.exe`
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기만, W40 스냅샷 `original.bin`과 동일),
  후보 `candidate.bin` `a10024de…bb2d68`. 게임 실행 0. fixture는 W40 그대로(재실행 없음).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 recompute_w40.py`, `python3 diff_windows_w40.py`, `python3 decode_diffs_w40.py`.
  입력 원시: `triggers.jsonl` `bd8836f1…`, `trace.jsonl` `24e871e6…`. `h16_report_*.json`·`run_summary.json`의 판정은 참조하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **(1) 라벨 재현 PASS.** CmdStop 127·CmdMove 44 재계산 일치. 트리거 20건(WA8·WB8·WC4), 전이·pc 분포가 lap539와 같다. `M0'` 참(A t1087 `1→4`).
    I_A = t1103, I_B = t1281, 둘 다 스택 idx25 `0x48e841` ⇒ site `0x48e83c`. R_B = t1283 idx25 `0x48bba8` ⇒ site `0x48bba3`.
    WC: 대기 목표 (61,12) → 정지 시 0 → 복귀 이동 (56,17) → 0. **B 복귀 좌표 (56,17) 확인.**
    추가 관측(lap539 보고에 없음): A·B의 **두 번째** 정지(t1112·t1470)는 c1 `0x40c3a9`(`FUN_0040C390`, 호출자 `0x48e70b` = 이동 case)다.
    즉 순서는 공격 case 중단(`0x48e83c`) → idle 복귀 이동(`0x48bba3`) → 도착 정지(c1)다. c1은 첫 정지의 발행자가 아니다.
  - **(2) 분류: A=`UNIT_OTHER`, B=`UNIT_OTHER` ⇒ 라벨 `ISSUER_FOUND(A=UNIT_OTHER,B=UNIT_OTHER)`.** 상세 주소는 memory map 문서.
    - `ISSUER_FN` = `FUN_0048DDD0`: 유닛 1기 갱신 상태기계(thiscall, `switch(+0x290)`). site는 **값 4(공격 명령) case**다.
      `0x471600`은 항상 1인 스텁이고, 실질 게이트는 `FUN_00471AF0`(공격 명령 1틱 처리)의 0 반환이다.
    - 호출자 1단 = `FUN_0040FC70(slot)` ← `FUN_0041CB40`의 **슬롯 순회**(`0x41cd11`). AI owner 스텝(`0x43F5D0`, `tick&7`)을 거치지 않는다 ⇒ owner 루프 아님.
    - `FUN_00471AF0`이 보는 것은 유닛 필드(표적 슬롯·종류·사거리·추격 계수 `+0x216`/상한 `+0x218`·하위상태 `+0x1f0`·자기/표적 xy)다.
    - **주의(정의 경계):** `FUN_00471AF0`에는 `PlayerStruct[owner].+2`(ai) 읽기가 **한 곳** 있다(`0x471bbb`). 그러나 이 읽기는
      `0x4177a0(자기, 표적 owner)`==1(**같은 편 표적**) 조건 안에만 있다. W40 표적은 다른 owner이고 8 owner의 편 byte가 모두 다르다(lap525).
      그래서 이번 정지에는 도달할 수 없다고 판단해 `OWNER_AI`로 보지 않았다. 카드 문구("AI 필드를 읽거나")를 글자대로 적용하면 `OWNER_AI`가 되므로 이 해석을 §94에 명시했다.
      `FUN_0048DDD0` 앞머리의 PlayerStruct `+0xD32`/`+5` 읽기는 `[0xb631f4]` 디버그 문자열 출력뿐이다.
    - R_B `FUN_0048BB20`: idle(`+0x290`==1) ∧ `+0x390`==3 ⇒ `+0x390`=1, `+0x634`≠1이면 `CmdMove(uid, +0x394 xy)`. 유닛 필드만 본다(`UNIT_OTHER`).
      trace에서 op8 수락 직후 `f_0x390`=3이 된다 ⇒ **복귀는 op8 명령이 남긴 "복귀 모드" 때문이다**(`+0x390`=3·`+0x394` writer는 미확인).
    - 원본↔후보 창 대조: `FUN_0048DDD0` 56B·`FUN_00471AF0` 24B·`FUN_0040FC70` 4B 차이는 전부 유닛 풀 기준 재배치(`0x66b790+off→0x108c000+off`).
      `0x471600`·`0x48bb20`·`0x4177a0` 차이 0 ⇒ `REVERT_CANDIDATE_DIFF` 아님. lap539의 R_B 창 56B "커버리지 사각" 판단도 값 디코드로 확인했다.
  - (3) 어느 0 반환 출구를 탔는지는 **미확정(UNKNOWN)**이다. W40은 `+0x1f0`·`+0x216`·`+0x218`·`+0x31c`를 기록하지 않았다.
    B는 (56,17)→(63,19)로 움직였지만 사거리에 못 들고 수락(t1119) 162 tick 뒤 중단했다. 추격 상한 출구 `0x472042`(`+0x216`>`+0x218`)와 맞지만 정황뿐이다.
    A는 수락(t1088) 15 tick 만에 중단됐다. 출구 후보가 여럿이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임 실행 0, source 변경 0, 커밋 0. `checks/safety.sh check` `SAFETY_PASS`,
  `checks/context_limits.py` `CONTEXT_PASS`(이 회차 산출 뒤 재확인). source 불변이라 `make check` 생략(N22).
  위험: 위 정의 경계를 strategy/사용자가 글자대로 보면 §3 1행(`BLOCKED`·사용자 보고)으로 바뀐다. 문서 회차 streak은 1회(lap539는 실행 회차).
- 다음 한 가지: **middle(Opus5.5)** — 카드 §3 2행. `0x48e83c`로 가는 분기(= `FUN_00471AF0` 0 반환 출구) 하나를 읽는다(문서 1회, 60분).
  A·B 각각 탄 출구를 원시/정적 근거로 특정하고, 그 **주소·비교 필드·뒤집는 fixture 값**을 적으면 E2 work 1회(H7' + 그 fixture). 특정 못 하면
  S1 `BLOCKED`, 사용자 보고(§4 선택지). 새 probe는 E2 밖에서 허용되지 않는다(K2).

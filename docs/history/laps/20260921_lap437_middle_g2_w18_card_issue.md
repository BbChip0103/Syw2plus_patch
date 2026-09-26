# 2026-09-21 | lap 437 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  **middle(중간계획·검수·컨펌)**. 게임 코드 hands-on 수정 없음, 게임 실행 0회, probe 작성 0.

- 가설 / 사용자 관찰: STATUS「다음 한 가지」와 `ESCALATE_SOL` §23 판정③이 지정한 대로
  **W18 카드(하드웨어 write watchpoint EIP 귀속) 발행**이 이번 회차의 유일한 작업이다.
  동시에 PROMPT ④-2에 따라 lap436의 (L2) 재채점을 독립 검수한다.

- 예상 PASS / FAIL 조건:
  - 검수 PASS = lap434 원시 산출물을 **비참조 재계산**해 lap435/lap436 수치와 불일치 0.
  - 카드 PASS = §23이 middle에 맡긴 판정식·산출물·금지 목록을 **실행 전에** 서로소로 고정하고,
    §23 재발 방지 조항(전체창·표적축 두 지표 동시 고정)을 이행.
  - 판정 자체는 문서 산출물이며 실행 검증 대상이 아니다.

- 변경 파일 / source fingerprint / 커밋:
  - 신규 `docs/work/active/G2_UNIT_700_WATCHPOINT_EIP_ATTRIBUTION_LAP437.md` (W18 카드)
  - 추가 `loop/ESCALATE_SOL` (§24)
  - 신규 `docs/history/laps/20260921_lap437_middle_g2_w18_card_issue.md` (본 파일)
  - 갱신 `docs/STATUS.md` / 신규 `docs/history/laps/20260921_status_lap437_precompaction.md`
  - 신규 계측 스크립트(비제품)
    `temp/Syw2plus_patch/g2_capacity/20260921_lap437_middle_w18_recheck/recheck437.py`·`recheck437.out`
  - **제품 코드/바이너리 변경 0. 이번 회차 source 미변경**(N22 ⇒ 통합 `make check` 생략).
  - `LOOP_ALLOW_COMMITS` 미허용 ⇒ **커밋 0**, uncommitted 보존.

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    (`Syw2plus/syw2plus_original.exe`) — safety 결과에 기대지 않고 **직접 `sha256sum` 재해시 불변**.
  - 후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`(marked compat, N=4001).
  - **이번 회차 게임 실행 0회 ⇒ 자체 fixture 없음.** 검수 입력은 lap434 run
    (op7 resource-only / 8 owner / N=4001 / seed42)의 기존 산출물.
  - 기술 전제 실증은 게임과 무관한 throwaway 로컬 프로세스(`/tmp/wptest64`)로만 했다.

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 독립 재계산: `python3 recheck437.py`
    (`temp/Syw2plus_patch/g2_capacity/20260921_lap437_middle_w18_recheck/`, 출력 `recheck437.out`).
    입력 = lap434 `poolwide_diff.jsonl`(76행) / `samples.jsonl`(379표본) /
    `poolwide_spawn_diff.jsonl`(2행). `recompute434.py`·`recheck435.py` **비참조**.
  - 감시 주소 산출: `0x0108C000 + 3565*0x758 = 0x016F0478`.
  - watchpoint 기술 전제: `cat /proc/sys/kernel/yama/ptrace_scope` → `0`;
    `gdb -q -p <pid> -batch -ex "watch *(int*)0x404014" -ex continue` → `hw watchpoint` 삽입·트리거;
    `gdb -ex "set architecture i386"` 지원; `file <게임exe>` → `PE32 … Intel 80386`.
  - 게이트: `checks/safety.sh check` → **`SAFETY_PASS`**;
    targeted `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
    patches/population/test_runtime_bridge_contract.py -q` → **6 passed (52.08s)**;
    `df -h /` → 여유 **300G**.

- 측정값 / 판정:
  - **검수 = ACCEPT, 불일치 0.** 전이 **s343/t10402/slot3565 유일**(idx6/7/8을 건드린
    `(sample,tick,slot)` 그룹이 전체에서 이 하나뿐), `|S_full|=2={3565,3604}`,
    `|S_triplet|=1={3565}`, `B_full` 엄밀 n=48 `{0:14,1:16,2:11,3:7}` 중앙값 **1** /
    as-run n=49 `{0:15,1:16,2:11,3:7}` 중앙값 **1**, `B_triplet` `{0:48}` 중앙값 **0**,
    배경 73행 전량 `+0x6e8`/`+0x70c..+0x71c`이고 **idx5/6/7/8/9 전부 0행**, 3604은 s342에도
    변한 `+0x71c` 상시 카운터, 대조 3562 diff 0행, diff 행의 dense 범위 이탈 0건.
    ⇒ §9-A 분기표 전체창 `(L3)` / 표적축 **`(L2)`** — **§23 판정① 재확인.**
  - **정정 C2(경미):** §23의 `B_triplet` 분포 `{0:49}`는 as-run 기준. C1 적용 엄밀 기준은
    `{0:48}`. 둘 다 0이라 (L2) 무영향.
  - **신규 N49(전제 강화):** 전이 표본 s343(t10402)의 직전 표본이 s342(**t10398**)이므로
    diff 창이 **4 tick**(10399~10402)을 덮는데도 idx6/7/8이 바뀐 슬롯은 3565 하나다
    ⇒ (L2)는 해상도 면에서 **보수적**이다.
  - **신규 N50(범위 주석):** (L2)가 소거한 것은 "**같은 오프셋**을 여러 슬롯에 쓰는 순회 루프"다.
    잘못된 **stride**로 슬롯마다 다른 오프셋에 착지하는 루프는 소거되지 않는다. W18의 EIP가
    그 구분을 직접 끝내므로 별도 카드를 만들지 않는다.
  - **W18 카드 발행 완료.** 감시 주소 `0x016F0B70`/`0x016F0B74`/`0x016F0B78`(전부 4B 정렬,
    DR 3개로 정확히 피복). `0x016F0B78`은 **lap428 N43과 독립 일치**(교차검증).
    판정식 (M1) `.text` 내 귀속⇒**수리 카드** / (M2) `.text` 밖 귀속⇒**보고 후 strategy 판정** /
    (M3) 전이났으나 미발화⇒1회 재시도 후 `BLOCKED` / (M4) 전이 비재현⇒1회 재시도 후 `BLOCKED` /
    (M5) 기술 불가⇒**즉시 `BLOCKED`**. 예산 실행1+재시도1/60분.
  - **기술 전제 실증(게임 미실행) = 카드 발행 전 불확실성 축소.** ptrace_scope 0, gdb 15.1이
    raw 주소에 **hw watchpoint**를 실제로 삽입·트리거함을 확인. §23이 BLOCKED 사유로 열어 둔
    "ptrace/DR 사용 불가"의 대부분을 사전에 걷어냈다.
  - **실증으로 드러난 함정 2건을 카드 §3-C에 사전 등록:** (1) `$pc`는 store **다음** 명령을
    가리킨다(실측 `pc=0x401122`, 실제 store `0x40111c`) ⇒ 보고 EIP는 직전 store 주소.
    (2) gdb 역디스어셈블이 어긋난다(`0x40111a`를 존재하지 않는 `rex.RB clc`로 해석)
    ⇒ 핀된 `candidate.bin`의 `eip-0x400000`에서 **정방향** 디스어셈블로 귀속한다.
  - **도구 선택 판정:** 직접 ptrace `POKEUSER(u_debugreg)` 신규 작성 **반려**(64bit tracer /
    32bit tracee `struct user` 레이아웃 + 스레드별 DR 전파를 떠안음). gdb는 inferior 전 스레드에
    전파하므로 둘 다 대신 처리한다. **소프트웨어 watchpoint는 게임 코드를 `0xCC`로 바꾸므로
    금지**하고 소프트웨어 폴백을 (M5) 즉시 BLOCKED로 고정했다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 제품/마일스톤 승인 아님. 사용자 되물음 2건((가)/(나), (B)/(C))·F4 트랙(§5~§13)은 답변 대기.
  - G1/G4 잠정 중단, G3 포기 고정, 목표 숫자 5000 불변.
  - **남은 기술 위험:** Wine이 WoW64로 32bit PE를 64bit 호스트에서 돌리면 gdb 컨텍스트가
    `$eip`가 아닐 수 있다 ⇒ 카드 Step 0이 `x/2xb 0x400000 == MZ` + `show architecture`를
    **arm 전 게이트**로 두고 어긋나면 즉석 우회 없이 (M5). Wine이 DR을 지우는 경우는 (M3).
  - **연속 게임 미실행 3회(lap435·436·437).** lap436 §23이 W18 1장으로 정한 예외 구간이며,
    카드 §8에 "다음 회차는 반드시 게임을 실행한다, 실행 불가 사유가 곧 (M5)"를 박았다.
  - 이 회차의 결과는 work가 아니라 **다음 회차 실행**으로 검증된다(자기 승인 없음).

- 다음 한 가지: **work(Sonnet5/high)가 W18
  `docs/work/active/G2_UNIT_700_WATCHPOINT_EIP_ATTRIBUTION_LAP437.md`를 실행**한다 —
  동일 fixture(op7/8owner/N=4001/seed42)에서 gdb 하드웨어 write watchpoint 3개를
  `0x016F0B70`/`0x016F0B74`/`0x016F0B78`에 걸고 `old==0 && new!=0` 첫 트리거의 EIP를 귀속한다.
  셸 background 금지·동기 대기, 계측 전용(게임 메모리 write 0건), 예산 실행1+재시도1/60분.

- uncommitted 파일 해시(세션 종료 시점):
  `docs/STATUS.md` `3efa77e79b89d394c1b25fb0b4f0035edc87ef44c0084780c035e493ef23549d`(129줄) /
  `loop/ESCALATE_SOL` `8f72d68f017ead68046aae5d547cda289b11bde8bec316d55085b19c172b885c` /
  `docs/work/active/G2_UNIT_700_WATCHPOINT_EIP_ATTRIBUTION_LAP437.md`
  `18946c151d5b18a19dba0317444d5bddea1f7d1397fa3048688e24564f85f208` /
  `docs/history/laps/20260921_status_lap437_precompaction.md`
  `898c74cc9abfe6cabe96a3533512526ae9ba11443dadd192f659db19d4798423`(127줄, lap436 종료 해시와 일치).
  원본 `Syw2plus/syw2plus_original.exe` 세션 종료 시 직접 재해시 `b56986e0…c9c08a8ac` **불변**.

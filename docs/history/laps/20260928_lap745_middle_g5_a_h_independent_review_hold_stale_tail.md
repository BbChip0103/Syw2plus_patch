# 2026-09-28 | lap 745 | 목표 G5 (middle: 체크리스트 A~H 전체 독립 재검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·컨펌). 게임 코드·EXE·probe 수정 없음.
- 가설 / 사용자 관찰: 2026-09-28 03:36·16:35 판정대로 A~H가 모두 채워졌으니 middle이 한 번에 재검수한다. 통과하면 사용자 milestone 재상정, 아니면 남은 결함을 work에 되돌린다.
- 예상 PASS / FAIL 조건: v7 재빌드 SHA 일치, v6→v7 바이트 차이가 저장/로드 훅 범위로 한정, raw JSON이 각 lap 주장과 일치, 새 부작용 경로 없음 → PASS. 하나라도 새 결함 경로가 있으면 HOLD.
- 변경 파일 / source fingerprint / 커밋: 문서만 — 이 파일, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`(압축 + 판정), `docs/feedback/INBOX.md`(처리 표시), `docs/history/20260928_approvals_lap745_work_g5_checklist_precompaction.md`(신규 보존본), `loop/ESCALATE_SOL`(lap745 섹션 추가). 커밋 없음(uncommitted).
- 원본 SHA / 후보 SHA: 보호 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(참고: 같은 폴더 `[ESL]Syw2plus 2606.exe`는 `716dde6a…`로 보호 원본이 아니다. v1 빌더가 SHA 불일치로 빌드를 거부하는 것까지 확인). v7 = `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`. v6 = `fdc913b5f42dc7cc…`, v5 = `29e61074c622c77d…`(이번 재빌드 기준).

## 실행 명령 (전부 이번 세션에서 독립적으로 실행)

1. `python3 -m patches.selection.g5_selection_cap50_v7 "<[HQ]Syw2plus 2002.exe>" /tmp/lap745_middle/v7.exe` → SHA `30efafa0…`로 **lap740/743 기록과 동일**(빌드 재현성 확인).
2. v5/v6를 메모리에서 재빌드해 바이트 비교: **v6→v7 = 17구간**(PE `.rsrc` 헤더 `0x270..0x28f` = VirtualSize `0x20f0→0x2200`, Characteristics `0x40000040→0x60000060`; 콜사이트 `0x440f0d`/`0x4412dd` 각 3B; 캐이브 `0x108f100..0x108f1c9`). **v5→v6 = 10구간**(`0x409cb8` 콜사이트 + `0x4e4f90..0x4e4ff9` 캐이브). lap733/740의 범위 주장과 일치한다.
3. `pytest -q patches/selection tests/test_g5_selection_inventory.py tests/test_g5_stock_selection_array_xrefs.py tests/test_g5_command_packer_xrefs.py` → **53 passed(13.62s)**. `checks/safety.sh check` → `SAFETY_PASS`. `checks/context_limits.py check` → `CONTEXT_PASS`(APPROVALS 압축 전후 모두).
4. raw 재계산: `temp/Syw2plus_patch/20260928_lap743_g5_h_longrun/candidate/probe-result.json`, `20260928_lap740_g5_f_saveload/{candidate,original,crossload_*}/probe-result.json`, `saves/*.dat` SHA.
5. capstone으로 v7 저장/로드 래퍼와 선택 추가/제거 루틴(`0x412d90`) 역어셈블, v7 전체에서 새 선택 배열(`0x108c000..0x108c0cc`)을 즉값으로 참조하는 명령 52곳 열거.

## 항목별 판정 (v7 기준)

| 항목 | 판정 | 근거 / 이번 재검수 메모 |
|---|---|---|
| A 정적 전수 | PASS(보완 필요) | 기존 inventory 결론 유지. 단 이번 열거로 **count 쓰기는 `0x412e6e` inc·`0x412ed2` dec 두 곳 + v7 래퍼 두 곳뿐**이고, 추가 루틴은 50칸에서 첫 빈칸에 쓰며, 제거 루틴은 핸들이 일치할 때만 칸을 0으로 만들고 count를 줄인다. 즉 "count = 0이 아닌 칸 수"라는 불변식에 기대는 구조다. 기존 표는 이 불변식이 저장/로드에서도 지켜지는지 판정하지 않았다(아래 F). |
| B 선택 변화 | PASS | v5/v6 runtime(lap725~728·734). v6→v7 차이는 저장/로드 훅뿐이라 영향 없음. |
| C 명령 | PASS(알려진 UNKNOWN/N/A) | 미니맵 우클릭·능력 v는 원본도 반응 없어 UNKNOWN, 건설·승선 N/A(lap736). |
| D 부대 | PASS | v6 사망 후 호출 31/31(lap733), 회귀(lap734). |
| E UI | PASS(조건부) | 체력바 46/50은 밀집 가림 때문이라는 설명이 PLAUSIBLE(부분선택 대조 13/13). CONFIRMED는 아니다. |
| F 저장/로드 | **HOLD** | 앞 20기 미러와 양방향 호환은 raw로 확인: 원본·v7 세이브 모두 2501702B, v7이 원본 세이브를 로드하면 legacy·new_base 모두 20/동일 slots, 원본이 v7 세이브를 로드하면 legacy 20. **그러나 새 결함 경로 H-STALE-TAIL이 검증되지 않았다(아래).** |
| G 멀티 | BLOCKED(env) 수용 | 체크리스트의 "불가 시 사유 명시" 조건을 충족한다. 누적 4조합, 원인은 Wine builtin dplayx의 SP 로드. 명령 청크 최대 3회·레코드 불변은 정적 근거라 PLAUSIBLE. |
| H 장시간 | PASS(안정성) | 387샘플 전부 50/50·unique 50, 회귀 0, crash false, 8019 tick, 최종 선택 = 초기 선택, `source_unchanged`. **정정:** `moving_count`는 `command != 0`인 유닛 수라서 stop/hold 뒤에도 50이 나온다. 따라서 "매 명령이 50기에 전달됐다"는 lap743 문구는 이 지표로 뒷받침되지 않는다. 명령 전달은 C/lap734 근거로만 인정한다. |

## 새 결함 경로 H-STALE-TAIL (v7 LOAD 래퍼, 정적 확인·런타임 미검증)

`LOAD_WRAPPER`(`0x108f180`)는 원래 로드 후 legacy count를 min(count,20)으로 잘라 `0x108c000`에 쓴다. 그리고 legacy 20칸을 `0x108c004`로 복사한 뒤 **(20-count)칸만** 0으로 채운다(`0x108f1bc: mov ecx,0x14`). **entries[20:50] 30칸은 로드 직전 값이 그대로 남는다.** 반면 원본은 선택 count와 20칸 전체가 저장 창(`0x892410+0xe397c`) 안에 있어 로드가 전부 덮어쓴다.

- 발생 조건: 로드 순간 라이브 선택에 21번째 이후 칸이 하나라도 있으면 된다. 예: 50기를 선택한 채 게임 안에서 불러오기, 또는 사망으로 희소해진 선택.
- 예상 결과(정적 추론, 미실측):
  - ① count(≤20)와 실제로 0이 아닌 칸 수가 어긋난다.
  - ② v5 청크 게이트(`entries[20:50]` 중 0 아닌 칸이 있으면 청크)가 남은 칸으로 명령을 보낸다. 로드된 판에서 선택되지 않은 유닛, 혹은 다른 유닛이 차지한 slot에 명령이 갈 수 있다.
  - ③ 전체 해제는 칸마다 제거를 호출하는 방식이다. 핸들이 같은 유닛(같은 판의 세이브)이면 제거 때마다 count가 줄어 **음수**가 된다. 핸들이 다르면 그 칸이 영구히 남는다.
  - ④ count가 음수인 채 저장하면 `SAVE_WRAPPER`의 `cmp ecx,0x14; jle`(signed)가 음수를 통과시켜 `rep movsd`가 약 4G dword를 복사한다 → **크래시 가능**.
- probe 사각지대: `tools/g5_candidate_drag_probe.py:192 selection_snapshot`은 `range(count)`칸만 읽는다. 따라서 남은 꼬리 칸은 지금까지 어떤 probe에도 보이지 않았다. lap740 roundtrip도 로드 전에 빈 지면 클릭으로 해제해 이 경로를 밟지 않았다.
- 관련 미검증 경로:
  - (i) 저장 당시 선택된 21~50번째 유닛은 unit byte `+0`(추가 루틴이 `mov byte [ebp],1`로 쓰는 선택 플래그로 추정)이 세이브에 1로 남는다. 로드 후 배열에는 없으므로 표시와 실제 선택이 어긋날 수 있다.
  - (ii) 50기를 선택한 채 메인 메뉴로 나갔다가 새 게임을 시작해도 새 배열(`.data` 확장 BSS, 저장 창 밖)이 초기화되는지 확인되지 않았다. v1부터 있었을 수 있는 경로다.

## 결론

**G5 체크리스트 A~H 전체 = HOLD(조건부).** B·C·D·H PASS, G BLOCKED(env) 수용, E 조건부. F는 새 결함 경로 H-STALE-TAIL이 검증될 때까지 보류한다. 그래서 사용자 milestone 재상정과 G1 착수는 하지 않는다. 사용자 3단 판단은 이 검수와 별개로 계속 대기 상태다.

## lap724가 남긴 middle 문항 답변

- ① lap724 raw 3건과 v4 패턴 대조: v6 재측정(lap734)과 v7 바이트 범위로 대체됐으므로 따로 재계산할 필요 없음.
- ② coverage probe 목적지 오프셋 확장: 측정 쪽만 바꾼 것이고 제품 바이트와 무관해 안전함.
- ③ Xvfb 고아 프로세스: 이후 모든 run에서 `cleanup.prefix_processes_after=[]`, `global_kill_used=false`였으므로 안전 위험으로 보지 않음. 자기 run만 정리하는 규칙은 유지.

## 다음 한 가지 (work tier handoff, 구현 우선)

기존 `tools/g5_candidate_drag_probe.py` roundtrip 경로를 재사용하되 두 가지를 바꾼다. 선택 스냅샷은 **count와 무관하게 50칸 전부**를 raw로 읽는다. 명령 수신은 유닛별로 명령 opcode/목적지가 이전과 달라졌는지로 센다(0이 아님 여부로 세지 않는다). 원본 1회·v7 1회를 paired로 실행한다.

1. **S1 로드 시 꼬리 칸**: 50 드래그 → 저장 → 해제하지 않고 50 선택 유지 → 로드. 기록할 것: count, 50칸, fixture 55기의 byte`+0`. 이어서 우클릭 이동 → 명령이 바뀐 유닛 수와 slot을 로드된 선택과 대조 → 빈 지면 클릭 → count와 50칸 → 다시 50 드래그 → 저장, 크래시 여부.
2. **S2 저장 시 21~50 플래그**: lap740과 같은 순서로 로드한 뒤 21~50번째 유닛의 byte`+0`, 체력바 표시, 해당 유닛 단독 클릭·드래그 선택 가능 여부.
3. **S3 새 게임 이월**: 50 선택 → 메인 메뉴로 나가기 → 새 게임 → count·50칸.

PASS 조건: 모든 시점에서 count = 0이 아닌 칸 수, 로드된 선택 밖 유닛에 명령 0건, 해제 후 count 0이고 50칸 모두 0, 크래시 0, 원본 대비 동작 차이 없음(원본은 ≤20).

FAIL이면 가장 작은 v8로 고친다. S1은 `LOAD_WRAPPER`의 0 채우기를 50칸까지로 바꾼다(`0x108f1bc` `mov ecx,0x14`→`0x32`). S3는 새 게임 초기화 지점 하나를 귀속한 뒤 같은 방식으로 0을 채운다. S2 플래그 불일치가 실제로 보이면 수정 설계는 middle로 되돌린다. 그 뒤 `make check`와 v7에서 v8로의 바이트 범위를 pytest로 고정하고, F 재측정 1회와 핵심 회귀 1회를 한다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 바이트 변경 0, 게임 실행 0회. 사용자 G5 milestone 재확인은 여전히 미요청. 멀티는 BLOCKED(env).

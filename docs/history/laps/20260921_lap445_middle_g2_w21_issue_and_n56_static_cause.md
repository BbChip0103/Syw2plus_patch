# 2026-09-21 | lap 445 | 목표 G2 (활성 8인 각각 전비 5000 안정성)

- **실제 provider/model/effort / 지정 역할:**
  Claude Code `claude-opus-5` / high, 지정 역할 **middle(중간계획·컨펌)**.
  게임 코드 hands-on 수정 없음. 카드 발행 + 이전 바퀴 독립 검수 + 정적 진단만 수행.

- **가설 / 사용자 관찰:**
  1. (검수) lap444 strategy가 판정 전에 했다는 "lap442 원시 721표본 직접 재계산, lap443과 불일치 0"이
     참인가. 2. (진단) N56 — lap442에서 owner0이 전 구간 `(used,count)=(20,2)` 고정이었던 원인.
  3. (진단) N57 — RSS 248MB→50MB 하강의 성격. 4. (계획) lap444 카드 §3 경계대로 W21 발행.

- **예상 PASS / FAIL 조건:**
  검수는 **비참조 재계산**(입력 = lap442 `samples.jsonl` 721표본 하나뿐, lap443 `recheck443.py`와
  lap444 산출물은 읽지 않음)으로 lap443/444 주장값과 전항목 일치하면 ACCEPT, 1건이라도 다르면
  MISMATCH로 기재. 진단은 소스/산출물로 귀속되면 확정, 아니면 UNKNOWN으로 남긴다.

- **변경 파일 / source fingerprint / 커밋(없으면 uncommitted):**
  제품 코드 변경 **0**. 이번 회차 **source 미변경**(N22 ⇒ 통합 `make check` 생략 근거).
  신규(문서/검수 스크립트, 전부 uncommitted):
  - `docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md` (W21 카드)
  - `docs/history/laps/20260921_lap445_middle_g2_w21_issue_and_n56_static_cause.md` (이 파일)
  - `temp/Syw2plus_patch/g2_capacity/20260921_lap445_middle_review/recheck445.py`
    + `recheck445_output.json` + `rss_profile445.txt`
  커밋 **0**(`LOOP_ALLOW_COMMITS=0`, 저장소는 여전히 unborn HEAD).

- **원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:**
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (safety 결과에 기대지 않고 **직접 재해시**, 불변).
  검수 대상 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`.
  **이번 회차 게임 실행 0** — 분석 대상은 lap442 run의 원시 표본이다(op7 resource-only /
  8 owner / N=4001 / seed42 / display `:3910`).

- **실행 명령 / 로그 / 캡처 경로 및 해시:**
  - `python3 recheck445.py` → `recheck445_output.json`
    (입력: `20260921_lap442_repaired_p2_long_soak/samples.jsonl` 단독)
  - RSS 국면 분석 → `rss_profile445.txt`
  - targeted `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
    patches/population/test_runtime_bridge_contract.py -q` → **6 passed** (48.76s, 기준선 일치)
  - `checks/safety.sh check` → `SAFETY_PASS`
  - `sha256sum` 원본 직접 재해시 → 위 값 일치

- **측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):**

  **(1) lap444 검수 = ACCEPT.** 비참조 재계산이 §27/§28·카드 §4의 핵심 수치와 전항목 일치했다.
  - samples **721**, tick **16 → 24,030**, 단조 비감소·역행 **0**
  - owner0~7 max `used` = **[20,570,1183,1111,620,1333,1698,1466]**, overall **1698**
  - `used>5000` **0건**, `≥4900` **0건**, `≥2500` **0건** ⇒ **(T2)** 재확인
  - owner0 distinct `(used,count)` = **`[(20,2)]` 단 하나** ⇒ 전 구간 고정 확인
  - `live == Σ owner.count` **721표본 전부 일치**, max live **583**
  - 사분위 tick `[6018,12022,18026,24030]`, sum(used) `[2963,6456,7076,8001]`,
    증분 **+3,493 → +620 → +925**(감속) ⇒ lap443의 "현 fixture로 5000 도달 불가" 근거 재확인
  - `max_slot_index` distinct = **{4000}** (전 표본 상수, sample0의 live는 16) ⇒ **N55 재확인**

  **(2) 정정 1건 (수치 정밀도, 판정 불변) — §27의 RSS 서술.**
  §27은 "248,636KB → tick14,690에 −95MB 단발강하 → 종료 50,120KB"라고 적었다. 재계산 결과
  **248,636KB는 첫 표본이 아니라 최댓값**이다(sample438/tick14,623). 첫 표본은 **236,416KB**이고
  하강 직전 표본은 241,588KB다. 그리고 **"단발"이 아니다** — 하강은 최소 두 국면이다:
  - 국면① sample439~446 / tick14,657~14,890: `−7,048 / −95,460 / −12,576 / −10,716` KB (≈−126MB)
  - 국면② sample688~711 / tick22,963~23,730: `−10,076 / −9,004 / −6,436 / −6,252` KB
  - 종료 **50,120KB(live 583)** < 시작 **236,416KB(live 16)**. 하강 후 구간은 단조가 아니다
    (plateau 114~118MB 후 2차 하강). 증가는 전부 소폭(최대 +880KB).
  ⇒ (T2) 판정은 바뀌지 않으나 **N57은 "단발 강하"가 아니라 "두 국면 하강 + 역상관"** 으로 다시
  써야 한다. W21 §5-4에 반영했다.

  **(3) N56 = 정적으로 귀속 확정(게임 실행 없이).**
  `tools/inmm_stub/control_executor.c:910-916`이 goal `_custom_game_chain_inject_g2_eight_seed42`의
  로비 레코드 8개(`G2_LOBBY_VA=0x00632CC0`, stride 6)를 채우면서
  **`record[2] = (BYTE)(owner == 0 ? 0 : 1);`** 로 **owner0만 0, owner1~7은 1**을 쓴다.
  lap442에서 owner0만 전 구간 무활동이었던 관측과 정확히 일치한다.
  ⇒ **"추정"이던 N56이 소스 한 줄로 좁혀졌다.** 다만 `record[2]`의 의미(1 = 컴퓨터/AI)는 주석이
  없어 **UNKNOWN**이며, W21 Step0이 런타임 대조 1회로 실증한다. 실질 활성이 7명이라는 §27의
  결론은 유지된다.

  **(4) W21 실행 가능성 사전 확인 — work의 한 바퀴를 아끼는 정적 검증 4건.**
  - **op5/op6 시딩은 gate-legal**: `runtime_bridge.c:175-229`가 원본 배치 `0x42ECB0` → 원본 생산
    gate **`0x43EDA0`** → 원본 spawn `0x443190` 순으로 호출하고, 개체마다 `count+1`/`used+cost`를
    검증하며, `old_used+[p+0x1c]+cost > [p+0x2012]`로 원본 cap을 존중한다
    ⇒ **lap444 경계2 충족**. op4는 장부 직접 write라 금지 대상으로 카드에 명시.
  - **1200 천장 없음**: `build_runtime_bridge.py:45-54`가 `--unit-pool-capacity`로
    `0x66b790u`/`0x8990c8u`/`1200`을 재배치 주소·N으로 치환한다. `runtime_bridge.c`의 `1200`
    리터럴 **5곳(L94,139,212,233 및 관련)이 전부 풀 슬롯 경계**임을 확인 ⇒ 문자열 치환이 의미상
    안전하고 N=4001이면 gate 수용 범위도 `<4001`이 된다.
  - **산술 성립**: op5(type5, cost **35**) 138기 + op6(type7, cost **10**) 5기 + 시작 2기(20)
    = owner당 `used 4,900`/145기 → 8 owner **1,160기 ≪ 4,001**. 요청당 `wanted≤200`이라 owner당
    2요청.
  - **혼합 구성의 실제 한계(숨기지 않음)**: 브리지 fixture에 **건물 계층이 없다**. lap444 경계3의
    "저전비 다수/고전비/건물 혼합" 중 건물은 이번 카드로 충족 불가이며 (가) 경로의 몫이다.
  - **함정 2건 신규 등록**: ①`fixture_failed`가 **static**(L17)이라 회계 불일치 1회로 그 프로세스의
    후속 op5/op6이 영구 잠긴다(`fixture_attempts`는 지역변수라 요청마다 리셋되므로 예산 문제는
    없다) ⇒ 본 시딩 전 `wanted=1` 스모크 의무. ②`build_runtime_bridge.py`의 주소 치환은
    `runtime_bridge.c` **에만** 적용되고 `tools/inmm_stub/`의 4개 `.c`는 여전히 stock
    `0x008990C8`/1200을 하드코딩한다(lap410 정정2 재확인) ⇒ 그 채널의 유닛 수를 판정 근거 금지.
  - **N57의 값싼 배제 1건**: `w20_step2_run.py:176-184,262,332`의 `read_rss_kb(pid)`는
    **메모리 read가 전부 성공한 바로 그 게임 PID**의 `/proc/<pid>/status` `VmRSS`를 읽는다
    ⇒ lap415/416식 **PID 혼동으로 N57을 닫을 수 없다**. 남은 갈래는 호스트 페이지 회수 /
    게임 측 해제 / 미해명이며 W21 §4-4가 `VmSize`+`VmSwap`+`MemAvailable`로 가른다.

  **(5) 이번 회차 검사**: targeted **6 passed**, `SAFETY_PASS`, 원본 직접 재해시 불변,
  제품 source 변경 **0**, 게임 실행 **0**, 커밋 **0**.

- **회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:**
  회귀 0(제품 코드 미변경). **G2 제품 완료 아님** — 전비5000 도달·144k·저장/LAN·메모리 전부 미검증.
  lap444 판정은 이번 회차가 독립 검수해 ACCEPT했고, **W21 카드 자체는 아직 미검수**이며 실행 후
  다음 middle이 검수한다. 사용자 마일스톤 승인 없음.
  **절차 관찰:** lap444는 자체 lap 기록을 남겼다(lap440·442의 누락이 재발하지 않음).
  남은 위험 — W21 Step0이 source를 바꾸면 통합 `make check` 1회가 필요하고, Step1의 건물 계층
  부재는 이 경로로는 해소되지 않는다.

- **다음 한 가지:**
  **work 회차**가 `docs/work/active/G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md`(W21)를 Step0 → Step1 →
  Step2 → Step3 순으로 실행한다. Step0 (U0) 실패 시 이후 Step에서 "8인"을 주장하지 않고 "7인 +
  미활성 1"로 기재하며 진행한다. 장기 실행은 동기 또는 root 소유 세션, work는 자체 lap 기록 필수.

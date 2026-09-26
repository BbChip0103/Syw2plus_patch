# 2026-09-21 | lap 417 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / work (hands-on, 실무).
- 가설 / 사용자 관찰: W10 카드(`docs/work/active/G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`) P-B —
  H1(1200-bound 순회 중 하나가 슬롯≥1200의 이동 상태 초기화/리셋을 건너뛰어 `+0x692`가 망가진다)이
  lap416 P-A로 지지된 뒤, `.text`의 잔존 0x4B0(1200) 즉치를 전수 분류해 "단 하나의 원인" site를 좁힌다.
- 예상 PASS / FAIL 조건: 이 lap은 정적 분류(P-B)만 수행한다 — "PASS/FAIL"이 아니라 풀-경계 관련 site의
  분류 완결과, 가능하면 단일 후보로의 축소가 목표. 단일 원인이 확정되지 않으면 P-C(수리)는 착수하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 저장소 source 변경 **0**(정적 읽기 전용 분석).
  `docs/STATUS.md` 갱신(다음 한 가지/검증 상태/바퀴 기록), 이 lap 기록 신규 생성. uncommitted(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`Syw2plus/syw2plus_original.exe`,
  재해시로 직접 확인), 후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`
  (`patches.population.g2_full_capacity_persistence_compat_v1.build_candidate(original, 4001)`로
  in-process 재빌드해 SHA 일치 확인, 게임 미실행). 게임 실행은 이 lap에서 하지 않았다 — 실행 증거는
  lap416의 `temp/Syw2plus_patch/g2_capacity/20260921_lap416_fault_root_cause_pa_run2/`(709 표본,
  op7 resource-only, 7 AI, N=4001)를 재분석만 했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 분석 스크립트/산출물
  `temp/Syw2plus_patch/g2_capacity/20260921_lap417_pb_site_inventory/`(`scan_4b0_sites.py`,
  `sites_4b0_raw.json`, `classification.json`, `onset_reanalysis.md`). 검사:
  `python3 -m pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → `6 passed`; `bash checks/safety.sh check` →
  `SAFETY_PASS`; `git status --short`로 저장소 source 미변경 확인.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **site 카운트 정정:** decoded-instruction-operand 기준(project evidence_policy와 동일 기준, raw
     byte-pattern 미사용) `.text`의 0x4B0 즉치는 **36곳**이다. lap414 N27의 "54곳"은 byte-pattern 스캔의
     오탐을 포함한 수치였다(N27 스스로 `0x0104b010`류 오탐을 언급했음). PASS(정정 완료, evidence_policy 준수).
  2. **전수 분류(36곳):** 2곳 `0x00441441`/`0x0044317d` 이미 0xFA1 패치(유지); 1곳 `0x0043ee37`는
     `roster_add`의 owner 유닛 개수 상한(lap397 확정, 풀 크기 아님 — 변경 금지); 26곳은 UI 다이얼로그
     빌더 `FUN_0049baa0`(12곳) 또는 서피스 빌더 `FUN_004a8100`(14곳)에 대한 push-인자 상수(주소 무관,
     그중 `0x004a8842`/`0x004a8847`는 직접 디스어셈블로 "1200×1200 서피스" 확인, lap414 오탐 노트와 일치);
     1곳 `0x004a3222`는 `this`-상대 오프셋(0x66990c류 아님, esi+오프셋) 위의 1200-word 버퍼 클리어로
     맵/월드 오브젝트 소속(절대주소 아님, 풀과 무관); 1곳 `0x004c470f`는 100단위 상수표(현재값의
     12번째 항목)로 풀과 무관. 남는 **풀-경계 관련 미패치 site 3그룹**(N27과 매칭):
     - `0x004183a8`/`0x004183be`/`0x00418425`(`FUN_004183a0`, 회전 커서 검색: 영속 커서
       `word[0xb93980]`을 idiv 1200으로 감싸며 owner/비트마스크 필터로 매칭되는 유닛의 `+0x29c`(full ID)를
       반환). 직접 호출자 3곳을 정적으로 특정: `0x0043ff8d`(매치 설정 시 owner별 1회, PlayerStruct
       `+0x2012` 전비상한 기록 + 카메라 중심 이동과 같은 루프), `0x0049ba0e`/`0x004a863f`(UI 범위,
       `0x49xxxx`/`0x4axxxx`). op7/7AI 무입력 fixture에서는 매치 설정 이후 재호출 근거 없음.
     - `0x00444f8a`(`FUN_00444ef0`, 선형 커서 위치 조회: 슬롯 0~1199 선형 스캔, owner/카테고리 필터
       매칭 시 `[0x974210]`/`[0x974212]`에 기록). 직접 호출자 8곳 전부 `0x004be000~0x004c2000`
       범위(UI/입력 처리 모듈과 동일 범위, `FUN_00444ef0` 자체가 "커서 아래 유닛 찾기"류 UI 헬퍼로 읽힘).
       op7/무입력 fixture에서 도달 근거 없음.
     - `0x00422dc7`(`FUN_00422dc0`, 재배치된 풀 기준 슬롯 0~1199만 순회하며 슬롯당
       `FUN_0048aff0`(`this`=unit) → `FUN_004119f0`(`this`=unit) 호출; 같은 호출 대상 `FUN_004119f0`가
       인접 case-블록에서 싱글톤 매니저 객체 `0x61e36c`/`0x66990c`에도 동일 패턴으로 호출됨 — "시스템별
       매 틱 update" 형태에 부합). **호출 경로 미해결:** `.text` 전체에서 `call 0x00422dc0`도, 파일
       raw bytes 안의 절대주소 `0x00422dc0` 참조도 **0건**(간접 호출/런타임 테이블 가능성, 이 스캔의
       범위 밖). 이 site만 유일하게 정적으로 배제되지 않았다. **UNKNOWN(호출 빈도·도달 여부 미확정).**
  3. **onset 재분석(신규 게임 실행 없이 lap416 `samples.jsonl` 709줄 재집계):** `bands.hi.max_abs`가
     tick15~11,904까지 전 표본 **정확히 0**이다가 11,921(6599)→11,928(19579)로 급변한다. 슬롯 3565의
     동시 표본 다른 필드(`f674/f676/f2a2/f2a4/f2b8/f2ba/f2bc/f2be`)는 여전히 정상 범위(10~13)다. 이는
     매치 내내 서서히 축적되는 drift가 아니라 **tick~11,900대 돌발 이벤트**임을 뜻하며, "lifecycle
     누락으로 소량 증분이 무기한 누적" 가설보다 "wild write" 또는 "카운터/커서 임계 최초 통과"에 더
     부합한다. PASS(재분석 완료, INBOX의 lap416 수치와도 독립적으로 일치 확인).
  4. 종합 판정: **H1/H2 미확정.** "단 하나의 원인" 요건을 충족하지 못해 P-C(수리)는 착수하지 않았다
     (카드 §3 P-C의 "추측 수리 금지" 조건).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품코드/게임 바이너리 변경 0, 게임 실행 0, 커밋 0.
  원본 2경로 SHA 재확인 불변, `SAFETY_PASS`, 표적 테스트 6 passed(기준선과 동일), 잔류 프로세스 없음
  (게임을 실행하지 않았으므로 해당 없음). **신규 provenance 결함 N29:** lap415(2026-09-21 00:51 KST, PID
  오추정으로 샘플링 미진입 FAIL)와 lap416(01:10 KST, run2 H1 지지)가 `docs/feedback/INBOX.md`에만
  기록되고 `docs/history/laps/`·이전 STATUS 갱신이 없다(lap408의 N20과 같은 계열의 미기록 회차). 이
  lap이 lap416의 원시 `samples.jsonl`을 독립 재확인해 INBOX 서술과 **일치**함을 확인했으므로 수치
  자체는 신뢰 가능하지만, 그 회차들의 의도/판단 근거는 소급 기록하지 않는다(날조 금지). 이 결함은
  러너 수준 게이트 여부가 미결(N14와 같은 부류)이며 여기서는 사실만 기록한다. 독립(다음 middle) 검수
  대기. 사용자 마일스톤 승인 해당 없음(중간 진행 회차).
- 다음 한 가지: `0x00422dc0`의 실제 호출 경로/빈도를 **동적으로** 확인한다(정적 스캔으로는 0건이라
  미해결). 도달이 확인되면 그 site의 `0x4B0`을 이미 패치된 두 자매 site와 같은 방식으로 0xFA1로
  최소 수리하고 동일 op7/7AI fixture로 재실행해 tick11,928 통과 + page fault 0건을 PASS 조건으로 삼는다
  (`docs/STATUS.md`의 "다음 한 가지" 참조). 도달하지 않으면 이 경로를 기각하고 남은 가설(포인터/수명주기
  stale, H2)로 넘어간다. 회전 커서(`0x004183a0`)와 선형 커서 조회(`0x00444ef0`)는 이 fixture에서
  배제됨을 다음 회차에 재활용한다(재조사 불필요, 근거는 이 기록의 §측정값 2).

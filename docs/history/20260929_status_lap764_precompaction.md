# STATUS — 매 바퀴 갱신하는 기억

lap676~741 상세(과거 압축 포인터, G5 milestone 승인 이력, G2 8인×10000 A/B 종료, G4 W2 post-load
종결, G5 A~F 체크리스트 완료 근거 전문)는 이 헤더 블록 152줄 SHA256
`11688804945df9fbd3f10e8df6f19d08b0f1ab4872dfca59d2f66fc33807b453`으로
`docs/history/20260928_status_lap717_741_precompaction_v2.md`에 원문 그대로 보존했다(과거
lap676~716분은 그 파일이 가리키는 `docs/history/20260927_status_lap717_precompaction.md`에
한 단계 더 있다). **lap745~751 상세 서사(H-STALE-TAIL 재현·v8 수정, S3 좌표확정·INCONCLUSIVE,
홀드버튼 편차·해소, S4/S5 추가, middle HOLD 판정 2회)는 이 파일 145줄 SHA256
`4f7182884ea7b6aae9b9e2705a7a5a1831b48e3a02d8bae964b949c50ca94e89`으로
`docs/history/20260928_status_lap751_precompaction.md`에 원문 그대로 보존했다.** 각 lap 전체
근거는 `docs/history/laps/20260926_lap67{6..9}_*.md`·`lap68{0..9}_*.md`·
`20260927_lap69{5..9}_*.md`·`lap70{0..9}_*.md`·`lap71{0..6}_*.md`·`20260928_lap7{17..51}_*.md`에
그대로 있다.

## 지금 상태

**G5는 2026-09-26 21:54 단일플레이 milestone 승인 후 2026-09-28 01:31 지시로 조건부 되돌아갔다** —
A~H 체크리스트 전부 PASS해야 종료. **lap754 middle(Opus5)이 lap753 v9 증거를 독립 재검수해 (F) PASS로
판정했다**: 원본에서 v9 재빌드 SHA `18181cdef6c7…` 일치, v8→v9 diff = hook+cave+헤더뿐, `0x4a3060`
호출자 3곳 전수(모두 `this=0x892410`, 절대참조 0)·hook 무조건 경로 확인, lap753 raw(원본 CLEARED/v8
PERSISTED/v9 CLEARED, v9 S1/S2/S4 원본 패리티) 재계산 일치, `make check` 1122 passed·5 skipped. (A) 표에
this-상대 초기화 §2b 추가. **A~H 2단 판정(v9): A·B·C·D·F·H PASS, E 조건부 PASS, G `BLOCKED(env)` 수용 →
사용자 3단 milestone 재상정 대기.** middle은 G5 종료·G1 착수를 선언하지 않는다.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료, 착수 대기(G5 사용자 판단 이후) | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성(복귀). 8인×10000 트랙 종료(근거 보존) | 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류(길찾기 종료, 생산게이트 계측 완료) | candidate AI 정책 없음, 사용자 승인 |
| G5 | v10, lap756(50기)+lap757(25/35/부대혼합) 항목(1) 전부 PASS | middle 재검수, 항목(2), 사용자 3단 판단 |

## 지금 막힌 것 (Blockers)

**G5 v10 사용자 항목(1)(2) 처리 중, 3단 milestone 미제출.** lap756이 항목(1)(부대 미지정 50기
선택 save/load 전부 복원+양방향 호환)을 v10으로 구현·런타임 3-way PASS(자체 복원/원본→v10/v10→원본)
했고, **lap757이 중간값(25/35)·부대(Ctrl+1) 혼합 저장/로드도 전부 PASS**했으나 **middle 독립 재검수
아직 없음**. 항목(2) 중 수확(V) paired는 **lap760 PASS**(원본20/v10 50 전원), 미니맵은 native
ddraw.dll override가 원인이 아님을 lap760이 반증해 **UNKNOWN 유지**(입력 핸들러 조사 미착수). 알려진
제한 ①~⑨(G 멀티 BLOCKED(env), 미니맵 우클릭/능력 v UNKNOWN, 건설·승선 N/A, E 체력바 46/50 가림
PLAUSIBLE, S3 초기메뉴 UI env 미실측, S5 정적 귀속, `FUN_004AE550` 간접호출 정적 미증명·R2, 부대
H1~H3 edge)는 lap754 상세 참고(①부대 미지정 20기 제한은 v10으로 해소, 아래 표 참고).
승인 전 G5 제품 작업 없음, G1 재개 금지(01:31 지시).

world (93,56)의 `long_distance_pan` 카메라-복귀 결함은 여전히 후순위 미해결(lap711). world
(10,49)를 baseline으로 계속 쓴다.

## 검증 상태

**[압축 포인터] lap717~750 검증 상태 계보**(매 lap `make check` PASS·`SAFETY_PASS`·크래시0·
`source_unchanged`, lap746 H-STALE-TAIL 재현·v8 수정, lap747~750 회귀/홀드버튼/S4·S5/middle HOLD 상세
수치)는 위 헤더 압축 파일(`docs/history/20260928_status_lap751_precompaction.md`)에 원문 보존.
**[압축 포인터] lap751~760 검증 상태 계보**(원문 40줄, SHA256
`92372da17c42f857a444b6369443337e53c64f7e41fbce5b243da35915e53236`) — 전문
`docs/history/20260929_status_lap751_760_verification_precompaction.md`. v9 falsification 확정
(lap753)·middle F PASS(lap754), v10 항목(1) 50기 save/load 3-way PASS(lap756)·중간값/부대혼합
보완(lap757), 수확(V) paired PASS+ddraw override 반증(lap760)이며, 매 lap `make check` PASS·
`SAFETY_PASS`·크래시0·`source_unchanged`.
**lap762(work)**: 미니맵 클릭 라우팅 체인 특정(enqueue→라우터→`FUN_004516A0`→폴백), LUT 50% 베이킹
확인(렌더-죽음 가설 부분 반증), gdb 5-breakpoint로 히트테스트 0회 호출 확정 → 필터체인 3곳으로
좁힘. `UNKNOWN` 확정(지시 조항 충족, 근거는 이전보다 구체적). 제품 코드 0 변경, 크래시0,
`source_unchanged` 2/2. `ruff`/`compileall` PASS, `SAFETY_PASS`/`CONTEXT_PASS`(제품 코드 무변경,
전체 `make check` 생략).
**lap763(work)**: 3-필터 브레이크포인트로 `0x41e332`/`0x41e365`가 무해한 커서-아이콘 분기임을
확정하고 유일한 실제 게이트 `call 0x41c450`이 관측 9430회 전부 `eax=0x0` 반환함을 실측. 게이트가
로비 "게임 타입"(`0x975914==3`) 조건에 걸려 있음을 정적 추적 후, **`0x97597c`를 격리 사본에서
진단 write로 1로 강제하자 `FUN_004516A0` 호출이 0→6232회(성공4195/실패2037)로 급증** — 미니맵
서브시스템이 죽은 게 아니라 이 게이트 플래그가 잠가놓았을 뿐임을 실증. fixture 명령효과
(`pending_xy`)까지는 미측정. 제품 코드 0 변경(진단 도구 2개 수정), 크래시0, `source_unchanged`
2/2. `ruff`/`compileall` PASS, `SAFETY_PASS`/`CONTEXT_PASS`(제품 코드 무변경, 전체 `make check`
생략).

## 다음 한 가지
**2026-09-29 12:57 운영자 판정(lap762, 미니맵 1 lap 연장 — 원인 위치가 3지점으로 좁혀짐):** 미니맵 입력은 WM 핸들러 enqueue(24회)·라우터 dequeue까지 도달, 히트테스트 `FUN_004516A0`는 0회. 다음 work 1 lap: 필터 3지점(`0x41e332` 버튼타입, `0x41e365` 좌표 sentinel, `0x41e43d call 0x41c450` 게이트)에 브레이크포인트로 어느 분기에서 떨어지는지 확정. 격리 환경 탓(예: 게이트가 창 포커스/미니맵 표시 플래그를 요구)이면 그 플래그를 브리지로 켜서 원본 미니맵 우클릭 이동을 성립시킨 뒤 원본20/v10 50 paired. 이번 lap에서도 성립 못 하면 **UNKNOWN 확정·원인 지점 기록**하고 middle 재검수로 넘어간다(추가 연장 없음).
**2026-09-29 12:37 운영자 지시(lap761 후속, 미니맵 마지막 1 lap):** 수확(V) paired PASS(원본20/20, v10 50/50) 수용. ddraw 네이티브 override는 미니맵 원인 아님(반증). 다음 work 1 lap 한정: 미니맵 클릭 입력 핸들러 — 미니맵 화면 영역 클릭 시 호출되는 함수(마우스 좌표→미니맵 영역 판정→월드 좌표 변환→이동/카메라)를 브레이크포인트로 찾고, 원본에서 입력이 도달하는지 확인. 도달하면 그 경로의 명령 발행이 선택 전원(원본20/v10 50)에 가는지 paired, 렌더와 무관하게 입력만 살아있으면 PASS 가능. 도달하지 않으면(격리 환경에서 미니맵 입력 비활성) 근거를 남기고 **UNKNOWN 확정**. 그 다음 middle이 사용자 항목 (1)+(2)와 v10 전체 재검수(v10 핵심 회귀 1회 포함).
**[압축 포인터] lap757~759 "다음 한 가지" 서사(원문 24줄, SHA256 `1ed5b5ed711017e8d8c70ff9efe0b7dc3c532a2ecbb05fb5e31e10a67ed3aa2f`)** — 전문 `docs/history/20260929_status_lap757_759_nextthing_precompaction.md`.
lap759가 카페 주소 전제를 반증하고 미니맵 위젯 초기화 1회 호출을 확인한 경위이며, 아래 lap760이
그 다음 지시(11:25 항목 2 가속)를 이어 처리했다.

**2026-09-29 12:37 지시 처리(lap762 work) = 브레이크포인트로 클릭 라우팅 체인 신규 특정, `UNKNOWN`
확정(더 구체적 근거로).** 정적(objdump 전수 xref)으로 실제 체인을 찾았다: WM_L/RBUTTON 핸들러 →
`FUN_004216B0`(마우스 이벤트 enqueue) → 매 틱 클릭 라우터(`FUN_004217B0`로 dequeue) → 필터 통과 시
`FUN_004516A0`(this=미니맵 위젯 `0x639350`, 히트테스트+좌표변환, 판정범위 x∈[0,180]·y∈(509,599],
lap710 다이아몬드 영역과 거의 일치) → 실패 시만 메인뷰포트 히트테스트로 폴백. **신규 반증: 위젯
생성자가 LUT을 0xFF로 먼저 채우지만 같은 함수의 후속 루프가 실제 타일 데이터로 굽는다 — 실측(원본
LUT-A 32400바이트 직접 읽기)으로 16200/32400(50%)이 0xFF가 아님을 확인.** "미니맵 렌더/좌표 서브
시스템이 완전히 죽어있다"던 lap677/710/758/760의 결론은 이 지점에서는 틀렸다. gdb 5-breakpoint
실측: enqueue 24회·라우터 dequeue 19086회(매 틱)는 확인되지만 **미니맵 히트테스트 `FUN_004516A0`는
0회** — 병목은 라우터 내부 필터 체인(버튼타입 검사·좌표 sentinel 검사·`0x41c450` 게이트 중 하나)로
코드 위치가 좁혀졌다. 크래시0, `source_unchanged` 2/2. 상세
`docs/history/laps/20260929_lap762_work_g5_minimap_click_router_hittest_blocked_upstream.md`,
`analysis/memory_maps/g5_minimap_click_router_lap762.md`.

**2026-09-29 lap763 처리 결과 = 게이트 확정 + 강제-플래그 실증(12:37/12:57 지시 완료, 추가 연장
없음).** 세 필터 지점 중 실제 게이트는 `call 0x41c450` 하나뿐(관측 9430회 전부 `eax=0x0`)이고,
그 조건이 로비 "게임 타입"(`0x975914==3`) 선택값에 걸려 있음을 확정. `0x97597c`를 격리 사본에서
진단 write로 강제 open하자 `FUN_004516A0`가 0→6232회로 호출됨 — 미니맵 서브시스템 자체는 살아있고
게이트 하나가 잠갔을 뿐임을 실증. **UNKNOWN을 그대로 재확정하지 않는다** — 12:37 지시의 "성립하면
강제로 열어라" 조항이 성립했기 때문이다. 상세
`docs/history/laps/20260929_lap763_work_g5_minimap_router_gate_flag_confirmed.md`,
`analysis/memory_maps/g5_minimap_router_gate_lap763.md`.

**다음 work (운영자 지정 대기, 두 후보 중 선택):** (a) fixture 유닛을 스폰·선택한 뒤 강제 플래그 +
실제 베이킹된 미니맵 픽셀 우클릭으로 원본20/v10 50 명령효과(`pending_xy`) paired 측정 — 항목(2)를
완전히 닫는 직접 경로. (b) 원본 로비 UI에서 `0x632d42`/`game_type` 옵션이 사람이 실제로 고를 수
있는 정상 경로인지 좌표 스윕/캡처로 먼저 확인 — "원본에서도 항상 이 상태"인지 "우리 로비 자동화가
옵션을 잘못 고르는지"를 가른다. 그 다음 middle이 사용자 항목(1)+(2)와 v10 전체 재검수(v10 핵심
회귀 1회 포함). 멀티·초기메뉴 경로는 알려진 제한 유지, G1 재개 금지.
**[압축 포인터] lap758~760 "다음 한 가지" 서사 + 바퀴 기록(원문 34줄, SHA256
`0aa62dacd2012fc10e0ed4a91e2899b059ff79199830193481439bcd1e47894d`)** — 전문
`docs/history/20260929_status_lap758_760_nextthing_wheel_precompaction.md`. 수확(V) paired PASS,
ddraw override 반증(둘 다 lap760), 위젯초기화 1회 확인(lap759), 능력명 확정(lap758) 요지는 이미
위 "검증 상태"에도 있다.

## 바퀴 기록

- lap763(work, Sonnet5): 12:37/12:57 지시 처리 — 3-필터 브레이크포인트로 `0x41e332`/`0x41e365`가
  무해한 커서-아이콘 분기임을 확정, 유일한 실제 게이트 `call 0x41c450`이 관측 9430회 전부
  `eax=0x0` 반환함을 실측. 게이트 조건을 로비 "게임 타입"(`0x975914==3`) 선택값까지 정적 추적.
  **`0x97597c`를 격리 사본에서 진단 write로 1로 강제하자 `FUN_004516A0` 호출이 0→6232회
  (성공4195/실패2037)로 급증** — 미니맵 렌더/좌표 서브시스템이 죽은 게 아니라 게이트 플래그
  하나가 잠가놓았을 뿐임을 실증(12:37 지시 "성립하면 열어라" 조항 충족). fixture 명령효과는 미측정
  (다음 work 과제). 제품 코드 0 변경(진단 도구 2개 수정), `source_unchanged` 2/2, `cleanup.ok`
  2/2, 크래시 0. `ruff`/`compileall` PASS, `SAFETY_PASS`/`CONTEXT_PASS` PASS(제품 코드 무변경이므로
  lap758~762와 동일 판단으로 전체 `make check` 생략). 상세
  `docs/history/laps/20260929_lap763_work_g5_minimap_router_gate_flag_confirmed.md`.
- **[압축 포인터] lap762 바퀴 기록**(원문 7줄, SHA256
  `94203d7fe82d29d349c6bc97c81006286735ddb788846cc905459dc06b2061cb`, 위 "검증 상태"에 같은 수치
  요약 있음)는 `docs/history/20260929_status_lap762_wheel_precompaction.md`에 원문 보존 — 12:37
  지시 처리, 클릭 라우팅 체인 신규 특정(enqueue→라우터→히트테스트→폴백), LUT 50% 베이킹 확인
  (렌더-죽음 가설 부분 반증), gdb 5-breakpoint로 히트테스트 0회 호출 확정 → 차단 지점을 필터 체인
  3곳으로 좁힘(lap763이 그중 실제 게이트를 확정). 상세
  `docs/history/laps/20260929_lap762_work_g5_minimap_click_router_hittest_blocked_upstream.md`.
- **[압축 포인터] lap756~758 바퀴 기록**(원문 7줄, SHA256 `00822f5735b61c815dc3256f036be49a2835105cc4511cb920179496a4ebd16f`, 이미 위
  "검증 상태"에 같은 수치 요약 있음)는 `docs/history/20260929_status_lap756_758_wheel_precompaction.md`에
  원문 보존. v10 구현+50기 save/load PASS(lap756), 중간값/부대혼합 보완측정 PASS(lap757),
  능력v/미니맵 provenance(lap758)이며 이후 lap759(위젯초기화 확인)·lap760(수확V PASS, 미니맵
  override 반증)으로 이어졌다.
- lap754(middle, Opus5): lap753 v9 독립 재검수 = **(F) PASS**, S3는 정적 전수+runtime 차분 커버로
  재분류, (A) 표 §2b 추가. A~H 2단 판정 완료 → 사용자 3단 재상정(ESCALATE_SOL). `make check` 1122
  passed·5 skipped, `SAFETY_PASS`. 상세 `docs/history/laps/20260928_lap754_middle_g5_f_s3_v9_review_pass_milestone_resubmit.md`.
- **[압축 포인터] lap751~753 바퀴 기록**(원문 17줄, SHA256
  `73369b17116c3a86a7bc05cd6967a38496745d9d803e0547df6f3d2b1f4c1375`, 이미 위 "검증 상태"에 같은
  수치 요약 있음)는 `docs/history/20260929_status_lap751_753_wheel_precompaction.md`에 원문 보존.
- **[압축 포인터] lap739~750 바퀴 기록**(v7 F-2 미지정선택 save/load, v8 H-STALE-TAIL 수정, S3/S4/S5
  탐색, 홀드버튼 편차·해소, lap745·750 middle HOLD 판정 2회)는 위 헤더 압축 파일
  (`docs/history/20260928_status_lap751_precompaction.md`, 그리고 그 파일이 가리키는
  `docs/history/20260928_status_lap717_741_precompaction_v2.md`)에 원문 그대로 보존했다.

G5의 선택/호출/이동/save-load/장시간 runtime 증거와 과거 실패 provenance는 `docs/history/laps/`
및 공유 `temp/Syw2plus_patch/`에 보존한다.

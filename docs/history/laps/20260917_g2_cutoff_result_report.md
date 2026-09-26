# G2 8인 각 전비5000 — 2026-09-17 결과 보고

## 결론

**전체 목표를 만족하는 버전/패치는 아직 없다.** 원본 풀 안에 들어가는 보조 고전비 8진영 구성은 실제로 동작했고, 저장/로드 및 24k 자연 시뮬레이션의 부분 증거를 확보했다. 그러나 임의의 합법적인 저전비 대군 구성까지 안정적이라는 증거는 없다.

**32비트라서 불가능하거나 메모리가 실제 고갈됐다는 결론은 아니다.** 확인된 주된 문제는 고정 개체 풀·개체 참조·보조 인덱스·소유자 배열·저장 포맷의 일관된 확장이다. 숫자 몇 개만 바꾸어 전체 목표를 달성할 수는 없다.

## 실제 확보한 증거

- 원본 기반 전비5000 후보(0a1d)와 승인된 private bridge(8de5), 기존 8진영 저장본을 fresh owned runtime에서 로드했다.
- 초기8명 각각 count145/USED5000/cap5000, 전체1160기 HP양수. 대부분 TYPE5 전투유닛은 보조 생성한 진단 구성이므로 원본 생산만으로 만든 군대라고 하지 않는다.
- 입력/bridge 요청 없이 원본 자연 시뮬레이션 tick10020→34144, **Δ24124틱/725.021초/146샘플**, 관측 오류0. 게임/owned prefix 프로세스 정리 성공, 잔류0. 실제 부모 CLI rc0과 별도로 생략한 G1 입력 검증은 FAIL로 보존한다.
- 사망 HP표본→개체 부재→같은 슬롯 다른fullID 25건을 관측했다. 중간 사망표본을 못 잡은 재사용119건은 원인을 단정하지 않는다. 전체 샘플 중65건은 tick 경계를 넘어 읽었고, 모든 읽기는 비원자적이다.
- 이전 300초 구간에서 생산대기하던 owner4는 이번 구간에서 TYPE7 새ID11건과 예약해제5회가 관측됐다. 이전 'stuck'은 해당 관측구간에 한정된 판정이지 영구 생산불가 결론이 아니다.
- 원본 static TYPE비용표 SHA를 확인하고 **146×8=1168회 진영별 점유 개체 비용합과 USED를 대조해 모두 일치**했다. HP양수 개체만 합산할 때50건 차이가 난 것은 제거대기 사망 개체 비용으로 설명된다.
- 최대 동시점유1176이었다. 슬롯1199를 사용했다는 사실과 1199개를 동시에 채워 풀을 고갈시켰다는 주장은 다르다. 실제 할당거절/풀고갈을 이번 실행에서 재현하지 않았다.

## 남은 정확성 문제

owner1 USED5003/cap5000이 마지막7샘플에 반복됐다. 같은fullID394322가 owner3에서 owner1로 바뀌며 +10 전비가 동반됐다. 원래 owner3에 있던 TYPE23이지 새 전역ID 생성 증거가 아니다. 소유권 이전과 초과 전비의 시간적 연관은 확인했지만 호출 경로/원인은 UNKNOWN이다. 원본 규칙의 예외, 새 숫자패치의 버그, 생성게이트 우회라고 단정하거나 전비를 강제로 보정하지 않는다.

RSS/CPU/game-heap 계열 측정, 144k 장기 지속, Windows native, 확장 저장본, 지원 LAN 동기화는 이번 증거에 포함되지 않는다.

## 확장 작업이 아직 어려운 이유

- 원본 UnitStruct는1200개이며 슬롯0을 제외하면1199개를 사용할 수 있다. 일반 소유자 생성 경계는 cap250에서242다.
- 조건부 예시로 전비10짜리 유닛만 만들면 각500기, 8명은4000기가 필요하다. 전비0 개체·부수 효과까지 포함하는 전체 필요 풀의 안전 상한은 별도로 결정해야 한다.
- 소유자 상한1200의 정확한7바이트 후보6074는 오프라인 생성·버전거부·원복 테스트를 통과했지만 **게임에서 실행하지 않았다.** 소유자 숫자 패치는 전역 풀을 늘리지 않는다.
- Unit 본체뿐 아니라 existence/age/active/category 목록, 공간 인덱스, 생성/제거, bulk-relative alias와 저장/로드까지 함께 맞아야 한다. 원본 Unit base를 유지하며 뒤 전역들을 이동하는 구조는 수치상 가능하지만 참조 분류와 비균일 보조배열/직렬화 계약이 닫히지 않아 구현 GO가 아니다.
- 이전 주소 소비자 국소 패치 두 번은 정상 시뮬레이션 진입 전에 잘못된 메모리 참조로 실패했다. 이는 OOM 증거가 아니다. 실패PC를 따라 무제한 패치를 더하는 방식은 중단했다.

## 이번 정상생산 경계 실험을 실행하지 않은 이유

기존 op1로 한 진영이242→243을 정상생산하는 별도 실험을 준비했지만 동결본4a14/testb62에 절대23:40 종료시각, 보수적 시간 예측, 명령owner/상한/pending 선행조건과 생산행동 회귀가 부족했다. Astra/medium이 추가 수리를 STOP하고 Sol/high가 동일 동결본을 REJECT했다. 부모 연결은 정상이고 cap250 생성게이트 충돌 가설은 기각했다.

게임/prefix 준비0회인 채 실패 동결본을 외부에 보존하고 active source6efd/test722로 정확 원복했다. 이 실패는 실험 코드의 계약 부족이며 게임의243기 생산이 불가능하다는 증거가 아니다. 추가 소스 수리/실제 재시도로 예산을 초기화하지 않는다.

## 속도와 가능성 평가

- **숫자패치+원본 풀 내 고전비 구성:** 실제 실행 부분 증거 있음.
- **8인 임의 저전비 구성 각5000의 완성품:** 없음. 현재 구조 통합 수준에서 이번 시간 안에 전달할 수 없음.
- **원천 불가능:** 입증하지 못함. 32비트 주소 폭 자체보다는 고정 배열·참조·직렬화 변경이 핵심이다.
- 이어서 할 가치가 있는 작업은 개별 주소 추측이 아니라 일관된 storage/lifecycle 계약과 실제 저전비 생성 검증이다. 이는 새 검토/시간 배분의 판단자료이며 자동 승인된 새 실행 큐가 아니다.

사용자 상한은 오늘밤 자정2026-09-18 00:00 KST로 해석했다. 시간 채우기용 재실험은 하지 않는다. 목표 완료 표시 없이22:24 KST에 안전 원복 검증과 기록을 마무리했다. 원복 후 fresh633 tests/149.68초, Ruff/compile/mypy/context/shell 및 추가mypy2 PASS, source전후 일치·보호8pins 일치·ownedprefix 잔류0을 확인했다. 원본/공유DLL 변경·배포·커밋은 없고, 반려된 실험 모드는 active 코드에서 제거했다.

## 증거 위치

원시 기록/실패 코드/분석 부산물은 메인 레포가 아닌 다음 외부 경로에 보존했다.

`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/`

- `20260917_stock_24k_observation_v1/actual_owned_v1/`: actual146samples, summary, cleanup receipt, 독립 분석 및 Root 재현/비용합/ID이전 대조.
- `20260917_owner_organic_feasibility_v1/`: 계획, 실패 동결본, STOP/정확 원복 영수증 및 원복 후 Fast 로그.
- `20260917_stock_cap_overshoot_audit_v1/audit.json`: 초과전비/같은ID 진영이전 조사.
- `20260917_organic243_major_decision_2217.json`: Astra 추가 수리 STOP 결정.


## 22:26~22:51 추가 읽기전용 조사 — 종료

목표연속 요청으로 bulk-relative/lifecycle/storage 3카드를15분씩 조사했다. 원문 산출물의 주소산술/명령경계/441441 함수주소 혼동/PlanC 혼입/Player-relative base 등을 발견해 원문을 보존하고 최초시간 안에서 erratum을 작성했다. 독립Sol/high1057 검수는16명령/3함수/3호출 및Root9구간401명령을 원본RAW와 대조하고 **selected facts만** 채택했다. sourceannotation 잔존오류는 불채택했다. 3개 초기화호출자는BULK892410/길이E397C를 사용하고, existence/age/8진영roster가 원본저장블록에 포함됨을 확인했다. stream40F4B0/F4F0는RET4; load441441는1200 loop bound이다. 이것은 전체확장 참조폐쇄/구현GO가 아니다.

Astra/medium은 마지막 질문하나만 추가했다: 전비0 출력 하나가 정상원본에서 반복·동시보유 가능한지. TYPE94 cost0@9CA290, producer49→94행/연구37 prerequisite는 확인했으나 flags11808 bit8에 positive indexed94 counter 거절이 있다. selector→issuer는 확인했고 **정상HQ 생산완료→반복동시생존은UNKNOWN**이다. Sol/highd950은 author의closed-static-repeatedpath/제한없음 주장을 기각했다. 더 많은TYPE나게임으로 확장하지 않는다. 따라서4000개 양수비용 산술도 전체안전풀 상한으로 확정하지 못했고9601/9904 용량도 승인되지 않았다.

최종읽기전용 조사는소스/native/DLL/게임변경0. 보호8pins 유지·knownownedWinePID소멸 및priorfinally remaining[] 확인. readable/proc exactprefix match0이지만 일부환경파일권한거부가 있어systemwide귀속전수증거라고 쓰지 않는다. 과도한UID assertion실패도 영수증989f4c32에 남겼다. 동일UID서비스3·zombie3에kill하지 않았다. nativechild6모두completed, 새실험 없음. docs/context check PASS; active source는마지막633Fast검증한6efd/test722 그대로다.

**속도/가능성 최종평가:** 원본풀안의보조고전비8인5000 actual24k 부분PASS를얻었지만, 실제확장저비용대군 버전은아직전달불가다. 숫자패치로끝나는작업이아니며 coherentpool/index/lifecycle/save/LAN 통합이남았다. 32비트주소폭/OOM때문에불가능하다는증거는없다. 오늘현재검수계약으로안전한완성품을자정전에내겠다는약속은불가다. Astra의명시적시간채우기금지/탐색종료에따라새카드를시작하지않고이결과로안전분기를마무리한다. 사용자00KST상한이후자동실행없음, goal미완료유지.

상세이력: `20260917_g2_storage_lifecycle_contract_review.md`; 모든RAW/검수산출물은지정공유temp/Syw2plus_patch/g2_capacity에보존했다.

## 2026-09-18T00:00:21.059764+09:00 — 사용자 자정 상한 도달/종료
owned timer session43513 rc0/actual00:00:00.009776 terminal, PID124104 absent; known gamePID3804916 absent; CLI STOP intact. Child6는23:54 authoritative completed. 추가게임/조사/구현 실행없음; 종료기록만작성. Nativegoal은전체G2미완료이며complete표시금지. Blocked audit 첫출현(연속goalturn1): 사용자명시시간상한종료/재개지시없음. 후속automaticgoal신호는시간재승인이아니며새사용자지시없이제품작업불가. Strict3turnthreshold전에는update_goalblocked호출하지않는다. 보호8pins pre_cutoff a3c205 PASS/source6efd/test722 유지/status130 및history원문9400 보존. 최종timerreceipt는공유temp/Syw2plus_patch/g2_capacity/20260917_cutoff_runner_guard_v1/cutoff_terminal_receipt.json.

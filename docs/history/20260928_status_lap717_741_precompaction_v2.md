# STATUS — 매 바퀴 갱신하는 기억

lap676~716 상세(과거 압축 포인터 4단, G5 milestone 승인, G2 8인×10000 A/B 종료, G4 W2 post-load
종결, G4-P1 baseline, G4 자유대전 AI baseline/생산게이트 히스토그램, G5 v3 명령범위 검증)는 이 헤더
블록 142줄 SHA256 `2bfbadb771c33798d56586406746ddf57888ac02343982ee5c66b109d3f2b34b`으로
`docs/history/20260927_status_lap717_precompaction.md`에 원문 그대로 보존했다. 각 lap 전체 근거는
`docs/history/laps/20260926_lap67{6..9}_*.md`·`lap68{0..9}_*.md`·`20260927_lap69{5..9}_*.md`·
`lap70{0..9}_*.md`·`lap71{0..6}_*.md`에 그대로 있다.

## 지금 상태

**G5는 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 승인됐으나, 2026-09-28 01:31 사용자
지시로 승인이 조건부로 되돌아갔다** — 아래 A~H 완료 체크리스트 전부 PASS해야 G5 종료, 그 전엔 G1
재개 금지(멀티 동기화는 `UNKNOWN` 메모 유지, 명령당 60B 레코드 최대3회 발행). 체크리스트
**(A) 정적 전수 표 = 완료(lap725,
`analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`)**. **(B) = 완료(lap723·725·
726·727·728)**: R3(앞/중간/뒤 사망) v5 PASS, Shift 제거 PASS, 51번째 거부 PASS, 더블클릭 같은종류선택
PASS(원본20/v5 50, 상한 준수), ALT/Ctrl 클릭 같은종류선택·포트레이트 클릭 해제는 **이 게임에 해당
기능 자체가 없음을 원본·v5 둘 다에서 확인**(미지원, 회귀 아님), **Shift+클릭 개별 추가 격리 재확인
= PASS(lap728, 원본·v5 6단계 전부 — 05:15 관찰은 조밀 fixture 겹침 아티팩트로 확정)**.
**(C) = 완료(lap729·730·731·735·736·737)**: 채집·수리 broadcast PASS,
승선하선 N/A(이 게임에 기능 자체 없음, lap731), 좌표일치는 기존 증거로 PASS(lap731). **건설 = N/A로
강화(lap736, 08:15 지시 이행)**: 설명서 3종에 건물배치 조작법 없음 확인 + 재부팅 16회로 솔로 로비
국가 풀이 정확히 3개(worker7/21/31, HQ49/58/70)로 수렴함을 확인, 세 번째 국가의 워커·HQ 그리드
전 버튼도 신규 existence 슬롯 0(배치 버튼 없음, lap731과 동일 결론 — 3개국 전수, 반증 없음).
특수능력 = "f" 셀 1종 paired PASS(원본20/후보v6 50 전원 수신, lap735). "i" 셀은 지면(worker
기준(0,6)) 우클릭으로 lone worker 발동 확인(command 1→8, 원본worker7·후보v6 worker21 둘 다
동일 레시피로 재현)되지만 **2~3기만 선택해도 원본·후보 둘 다 무반응 — 솔로 선택 전용 능력으로
판정(N/A, cap 결함 아님, lap737)**. "v" 셀은 button-only+지면 오프셋 8개 탐색에도 3개국
(worker7/21/31) 전부 원본·후보 동일하게 무반응 — 근본원인 미상 UNKNOWN 유지(원본도 0이므로
v6 회귀 아님, lap737) — 세 국가(worker7/21/31) 전부의 특수능력을 이제 측정했다.
**(D) = 완료(lap724·732·733)**:
Ctrl+숫자/호출/저장로드(lap724 roundtrip), Shift+숫자 추가(lap732, 미지원 확인+대안메커니즘 PASS),
부대원 사망 후 호출(lap733, v6 신규 훅으로 수정 후 PASS — 기준 후보가 v5→**v6**로 교체됨).
**(E) = 완료(lap738)**: 초상화/정보 패널·HUD·체력바 확인 PASS(원본20/20·후보46/50, 하드캡 반증).
**(F) = PASS(20 상한, lap740, 기준 후보 v6→v7 교체)**: lap739 FAIL을 2026-09-28 14:05 운영자
판정대로 v7(`patches/selection/g5_selection_cap50_v7.py`)로 수정 — 저장 직전 레거시 주소
`0x00899024`/`0x00899028`에 현재 선택(≤20)을 미러링, 로드 직후 역미러링하는 훅 2개(`.rsrc`
자신의 0-padding에 배치, 세이브 바이트 배치 무변경). raw 드래그 50 선택 후 저장→디셀렉트→로드
→ **count=20, slots가 원본 paired 결과와 완전 일치**. 그룹 저장/로드 재확인 PASS(회귀 없음,
7/7). 세이브 호환 양방향 PASS(원본이 v7 세이브를, v7이 원본 세이브를 크래시 없이 로드하고 둘 다
동일 20-슬롯 복원). entries 21~50은 원본과 동일하게 저장/로드를 왕복하지 않음(명시적 수용 한계,
다음 work 후보: 세이브 스트림 끝 trailing block).
**(G) = 진행 중, INCONCLUSIVE(lap741)**: Wine 내장 `dpwsockx` stub 경로는
`BLOCKED(env: wine9.0 dpwsockx stub)`로 확정(G2 lap580 N211 재사용, 현재 환경 `dpwsockx.dll` SHA
실측 일치로 환경 동일성 확정). 15:05 운영자 지시로 `[ESL]Syw2plus/`에 동봉된 **네이티브 IPXWrapper
DLL 세트**(`dpwsockx.dll`/`wsock32.dll`/`mswsock.dll`/`ipxwrapper.dll`, IPXWrapper 0.6.0)를
`WINEDLLOVERRIDES`로 강제해 재시도 — 단일 인스턴스 부팅 스모크는 크래시 없이 PASS했으나(레지스트리
공급자 등록 성공), 네이티브 DLL은 멀티플레이 메뉴 진입 시 지연 초기화라 부팅만으로는 활성화 여부를
확인 못했다(`ipxwrapper.log` 무변화 — 배포 당시 원본 PC의 과거 로그 그대로). 실제 확인에는 멀티
로비→DirectPlay 공급자 목록 화면까지의 UI 자동화(G2 lap577~580급 별도 작업, 저장소에 미보존)가
더 필요하다 — **INCONCLUSIVE로 정직하게 유지, FEASIBLE도 BLOCKED도 아님.** 대안 정적 패킷 대조는
완료: 실제 명령 발행 단일 호출부 `0x41F0A4`가 원본과 동일한 60바이트 레코드·20-word 포맷을 유지한
채 50기 주문당 최대 3회만 발행함을 v4 문서화 + v5→v6→v7 import 그래프 무변경 확인으로 재확인
(PLAUSIBLE, 와이어 미관측). **다음 판단 필요:** (가) UI 자동화를 새로 만들어 네이티브 override
재시도를 완결할지, (나) Wine-stub `BLOCKED`+정적 대조를 (G)의 최종 답으로 받아들이고 (H)로
넘어갈지 — middle/운영자 판단 대기. (H) 미착수.

**G2는 2026-09-27 03:21 사용자 판단으로 전비10000 트랙 종료, 전비5000(달성 판단 유지)으로 복귀.**
10000 후보(lap691~699, `g2_supply10000_*`)와 근거는 보존만 하고 더 진행하지 않는다.

**G4(길찾기·자유대전 AI)는 2026-09-27 15:12 사용자 지시로 보류.** W2 post-load
`EXACT_POSTLOAD_EDGE_PASS` CONFIRMED·종결, 길찾기 트랙 종료(원본에 개선 여지 없음), 생산게이트
히스토그램(H_AVAIL·PREREQ_OWN 100%)까지 완료 후 보류. candidate AI 정책 여전히 없음.

**G1(원본과 같은 화면 구성 1600×1200)은 2026-09-27 15:20 지시로 G5 완료 후 재개 예정, 현재 중단.**

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료, 착수 대기(G5 이후) | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성(복귀). 8인×10000 트랙 종료(근거 보존) | 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류(길찾기 종료, 생산게이트 계측 완료) | candidate AI 정책 없음, 사용자 승인 |
| G5 | **승인 조건부 보류** — A~H 완료 체크리스트(2026-09-28 01:31) 전부 PASS 전엔 미종결. A·B·C·D·E·F 완료(lap723·725~740, 기준 후보 **v7**, 건설=N/A 3개국 전수, "i"=솔로전용 N/A, "v"=UNKNOWN, F=20 상한 PASS), **G = INCONCLUSIVE(lap741, 판단 대기)** | G 최종 답(가/나) 선택 필요, H 미측정 |

## 지금 막힌 것 (Blockers)

**world (93,56)의 `long_distance_pan` 카메라-복귀 결함은 여전히 후순위 미해결**(lap711 run1이 raw로
재확인 — 카메라 팬 37.6타일 도달은 성공하나 복귀 보정 3회 후에도 drift 21~27타일, 드래그 선택
0/20). world (10,49)를 baseline으로 계속 쓴다.

## 검증 상태

**[압축 포인터] lap717~732 검증 상태 계보(원문 23줄, SHA256
`c6c7eddb77042a787bd1bb6c764b239812e30dbe15d3be4b843649d7ac1bdad9`,
`docs/history/20260928_status_lap737_verification_precompaction.md`에 보존)** — v4/v5 명령범위
PASS·R1 FALSIFIED·R3 발견/수정, (A) 정적 표, (B) 사망 시나리오·Shift 제거·51번째 거부·더블클릭,
Shift+클릭 개별추가 격리 PASS(lap728), (C) 채집 PASS(lap729), (D) 사망후호출 v5 FAIL 발견(lap732).
매 lap `make check` PASS·`SAFETY_PASS`·크래시0·`source_unchanged`.

## 다음 한 가지
**2026-09-28 15:23 운영자 판정(lap741 선택지):** **(가) 채택** — 사용자가 사이드 이펙트 전수 확인을 요구했으므로 멀티는 정적 대조로 끝내지 않는다. 다음 work는 멀티 로비 UI 자동화(호스트: 멀티→IPX 공급자→방 만들기, 게스트: 같은 공급자→방 목록 선택→참가→시작)를 구축해 IPXWrapper 동봉 DLL로 2인스턴스 세션 성립을 시도(15:05 지시 그대로). 한 lap에서 세션 성립까지 못 가면 막힌 화면 캡처·오류와 함께 진척을 기록하고 다음 lap이 이어간다. 3 lap 안에 불가하면 그때 (나)로 전환.
**2026-09-28 15:05 운영자 지시(lap741 G BLOCKED 재시도):** 새 원본 폴더 `[ESL]Syw2plus/`에는 **IPXWrapper 세트(`ipxwrapper.dll`, 네이티브 `dpwsockx.dll`, `wsock32.dll`, `mswsock.dll`, 2015)**가 동봉돼 있다 — 원래 LAN 플레이는 IPX-over-UDP로 이걸 쓴다. Wine 내장 dpwsockx stub가 아니라 이 DLL들을 격리 사본에 넣고 `WINEDLLOVERRIDES="dpwsockx,wsock32,mswsock,ipxwrapper=n,b"`로 두 인스턴스(각자 prefix·Xvfb, 같은 호스트 UDP 브로드캐스트/루프백, 필요시 ipxwrapper 설정 `ipxconfig.exe`/레지스트리)를 띄워 'IPX Connection For DirectPlay'로 방 생성/참가를 시도하라. 성공하면 원본20/v7 50 이동·정지·공격 명령을 한쪽에서 내리고 양쪽 유닛 상태·위치를 비교(desync 없음). 실패하면 구체 오류와 함께 BLOCKED 확정, 대안으로 명령 패킷 발행 경로(분할 발행 최대 3회)의 정적 대조를 기록.
**lap741(work, 이 세션) 결과 — INCONCLUSIVE(완전히 닫지 못함, 정직하게 보고):** 지시대로 `[ESL]Syw2plus/`의
네이티브 IPXWrapper DLL 세트를 실측 확인하고 `WINEDLLOVERRIDES="ddraw=b;dpwsockx,wsock32,mswsock,
ipxwrapper=n,b"`(첫 시도는 세미콜론 누락으로 파싱 실패 — 가설 실패 1/2, 문법 수정해 재시도)로
단일 인스턴스 부팅 스모크를 했다: 레지스트리 공급자 등록 성공, 크래시 없이 12초 생존. 그러나
`dpwsockx.dll`/`ipxwrapper.dll`은 멀티 로비 진입 시에만 지연 초기화돼 단순 부팅으로는 활성화
여부를 확인할 수 없었다(`ipxwrapper.log`가 배포 당시 원본 PC의 과거 로그 그대로 무변화). 실제
2인스턴스 세션 성립을 보려면 메인 메뉴→멀티 모드 선택(`G1_SETUP_POINTS`로 재사용 가능)→DirectPlay
공급자 목록 화면까지의 UI 자동화가 더 필요한데, 이 화면의 클릭 경로는 G2 lap577~580이 `/tmp`에서
한 번 만들었을 뿐 저장소에 보존되지 않았다 — 새로 만드는 것은 그 자체로 별도 작업 규모다. **(G)를
`FEASIBLE`도 `BLOCKED`도 아닌 INCONCLUSIVE로 정직하게 남기고, 다음 판단(가: UI 자동화 신규 구축
후 재시도 / 나: Wine-stub BLOCKED+정적 패킷 대조를 최종 답으로 수용하고 (H)로 진행)을 middle/
운영자에게 넘긴다.** 정적 패킷 대조(요청된 대안)는 이번 lap에서 이미 완료: 실제 명령 발행 단일
호출부 `0x41F0A4`가 원본과 동일한 60바이트 레코드·20-word 포맷을 유지한 채 50기 주문당 최대 3회만
발행함을 확인(v4 문서화 + v5~v7 무변경 재확인, PLAUSIBLE). 상세
`docs/history/laps/20260928_lap741_work_g5_checklist_g_multiplayer_env_blocked.md`.
**[압축 포인터] lap739~740 F/F-2 판정·v7 지시·구현 원문(원문 27+ 줄, SHA256
`c3b8bdf0122448c8bec73653ee58e02dacd371856fcb59e81bb964ff8d18251e`,
`docs/history/20260928_status_lap739_nextthing_precompaction.md`에 보존; 세부는 lap740 기록
`docs/history/laps/20260928_lap740_work_g5_checklist_f_v7_saveload_selection_shadow_fix.md`)**.
체크리스트 A~H 원문은 `docs/feedback/APPROVALS.md`의 2026-09-28 01:31 사용자 지시 항목을 참조한다.

## 바퀴 기록

- lap741(work, 이 세션): (G) 멀티 — Wine 내장 `dpwsockx` stub 경로는 `BLOCKED(env: wine9.0
  dpwsockx stub)`(G2 lap580 N211과 현재 환경 `dpwsockx.dll` SHA `3b4f6a9d…986c9` 실측 일치로
  확정). 15:05 운영자 지시로 `[ESL]Syw2plus/`의 네이티브 IPXWrapper DLL 세트를 `WINEDLLOVERRIDES`
  강제 override로 재시도 — 단일 인스턴스 부팅 스모크는 PASS(크래시 0, 레지스트리 등록 성공)했으나
  네이티브 DLL 지연 초기화 때문에 실제 활성화는 미확인(`ipxwrapper.log` 무변화). 실제 확인은 멀티
  로비→공급자 화면 UI 자동화(신규 구축 필요, G2 lap577~580급 작업)가 더 있어야 한다 — **(G) =
  INCONCLUSIVE**(FEASIBLE도 BLOCKED도 아님, 다음 판단은 middle/운영자에게 넘김). 대안(정적 패킷
  대조)은 완료: 실제 명령 발행은 단일 호출부 `0x41F0A4`뿐이며(기존 (A) 정적 표), v4가 문서화한
  "60바이트 레코드·20-word 리스트, 주문당 최대 3회" 청크 포맷이 v5→v6→v7까지 재정의 없이 그대로
  이어짐을 import 그래프로 확인(신규 확인). `make check` **1116 passed(793.43s)**, ruff/mypy/
  `CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개, 제품 코드 무변경, 진단 드라이버는
  `/tmp`에만 존재, 격리 사본은 스모크 종료 후 삭제). 상세
  `docs/history/laps/20260928_lap741_work_g5_checklist_g_multiplayer_env_blocked.md`.
- lap740(work): (F) v7 구현 — lap739가 확정한 원인(레거시 선택 주소 `0x00899024`/
  `0x00899028` 방치)을 저장 직전 미러링·로드 직후 역미러링 훅 2개로 수정. raw 50 선택→저장→
  디셀렉트→로드 → **count=20, slots 원본 paired와 완전 일치(PASS, 20 상한)**. 그룹 저장/로드
  재확인 **PASS**(7/7, 회귀 없음), 세이브 호환 **양방향 PASS**(원본↔v7 크로스로드 크래시 0, 원본
  세이브를 v7이 로드하는 역방향 포함). entries 21~50은 원본과 동일하게 미보존(수용된 한계).
  크래시 0(4/4), `source_unchanged` 4/4, `make check` **1116 passed(808.52s)**, `SAFETY_PASS`.
  상세 `docs/history/laps/20260928_lap740_work_g5_checklist_f_v7_saveload_selection_shadow_fix.md`.
- lap739(work): (F) 저장/로드 — raw 드래그 선택 자체는 후보 v6에서 저장/로드 시 항상 0으로
  소실(부분 **FAIL**, 원본은 PASS), 그룹 저장/로드는 재확인 **PASS**, 원본 세이브 호환(크로스 로드)은
  **PASS**(크래시 0). 근본 원인은 v1의 레거시 주소 `0x00899024` 완전 미사용 방치로 정적 확정.
  마일스톤 경계라 `loop/ESCALATE_SOL` 승격, v7 임의 작성 안 함. `make check` 1111 passed(858.42s),
  `SAFETY_PASS`. 상세
  `docs/history/laps/20260928_lap739_work_g5_checklist_f_saveload_selection_regression.md`.
- **[압축 포인터] lap728~738 바퀴 기록(원문 23줄, SHA256
  `a536492c9d91ac79e6d66eef3aabd2499d674aaa990c3f79d003f6b2bc060576`,
  `docs/history/20260928_status_lap728_738_precompaction_v2.md`에 보존)** — (E) UI PASS(lap738),
  (C) 건설 N/A 강화·특수능력 탐색 완료(lap736~737), 특수능력 paired 측정(lap735), (D) FAIL 발견·v6
  수정 PASS(lap731~733), v6 핵심 회귀 PASS(lap734), Shift+클릭·채집·수리(lap728~730),
  G4 baseline→G5 v3/v4/v5 명령범위·(A)(B) 완료(lap712~727).

G5의 선택/호출/이동/save-load 부분 runtime 증거와 과거 실패 provenance는 `docs/history/laps/` 및
공유 `temp/Syw2plus_patch/`에 보존한다. G5 milestone 승인은 2026-09-28 01:31 지시로 조건부 보류(A~H
체크리스트). 명령범위 FAIL v4 수정·R1 확정 반증(lap721)·R3 lap723에서 v4 CONFIRMED FAIL·v5 PASS.

# INBOX — 압축 포인터

원문 360줄·SHA256 `787d9ce2e2964f6cc1a5f7de81a3e136ee1bed47bffc426ee972a38e61210b24`(lap643 이전)은
`docs/history/20260926_inbox_lap643_precompaction.md`에 보존했다. **lap643~741 원문 382줄·SHA256
`33437bac42033c4f584e23168ee710f3456cbf0a2b040777584f06f9fea91317`은
`docs/history/20260928_inbox_lap742_precompaction.md`에 원문 그대로 보존했다** — G5 v1→v6 선택
상한50 조사 전체 계보(명령범위·공격판정·부대지정·선택축소 R1~R3·사망후호출 등 lap644~738),
G4 길찾기/AI 계측 계보(lap704~715, 2026-09-27 15:12 지시로 보류), G2 8인×10000 계보(lap691~699,
2026-09-27 03:21 사용자 판단으로 5000 복귀·종료)가 모두 여기 있다. 미결 지시·반려·근거는 삭제하거나
재해석하지 않았으며, 다음 랩은 해당 원문과 이 포인터를 함께 참조한다.

## 상시 지시 (미결, 원문 요지 — 압축 대상 아님)

- [ ] **상시: 구현 우선**(2026-09-25 18:40 사용자) — 긴 정적 전수 조사·다단 카드 대신 최소 근거로
  먼저 구현·빌드·격리 실행하고, 크래시/오동작이면 원인을 추적해 고친 뒤 다시 실행하는 반복을
  기본으로 한다. 실행 횟수 예산·strategy 재회부로 이 반복을 막지 않는다. 재요약만 하는 회차 금지.
- [ ] **상시: 묻지 말고 결정**(2026-09-24 사용자 "나한테 묻지 말고 너가 알아서") — 절차·해석·재시도는
  모델이 결정·기록·진행한다. 비가역(원본/참고 저장소 쓰기·커밋/푸시·유료·제품 목표 변경)만 질문한다.
- [ ] **상시: 안전 규칙 불변** — 원본/참고 저장소 쓰기 금지, 커밋 금지(`LOOP_ALLOW_COMMITS=0` 기본,
  사용자 명시 허용 시에만), 격리 실행(전용 사본·prefix·display).
- [ ] **현행 목표 우선순위**(2026-09-27 15:20 사용자, DESIGN.md와 동일): **G5 최우선** → G1(원본과
  같은 화면 구성 1600×1200) → G2(전비5000, 8인×10000 트랙은 종료) → G4(길찾기/자유대전 AI, 현재
  보류) → G3(16인, 중단). G5는 2026-09-28 01:31 지시대로 **A~H 완료 체크리스트 전부 PASS 전엔
  종료 선언 금지, 그 전엔 G1 재개 금지**.

## G5 체크리스트 A~H — 현재 진행 스레드 (원문, 2026-09-28)

- [ ] **lap765 HOLD → lap766/767 해소 → lap768/769 미니맵 세 모드 PASS, 사용자 3단 경계:** lap766 fresh paired와 lap767 middle raw
  재계산에서 원본20/v10 50 모두 Shift 추가 `1→2`, 제거 `2→1`, anchor 제거·잔여 명령 배제 PASS.
  lap765 `2→0/0→1`은 첫 클릭부터 비anchor slot이 섞인 재현되지 않은 단일 실행 이상치로 분류한다.
  lap768의 진단 gate 이동·어택땅·순찰 원본20/v10 50 raw를 lap769 middle이 독립 재계산해 전원 목적지
  변화와 명령 종류 parity를 수용했다. v10 2단은 `PASS_WITH_LIMITS`(A/B/C/D/F/H PASS, E 조건부,
  G `BLOCKED(env)` 수용)로 18:4x 사전 승인 조건을 충족했다. 이 세션은 마일스톤 경계라 승격 작업자가
  승인 적용·G5 종료를 기록하고 재질문 없이 G1로 전환한다. 상세
  `docs/history/laps/20260929_lap769_middle_g5_v10_minimap_modes_review_pass_escalate.md`.

- [x] **2026-09-28 01:31 사용자 지시(체크리스트 원문):** "이런 사이드 이펙트 다 고려하고, 다 문제
  없는 경우에야 G5 끝내야 할거 아냐" — G5 v4 승인을 조건부로 되돌리고, 아래 (A)~(H) 전부 PASS(또는
  원본과 동일 동작)해야 G5 종료. (A) 정적 전수: 선택 count/엔트리 읽기·쓰기 전 지점 + `FUN_004AE550`
  호출자 전수 표. (B) 선택 변화: 드래그/Shift 추가·제거/ALT/Ctrl/더블클릭/포트레이트 해제/사망 등
  자동 해제(R3 포함)/51번째 거부. (C) 명령 전부: 이동·미니맵·공격·정지·홀드·순찰·채집/건설/수리
  등 일꾼 명령·특수능력/변신·승선/하선 등 전 버튼·단축키, 명령 직후 좌표 일치. (D) 부대: 지정·호출·
  Shift 추가·사망후호출·저장로드 전후. (E) UI: 50기 선택 시 정보패널·HUD·체력바. (F) 저장/로드:
  50기 선택·부대 저장 후 로드, 원본 세이브 호환. **(G) 멀티: 2인 LAN 격리 실행에서 50기 명령
  동기화(패킷 최대 3배) 또는 불가 시 사유 명시.** (H) 장시간: 수천 tick 안정성.
- [x] 처리(lap723~740): (A)~(F) 전부 완료, 기준 후보 **v7**(`patches/selection/
  g5_selection_cap50_v7.py`). 상세는 위 보존본 + `docs/history/laps/20260928_lap7{23..40}_*.md`.
- [ ] **2026-09-28 14:45 운영자 판정(lap740 v7 수용, G 착수 지시):** 다음 work: (G) 멀티 — 2인 LAN
  격리 실행(두 인스턴스·가상 네트워크)에서 50기 이동/정지/공격 명령이 양쪽에 동기화되는지(유닛
  위치·명령 상태 비교, desync 없음). 격리 환경에서 LAN이 불가하면 사유와 대안(원본 20 대비 명령
  패킷 수·형식 정적 대조)을 기록. 이어서 (H) 장시간.
  - [x] 처리(lap741 work): Wine 내장 `dpwsockx` stub 경로는 `BLOCKED(env: wine9.0 dpwsockx stub)`
    확정(G2 lap580 N211 재확인). 15:05 운영자 추가 지시(네이티브 IPXWrapper DLL override)로 단일
    인스턴스 부팅 스모크는 PASS했으나 활성화 여부 미확인 — **(G) = INCONCLUSIVE**, UI 자동화
    (가)/정적대조 수용(나) 중 선택을 middle/운영자에게 넘김. 근거
    `docs/history/laps/20260928_lap741_work_g5_checklist_g_multiplayer_env_blocked.md`.
- [ ] **2026-09-28 15:05 운영자 지시(lap741 G BLOCKED 재시도):** 새 원본 폴더 `[ESL]Syw2plus/`에는
  **IPXWrapper 세트**(`ipxwrapper.dll`, 네이티브 `dpwsockx.dll`/`wsock32.dll`/`mswsock.dll`, 2015)가
  동봉돼 있다. `WINEDLLOVERRIDES="dpwsockx,wsock32,mswsock,ipxwrapper=n,b"`로 두 인스턴스를 띄워
  'IPX Connection For DirectPlay'로 방 생성/참가를 시도하라. 성공하면 원본20/v7 50 명령 동기화
  비교. 실패하면 구체 오류와 함께 BLOCKED 확정, 대안으로 명령 패킷 발행 경로 정적 대조를 기록.
- [ ] **2026-09-28 15:23 운영자 판정(lap741 선택지, (가) 채택):** 멀티 로비 UI 자동화(호스트:
  멀티→IPX 공급자→방 만들기, 게스트: 같은 공급자→방 목록 선택→참가→시작)를 구축해 IPXWrapper
  동봉 DLL로 2인스턴스 세션 성립을 시도. 한 lap에서 세션 성립까지 못 가면 막힌 화면 캡처·오류와
  함께 진척을 기록하고 다음 lap이 이어간다. **3 lap 안에 불가하면 그때 (나)로 전환.**
  - [x] 처리(lap742 work) 원문 11줄은 `docs/history/20261004_inbox_lap933_precompaction.md`에 byte-exact 보존(전체342줄, SHA256
    `a89aa567951c03017fedce91ba9778885479dcf2f0b5fc3a80ad70cd7df68e16`). 요지: PS13 도달, 네이티브 IPXWrapper '방만들기' 크래시 2/2로 (G) `BLOCKED(env)`. 체크 완료·G5 종료 계보이며 새 지시 아님.
- [ ] **2026-09-28 15:55 운영자 지시(G 2/3 lap):** lap742 진척 수용 — IPX 로비(PS13 세션 목록)까지 자동화 성공, 그러나 네이티브 IPXWrapper override에서 '방만들기' 직후 Wine 크래시(재현 2/2, builtin stub은 크래시 없이 PS7 복귀). 다음 lap: ① Wine 크래시 대화상자의 백트레이스/모듈·주소를 캡처·기록(`WINEDEBUG=+seh,+loaddll` 등), ② override 조합 축소 실험(ipxwrapper만 native / dpwsockx만 native / wsock32·mswsock builtin 유지 등 3~4조합), ③ `ipxconfig.exe`로 인터페이스/UDP 포트 설정 후 재시도. 방 생성이 되면 두 번째 인스턴스 참가까지. 이번 lap도 안 되면 다음(3번째) lap에서 (나) 정적 대조로 전환.
- [ ] **2026-09-28 16:35 운영자 판정(lap743):** (H) 장시간 PASS 수용(v7, 8019 tick, 6단 명령 반복, 크래시·선택 손상 0). 단 lap743이 (G) BLOCKED를 자체 수용한 것은 15:55 지시(3번째 시도)와 다르다 — **(G) 마지막 1회 시도**: 크래시 백트레이스 모듈/주소 기록, override 3~4조합(ipxwrapper만 native, wsock32/mswsock builtin 등), `ipxconfig.exe` 설정 후 방만들기. 이 lap에서 세션 성립 실패 시 **(나) 확정**: BLOCKED 사유 + 명령 발행 경로(청크 최대 3회, 레코드 형식 불변) 정적 대조 문서화. 그 다음 **middle이 G5 체크리스트 A~H 전체를 독립 재검수**(v7 기준, 알려진 제한: 부대 미지정 선택은 로드 후 20기, 미니맵 우클릭·특수능력 v는 원본도 무반응 UNKNOWN, 건설·승선 N/A, 멀티 결과).
  - [x] 처리(lap743 같은 세션·lap745 middle·lap746 work) 원문 21줄은 `docs/history/20261004_inbox_lap938_precompaction.md`에 byte-exact 보존(전체345줄, SHA256
    `ec258fbd4a4a02f9d4fa4e6ad5964c1e936620fcc8dfdf71f9f6b5a29a17dddc`). 요지: (G) `BLOCKED(env)` 최종 확정(누적 4조합) → lap745 A~H 재검수 `HOLD(조건부)`(H-STALE-TAIL)
    → lap746 v7 `FAIL_STALE_TAIL_CONFIRMED`·v8 1바이트 수리 PASS. 체크 완료·G5 종료(2026-10-03 사용자) 계보이며 새 지시 아님.
- [x] 17:45/18:05 운영자 판정(lap747 처리)·18:35 운영자 지시 ①②(lap747·748 처리)·lap749 홀드버튼 처리 원문은
  `docs/history/20261004_inbox_lap925_precompaction.md`에 byte-exact 보존(전체348줄, SHA256 `85ee0ec2260db754e700aeb0d073e5000b6425ae231572718e55ccb30c6cfb2a`).
  체크 완료 항목이고 G5는 2026-10-03 사용자 종료 계보다. 새 지시 아님.
- [ ] **lap750 middle 최종 재검수 = `HOLD(좁은 조건부)`:** 홀드버튼 PASS 수용(원인은 클릭→첫 샘플 race로
  정정). 단 18:35 지시 ①의 S5는 raw상 선택0 상태에서 실행돼 공허하고, S3(초기메뉴→새 게임)는 "F에 영향
  없음"이 아니라 실제 이월 위험으로 재분류 — 다음 work 1 lap이 v7 재시작 귀속 + S3 실측(→필요 시 v9).
  상세 `docs/history/laps/20260928_lap750_middle_g5_v8_final_review_hold_s3_s5_gap.md`.
  - [x] 처리(lap751 work): v7 재시작 = 해체(dec) 경로 확정, 초기메뉴 전환은 fixture 무관 env 제약.
  - [x] **lap752 middle = `HOLD` 유지:** analogy 거부 — 원본 새 게임 초기화 `0x4a3060`이 선택 count/
    엔트리를 직접 0으로 만들지만 v8 새 배열은 빠짐(H-NEWGAME-INIT). 다음 work 1 lap: v9 1지점 + 게임
    시작/재시작 stale 주입 paired probe. 상세
    `docs/history/laps/20260928_lap752_middle_g5_f_s3_newgame_init_gap_v9_handoff.md`.
  - [x] **lap754 middle(Opus5) = (F) PASS(v9):** v9 재빌드 SHA·hook 무조건 경로·`0x4a3060` 호출자 3곳 전수·
    lap753 raw 재계산 일치, `make check` 1122 passed. A~H 2단 판정 완료(G `BLOCKED(env)`, E 조건부) →
    **사용자 3단 milestone 재상정 대기**(G1 재개는 사용자 승인 후). 상세
    `docs/history/laps/20260928_lap754_middle_g5_f_s3_v9_review_pass_milestone_resubmit.md`.
  - [x] **처리(lap753 work): v9 빌드 + falsifiable stale-injection paired probe.** 유닛의 selected-flag를
    건드리지 않고 선택 배열에 직접 가짜 stale을 주입(dec 경로가 개입 불가한 상태)한 뒤 재시작 →
    **원본 `NEWGAME_STALE_CLEARED`, v8 `NEWGAME_STALE_PERSISTED`(H-NEWGAME-INIT 런타임 최초 실증), v9
    `NEWGAME_STALE_CLEARED`**(사전 등록한 세 갈래 그대로 확정). v9 S1/S2/S4 회귀 `PASS_NO_STALE_TAIL_
    EFFECT`, 크래시 0. `make check` 1122 passed·5 skipped, `SAFETY_PASS`/`CONTEXT_PASS`. 호출자 gdb
    귀속(핸드오프 ②)은 work 판단으로 생략(세 호출자 모두 동일 hook을 타 정확성과 무관, 핸드오프 자신이
    "귀속은 증거용"이라 명시 — middle이 동의 안 하면 다음 lap 보강). **다음은 middle이 이 새 runtime
    증거로 (F)/S3 재검수.** 상세
    `docs/history/laps/20260928_lap753_work_g5_f_s3_v9_newgame_init_falsified_confirmed.md`.
- [ ] **2026-09-29 00:59 사용자 판단(AskUserQuestion):** G5 v9 milestone **보류**. 추가 확인 항목: **(1) 부대 미지정 드래그 50기 선택이 저장/로드 후 50기 전부 복원**(현재 앞 20기만; 원본 세이브 형식과 양방향 호환 유지 조건 — 원본 EXE가 v10 세이브를 열어도 크래시 없이 앞 20기, v10이 원본 세이브를 열어도 정상), **(2) 미니맵 우클릭 이동과 특수능력 v를 실제로 동작하는 조건에서 원본20/후보50 paired 확인**(격리 환경에서 미니맵이 검게 그려지고 무반응인 원인 — 렌더/입력 좌표/미니맵 활성 조건 — 을 찾고, v는 설명서·툴팁·대상 조건 탐색). 멀티·초기메뉴 경로는 알려진 제한 유지. G1 재개 금지. 진행: work가 (1)을 먼저 구현(v10: 21~50번째 엔트리를 저장 창 안의 미사용 영역 또는 세이브 파일 뒤 추가 블록에 보존, 로드 시 복원) → paired 재측정 + 회귀, 그 다음 (2). 끝나면 middle 재검수 후 사용자 재상정.
  - [x] 처리(lap756 work, Sonnet5): **(1) 구현+런타임 3-way PASS.** v10이 각 save/load 루프의
    "레거시 미러 호출부가 아닌, 진짜 마지막 block-transfer 호출"(`0x00440F1E`/`0x004412EE`, 그 뒤는
    fclose 등가+return뿐임을 디스어셈블로 확인) 뒤에 magic+전체 50슬롯 배열 트레일러를 추가 —
    `fread`(=`STREAM_LOAD_FN`, 원본 CRT 그 자체)의 표준 short-read로 magic 유무를 판별해 신규/구형
    포맷을 가른다. 자체 save→load(count 50/50 전부 복원), 원본EXE→v10세이브 로드(크래시0·레거시20
    정상), v10→원본세이브 로드(크래시0·앞20+21~50zero, 기존 v7~v9와 동일) **전부 PASS**. 개발 중
    scratch 배치를 `.rsrc`(W 아님)에 뒀다가 로드 시 크래시 1회 발생 → `.data`의 기존
    `STORAGE_END` 여유 공간으로 이동해 해소. `make check` 1131 passed·5 skipped, `SAFETY_PASS`.
    **다음은 middle의 (1) 독립 재검수 또는 work의 (2) 착수.** 상세
    `docs/history/laps/20260929_lap756_work_g5_v10_saveload_full50_restore_confirmed.md`.
- [ ] **2026-09-29 09:55 운영자 지시(lap756 v10 수용, 다음 work):** 기준 후보 **v10**. work가 이어서 한 lap에: ① v10 보완 측정 — 부대 미지정 선택 count 중간값(예: 25, 35) 저장/로드, 부대(Ctrl+숫자)와 섞인 상태 저장/로드, v10 핵심 회귀 1회(드래그4종·명령·공격·그룹·사망후호출·R3·Shift). ② 사용자 항목(2) 착수 — 미니맵이 격리 환경에서 검게 그려지는 원인(렌더 옵션/미니맵 토글 키/시야·탐색 상태)을 찾아 미니맵 우클릭 이동을 원본에서 먼저 작동시키고 원본20/v10 50 paired, 특수능력 v는 설명서·툴팁 텍스트로 대상 조건 확인 후 paired. 끝나면 middle이 v10 전체 재검수.
  - [x] 처리(lap757 work): ①의 중간값(25/35)·부대혼합 save/load 신규 probe로 전부 PASS(상세
    `docs/history/laps/20260929_lap757_work_g5_v10_partial_squad_saveload_pass.md`). "핵심 회귀 1회"는
    v9→v10 diff가 저장/로드 hook 2곳+cave로 pytest 고정돼 있고 v9가 이미 A~H 통과했다는 근거로 work가
    범위를 저장/로드 인접 항목으로 좁혀 미착수(필요시 middle 지시로 다음 lap 보강). **다음 work는
    ② 미니맵/능력v 착수 또는 middle의 (1) 전체 재검수.**
- [ ] **2026-09-29 10:35 운영자 지시(lap757 후속):** 이번 work는 **사용자 항목 (2) 미니맵 우클릭·특수능력 v만** 한 lap에 집중(v10 회귀는 diff가 저장/로드 hook 한정이라 middle 최종 검수 때 1회로 충분). ① 미니맵: 격리 환경에서 검게 그려지는 원인 규명(미니맵 토글 단축키·옵션 메뉴, 탐색/시야 상태, 렌더 경로), 원본에서 미니맵 우클릭 이동이 되는 조건을 먼저 만들고 원본20/v10 50 paired. ② 특수능력 v: 설명서·툴팁 텍스트로 기능과 대상 조건 확인(적/아군/지면/건물), 조건 충족 fixture로 원본20/v10 50 paired. 원본에서도 구조적으로 불가하면 그 근거를 명확히 기록.
  - [x] 처리(lap758 work, 부분): ② "V"=수확(raw btn 0x05)·"F"=옮기기(raw btn 0x06, 우클릭 시
    `+0x290` 1→3 실측 확인)를 게임 자체의 클릭-후-라벨 표시로 직접 확정. "V"의 정확 발주 대상은
    미확정(밭 타일 5회 시도 무반응), "I"는 이 국가 fixture에 없음(미확인, 다른 국가 필요). ① 미니맵은
    참고 저장소 `Syw2plus_re`(read-only)도 원본 렌더 함수를 못 찾았다는 독립 negative 증거만 확인,
    실행 증거 추가 없음 — 후보 주소 `0x451C12`/`0x451C19`/`0x4F2E8B`(cafe 커뮤니티 실측) 실측은 다음
    work. 상세 `docs/history/laps/20260929_lap758_work_g5_ability_v_identified_minimap_provenance.md`.
  - [x] 처리(lap759 work): ① lap758이 제안한 "`0x451C12`/`0x451C19` 실시간 읽기"의 전제를 objdump
    정적 확인으로 반증(그 두 주소는 `mov [ecx±],imm32`의 피연산자 내부 상수 바이트 — 실행 무관하게
    항상 0/509). 전수 xref로 진짜 타겟(`0x451130`/`0x451C10`, this=정적주소 `0x639350`)을 찾아 gdb
    전수 진입 trace(신규 `tools/g5_minimap_init_breakpoint_probe.py`)로 프로세스 시작→메뉴→솔로
    로비→인게임→미니맵 클릭/키 전체 세션 관찰 — **둘 다 1회씩 호출 확인(PASS)**: 미니맵 위젯은
    완전 비활성이 아니라 새 게임 시작 시 실제 초기화됨(기존 새게임초기화 `0x892410` 코드 영역과
    동일). 렌더 진입점은 여전히 미발견(별개 질문). "V" 정확 대상(a)·"I" 국가(b)는 미착수. 상세
    `docs/history/laps/20260929_lap759_work_g5_minimap_widget_ctor_live_trace.md`,
    `analysis/memory_maps/g5_minimap_widget_ctor_lap759.md`. **다음 work:** `0x639350`/`0x639354`
    재읽어 값 변화 확인, 또는 (a)/(b) 착수.
- [ ] **2026-09-29 11:25 운영자 지시(항목 2 가속, 구현 우선):** 정적 추적을 줄이고 실측으로 간다. ① **수확(V=0x05)**: 일꾼 선택→V→자원(밭/나무 등 lap729 gather에서 채집이 된 타일)을 좌클릭, 원본20/v10 50 paired로 pending 수신 수 측정(원본 먼저 성공 조건 확보). ② **미니맵 검은 화면**: 원본 폴더의 `ddraw.dll`(2.3MB, DirectDraw 래퍼 추정)이 격리 사본에서 실제로 로드되는지(`WINEDLLOVERRIDES=ddraw=n,b`)와 미니맵 렌더 차이를 캡처로 비교 — 래퍼로 미니맵이 그려지면 그 상태에서 미니맵 우클릭 이동 원본20/v10 50 paired. 래퍼로도 안 되면 미니맵 클릭 입력 핸들러(미니맵 영역 좌표→월드 변환→이동 명령)를 브레이크포인트로 확인. 둘 다 한 lap 안에 원본 성공 조건을 못 찾으면 근거와 함께 UNKNOWN 유지 판단을 기록.
  - [x] 처리(lap760 work): **① PASS** — 랜덤 국가 일꾼 unit_type이 op=5 fixture의 고정
    allow-list와 5회 충돌(`unsupported_army_fixture_type`, 새 결함 아니고 lap730 기존 관측 재확인)
    한 뒤, 이미 검증된 private fork `patches/population/g5_c_repair_bridge.c`(고정 allow-list
    대신 구조적 게이트만 사용, 공유 G2-pinned `runtime_bridge.c` 무변경)로 브리지 소스를 바꿔
    해소 — 원본20/20·v10 50/50 전원 V-버튼+좌클릭 채집 pending 수신 PASS. **② 부정 결과(UNKNOWN
    유지)**: native ddraw.dll override 3변형 전부 렌더/클릭 신호 없음, 원인이 아님을 반증. 크래시0,
    `source_unchanged` 전부 true. `pytest -ra` 1131 passed·5 skipped, ruff/mypy/compileall/
    `CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 상세
    `docs/history/laps/20260929_lap760_work_g5_item2_harvest_v_pass_minimap_ddraw_negative.md`.
    **다음 work:** 미니맵 클릭 입력 핸들러 브레이크포인트 조사 계속, 또는 lap758 잔여(V 정확
    대상·I 국가) 착수. 그 다음 middle이 항목(1)+(2) 전체 독립 재검수.
- [ ] **2026-09-29 12:37 운영자 지시(lap761 후속, 미니맵 마지막 1 lap):** 수확(V) paired PASS(원본20/20, v10 50/50) 수용. ddraw 네이티브 override는 미니맵 원인 아님(반증). 다음 work 1 lap 한정: 미니맵 클릭 입력 핸들러 — 미니맵 화면 영역 클릭 시 호출되는 함수(마우스 좌표→미니맵 영역 판정→월드 좌표 변환→이동/카메라)를 브레이크포인트로 찾고, 원본에서 입력이 도달하는지 확인. 도달하면 그 경로의 명령 발행이 선택 전원(원본20/v10 50)에 가는지 paired, 렌더와 무관하게 입력만 살아있으면 PASS 가능. 도달하지 않으면(격리 환경에서 미니맵 입력 비활성) 근거를 남기고 **UNKNOWN 확정**. 그 다음 middle이 사용자 항목 (1)+(2)와 v10 전체 재검수(v10 핵심 회귀 1회 포함).
- [ ] **2026-09-29 12:57 운영자 판정(lap762, 미니맵 1 lap 연장 — 원인 위치가 3지점으로 좁혀짐):** 미니맵 입력은 WM 핸들러 enqueue(24회)·라우터 dequeue까지 도달, 히트테스트 `FUN_004516A0`는 0회. 다음 work 1 lap: 필터 3지점(`0x41e332` 버튼타입, `0x41e365` 좌표 sentinel, `0x41e43d call 0x41c450` 게이트)에 브레이크포인트로 어느 분기에서 떨어지는지 확정. 격리 환경 탓(예: 게이트가 창 포커스/미니맵 표시 플래그를 요구)이면 그 플래그를 브리지로 켜서 원본 미니맵 우클릭 이동을 성립시킨 뒤 원본20/v10 50 paired. 이번 lap에서도 성립 못 하면 **UNKNOWN 확정·원인 지점 기록**하고 middle 재검수로 넘어간다(추가 연장 없음).
  - [x] 처리(lap763 work): 3지점 개별 브레이크포인트로 `0x41e332`/`0x41e365`는 무해한 커서-아이콘
    분기(히트테스트 호출과 무관)임을 확정하고, 유일한 실제 게이트 `call 0x41c450`이 관측 9430회
    전부 `eax=0x0` 반환함을 실측. 게이트 조건을 분해해 `0x97597c`(로비 "게임 타입" 전역
    `0x975914==3`일 때만 새게임초기화가 1로 씀, `0x975914`는 로비 UI 접근자 `0x4ced40`의 반환값)가
    원인임을 정적으로 추적. **`0x97597c`를 격리 사본에서 진단 write로 1로 강제하자
    `FUN_004516A0` 호출이 0→6232회(성공4195/실패2037)로 급증** — 미니맵 서브시스템이 죽은 게
    아니라 이 게이트 플래그가 잠가놓았을 뿐임을 실증(12:37 지시의 "성립하면 강제로 열어라" 조항
    충족, "성립 못 하면 UNKNOWN" 조항은 미적용). fixture 명령효과(`pending_xy`)까지는 미측정.
    제품 코드 0 변경(진단 도구 2개 수정), `source_unchanged` 2/2, 크래시0. 상세
    `docs/history/laps/20260929_lap763_work_g5_minimap_router_gate_flag_confirmed.md`,
    `analysis/memory_maps/g5_minimap_router_gate_lap763.md`. **다음 work:** fixture 유닛으로
    강제 플래그+베이킹된 미니맵 픽셀 우클릭 원본20/v10 50 명령효과 paired, 또는 원본 로비 UI에서
    `game_type==3`이 사람이 고를 수 있는 정상 옵션인지 확인. 그 다음 middle이 항목(1)+(2)+v10
    전체 재검수.
- [ ] **2026-09-29 14:33 운영자 지시(lap765 HOLD 후속, work):** G5 v10 Shift 단일추가 `2→0`/제거 `0→1`은 원본20 vs v10 50 **paired**로 먼저 대조한다(G5 전용 격리 runtime만). 사용자가 G2 Shift+클릭 추가 회귀를 Codex로 **별도 조사 중**이므로 `local/runtime/g2_*`·`g2shift*`와 G2 패치 소스는 건드리지 않는다. 원인이 G2 기반 공통이면 증거만 기록하고 G2 수정은 하지 않는다. 원본도 같으면 하네스 클릭 계약만 최소 수리.
  - [x] 처리(lap766 work): 동일 `g5_command_coverage_probe` 계약으로 원본20/v10 50을 fresh paired 실행했다. 양쪽 모두 Shift 추가 `1→2`, 제거 `2→1`, anchor 제거·잔여 anchor 유지·잔여 명령 배제 PASS; 원본20/20·v10 50/50, `source_unchanged`·cleanup PASS. 초기 `PYTHONPATH` 누락 import 실패는 실행 래퍼 오류로 보존했고, 수정된 명시적 v10 바인딩 실행은 `make check` 1134 passed·5 skipped까지 통과했다. 제품/G2 코드 변경 없음. 다음은 새 middle의 독립 raw 재검수이며 G5 종료/G1 재개는 금지한다.
- [x] **2026-09-29 15:16 사용자 G5 v10 3단 보류(lap767 PASS_WITH_LIMITS 재상정 후, lap768/769 처리):** 사용자 질문 "미니맵 어택땅 같은건 먹히냐". 미검증이다. work가 lap764 미니맵 probe(진단 gate 동일 조건, 55기 fixture)를 확장해 **원본20 vs v10 50 paired**로 미니맵 대상 명령을 측정한다: ① 공격 버튼/단축키(A)→미니맵 좌클릭(어택땅) ② 이동 버튼/단축키→미니맵 좌클릭 ③ 순찰→미니맵 좌클릭. 지표: 선택 전원 command 필드·pending_xy 변화 수, 명령 종류가 공격/이동/순찰로 원본과 같은지, 크래시0, source 불변. 원본에서도 안 먹히면 N/A로 기록. 결과 후 middle 재검수→사용자 재상정. G2 영역(`g2_*`,`g2shift*`) 금지 유지.
- [x] **2026-09-29 사용자 이전 순서 결정(18:4x 최신 지시로 대체):** G5 사용자 승인 후 **G2(전비5000 배포 빌드) 전체 점검**을 먼저 하고, 그다음 G1. G2 점검은 G5 A~H 체크리스트 방식으로 원본 대비 paired 실측: 드래그/ALT/Ctrl/Shift 선택·20기 부대, 이동/공격(교전)/정지/홀드/순찰, 미니맵, 생산→UI 집결지 지정(장수 포함), 창모드(DxWnd) 스크롤, 대량 유닛 틱 안정성, 저장/로드, 자연 등용 장수 초상화, 멀티(가능 범위). Shift+클릭 단일추가는 사용자가 Codex로 별도 조사 중 — 그 결과와 합치고 `g2_*`/`g2shift*` 디렉터리는 건드리지 않는다.
- [x] **2026-09-29 18:4x 사용자 지시(최신, 이전 순서 대체; 18:45 lap769 PASS_WITH_LIMITS로 적용 완료):** G5 재상정 질문 금지. lap769 PASS_WITH_LIMITS면 G5 종료(APPROVALS 사전 승인) → **다음은 G1**(1600×1200 원본 화면 구성) 착수. G2 전체 점검은 삭제가 아니라 G1 뒤로 순연(사용자가 별도 지시하면 앞당김). lap769 FAIL/HOLD면 G5 수정 우선.
- [x] **2026-09-29 18:45 운영자 지시 "G1 재착수 전략 1회" 처리(lap770 strategy, Claude Code `claude-opus-5-5`):**
  새 경로 **W60 = 논리800 유지 + 렌더러 `0xE5BF18` 픽셀 프리미티브 2배 미러 재그리기 + content-keyed present +
  입력 1/2**를 채택하고 work 카드 `docs/work/active/G1_STRATEGY_W60_MIRROR2X_COMPOSITOR_LAP770.md`를 발행했다.
  이전 `BLOCKED(attribution)`의 원인(caller 주소 `0x0049273F`가 메뉴 present였음, N224)과 whole-frame 2배 구조
  한계(N223)를 둘 다 넘는다. 다음 work가 S1(섀시·입력 parity)→S2(스프라이트 blit 미러, 오라클=nearest 2배 일치)
  를 구현·실측한다. G1 완료·사용자 승인 아님. 상세 `docs/history/laps/20260929_lap770_strategy_g1_w60_mirror2x_compositor.md`.
- [ ] **2026-09-29 19:28 운영자 힌트(lap771 G1 W60 r4 미니맵 `FAIL_NO_EFFECT`):** lap763/764에서 **원본도** 미니맵 클릭은 `call 0x41c450` 게이트(`0x97597c`, game_type==3 계열)로 닫혀 hit-test 0회·효과 없음이 확인됐다. 따라서 W60 미니맵 FAIL은 W60 회귀가 아닐 수 있다. 먼저 동일 fixture/입력으로 **원본(W60 off) paired** 미니맵 카메라 결과를 확인하고, 원본도 no-effect면 이 항목은 원본 parity(N/A)로 처리하거나 lap764처럼 진단 gate write를 양쪽에 동일 적용해 비교한다. W60 on/off 차이만 회귀로 본다.
- [ ] **2026-09-29 20:11 운영자 지시(G1 W60 반복 속도):** lap771~773이 work 1회 runtime 실패 → 즉시 ESCALATE → middle 재검수 → work 순환을 반복해 진척이 느리다. middle은 lap773 인계가 "수리 대상이 명확한 구현 결함"이면 재측정 없이 짧게 확인만 하고 work로 넘긴다. **work는 한 lap 안에서 구현→격리 실행→원인 확인→수정을 최소 3회 반복**한 뒤에만 ESCALATE한다(예상 밖 증거 충돌·마일스톤 경계·안전 위반은 즉시 ESCALATE 유지). 이번 대상: native 1600 self-source present 귀속(converted=0), live primitive metrics 미출력, 미니맵은 진단 gate=1을 off/on 양쪽 동일 적용해 paired.
- [ ] **2026-09-29 22:01 운영자 힌트(lap777 PS7 로비 입력 실패):** lap777에서 메뉴(PS9/PS7)가 처음 2배 변환됐다(converted 739). 이전 lap들은 메뉴가 좌상단 800×600이라 하네스 메뉴 클릭이 논리 좌표로도 맞았을 수 있다. 1순위 가설: 메뉴가 1600으로 올라온 뒤 하네스 메뉴 클릭 좌표(또는 bridge의 1/2 환원 적용 범위)가 PS7에서 어긋남. middle은 raw의 PS7 클릭 physical/logical 좌표만 확인해 짧게 work로 넘기고, work는 loop.sh 새 규칙(추적 가능한 결함은 3회까지 수정→재실행)으로 PS3·tick≥300·off/on paired까지 완주한다.
- [ ] **2026-09-30 00:38 운영자 결정(G1 "production mapping" blocker):** 이 blocker는 사용자 승인 대상이 아니라 **하네스 미해결 항목**이다. `tools/runtime_env.py:1924 _g1_production_click_if_authorized`가 인게임 명령패널 `production(670,490)` 셀의 primary 필드/action·worker 매핑을 모른다는 이유로 클릭을 거부한다. 사용자 승인을 기다리지 말고 루프가 해소한다: 원본에서 해당 셀이 어떤 버튼인지(G5 lap758/760의 일꾼 명령패널 V=Harvest·F=Move 레이아웃 근거 참고) 원본 fresh run으로 확정해 매핑을 코드/테스트에 고정하고, 원본·W60 off/on에서 같은 클릭의 효과를 paired로 측정한다. 확정 불가면 production 단계를 원본 parity 기준 N/A로 명시하고 나머지로 판정. "승인 부재"를 G1 HOLD 사유로 반복 기록하지 않는다.
- [ ] **2026-09-30 02:1x 사용자 결정(최신, 우선순위 변경): G2 점검을 G1보다 앞당긴다.** 대상: `../260921_temp/`의 `[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092.exe`(SHA 83c7df80…) 및 `..._시작자리고정_G2_개인500_공용4092.exe`(SHA 1bdcadf9…), 소스 `patches/population/g2_esl2608_{pool4092_owner500,supply1500_500_5000}.py`. 목표: 두 EXE를 **ESL2608 비패치판(같은 AI상점개설·장수7명 계열) 대비** 체크리스트로 격리 실측해 버그를 찾고, 고친 뒤 **새 이름**의 수정판 EXE 2개를 `../260921_temp/`에 생성(기존 파일 덮어쓰기 금지, 독점 생성+SHA+읽어주세요 txt). 체크리스트: 드래그/ALT/Ctrl/Shift 선택·**Shift+클릭 단일 추가(사용자 실플레이 신고, 20기 초과·부대 선택 상태 포함)**·20기 부대, 이동/공격(실교전)/정지/홀드/순찰, 미니맵(원본 gate parity), 생산→**UI로 집결지 지정**(장수 포함), **창모드(DxWnd) 스크롤**(새 EXE 파일명 프로필 누락 가설), 저장/로드(구 세이브 포함), 대량 유닛·고슬롯 초상화, 장기 tick 안정성, 멀티(가능 범위). `local/runtime/g2_*`·`*g2shift*`(사용자 Codex 작업) 디렉터리는 건드리지 않는다. G1 W60은 lap785 결과를 `docs/history/20260930_lap785_g1_paused_escalate_sol.md`에 보존하고 일시중단 — G2 수정판 전달 후 middle 재검수부터 재개.
- [x] lap786 전사 오류 처리·lap802/803/804 G2 Phase C·D·17:0x G1 production cell 힌트(lap816 `UNKNOWN(original parity)`)·lap908 middle 색인 원문은
  `docs/history/20261004_inbox_lap914_precompaction.md`에 byte-exact 보존(전체342줄, SHA256 `c8202281b74db18593ed189eb96d48faec7c0fa7904391c77b9f1e8067995546`). 체크 완료 항목이며 새 지시 아님.
- [ ] **2026-09-30 03:48 운영자 힌트(lap788 G2 candidate anchor 0):** 9/26 실측(`docs/history/laps/20260926_direct_g2_esl2608_supply1500_500_5000_two_variants.md`)에서 같은 두 후보는 시작 시 player `count=2, used=20, count_cap=500`, **HQ slot4092**로 정상 관측됐고, 그 probe(`../temp/Syw2plus_patch/g2_esl2608_20260926/high_slot_normal_production_roundtrip_probe.py`)는 relocated pool을 올바른 base/stride로 읽었다. lap788 probe의 "relocated/stock 둘 다 live owner0 0개"는 제품 결함 전에 **9/26 probe의 pool base·stride·live 판정·슬롯 범위(4092 근처 고슬롯)와 대조**해 하네스 읽기 오류인지 먼저 가린다. 대조 후에도 0이면 그때 제품 결함 후보로 승격.
- [ ] **2026-09-30 06:08 운영자 힌트(lap792 G2 Phase C 집결지 UI 미확정):** 같은 UI 좌표 추측을 반복하지 말고 **정적 역추적**으로 입력 계약을 찾는다: ESL2608 baseline EXE에서 건물 집결 필드 `+0x654/+0x656`에 **쓰는 코드(xref)**를 찾아 그 호출 경로의 명령 ID/버튼 셀/단축키·마우스 버튼 조건을 확정한 뒤 그 입력으로 실측한다(G5 때 미니맵 라우터를 역추적한 방식). 장수 생산 버튼 활성 조건도 같은 방식으로 명령패널 활성 판정 함수에서 찾는다. 사용자에게 조작법을 물어 둔 상태이며 답이 오면 INBOX에 추가한다. 확정 불가 시 원본 parity N/A로 두고 나머지 체크리스트(미니맵·창모드 스크롤·저장/로드·교전·고슬롯 초상화)로 진행.
- [ ] **2026-09-30 운영자 처리(lap793 승격):** lap792 첫 raw는 사전수리 실패로 제외(lap792 기록 정정). lap793 handoff(`docs/history/20260930_lap793_escalate_sol_archive.md`)의 2·3번을 work가 바로 수행: baseline EXE에서 HQ `+0x654/+0x656` writer xref와 장수 `+0x980` writer/명령패널 활성 경로를 정적 추적해 입력 계약 고정 → 현 스키마로 normal baseline fresh 1회(worker 2→3·rally 변화·hero) → 성공 시 4-way Phase C. 확정 불가면 N/A로 두고 다음 체크리스트(미니맵·창모드 스크롤·저장/로드·교전)로 진행.
- [ ] **2026-09-30 07:2x 운영자 지시(G2 Phase C 집결지 시간상한):** 집결지 UI 입력은 lap792~794 3회 work로도 미확정이다. middle(lap795)은 `+0x654/+0x656` writer xref를 **정적으로 1회** 확정해 입력 계약을 제시하고, work는 그 계약으로 **1회만** fresh 확인한다. 그래도 필드가 안 바뀌면 집결지 UI는 `UNKNOWN(입력 계약 미확정, 사용자 조작법 문의 중)`으로 기록하고 **Phase D(미니맵·창모드 스크롤·저장/로드·교전·고슬롯 초상화)로 넘어간다.** 장수 생산 셀 `(704,540)`·worker 생산은 확인됐으니 4-way 생산 parity(집결지 제외)는 Phase D와 함께 수행한다.
- [ ] **2026-09-30 08:0x 운영자 판정(lap796 집결지):** 입력 계약은 **확정**이다(slot3 `(776,503)`→action `0x15`→지도 좌클릭→writer `ecx`=HQ slot1199). 필드 불변 원인은 목표점 `(450,300)`→월드 `(92,54)`가 HQ 자리와 겹친 것뿐이다. middle 재검수 없이 work가 **HQ에서 충분히 떨어진 목표점**(HQ 월드좌표와 다른 좌표, 이동 가능 지형)으로 같은 절차를 수행해 `+0x654/+0x656` 변화→생산 유닛(일꾼·장수 `(704,540)`)의 집결지 도착을 normal baseline에서 확인하고, 성공하면 같은 lap 안에서 4-way(normal/fixed_start × baseline/candidate) Phase C를 완주한다. 이전 handoff는 `docs/history/20260930_lap796_escalate_sol_archive.md`.
- [ ] **2026-09-30 09:58 운영자 지시(G2 hero 시간상한):** hero UI 생산 fixture는 lap799~800에서 5회 시도에도 prerequisite 보유 캐시(`PlayerStruct+0x315C[37]=0`) 계약이 안 잡혔다. 더 fixture를 파지 말고 **정적 판정으로 닫는다**: (a) 생산 완료 시 신규 유닛에 HQ 집결지(`+0x654/+0x656`)를 적용하는 코드와 hero 생성 경로가 같은지/다른지를 baseline에서 xref로 확정, (b) G2 후보의 변경 바이트 범위가 그 경로(hero 생성·rally 적용)를 건드리는지 diff로 확인. 안 건드리면 hero 집결지 동작은 **원본 parity(G2 무관)**로 기록하고, 원본에서 hero가 rally를 안 따르는 구조면 그 사실을 사용자 신고("장수 생산 시 집결지로 안 감")의 원본 동작 설명으로 남긴다. 그 다음 바로 **DxWnd 창모드 스크롤**로 넘어간다.
- [ ] **2026-09-30 10:3x 운영자 판정(lap801 DxWnd):** Wine에서 DxWnd `/r:1`이 대상 EXE를 띄우지 못해(메모장 대조는 성공) 실측은 `BLOCKED(env)`. 대신 정적 근거: 사용자 배포 `[ESL]Syw2plus/dxwnd/dxwnd.ini`의 프로필은 `path0=...\[ESL]Syw2plus 2603.exe` **특정 파일명 1개**에만 걸려 있다. DxWnd는 경로/파일명으로 대상을 매칭하므로 G2 새 파일명(`...G2_개인500_공용4092.exe`)은 이 프로필(CLIPCURSOR 등 창모드 커서 가두기 flag)을 받지 못해 창모드 가장자리 스크롤이 약해지는 것이 가장 유력한 원인(EXE 코드 결함 아님). 조치: 수정판 배포 시 읽어주세요에 "DxWnd에 새 EXE를 프로필로 추가(또는 기존 프로필 경로를 새 EXE로 변경)" 안내를 넣고, 가능하면 새 EXE용 프로필 항목 예시를 동봉. DxWnd 항목은 이것으로 닫고 **hero 정적 판정(INBOX 09:58) → 미니맵·교전·고슬롯 초상화**로 진행. 멀티는 마지막에 짧게.
- [ ] **2026-09-30 12:4x 운영자: G2 점검 종료 → G1 재개.** G2 ESL2608 두 EXE 체크리스트는 lap788~806으로 마감(보고서 `docs/work/G2_ESL2608_CHECK_REPORT_20260930.md`, 제품 결함 미발견, EXE 재생성 없음, DxWnd 안내 txt만 신규). 남은 G2 UNKNOWN(hero runtime)·BLOCKED(env)(DxWnd·멀티)는 보고서에 유지. 이제 **G1 W60 재개**: `loop/ESCALATE_SOL`에 복원한 lap785 인계(`docs/history/20260930_lap785_g1_paused_escalate_sol.md`)부터 middle이 검수한다. lap785 이후 G1 소스는 G2 작업 중 변경되지 않았는지(g1_mirror2x.c·direct_draw_trace.c·runtime_env G1 경로) 먼저 확인.
- [ ] **2026-09-30 22:2x 사용자 결정(G1 목표 범위):** G1 완료 기준 = **"고해상도 그림까지"**. 즉 단순 2배(nearest) 출력으로 마감하지 않고, W60 mirror가 유닛 스프라이트뿐 아니라 **지형·타일·HUD 등 화면 전체의 그리기 경로**를 덮어(현재 covered 최대 ~27%) 원본 구성 그대로 1600×1200에서 **2배 해상도 그림**을 그릴 수 있어야 한다. HD 그림의 출처는 전략이 정한다: (a) 원본 스프라이트를 로드 시 알고리즘 업스케일(xBRZ/hqx/ESRGAN류, 결정적·오프라인 변환 가능)해 HD 세트를 자동 생성, (b) 사용자 제공 HD 자산 슬롯. (a)를 기본 경로로 검토하되 원본 파일은 읽기 전용, 생성물은 별도 경로. 입력·게임 로직은 800 논리 좌표 유지. production/minimap UNKNOWN은 원본 parity로 두고 진행.
  - [x] 처리(lap819 strategy): HD 출처 기본 = (a) 원천 프레임 단위 **Scale2x(팔레트 인덱스, 새 색·의존성 없음)**, (b) `SYW2_G1_HD_PACK` 사용자 슬롯(xBRZ/ESRGAN류는 32bpp/양자화 필요로 이 슬롯으로만). 화면 전체는 W70 P1 writer census→P2 identity 치환→P3 Scale2x→P4 지형→P5 HUD→P6 색조/P7 텍스트 순. 카드 `docs/work/active/G1_STRATEGY_W70_FULLSCREEN_HD_LAP819.md`, 다음 work=P1. **G1 사용자 3단 기준 미충족·승인 전.**
- [ ] **2026-10-01 01:0x 운영자 지시(동시 세션):** 사용자의 별도 Claude 세션이 같은 저장소에서 **G5→ESL2608 G2 이식**을 진행 중이다(`patches/selection/g5_esl2608_g2_port.py`, `tools/g5_esl2608_port_probe.py`, `patches/selection/test_g5_esl2608_g2_port.py` 등 `*g5_esl2608*`). 루프는 이 파일들과 그 세션의 runtime/산출물을 **읽기·수정·삭제·정리하지 않는다**. `make check`가 그 세션의 작업 중 파일 때문에 실패하면 루프 결함으로 오인하지 말고, 실패가 그 파일에 국한됨을 확인한 뒤 G1 관련 파일 SHA를 고정해 재실행하거나 G1 targeted+lint/typecheck 근거로 기록한다(사용자 결정: 루프 계속).
- [ ] **2026-10-01 09:3x 운영자(문서 한도):** STATUS 130/130, APPROVALS 249/250(소프트 한도 직전). 다음 lap은 기록을 추가하기 **전에** STATUS·APPROVALS 원문을 `docs/history/`에 SHA와 함께 보존하고 압축한다(현재 G1 W70 판정·blocker·다음 한 가지·사용자 결정 줄은 유지).
- [ ] **2026-10-01 13:0x 운영자(문서 한도):** STATUS 130/130. 다음 work lap은 기록 추가 **전에** STATUS 원문을 `docs/history/`에 SHA와 함께 보존하고 70줄 이하로 압축한다(현 G1 W70 P2 HOLD 판정·blocker·다음 한 가지·사용자 결정 유지). 넘기면 safety STOP.
- [ ] **2026-10-02 lap847 middle 검수(사용자 지시가 아닌 기술 판정):** lap844 P3 partial 증거는 재확인했으나
  trace 시간값0x9B5210을 게임 tick rate로 수용한 근거가 실제0x8924B8 snapshot과 충돌한다. 기존 행동 구간
  후보 rate delta −38.87/−38.50/−39.71%, P3 gate HOLD·ESCALATE_SOL 이관, P4 전환 없음. 현재 큐는 STATUS만 따른다.
  상세 `docs/history/laps/20261002_lap847_middle_g1_w70_p3_performance_conflict_escalate.md`.

- [ ] **2026-10-02 lap848 일반 middle 기술 확인(사용자 지시 아님):** 기존 trace 시간값과 실제 sim tick
  불일치 및 rate delta−38.50~−39.71%를 독립 확인했다. 사용자 stop 조건으로 즉시 승격 인계, 구현0.
  현재 큐는 STATUS만 따르며 근거/수리안은 `docs/history/laps/20261002_lap848_middle_g1_p3_conflict_confirmation_handoff.md`.
- [x] lap851(P3 성능 FAIL 재판정)·lap853(P3b compose env 조회 결함) strategy 판정 원문은 `docs/history/20261003_inbox_lap911_precompaction.md`에
  byte-exact 보존(전체345줄, SHA256 `03363aa81a0ae8c277e5b17dae24aaf3b7e6bf7bdcc5f5846d27aea14805ef2c`). lap858 P3 통합 수용으로 종결된 계보이며 새 지시 아님.
- [ ] **2026-10-02 lap858 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap855·857 P3 gate 재승격 순환 해소):**
  P3c 2단은 lap855(성능·latch·source·입력)와 lap857(validator 수리) middle 검수의 합으로 **`PASS(partial)` 통합 수용**한다
  (이 세션이 SHA·validator·5049 present 부등식·tick ratio/p95를 다시 계산해 일치 확인). **W70 P단계 전환은 마일스톤 경계가
  아니다** — middle이 직접 PASS/HOLD를 판정하고 `ESCALATE_SOL`은 미설명 실패·근거 충돌·G1 사용자 제출 경계에만 쓴다.
  지형은 같은 렌더러 `0xE5BF18`의 blitter 5종(`0x468C30`·`0x468CC0`·`0x468E10`·`0x468F00`·`0x4690A0`)이 직접 그리므로 **P4
  `FEASIBLE`(정적, 실행 미검증)**, 구조 판정 회차 없이 다음 work가 구현한다. 현재 유효 HD coverage는 PS3 프레임 p50 6.23%다.
  기준 §3.5·validator 불변. 카드 `docs/work/active/G1_STRATEGY_W70_P4_TERRAIN_BLITTER_HD_LAP858.md`, 기록
  `docs/history/laps/20261002_lap858_strategy_g1_w70_p3_accept_p4_terrain_card.md`. 계획 승인·G1 마일스톤 아님.
- [ ] **2026-10-02 lap863 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap862 P4 `<30%` 승격 해소):**
  `<30%`는 지형 귀속 반증이 **아니다**. 같은 raw에서 키 전 고정 카메라 유효 coverage는 68.4~70.6%다. 스크롤 뒤 결손은 원본
  `0x4324E0`이 지형 캐시 `0xBA3D30`(832×512)을 `memmove`(`0x4DB1D0`, 호출 8곳)로 밀고 새 띠만 다시 그리기 때문이며, 캐시→화면은
  `0x41BF20`의 `0x466280`이 매 프레임 복사한다. **P4 `FEASIBLE` 유지**, 다음 work 1 lap = **P4b**(gdb 없는 스크롤 pair·lane 동일
  키 순서로 하네스 수리 → 캐시 층 미러 구현 → 고정+DOWN+RIGHT 측정, 수리 ≤3회). DOWN lane 불일치는 하네스 귀속 유력(가설),
  PS3 census는 선행 조건 아님(PS3 한정 snapshot opt-in만 허용). 기준·validator 불변. 카드
  `docs/work/active/G1_STRATEGY_W70_P4B_TERRAIN_CACHE_LAYER_LAP863.md`, 주소
  `analysis/memory_maps/g1_w70_p4b_terrain_cache_scroll_lap863.md`, 기록
  `docs/history/laps/20261002_lap863_strategy_g1_w70_p4b_terrain_cache_layer.md`. 계획 승인·G1 마일스톤 아님.

- [ ] **2026-10-02 lap869 일반 middle:** lap868 raw·원본/fixture/DLL·42build SHA MATCH, action24730/24826 일치·final24862 owner6 rice Δ800 독립 확인. 실제 captured 값 차이이나 stable tick은 완료 update phase/atomicity 증거가 아니므로 지속 simulation divergence·원인 UNKNOWN. 사용자 충돌 stop으로 HOLD·승격; work는 tick/rice writer 정적근거→동일 phase 관측+baseline 대조 진단, 게임 직접수정 금지. doctor/focused25/lint/typecheck PASS, full Fast/runtime SKIP. 상세 `docs/history/laps/20261002_lap869_middle_g1_p4b_same_tick_rice_hold_handoff.md`, `loop/ESCALATE_SOL`.

- [ ] **2026-10-02 사용자 후속(현재 세션):** 승격 검수 전에 **읽기 전용 쌀 값 원인 조사만** 진행하는 것을 승인하고, 루프 지속 및 약10분 간격 보고를 요청. 게임/검증 코드 변경·격리 runtime·제품 승인까지 허가한 것은 아니다. 실제 승격 기술검수 요건과 G1 HOLD는 유지한다. 조사 결과는 `analysis/memory_maps/g1_p4b_tick_rice_writer_readonly_20261002.md`와 `docs/history/laps/20261002_operator_g1_p4b_tick_rice_readonly_xrefs.md`.

- [ ] **2026-10-02 승격 기술검수(사용자 지시 아닌 모델 판정):** 별도 OMX Team architect/Codex Sol이 read-only 재계산 후 세 바퀴 정체 해소용 **관측 전용 probe/tests + 격리 진단 runtime만 승인**. baseline-baseline/후보 대조는 완료 경계·all-writer quiescence 증거 후 조건부, B'·G1은 HOLD. 실제 +800은 후보 증가가 아니라 RIGHT→FINAL 기준 baseline rice 감소800/후보 유지로 재계산됨. `docs/history/laps/20261002_elevated_g1_p4b_rice_diagnostic_decision.md` 및 공유 temp task JSON 참조. 다음 work는 STATUS만 따른다.

- [x] **2026-10-02 23:08 KST 사용자 새 승인:** “그 오류 2개에 한해 추가 수리 허”. lap885 raw seq gap 및 no-update return PTID 불일치 false acceptance 두 건의 추가 수리를 명시 허용했다. 이전 Astra 예산 STOP을 이 범위에 한해 override하는 새 사용자 결정이며 자동 예산 리셋/제품 합격이 아니다. 실무 Luna의 두 파일 최소 수리·관련 offline/회귀/Fast 및 새 Sol 독립 검수만 수행, 원본/기준/기존raw/게임runtime/B'/C/P5/커밋 금지. 약10분 보고 지속. **lap886 수리·lap887 독립 offline 수용 및 최종Fast 완료로 이 한정승인 처리 완료**, 새 runtime/제품승인 아님. 현재 큐는 STATUS만 따른다.

## 2026-10-03 사용자 플레이 확인·종료 및 문서 게시 승인

- [x] 사용자가 직접 플레이 후 **G2·G5 달성·종료**를 승인하고 README 반영·GitHub 푸시를 요청했다.
  G2 전비5000·G5 선택20→50을 종료한다. 기존 기술 UNKNOWN/BLOCKED는 보존하되 종료를 되돌리지 않는다.
  새 결함/지시 없이 자동 재개하지 않으며 G1 HOLD/STOP·G3 중단·G4 보류는 유지한다.
  [사용자 원문·한계·문서만 커밋/푸시 범위](G2_G5_USER_COMPLETION_20261003.md).

## 2026-10-03 14:37 KST 사용자 G1 자율 지속 — 최신 상시 지시

- [ ] **사용자 원문:** “아니 걍 G1 달성할 때까지 계속 하라니까? 왜 맘대로 자꾸 허가를 받으려고 하고 멈춰. 걍 니가 최적이라고 생각하는걸로 계속 하라고”.
  G1 달성까지 구현·새 복사본 빌드·격리 실제 실행·원인 수리·새 세션 독립검수·기술 전략 재평가를 자동 연결한다.
  기존 두 결함 한정승인 소진/한-work예산/runtime재허가 대기 STOP은 **G1 계속 지시로 대체**하되 원문 이력은 보존한다.
  모델의 기술 HOLD·회차 종료·실패 횟수는 내부 재평가/다른 안전한 접근 선택 신호이지 사용자에게 일반 작업 허가를 재요청할 이유가 아니다.
  현재 다음 한 가지는 STATUS만 따른다. 실무=Luna, 새 독립 검수=Sol, 큰 방향=Astra/Fable, 실제 high/Fast argv 유지·자동모델폴백 금지.
  원본/참고/기존raw/golden/안전핀 보호·validator/기준 무완화·개인세션 비접촉·커밋/게시/자동deploy 별도권한·G2/G5종료/G3중단/G4보류 유지.
  G1 제품 PASS는 새 실행 증거/독립 검수로만 판정하고 최종 사용자 마일스톤 승인과 구분한다. 약10분 보고를 계속하며 일반 다음 단계마다 되묻지 않는다.

- [ ] **2026-10-03 lap892 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap890·891 B' final 차이 승격 해소):**
  lap890 final tick24861의 player 2명·unit 1개 차이는 **host live 읽기가 update 도중 상태를 찢어 읽은 것**이다. candidate snapshot은
  owner2 `count 95`인데 유닛은 96개로, 완료-phase snapshot 22개(lap874·888)에서 한 번도 깨지지 않은 불변식을 깬다(live 30개 중 이 1건).
  두 lane이 다른 6개 필드는 완료24860·완료24862 상태와 쌀 일시값으로 설명된다. 시뮬레이션 발산 증거로 쓰지 않되 lap890 pair는 HOLD 그대로.
  lap891의 "lap890 일정 전용 GDB 진단"은 채택하지 않는다(PASS해도 B'는 같은 live 표본으로 다시 깨질 수 있다, 지금까지 5 pair 중 3 HOLD).
  다음 work 1 lap = **P4b-S**: 진단 DLL이 `call 0x41C770` 호출 지점 2곳에서 update 반환 시점 snapshot을 남기고 B' gate가 그것을 쓴다
  (gdb 없음, 절대 r1 일정, lap888 완료 상태와 대조, fresh pair 연속 2회). 비교 필드·완전 일치·임계값·validator 불변. 관측 장치 추가·raw 변이
  내성 강화는 실제 실행 불일치가 있을 때만 strategy가 연다. 카드 `docs/work/active/G1_STRATEGY_W70_P4B_S_INPROCESS_SNAPSHOT_LAP892.md`,
  기록 `docs/history/laps/20261003_lap892_strategy_g1_p4b_torn_live_read_inprocess_snapshot.md`. 계획 승인·G1 마일스톤 아님.

- [ ] **2026-10-03 lap900 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap899 C 시각 HOLD 승격 해소):**
  후보 화면의 검은 마름모 격자는 캡처가 아니라 **렌더러의 지형 HD 합성 결함**이다. P4 지형 blitter를 처음 미러한 lap858부터 후보 캡처
  44개 전부에 있었고(이전 40개는 정상), 같은 프레임의 800 원본과 1600 출력을 프로세스 안에서 비교한 기존 수치로 P4 이후 PS3 present
  전부가 Scale2x의 정확한 상한 `inside_diff ≤ 2×(covered−stale)`를 어긴다(P3·P3c는 위반 0). Scale2x validator에 안쪽 상한이 없어 PASS였다.
  원인 후보(실행 미검증): 지형 writer `0x468C30`·`0x468CC0`·`0x468E10`의 identity frame을 scratch (0,0)에서 복사(`g1_mirror2x.c:1090~1092`).
  P4·P4b는 `HOLD(화면 정합)`로 환원, lap898 C 수용 없음, lap897 B'의 상태·입력 parity만 유지. 화면 정합 gate V1(정확식)·V2(캡처 검정 초과 ≤2000)·
  V3(middle이 PNG 직접 확인)를 모든 HD 단계에 추가한다. 다음 work 1 lap = **P4c**(V1·V2 RED → 바인딩 수리 → fresh pair GREEN → B' 2 pair → C 3 pair,
  수리 ≤3회 반복). 기준·임계값 완화 0. 카드 `docs/work/active/G1_STRATEGY_W70_P4C_TERRAIN_BIND_VISUAL_GATE_LAP900.md`, 기록
  `docs/history/laps/20261003_lap900_strategy_g1_p4_terrain_bind_defect_visual_gate.md`. 계획 승인·G1 마일스톤 아님.

- [ ] **2026-10-03 lap903 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap902 P4c 격자 귀속 승격 해소):**
  P4c 뒤 남은 가는 검은 격자는 **identity frame이 write mask를 잃어 Scale2x가 미기록 0을 색으로 읽는 렌더러 결함**이다. 기존 캡처
  30쌍 재계산에서 "원본 non-black 위, 블록당 검정 1개" 블록이 P4c는 18,882~20,056개이고 타일 변의 예측 축(`x±2y` mod 64)에 0.956~0.974가
  몰린다(균등 0.031). 지형 미러 이전은 476~614개, 0.07~0.16. 같은-call 관측 회차는 열지 않는다(수리 뒤 격자가 남을 때만).
  수리는 비클립·클립 두 바인딩 경로 모두에 mask를 주고 미기록 이웃을 E로 본다(M1~M5). V2는 순증가만 세어 minimap tag 2건이 격자가 있는 채
  PASS했으므로 **V2s(단일 검정 블록 ≤ 2000)**를 추가한다. V1·V2·V3·임계값 완화 0. 다음 work 1 lap = **P4c-M**(단위 RED → 수리 → fresh pair GREEN →
  B' 2 pair → C 3 pair, 수리 ≤3회 반복). 카드 `docs/work/active/G1_STRATEGY_W70_P4C_M_WRITE_MASK_SEAM_LAP903.md`, 기록
  `docs/history/laps/20261003_lap903_strategy_g1_p4c_write_mask_seam_attribution.md`. 계획 승인·G1 마일스톤 아님.

- [ ] **2026-10-03 lap906 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap905 B′ 우측 검정 띠 귀속 승격 해소):**
  스크롤 뒤 우측의 검은 쐐기는 **캐시 대상 scratch clear가 폭 800에서 멈춰 캐시 x800..831의 묵은 A==B를 compose가 쓴 픽셀로 읽는 렌더러 결함**이다.
  기존 캡처 60장 재계산에서 "원본 non-black 위, 네 subpixel 전부 검정" 블록이 RIGHT 뒤 8장에서만 화면 x736..767(=캐시 x800..831이 64px 밀린 자리)에
  2164~2370개 있고, 가로 이동 없는 22장은 0이다. 띠는 `y mod 32 ∈ [16,31]`·기울기 2:1의 쐐기다. 같은-present ROI 관측 회차는 열지 않는다
  (수리 뒤 띠가 1500 이상 남을 때만 진단 카운터 1개). 수리는 W1 하나(clear와 compose가 같은 프레임 폭)다. V2는 B′2 drag에서 결함이 있는 채
  PASS(1863)했으므로 **V2q(네-검정 블록 ≤ 2000)**를 추가한다. V1·V2·V2s·V3·임계값 완화 0. 다음 work 1 lap = **P4c-W**(단위 RED → W1 →
  fresh scroll pair GREEN=B′ 1번째 → B′ 2번째 → C 3 pair, 수리 ≤3회 반복). 카드 `docs/work/active/G1_STRATEGY_W70_P4C_W_CACHE_SCRATCH_WIDTH_LAP906.md`,
  기록 `docs/history/laps/20261003_lap906_strategy_g1_p4c_cache_scratch_width_attribution.md`. 계획 승인·G1 마일스톤 아님.


- [ ] **lap910 middle 기술검수(사용자 지시/승인 아님):** lap909 raw/map 산술·build46/SHA MATCH이나 PS9-associated 버퍼를 누적면적으로 선택, actual PS3 present 연결 누락·header 불일치 gate PASS 반례 확인.
  D-1 `HOLD_PRESENT_BUFFER_IDENTITY`·ESCALATE_SOL, P5 순서/실제overwrite UNKNOWN·G1 HOLD. 승격확인→work 관측하네스 최소수리 handoff, 새runtime/fullFast SKIP(사용자근거충돌stop).
  상세 `../history/laps/20261003_lap910_middle_g1_d1_present_buffer_identity_hold.md`; 현재 다음 한 가지는 STATUS만 따른다.

- [ ] **2026-10-03 lap911 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap910 D-1 present 버퍼 승격 해소):**
  lap909의 "PS3 last-writer 맵" 64장은 **메인 메뉴(PS9) 화면의 맵**이다. payload가 한 가지이고(SHA `e40210e0…45c9`), 그 버퍼의 표본 59개는 전부 PS9,
  맵을 그리면 `rle_clip` 28,654px이 메뉴 버튼 여덟 개 자리(y 488..577)다. 화면·월드 비율과 "전사 뒤 block_copy가 덮는다"는 수용하지 않는다.
  gate는 `selected_buffer`를 `0xDEADBEEF`로 바꾼 사본도 PASS한다(재현). **P5 순서는 지금 정한다: P5-H(HUD 패널 표면) → P5-T(tinted RLE 2종).**
  후보 유효 coverage p50 0.692, HUD 행이 화면의 20%라 월드를 다 덮어도 80%다. 수리는 B1~B5(present source를 잠가 얻은 포인터·pitch로만 결합,
  상태별 세대, DD blt 범주 10, 버퍼 요약)와 gate G1~G4. lap910 handoff 2번(전사 순서 관측)은 열지 않는다. 다음 work 1 lap = **D-1R**
  (단위 RED → 수리 → 원본 census-only fresh → 표). 계측기가 다시 막히면 strategy로 올리지 않고 다음 work가 P5-T를 먼저 한다. 기준·임계값 완화 0.
  카드 `docs/work/active/G1_STRATEGY_W70_D1R_PRESENT_BINDING_P5_ORDER_LAP911.md`, 기록
  `docs/history/laps/20261003_lap911_strategy_g1_d1_present_binding_p5_order.md`. 계획 승인·G1 마일스톤 아님.

- [ ] **2026-10-04 lap914 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap913 P5-H 패널 원천 승격 해소):**
  패널 바닥은 **`fnt\pannel{k,j,c}.spr` 한 프레임(831×h)을 렌더러 프리미티브 `0x4663E0`(키 채움 RLE)이 패널 표면 `[0x104F814]`에 그린 것**이다.
  census 9 pin에 이 함수가 없어 161,878픽셀이 미분류였다. 기존 raw 대조: 범주 10 픽셀 4,449,556개 전부 pannelj 불투명 칸 위(무관하면 0.823),
  PNG 일치율 pannelj 0.735~0.796·다른 그림 0.26~0.28·어긋난 대조군 0.31~0.35. **P5-H `FEASIBLE`**, 층 미러 가설 유지(lap911 §7 재판정 조건 아님).
  계약 H1~H5: 반환 주소 4곳으로 패널 결합, `0x4663E0` hook(폭 831이 pitch 800에서 접히므로 frame은 800×h), 색상키 `0xFE` 전사, 내용 대조(미니맵 직접 쓰기·점은 nearest).
  lap913 handoff의 관측 probe·P5-T 우선은 고르지 않는다. census 결함 두 건은 다음 census 회차로 보류. 기준·임계값 완화 0. 다음 work 1 lap = **P5-H**
  (단위 RED → 구현 → fresh pair GREEN(frame SHA 대조 PH-b) → B′ 2 pair → C 3 pair, 수리 ≤3회 반복, 막히면 strategy 없이 P5-T).
  카드 `docs/work/active/G1_STRATEGY_W70_P5H_PANEL_LAYER_LAP914.md`, 주소 `analysis/memory_maps/g1_w70_p5h_panel_surface_writers_lap914.md`,
  기록 `docs/history/laps/20261004_lap914_strategy_g1_p5h_panel_origin_layer_contract.md`. 계획 승인·G1 마일스톤 아님.

- [ ] **2026-10-04 lap925 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap924 P5-T observation-window 승격 해소):**
  lap923 B′1이 30개로 센 표본 중 **DOWN 4개·RIGHT 12개는 observation snapshot 뒤의 present**다(epoch 가정 없는 상한으로도 뒤, 경계 안 26/18).
  B′1 raw PASS 불수용, "B′ 연속 2회" 미충족, P5-T·G1 HOLD. 경계는 **sim tick**으로 센다 — 전환 뒤 present 중 `sim_tick ≤ observation tick`만 표본,
  30개·일정·임계값 불변. 기존 필드로는 정확히 못 그어 `mirror2x_present`에 `sim_tick` 한 필드를 더한다(O1~O7, 시계 비교는 대조값뿐).
  **새 사실: P5-T는 스크롤 뒤 present 간격이 56.0~58.5ms다**(P4c-W·P5-H 16회 48.97~49.83ms). 재호출 시간이 present당 4~7ms → 26~27ms로 올라
  36 tick 창의 present가 35~36개 → 30~31개로 줄었다. B′1은 여기에 보관 작업 I/O가 겹친 것이다. 하네스만 고치면 다시 HOLD다.
  다음 work 1 lap = **P5-T-R**(경계 수리 → fresh GREEN → 스크롤 뒤 비용 수리 ≤3회 → GREEN→B′2→C3). P5-T 2단 수용에 PT-c(전환 뒤 30 present ≤ 52.0ms)를 넣는다.
  기준·임계값 완화 0. 카드 `docs/work/active/G1_STRATEGY_W70_P5T_R_OBSERVATION_TICK_BOUND_LAP925.md`, 기록
  `docs/history/laps/20261004_lap925_strategy_g1_p5t_observation_tick_bound_scroll_cost.md`. 계획 승인·G1 마일스톤 아님.

- [ ] **2026-10-04 lap933 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap931·932 P5-T timer 범위 승격 해소):**
  timer 범위 결함은 사실이고 lap930의 `clip − 세 bucket` 잔차는 승인하지 않는다. **스크롤 뒤 비용의 뿌리는 클립 바인딩의 두 번째 검증이
  00 배경 클립 프레임(`scratch_a`)을 FF 배경 replay(`unclipped_ff`)와 비교하는 것이다**(`g1_mirror2x.c:1381~1383`). 9회 실행의 마지막 mismatch 값이 전부
  `[0, 255]`, replay ÷ mismatch 2.008~2.010, 클립 호출 82/present 중 74가 매 present full replay 2회를 반복한다. 같은 499,200바이트 fill이 고정 카메라
  4.6~4.9µs, 스크롤 뒤 140~147µs라 비용은 바이트 수가 아니라 메모리 상태다. 다음 work 1 lap = **P5-T-V**(두 번째 검증을 FF lane끼리 → fresh GREEN →
  PT-c가 남을 때만 lap931 §3 capacity 재사용 → GREEN→B′2→C1~C3). PT-d 절대 하한 11439는 시작 구간 값이라 폐기하고 PT-d′(tinted 호출 유지 +
  coverage·stale 악화 금지)로 바꾼다 — 과거 미달 값을 PASS로 바꾸지 않는다. 임계값·미러 범위·full sentinel fill 완화 0. **G1 계속.** 카드
  `docs/work/active/G1_STRATEGY_W70_P5T_V_CLIP_VERIFY_LANE_LAP933.md`, 기록
  `docs/history/laps/20261004_lap933_strategy_g1_p5t_clip_verify_lane_attribution.md`. 고친 빌드 미실행, 계획 승인·G1 마일스톤 아님.

- lap935 middle 검수: lap934 source48×6/6DLL·159입력SHA·snapshot30·V1 6881/PNG·B′2/PT-c/PT-d′/C3 독립PASS(partial), G1 HOLD·마일스톤판정0. 기존input-effect HOLD 보존, work 인계는 `G1_MIDDLE_W70_P5T_V_ACCEPTANCE_INPUT_HANDOFF_LAP935.md`(unscrolled 실제입력pair·필요시하네스최소수리), 현재큐는 STATUS만. 게임/source/tests/commit0·counter935읽기만·ESCALATE조건없음; fresh Fast 종료수치는 STATUS에만 보강.

- [ ] **2026-10-04 lap938 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap937 post-release present 승격 해소):**
  lap937이 짚은 caller·binding 결함은 사실이다. 그리고 lap936의 **"button-up 뒤 present 2건(seq1052/1056)"은 미입증이 아니라 반증**이다 — 후보 DLL이 같은 프로세스·같은
  thread·같은 `GetTickCount`로 적은 `WM_LBUTTONUP`(ts …538)보다 88ms·39ms 앞이다(같은 실행 prefix의 `inmm_g1_input_trace.jsonl`, lap936·937 미열람). gate는 10.7ms 만에
  이미 있던 7행의 마지막 둘을 돌려줬다. 캡처 자체는 release 뒤 present 5개 이후라 선택 의미 부분수용(151·빈0·drag4)은 유지, r3 binding `PASS`는 불수용.
  경계는 lap937 인계 1번(호스트 반환 뒤 seq) 대신 **게임 WndProc의 `WM_LBUTTONUP` 행**으로 확정한다(R1~R5, DLL 변경 없음, baseline `PASS_WITH_LIMITS` 그대로).
  다음 work 1 lap = 회귀 RED → 수리 → fresh unscrolled pair(P-1~P-6) → GREEN이면 minimap 유효좌표 pair. 기준·임계값·기대 ID 완화 0. **G1 계속.** 카드
  `docs/work/active/G1_STRATEGY_W70_INPUT_RELEASE_BOUNDARY_LAP938.md`, 기록
  `docs/history/laps/20261004_lap938_strategy_g1_input_release_boundary_inprocess.md`. 고친 gate 미실행, 계획 승인·G1 마일스톤 아님.

- [x] **2026-10-04 사용자 최신 지시: “이제 돌리는 모델들에서 fast는 빼자”.** Codex work/middle/strategy의 다음 fresh 호출은 일반 `service_tier=default`·`fast_mode=false`로 실행한다. `loop/env.local.sh`와 두 Codex config에 적용했고 CLI feature=false 및 세 역할 command assembly를 확인했다(`logs/gates/20261004_fast_off_argv.txt`). 모델ID·high effort·역할분리·G1 자율 지속·약10분 보고는 유지한다. 이미 호출된 lap943은 격리 검증/cleanup/full check를 안전하게 마무리했으며 이후 Fast 재활성화 금지. 기존 `/fast`/high-Fast 지시보다 이 지시가 우선한다. 검사 이름 Fast=`make check`는 계속 수행한다.

- [ ] **2026-10-04 lap944 strategy 판정(Claude Code `claude-fable-5-1`, 사용자 지시 아님 — lap943 생산 type31 대 type7 승격 해소):**
  **queue type31이 slot1199(타입58, 진영2)의 올바른 원본 witness다.** 원본 발행 코드 `0x40DF05`가 command 15·progress 0과 함께
  `+0x320 = [descriptor*24 + 0x9E2F34]`를 쓴다(고정값 아님). type7은 진영1 건물 타입49의 생산물로, G2 ESL2608 fixture 상수가 lap815에서 옮겨진 것이다.
  `(668,540)` 칸은 캡처 툴팁 `일본 농부 800/300/10`으로 일꾼 생산 칸. 클릭 전 `31/100`은 잔류값이라 type 전이 조건은 성립 불가 → witness를
  command 15 + progress 되감김 + **발행 단계 비용 정확 일치**로 바꾸고, control은 건물 필드로 판정하되 자원 변화는 `control_global_delta`로 공개한다(K1~K6).
  lap943 r4 production은 UNKNOWN/HOLD 그대로(원본 lane 미클릭). 다음 work 1 lap = 회귀 RED → 수리 → fresh pair(P-1~P-6). **G1 계속.** 카드
  `docs/work/active/G1_STRATEGY_W70_PRODUCTION_QUEUE_WITNESS_LAP944.md`, 주소 `analysis/memory_maps/g1_production_issue_path_40df05_lap944.md`,
  기록 `docs/history/laps/20261004_lap944_strategy_g1_production_queue_witness_contract.md`. 고친 하네스 미실행, 계획 승인·G1 마일스톤 아님.

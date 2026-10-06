# 2026-09-28 | lap 733 | 목표 G5 (D) 잔여 — 사망 후 그룹 호출 유령 재선택 수정(v6)

- 실제 provider/model/effort / 지정 역할: Claude Code (Sonnet 5), 실무(work) 역할.
- 가설 / 사용자 관찰: 2026-09-28 09:05 운영자 판정(lap732 D 결과) — 후보 v5에서 41기 그룹 중 10기
  사망 후 호출 시 37기 선택(기대 31기), 원본은 15기 중 3기 사망 후 12/12 정확. 지시: 호출된 슬롯을
  생존/사망/비멤버로 분류, 원인이 그룹 훅의 사망 시 그룹 필드 미정리인지 확인, 원본 사망 처리
  `FUN_00409C70`가 원본 20칸 그룹 배열만 정리하는지 대조 → v6 수정 → 원본/v6 paired 재측정 + 회귀.
- 예상 PASS / FAIL 조건: v6 후보로 lap732와 동일 시나리오(41명 중 앞3·중4·뒤3=10명 사망) 재실행 시
  `recalled_after_death.slots`가 `survivor_slots`(31명)와 정확히 일치하고 유령(사망 슬롯) 포함 0,
  크래시 0, `source_unchanged`, 기존 `make check`/`checks/safety.sh` 전부 PASS.
- 정적 조사(이번 lap, 신규): 보호 원본 EXE(`b56986e0…`)를 capstone/pefile로 직접 disasm.
  - `FUN_00445E30`(원본 recall, v5도 byte-identical — H1/H2/H3는 이 함수의 다른 위치만 건드림)의
    20칸 레거시 루프는 각 저장 슬롯을 `0x00416F40`(존재)와 `0x0040F790(slot)==1`
    (`unit+0x31C` "selectable" 바이트, H3가 오버플로 스캔에 쓰는 것과 **동일 게이트**)로
    검증한 뒤에만 선택한다.
  - `FUN_00409C70`(사망 처리, 사망 직후 `+0x31D`=1만 설정)는 `+0x31C`를 전혀 건드리지 않고,
    그룹 정리는 `FUN_00445A90(G, handle=dword[unit+0x29C])` 단 1회 무조건 호출뿐이다.
    `FUN_00445A90`은 **자기 그룹의 20칸 배열만, `unit+0x29C` 전체 dword(저word=slot,
    고word=aux) 정확 일치로** 검색해 지운다 — 오버플로(`unit+0x344`만으로 존재하는 21~50번째
    멤버)는 애초에 이 20칸 배열에 없으므로 검색 대상이 아니다.
  - lap732 자체 원시 JSON(`fixture_unit_group_snapshot`이 `handle=dword[unit+0x29C]`를 이미
    기록)을 재확인: 배정 직후 스냅샷의 handle 값이 사망 후 호출 결과의 raw 슬롯 값과 정확히
    일치해 "handle이 시간에 따라 드리프트해서 매치가 실패한다"는 가설은 반증됨.
  - v2가 실제로 굽는 H1/H2/H3 캐이브 원시 바이트(`g5_selection_cap50_v2.py`의
    `H1_CODE/H2_CODE/H3_CODE`)를 직접 disasm — 설계 문서(lap661)와 일치하며 그 자체로는
    코드 결함이 보이지 않음(레거시 루프와 동일한 `unit+0x344==g` + 동일 게이트).
  - 결론: 정확한 단일 원인(2단계 재배정의 재정렬 부작용인지, 엔진 자체의 비동기 사망
    정리가 이 짧은 창에서 아직 따라잡지 못한 것인지)은 끝까지 확정하지 못했으나, **양쪽 경로
    모두에서 안전하고 근본 원인에 무관하게 통하는 수정**을 특정했다: 사망 유닛 자신의
    `unit+0x344`가 여전히 유효한 그룹번호를 가리키면, `FUN_00445A90` 호출 직후 **그 그룹
    하나(전체 10개가 아님)의 20칸만, aux 없이 slot(저word)만으로** 재검색해 지우고, 마지막에
    `FUN_0040F750(slot,-1)`로 자기 필드를 무조건 강제 클리어한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `patches/selection/g5_selection_cap50_v6.py`
  (SHA256 `0eb0c0dd39862ef75565141a6acdc7bf1b0268ea76bb340cb5dd28d0026a634a`),
  `patches/selection/test_g5_selection_cap50_v6.py`
  (SHA256 `1ac6e0429c487beda25a8727f3d817c9d9a608d8d63c289f21cf3f08678b3e6f`). H4 훅은
  `FUN_00409C70` 내부 `call FUN_00445A90` 호출부(`0x00409CB8`, 5바이트) 단 하나만 건드리며,
  새 캐이브는 v3/v4/v5가 이미 쓰는 0x004E4C00~0x4E5000 zero-tail의 남는 124바이트 중 106바이트
  (`0x004E4F90..0x004E4FFA`)만 사용한다. H1/H2/H3, v3/v4/v5의 order-dispatch wrapper, 원본
  assign/recall 본문은 1바이트도 바뀌지 않는다(`test_only_the_h4_site_and_cave_differ_from_v5`로
  파일 전체 diff가 정확히 그 두 구간뿐임을 확인). uncommitted(`LOOP_ALLOW_COMMITS=0` 유지).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 v6
  `fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f`(v5 위에 H4 하나만 추가,
  `v5_candidate_sha256`=`29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`와 일치
  확인). 솔로 로비, 1600x1200 Xvfb, worker 기준 fixture(63칸 후보 풀 중 41기로 41명 그룹
  구성, lap732와 동일 시나리오).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 기존 `tools/g5_group_shift_add_death_recall_probe.py`를
  무수정 재사용하되(제품코드 아님, 순수 검증 목적), 모듈 임포트만 v5→v6로 일시 스왑하는 임시
  드라이버(`/tmp/run_v6_probe.py`, 세션 임시 파일, 저장소에 없음)로 `variant=candidate` 1회 실행.
  런타임 `local/runtime/lap733_v6_verify/`, 산출물
  `../../temp/Syw2plus_patch/20260928_lap733_v6_death_recall_verify/candidate-v6/probe-result.json`.
  이어서 `make check`(`/tmp/make_check_v6.log`), `checks/safety.sh check`(`/tmp/safety_check_v6.log`).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS.** v6 후보 재실행 결과
  `status=COMPLETE`, `structural_ok=true`, `death_recall_check={"expected_survivor_count":31,
  "recall_ok":true}`, `recalled_after_death.slots`(31개)가 `kill_plan.survivor_slots`(31개)와
  정확히 집합 일치 — lap732에서 유령이던 6명(1134,1146,1147,1163,1164,1165) 전원 정상 제외,
  나머지 4명(1166,1193,1194,1195)도 계속 정상 제외. `source_unchanged=true`,
  `cleanup.prefix_processes_after=[]`, 크래시 없이 완주(게임 실행 끝까지 세션 유지, background
  누락 없음). `make check` **1111 passed(776.51s)**(신규 v6 pytest 5개 포함, 기존 1106+5=1111
  일치), ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS. `checks/safety.sh check`:
  `SAFETY_PASS`. `local/runtime/lap733_v6_verify/*/game`(~830MB) 실행 후 삭제,
  output/manifest/log/prefix 보존.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: v6는 v5 대비 정확히 5바이트(훅 사이트)+106바이트
  (캐이브) 딱 두 구간만 다르고 나머지 전체가 byte-identical임을 `test_only_the_h4_site_and_cave_
  differ_from_v5`로 고정했으므로, lap723~731이 이미 PASS한 드래그/이동/공격/정지·홀드·순찰/
  Ctrl+숫자/숫자호출/Shift+클릭 추가/저장로드/채집/수리/특수능력/좌표일치 등은 이 훅 코드 경로
  자체에 닿지 않아 회귀 위험이 극히 낮다고 판단하나, **이번 lap은 그 항목들을 v6로 재실행해
  실측 재확인하지 않았다** — v5로 이미 확정된 결과를 그대로 물려받는다는 가정에 의존한다.
  근본 원인(2단계 재배정 재정렬 vs 엔진 비동기 사망정리 타이밍)은 끝내 disasm/라이브 추적으로
  완전히 확정하지 못했고, 이 fix는 "원인이 무엇이든 통하는" 방어적 수정이라는 것이 이번 lap의
  명시적 판단이다. (E)~(H) 체크리스트 항목은 여전히 미측정. middle 독립 검수는 2026-09-28 03:36
  운영자 판정대로 체크리스트 전체(A~H)가 채워진 뒤 한 번에 진행하며, 이번 lap은 그 대상이 아니다.
  사용자 milestone 승인 없음.
- 다음 한 가지: (D) 체크리스트는 이 fix로 완료 판단(Ctrl+숫자/숫자호출/저장로드=lap724,
  Shift+숫자 추가=lap732 대안메커니즘, 부대원 사망 후 호출=이번 lap v6). 다음 work는 v6를 새
  기준 후보로 놓고 (E) UI(50기 선택 시 초상화/정보패널·HUD·체력바) → (F) 저장/로드(50기 상태,
  원본 세이브 호환) 순서로 진행한다. 시간이 허락하면 lap723~731의 핵심 회귀(드래그/이동/공격/
  정지·홀드·순찰/그룹저장로드)를 v6 기준으로 1회 재확인해 "byte-diff 스코프 인자에만 의존"이라는
  현재 가정을 실측으로 보강한다.

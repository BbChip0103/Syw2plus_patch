# 2026-09-28 | lap 754 | 목표 G5 (middle: lap753 v9·H-NEWGAME-INIT falsification 독립 재검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인).
  게임 실행 0회, 제품 코드(패치·EXE) 0 변경. 문서와 (A) 정적 표만 갱신.
- 가설 / 사용자 관찰: lap753 work가 보고한 3-way(원본 `NEWGAME_STALE_CLEARED` / v8 `PERSISTED` / v9
  `CLEARED`)와 v9 S1/S2/S4 회귀가 독립 확인되면, lap752가 연 (F)/S3 HOLD 사유(H-NEWGAME-INIT)는 닫힌다.
- 예상 PASS / FAIL 조건: PASS = v9 재빌드 SHA 일치 + hook이 `0x4a3060`의 무조건 경로에 있고 모든
  호출자가 같은 `this`로 진입 + probe raw가 주장과 일치 + `make check` PASS. FAIL = 하나라도 불일치,
  또는 `0x4a3060`을 거치지 않는 새 게임 경로 발견.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `analysis/memory_maps/
  g5_selection_consumers_inventory_20260928.md`(§2b this-상대 초기화 행 추가), 이 파일, `docs/STATUS.md`,
  `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`, `loop/ESCALATE_SOL`(lap754 절 추가). 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `[ESL]Syw2plus/[HQ]Syw2plus
  2002.exe` = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(재확인). 이 세션에서
  원본으로부터 재빌드: v8 `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`, **v9
  `18181cdef6c787a2be9a3cf78a2851eb4d764074c972e2b13690f27af0fd2017`** — 둘 다 기록 일치. 런타임 증거는
  lap753 artifact(솔로 로비, 1600×1200 Xvfb, 격리 prefix, stale 주입은 fixture 없이 매치 시작 직후).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 재빌드·diff·디스어셈블: `v9.build_candidate(orig)`/`v8.build_candidate(orig)` + capstone(인라인 python).
  - `python3 -m pytest -q patches/selection/` → 56 passed. `checks/safety.sh check` → `SAFETY_PASS`.
  - `make check` → **1122 passed, 5 skipped(730.26s)**, ruff PASS, mypy 0 issue(10 files), `CONTEXT_PASS`.
    로그 `/tmp/lap754_middle_make_check.log`.
  - raw 대조: `temp/Syw2plus_patch/20260928_lap752_newgame_stale/{original,v8,v9}/probe-result.json`,
    `temp/Syw2plus_patch/20260928_lap752_v9_s124/probe-result.json`(v9 S1/S2/S4), 과거 비교용
    `20260928_lap746_*`·`lap747_*`·`lap748_*` probe-result.json.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **v8→v9 diff 범위** = PE 헤더 1바이트(`0x270`, `.rsrc` VirtualSize) + hook 6바이트 중 5바이트
     (`0xa3168..0xa316d`) + cave(`0xfb200..0xfb21a`)뿐. PASS.
  2. **hook 정합성(정적)**: 원본 `0x4a3060` 본문을 entry부터 `0x4a3227`까지 디스어셈블 — entry→`0x4a3168`
     사이에 조건 분기가 없고(루프 `0x4a307d`/`0x4a30cd`는 되돌아올 뿐, 나머지 call은 모두 복귀) hook은
     매 진입마다 실행된다. v9: `0x4a3168 jmp 0x108f200; nop` → cave `mov [esi+0x6c14],ebx; pushad; mov edi,
     0x108c000; mov ecx,0x33; xor eax,eax; rep stosd; popad; jmp 0x4a316e`. 레지스터 전부 보존, 이후
     코드가 flags를 읽기 전에 다시 설정(`dec edx` 등)하므로 flags 비보존 무해. 51 dword = count+50칸. PASS.
  3. **호출자 전수**: `.text` 전체 rel32 `call/jmp` 스캔 → `0x4a3060` 직접 호출 정확히 3곳(`0x41b9c0`,
     `0x41bc4f`, `0x4c3e59`), 파일 전체 절대 dword 참조 0(간접/함수포인터 경로 없음). 세 곳 모두 직전에
     `mov ecx,0x892410` — cave가 전역 새 배열을 비우는 것이 `this`와 항상 일치. PASS.
  4. **this-상대 선택 필드 재스캔**: `.text` 전체에서 `[reg+disp]`, disp ∈ `[0x6c14,0x6c68)`은 `0x4a3168`
     (count)과 `0x4a31ff lea eax,[esi+0x6c18]`(엔트리 20칸 루프) 2건뿐 — lap752 정적 결론과 일치.
     즉치 `0x6c34`(`0x4c516a`)는 stride 0x64 상수표로 무관. PASS.
  5. **probe raw(lap753)**: 원본 주입 count=20·nonzero=20 → 재시작 후 0/0; v8 50/50 → **50/50 잔존**;
     v9 50/50 → 0/0. 세 run 모두 `injected_slots_have_no_selected_flag=true`, `restarted=true`(tick
     6→5/2/1), `cleanup.ok=true`, `source_unchanged=true`. v8과 v9의 차이는 hook뿐이므로 **v9의 CLEARED는
     재시작 경로가 `0x4a3168`을 실제로 통과했다는 차분 증거**다. PASS.
  6. **v9 S1/S2/S4 회귀 raw**: 드래그 50/50, 저장·재개 50/50, 로드 후 20/20(레거시 20과 일치, stale-tail
     0), 이동 명령 19/20·`commanded_outside_legit_selection=[]`, 해제 0, 재드래그 50, 재저장 생존,
     S4 재시작 후 0/0. 이동 19/20의 누락 slot 1198은 **원본(lap746/747/748)·v8 전 run과 동일**(원본 패리티).
     PASS.
  7. **핸드오프 ②(gdb 호출자 귀속) 생략 판단 동의**: 3번(정적 전수)과 5번(v8/v9 차분 runtime)이 귀속보다
     강한 근거다. 추가 gdb 불필요.
  8. **lap747 핵심 coverage를 v9로 재실행하지 않은 점**: 변경 바이트는 `0x4a3060`(게임 시작/재시작 초기화
     전용 3 호출자) 안에서만 실행되므로 인게임 명령·선택 경로에 도달하지 않는다. S1/S2/S4 run이 v9에서
     드래그·이동·저장/로드·재시작을 실제로 통과했다. 재실행 없이 수용.
  - **종합 판정: G5 (F) = PASS(v9). S3 = "초기메뉴 UI 전환 자체는 env 미실측, 새 게임 초기화 주체는 정적
    전수(3 호출자·단일 무조건 경로) + runtime 차분으로 커버"로 재분류.** (A) 표에 §2b 추가로 누락 2행 해소.
  - **G5 체크리스트 A~H 2단 middle 판정(v9 기준): A PASS, B PASS, C PASS(미니맵 우클릭·능력 v는 원본도
    무반응 UNKNOWN, 건설·승선 N/A), D PASS, E 조건부 PASS(체력바 46/50 가림 PLAUSIBLE, lap745/750 유지),
    F PASS, G `BLOCKED(env: native ipxwrapper crashes on room creation, wine9.0)` 수용, H PASS(v7 8019 tick;
    v8/v9 차이는 로드 래퍼 폭과 게임 시작 초기화뿐이라 장시간 경로 불변).** → **3단 사용자 milestone
    재상정 대상.** middle은 G5 종료·G1 착수를 선언하지 않는다(사용자 판단 경계).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 알려진 제한(사용자에게 명시) — ① G 멀티 BLOCKED(env),
  ② 부대 미지정 드래그 선택은 로드 후 앞 20기만 복원(원본과 동일 20), ③ 미니맵 우클릭·특수능력 v UNKNOWN
  (원본도 무반응), ④ 건설·승선 N/A, ⑤ E 체력바 46/50 가림 PLAUSIBLE, ⑥ S3 초기메뉴 UI 전환 env 미실측,
  ⑦ S5 정적 귀속, ⑧ `FUN_004AE550` 간접 호출 부재는 정적 미증명(경험적 반증), R2 opcode 값 미실측,
  ⑨ 부대 H1~H3 edge case(lap661 수용분). 실사용 EXE 배포는 사용자 결정 후. 사용자 승인: 대기.
- 다음 한 가지: **사용자 3단 판단 — G5 v9(`18181cde…`)를 알려진 제한 ①~⑨와 함께 단일플레이 milestone으로
  승인하고 G1(1600×1200 원본 구성)을 재개할지.** 승인 전 work/middle이 할 G5 제품 작업은 없다(루프는 이
  경계에서 멈춘다). 반려 시 반려 항목만 다음 work가 처리.

## 3단 제출 양식 (APPROVALS 제출 양식 필드)

- 마일스톤/목표: G5 드래그 선택 20→50, 체크리스트 A~H(2026-09-28 01:31 지시).
- 후보 SHA: v9 `18181cdef6c787a2be9a3cf78a2851eb4d764074c972e2b13690f27af0fd2017`
  (`patches/selection/g5_selection_cap50_v9.py`, 보호 원본 `b56986e0…`에서 결정적 재빌드).
- 기준·후보 캡처: `temp/Syw2plus_patch/20260928_lap752_newgame_stale/{original,v8,v9}/*.png`,
  `temp/Syw2plus_patch/20260928_lap752_v9_s124/*.png`, 이전 항목별 캡처는 lap723~753 상세 기록.
- 실제 입력·부하조건: 솔로 로비 1600×1200, 55기 fixture, 실제 드래그/우클릭/툴바/단축키/일시정지 메뉴.
- 1단 결과: `make check` 1122 passed·5 skipped, `SAFETY_PASS`, `CONTEXT_PASS`, G5 pytest 56 passed.
- 2단 판정자: Claude Code `claude-opus-5-5`/high(이 lap) — 위 A~H 판정.
- 다른 점/허용 오차·남은 위험: 위 알려진 제한 ①~⑨.
- 사용자 판정: 대기.

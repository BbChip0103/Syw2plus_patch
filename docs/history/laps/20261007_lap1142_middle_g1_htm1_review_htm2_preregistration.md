# 2026-10-07 | lap1142 | G1 middle — H-TM1 독립 검수, `0x466480` 도달 범위 정적 확정, H-TM2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행·C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1141 work → middle 검수 요청, `9ddb17db…`, 원문 byte 일치 보존 `docs/history/laps/20261007_lap1142_preserved_lap1141_escalate_sol.txt` 뒤 삭제). INBOX 새 사용자 지시 없음(마지막 = lap1141 처리 메모), APPROVALS 새 반려·사용자 시험 결과 없음(lap1136 재요청 대기), `loop/STOP` 없음.
- 목표: G1. 가설(검수 대상): 팝업 바탕 writer = 미후킹 `0x466480`, diff 미러로 팝업 정착 HD ≥98.6, 다른 상태 영향 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- 후보 source SHA(ESCALATE_SOL 기록과 7/7 일치): `g1_screen_watch.h` `3880b0025f58`·`g1_mirror2x.c` `1b056280f662`·`g1_mirror2x.h` `0fc9cc4b1edf`·`direct_draw_trace.c` `0de218aa84d6`·`g1_saved_scene_probe.py` `a82a0308fa18`·`test_g1_screen_watch.py` `923dd9325397`·`test_g1_rect_fill.py` `d8e4430db905`.
- fixture: 없음(lap1141 raw 재사용, 새 실행 없음).

## 1. raw 독립 재계산 (새 스크립트, 공유 temp `20261007_lap1142_middle_review/`)

`recalc_lap1142.py` → `recalc_lap1142.json` `7c485787…`. 결과 JSON SHA 6/6 일치(r1 `5cfdd2b2`·on_a `9c557ec3`·on_b `0d47e43e`·off `1013ff70`·scn `0d9e0336`·ng `c41f6c75`), run exit 파일 6/6 = 0, 각 lane `source_unchanged` true·cleanup ok·`game` 사본 잔존 0. HD = (480,000 − stale)/480,000.

| run | 후보 상태·present | 정착 stale(첫 present 제외, 최빈) | HD | `0x466480` 호출 / mirrored / reject |
|---|---|---|---|---|
| r1(수리 전 빌드) | PS9 1,576 | 76,319 ×1,515·0 ×60 | 84.100 | 키 없음(수리 전) |
| on_a | PS9 1,636 | **871** ×1,570·0 ×65 | **99.819** | 1,570 / 1,570 / 0 |
| on_b | PS9 1,522 | **871** ×1,467·0 ×54 | **99.819** | 1,467 / 1,467 / 0 |
| off(`SYW2_G1_KEYED_COPY=0`) | PS9 1,785 | 76,319 ×1,714·0 ×70 | 84.100 | 1,714 / 0 / 0 |
| scn | PS9 71·PS15 1,013 | 0 | 100 | **0** / 0 / 0 |
| ng | PS9 61·PS7 158·PS5 753·PS3 2,971 | PS3 0 ×2,969·12 ×1; PS7 8,803·PS5 5,752~6,147 | PS3 ≥99.998 | **0** / 0 / 0 |

- 호출 수 = 팝업 열린 present 수(present당 1회). 안전 9종(hd_mask_outside·identity_key·clip_replay·viewport_restore·cache_clip_verify·palette·identity_invalid·viewport_field·fallback) max 0, success min 1, hresult 0, dropped 0(전 run).
- screen watch(r1 `screen_watch.jsonl` `17632a56e7e2`, 9,716줄): 표본 주소 3개를 버퍼 `0x04460030`·stride 1,600으로 역산 = (300,250)·(270,300)·(480,400) 일치. 표본마다 EIP 둘뿐: `0x004662DE` 1,575 present(0..1574) + **`0x004664BF` 1,515 present(60..1574)**, 스택 상단 `0x4C8773→0x495093→0x4248C5` 1,515/1,515, tid 280 하나. ESCALATE_SOL의 "1,549·1,489"는 present 구간 표기 차이로 보이며(r1 present 1,576 기준 재계산 1,575·1,515) 귀속 판정에는 영향 없음 → **정정 1(계수 표기)**.
- **불일치 0(판정 수치), 정정 1(screen watch 계수 1,549/1,489 → 1,575/1,515).**

## 2. 원본 역어셈블·도달 범위 정적 확정 (`exe_disasm.txt`, objdump 원본 EXE)

- `0x466480`: `mov edx,[ecx+0x10]; push ebx; mov eax,edx`(=`8B 51 10 53 8B C2`, 원본 바이트 직접 확인·C `expected_keyed_copy` 일치), 인자 (x=[esp+8]→…, y, w, h, src), 목적지 `[ecx+0x1514]+y*[ecx+0x10]+x`, `cmp cl,0xFE; je` 건너뜀, `mov [eax],cl`@`0x4664BD`(다음 EIP `0x4664BF`), 부호 비교 `jle`, 클립 없음, `ret 0x14` — lap1141 기술 일치.
- **호출 그래프(전부 유일):** `0x466480` 직접 호출 = `0x4C876E` 1곳(imm32 참조 0) ∈ `0x4C8720`(팝업 그리기, this `0xE5BF18`) ← `0x49508E` 1곳(imm32 0) ∈ PS9 프레임 함수 `0x494BC0`, 조건 `[0x1050F98]≠0`, 객체 `0x1050FA0` ← `0x4248C0` 1곳(`0x4248A7`의 `0x494880` 초기화 뒤 `[0x4ED818]=9`).
- `[0x1050F98]` 쓰기: `0x494BAA`(초기화 — 사용자 목록 `0x669590`이 비면 1), `0x494D48`(버튼 객체 `0x1050DB8` 클릭 시 1 = 사용자변경, run과 일치), `0x494CB1`(팝업 `0x4C8920` 완료 시 0).
- **결론:** 새 훅은 PS9 타이틀에서 사용자등록 팝업이 열린 동안만 실행된다. 인게임 PS3(save006 포함)·결과·일시정지 화면에서는 정적으로 호출될 수 없고, 런타임에서도 scn·ng 호출 0으로 일치한다. 그 밖 상태에 남는 영향은 6바이트 트램펄린 설치뿐(설치 체인 `||`·원복 `restore_hook` 포함, 기존 훅과 같은 방식). → **H-TM1 자체 수용에 save006 pair는 필요 없다.** 단 시험판 재스테이징 때는 H-TR2 선례대로 현재 트리 full pair를 다시 돈다.
- 새로 알게 된 점: 등록 사용자가 없는 새 설치에서는 타이틀 진입 즉시 이 팝업이 뜬다(`0x494BAA`) → 실제 사용자 첫 실행 화면에 해당하는 수리다.

## 3. 캡처·잔여·성능

- `popup_residual_lap1142.py` → `popup_residual_lap1142.json` `96382fbd…`(독자 Scale2x(baseline 800×600) 대 후보 1600×1200, 팝업 상자 논리 (256,145)-(544,456)). 판별 가능 블록 23,501 중 후보 = nearest: **끔 21,656(lap1140 값과 동일) → 켬 923**, 팝업 안 Scale2x 정확 일치율 0.93173 → **0.99345**. 팝업 밖 nearest 653은 켬/끔 동일(이번 훅 무관). on_a·on_b 캡처 SHA 동일(`3888a981b348`).
- 잔여 위치: 팝업 안 1,833개 작은 조각(최대 29블록 @(496..503,411..421) = 확인 버튼 테두리 부근), 행 집중 y 181·218·234·265·294(제목·ID 버튼 글자 행), 열 집중 x 457..471(버튼 열). `seam_check_lap1142.py`: 타일(320×160) 이음새 y≈305 주변 행 3~20으로 이웃과 같은 수준 → 타일 경계 결함 아님. 잔여 871(0.18%)은 글자·버튼 테두리 계열 소잔여로 판단(writer 미귀속, TextOutA `reject_target` 계열 backlog와 같은 종류 추정) → **수용 가능한 부분 잔여**, backlog.
- 캡처 열람(`view_on_a_candidate_popup.png`·`view_off_candidate_popup.png`): 두 쪽 모두 팝업 바탕·초상화·ID 버튼 3개·확인·글자 정상, 색·위치 오류 없음. 켬 쪽 초상화·돌 질감 윤곽이 Scale2x로 매끄럽다.
- 성능(`perf_lap1142.py` → `perf_lap1142.json` `1bbc7bc3…`, 팝업 열린 present만): 평균 켬 9.53/9.93 ms·p95 15/16 vs 끔 8.91·p95 13. 같은 무미러 조건 r1(수리 전 빌드)이 평균 6.42·p95 11이라 run 간 환경 변동(~2.5 ms)이 켬/끔 차(+0.6~1.0 ms)보다 크다 → 성능 회귀 판정 불가·의미 있는 증가 근거 없음, 모두 16.7 ms 프레임 안. 정지 메뉴 화면이라 공개만 한다.

## 4. 판정

- **H-TM1 `PASS(partial, 기술·격리)` 수용.** TM1-1 귀속 PASS(3/3 단일 writer), TM1-2 PASS(정착 HD 84.100→99.819 ≥98.6, 켬 2/2·끔 재현·reject 0·안전 0), 도달 범위 PS9 팝업 한정(정적+런타임). partial = 잔여 871 미귀속·실제 Windows 미검증.
- 하네스 off 첫 실행 중단(도구 타임아웃) 보존·판정 제외는 타당.
- **시험판 재스테이징: 보류.** 이유: 사용자가 lap1135판 결과를 아직 주지 않았고, 이번 변화는 타이틀 팝업 화질(허용 차 범주)뿐이라 폴더를 또 늘릴 만큼 급하지 않다. H-TM2 결과까지 묶어 다음 middle이 재스테이징(현재 트리 save006 full pair+스테이징 work → root 전달)을 정한다. 사용자 결과가 오면 판을 구분해 처리한다.

## 5. 다음 work 사전등록(Sonnet) — H-TM2: 종료하기 확인 팝업 `(410,560)` HD 관측 → 조건부 귀속·수리

**근거.** PS9의 남은 미측정 버튼은 종료하기·HQNET(외부 접속, 계속 제외)뿐이다. §2로 사용자등록 팝업(`0x1050FA0`)의 표시 조건은 `0x1050DB8` 클릭과 빈 사용자 목록뿐이므로, 종료 확인 화면(있다면)은 다른 writer일 가능성이 크다.

- **TM2-0 하네스(TDD):** `TITLE_BUTTONS`에 `"quit": (410, 560)` 추가. **quit은 재시도 클릭 금지**(첫 클릭 뒤 1초 안에 PS9 이탈이 없으면 같은 좌표 재클릭 로직이 확인 팝업의 예/아니오 버튼을 누를 수 있다). quit 결과 분류: (a) in-place 팝업(PS9 유지) → 기존 `IN_PLACE` 캡처 2장, (b) 게임 프로세스 종료·PS 이탈(확인 없이 종료) → `EXITED`로 기록(실패 아님, 관측 결과). 테스트: choices·quit 재시도 없음·EXITED 분류.
- **TM2-1 관측(격리 1 run, 현재 트리 기본 켬):** `--hd-source scale2x --title-button quit`. (a)면 팝업 정착 HD(첫 present 제외) min, stale 최빈값, 캡처 열람; 사용자등록 팝업과 같은 `0x466480` 경로인지 `keyed_copy_466480_invocations` 증가로 확인. 판정: ≥98.6 = PASS(수리 불필요) / 90~98.6 partial / <90 FAIL → TM2-2. (b)면 `PASS(관측, 확인 팝업 없음)`으로 종결.
- **TM2-2 조건부(같은 회차, 구현 우선):** HD <98.6이면 lap1141 방식 그대로 — `--screen-watch --screen-watch-state 9 --drift-samples`(팝업 바탕 3점, TM2-1 캡처에서 좌표 판독) → 단일 미후킹 writer면 diff 미러(env 기본 켬+끔 대조), 켬 2·끔 1, 비회귀 `--title-button user` 1회(99.819 유지)+scenario 1회. writer가 여럿·wined3d/GDI면 귀속만 기록해 넘긴다.
- **금지·공통:** 확인 팝업 안 버튼(예/아니오) 클릭 금지, HQNET `(302,560)` 제외, 사용자등록 팝업 ID 버튼 클릭 금지 유지. 원본/참고 쓰기·커밋·`260921_temp` 쓰기 금지. 각 run 뒤 `game` 사본 삭제·디스크 ≥20GiB(현재 91GiB). 긴 실행은 `setsid nohup`+생존 확인(lap1141 off 중단 재발 방지). 하네스·C 변경 시 lint·typecheck → 기록 freeze → `make check` 1회. **사용자 G1 시험 결과가 오면 그것이 최우선.**
- 연속 규칙: lap1141은 실행 증거가 있는 work. 이번 middle은 실행 증거 없음 1회째. 다음은 실행 증거를 남기는 work여야 한다.

backlog 추가: H-TM1 잔여 871(팝업 글자·버튼 테두리, writer 미귀속). 기존 backlog(Wine 영상 재생 불가·victory-poke readback 경합·STATUS 목록) 유지.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check` SKIP: 이번 회차 변경은 문서·공유 temp 스크립트뿐이고 C·하네스·테스트 source는 lap1141 full PASS(1798 passed·5 skipped/781.36s, exit 0, 로그 `03c76372652a` 직접 확인) 때와 SHA 7/7 같다.

## 다음 행동

work(Sonnet): §5 H-TM2(TM2-0 하네스 quit·재시도 금지 → TM2-1 관측 → 조건부 TM2-2). 그 뒤 middle이 H-TM1+H-TM2 묶음 재스테이징 여부를 정한다. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.

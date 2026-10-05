# G6 middle 검수 — lap977 H-G6a 수용(partial)과 실제 자리 재현 H-G6s handoff (lap978)

- 작성: 2026-10-05, lap978 middle(Claude Code `claude-opus-5-5`, high). 게임 실행·source 변경·commit 0.
- 입력: `loop/ESCALATE_SOL`(lap977 work), 기록 `docs/history/laps/20261005_lap977_work_g6_shift_click_count_bound_hg6a.md`, 이전 카드 `G6_MIDDLE_LAP976_SHIFT_CLICK_COUNT_BOUND_HANDOFF.md` §2~§6.
- 이번 lap 산출물(공유 temp, 직접 생성): `temp/Syw2plus_patch/20261005_lap978_middle_review/`
  `recalc_lap978.py`→`recalc_lap978.json`(SHA256 `e1fcd193f04873ba7553bfc110c563e81549d088c538610766b0e2fe11854c46`), `verify_bytes.py`→`verify_bytes.json`,
  캡처 diff `seat_panel_diff.py`→`seat_panel_diff.json`(SHA256 `23f92baf…efb83`), 정적 스캔 `xref_scan.py`·`gaks_scan.py`·`vk_scan.py`·`vk_switch_scan.py`·`vk_mem_scan.py`·`port_vk_scan.py`, `orig_4B8D60.txt`, `disasm_range.py`.

## §1 독립 재계산 (제품 helper 미사용, stdlib만)

probe-result 5개 SHA256이 lap977 기록 앞 16자와 모두 일치한다. 재계산 결과 기록과 **불일치 0**:

| run | EXE SHA | G6-1 개수열 | 클릭 slot 합류 | G6-2 | G6-3 | G6-4 | 최대/cap | 중복 | slot0 poke |
|---|---|---|---|---|---|---|---|---|---|
| orig@1 | `b56986e0…` | 1,1,1,1,1,1 | 0/5 | 1→3(쌍 합류, 외부0) | 3→2(희생 제거·나머지 유지) | — | 3/20 | 0 | `0x66B81E` 0→1 readback 1 |
| port@1 | `0e28ef57…` | 1,1,1,1,1,1 | 0/5 | 1→3 | 3→2 | 50→50(집합 불변) | 50/50 | 0 | `0x112E08E` 0→1 readback 1 |
| cand@1 r3 | `b50af2a6…` | 1,2,3,4,5,6 | 5/5(앞 선택 보존) | 1→3 | 3→2 | 50→50(추가 slot 미포함·집합 불변) | 50/50 | 0 | `0x112E08E` 0→1 readback 1 |
| port@0 | `0e28ef57…` | 1..6 | 5/5 | 1→3 | 3→2 | 50→50 | 50/50 | 0 | 없음 |
| cand@0 | `b50af2a6…` | 1..6 | 5/5 | 1→3 | 3→2 | 50→50 | 50/50 | 0 | 없음 |

- 모든 스냅샷 `count == len(slots)`, cap 초과 0, 다섯 run 모두 `local_at_ps3=0`·cleanup 프로세스 0·game 제거·game_alive.
- fixture는 합성(op5, owner 0, 활성 78~96기, 격리 10기) — 기록과 같다.

## §2 후보 바이트 독립 확인

배포 이식판 두 lane(normal `0e28ef57…`, fixed_start `703deaf4…`)에서 메모리 빌드(파일 쓰기 0) → 후보 SHA normal `b50af2a6…`(= cand run의 private EXE SHA)·fixed_start `7c891658…`.
diff = 파일 offset `0x1DD82` 8바이트 + cave `0x108C00` 17바이트·`0x108C12` 5바이트(사이 1바이트는 imm `0x0061E36C`의 `00`이라 원래 0과 같음) = 30바이트.
capstone: hook `jmp 0x18A7C00; nop×3`, cave `cmp edi,[esp+0x10]; jge 0x41DDE9; mov ax,[esi]; mov ecx,0x61E36C; jmp 0x41DD8A`.
`[esp+0x10]`은 `0x41DD74`에서 압축 개수로 쓰이고, 루프 안 `push`는 `0x40F560`/`0x40F670` 호출이 정리하므로 루프 머리의 esp가 같다(이식판 역어셈블 lap976 `port_41DC40.txt`).
이미 선택된 유닛 제거 검사(`0x41DDBB` `[0xB938E0]` 비교)도 압축된 앞쪽 칸만 보면 충분하다. 이식판에서 cave 범위 절대 참조 0, `.g5code` VA `0x18A7000` 크기 0x1000, rollback byte-identical.

## §3 판정

- **H-G6a PASS(partial) 수용** — 결함 분기(`0x41DD93` 빈 칸 owner≠local → `0x41DDB3` 중단 플래그)를 O·P에서 재현했고, C는 이 분기만 없애며 1P·드래그·제거·50 상한을 퇴행시키지 않는다.
- **DESIGN G6 합격은 아님** — 합격 문구는 "1P가 아닌 자리에서 재현"이다. slot0 emulation은 local=0을 유지하고 빈 칸 비교 한 곳만 같게 만든다.
  실제 local=k에서 시작 유닛 owner·AI 배정·DPID가 달라지는 경로는 실행하지 않았다.
- G7은 실제 local≠0 저장/불러오기가 전제이므로 emulation으로 대체할 수 없다 → **실제 자리 재현이 G6 마감과 G7 착수의 공통 선행 조건**이다. H-G7o는 그 뒤로 미룬다.

## §4 자리 이동 BLOCKED 검토

- lap977 lobby run 5개 캡처를 픽셀 비교했다: 방향키 12회·번호칸 클릭 뒤 방향키 모두 **좌측 자리 패널(0..190×0..520) 변화 0**. 바뀐 곳은 채팅 입력 커서(241,509)와 마우스 커서뿐이다.
  즉 키 입력은 들어갔지만 자리 이동은 일어나지 않았다(측정 변수 문제 아님).
- 대기실에서 local은 바뀔 수 있다: `0x4B7700`이 `[0xC0D0F4]`≠0이면 로비 스냅샷 `0x632E0C`(0x5C dword)를 `0x632C9C`로 복사하고 `0x43AF40(&0xB63FC4)`로 다시 계산한 뒤 플래그를 0으로 지운다.
  게임 생성 경로 `0x4219A0`은 `0x439B90`(자기 DPID) → `0x43AE80`(첫 빈 `0x632CA0` 칸에 넣고 행 `0x632CC0+6i`를 사람/국가5로) → `0x43AF40`.
  혼자하기 초기화 `0x4B6355..0x4B63C8`은 8칸 `0x632CA0[i]`를 같은 값(ebp)으로 채우고 0번 행만 사람, 나머지 행은 `+2`=1(컴퓨터/없음)로 둔다.
- 정적 스캔(원본 `.text` 전체, 이식판 전 실행 섹션): `GetAsyncKeyState`로 방향키를 읽는 곳은 인게임 스크롤 `0x41D09F` 하나다. VK 0x25~0x28 레지스터/메모리 비교·스위치에서 대기실 처리기는 찾지 못했다.
  WM_KEYDOWN(0x100) 비교 15곳 중 확인한 `0x43A520`/`0x43A5B8`은 네트워크 메시지 처리다. → **사용자가 쓰는 정확한 입력 경로는 미확정(UNKNOWN)**. 키를 누르고 있는 시간이 0인 `xdotool key` 탭을 놓쳤을 가능성도 남는다.
- 결론: 하네스 BLOCKED는 사실로 확인했다. 실제 입력 경로를 계속 찾는 것은 한 lap 범위로 제한하고, 실패하면 게임 자체 로비 갱신 경로를 쓰는 재현으로 넘어간다(§5).

## §5 다음 work: H-G6s (Sonnet work 1 lap, 하네스만, 제품 패치 불변)

`tools/g6_shift_click_probe.py`에 `--seat-method` 값 2개(`keys-held`, `lobby-snapshot`)를 추가한다. 기존 `slot0`/`keys` 동작은 byte/결과가 바뀌지 않게 하고 테스트로 고정한다. 대상은 P(이식판) lobby-only부터.

**A. 실제 입력(먼저, lobby-only run ≤3회, 각 약 1분)** — 대기실(ps7 단계, 확인 클릭 전)에서 포커스 3종 {없음, 내 이름 줄(약 40,50) 클릭, 내 번호칸(40,78) 클릭} × 누르고 있는 방향키(`xdotool keydown <k>`; 0.25초; `keyup`) Right·Down·Left·Up.
매 입력 뒤 좌측 패널 캡처 diff(커서 bbox 제외)와 raw 덤프 `0x632C9C..0x632F80`·`0xC0D0F4`·`0xB63FC4`를 직전과 비교해 기록한다.
- **S-1 PASS** = 내 이름이 k행(k≥1)으로 옮겨진 화면 + 표 바이트 변화, 확인 뒤 `local_at_ps3==k`(local/owner 직접 쓰기 0).

**B. 게임 자체 로비 갱신 경로(A 실패 시 같은 lap)** — 확인 클릭 전, 현재 `0x632C9C`(0x170바이트)를 읽어 0번과 k번 칸을 바꾼 사본을 만든다(k=2 = "없음" 행, 컴퓨터 행 1은 그대로).
바꿀 칸은 `0x632CA0` dword[i], `0x632CC0` 6바이트 행[i], `0x632CF0` dword[i], `0x632D94` 15바이트 이름[i]이다. 사본을 `0x632E0C`에 쓰고 `[0xC0D0F4]=1`로 둔다.
쓰기 전에 원래 값을 raw로 남긴다. 혼자하기라 `0x632CA0` 8칸이 모두 같으면, 바꾸기 전에 0..k-1 칸에 무엇을 넣어야 `0x43AF40`이 k를 고르는지 관측값을 근거로 정하고 그 판단을 기록한다.
- **S-2 PASS** = 5초 안에 플래그가 0으로 돌아오고(게임이 복사함), `0x632C9C`가 사본과 같고, `[0xB63FC4]==k`를 게임이 직접 쓰며, 패널 k+1행에 내 이름이 보인다.
  이어서 확인 → ps3에서 `local_at_ps3==k`가 60초 유지되고, "게임을 떠나 나갔습니다" 문구 0, owner k 시작 유닛 ≥1, 입력 없이 30초 동안 owner k 유닛 위치·명령 변화 0(AI 비조종).
- **S-1 또는 S-2 PASS 뒤 같은 lap**: 새 seat method로 G6-1~G6-5를 O·P·C@k로 다시 실행한다(fixture owner=k, 카드 lap976 §4 표 그대로, slot0 poke 0).
  기대값: O·P `[1,1,1,1,1,1]`, C `[1..6]`, G6-2/3/4/5 lap977과 같음. C@0 결과는 lap977 값을 그대로 쓴다.
- 반증·중단: (i) S-2에서 플래그가 소비되지 않거나 local이 바뀌지 않음 → `0x4B7700` 미호출이므로 BLOCKED. 추측 poke로 넘어가지 않는다.
  (ii) local=k인데 O/P G6-1이 정상 증가 → 정적 원인 반증, middle로. (iii) ps3 불안정·떠남 문구·AI 조종 → emulation 부적합, 기록 후 middle로.
- 둘 다 BLOCKED이면 G6은 PASS(partial, emulation)로 남고, G7과 함께 사용자 답(APPROVALS 질문)을 기다린다. G1 H-F 재개 여부는 다음 middle이 판단한다.
- 실행 위생: 각 run은 game 사본을 정리하고 prefix를 남긴다. 회차 끝에 이번 run prefix의 archive 여부를 기록한다. 디스크 여유가 20GiB 미만이면 실행 전 확인한다.

## §6 사용자 질문(비차단, APPROVALS 큐)

혼자하기 대기실에서 1P가 아닌 자리로 옮길 때 정확히 무엇을 눌렀는지(예: 어느 칸을 먼저 클릭했는지, 방향키를 누르고 있었는지, ESL 판인지 원본인지).
답이 오기 전에는 §5 A/B로 진행한다.

## §7 디스크

lap977 prefix 20개(약 11.4GB, 모두 probe-result cleanup 프로세스 0·game 제거 증거 있음)를 `local/maintenance/20261005_lap978_g6_prefix_archive/archive.py`로
lossless archive → 전파일 내용/metadata 검증 → 첫 1개 실제 full restore MATCH → 해당 prefix만 제거한다. manifest/output/raw/PNG는 그대로 둔다. 결과 수치는 STATUS에 적는다.

# 2026-10-07 | lap1138 | G1 middle — 루프 교착(root 전달문 → middle 재기동) 진단, STOP 관측으로 정지, H-TM0 보강

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 게임 코드·하네스·테스트 변경 0, 커밋 0.
- 입력: INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1136 재요청 대기). STATUS 다음 = work H-TM0(lap1137 §3).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: 없음(재실행 0).

## 1. 진단 — middle이 연속으로 다시 뜨는 이유

- `loop/loop.sh` 641~653행: 일반 세션이 끝났을 때 `loop/ESCALATE_SOL`이 있으면 `rc=75`, 829행에서 `LOOP DOWN | middle-review-pending`으로 끝난다. root 드라이버는 이 종료를 보고 30초 뒤 `--role=middle`을 다시 띄운다(`logs/loop-2026-10-07.log`: lap1136 11:09:15 → lap1137 11:09:45 → lap1138 11:16:28).
- 현재 `loop/ESCALATE_SOL`(lap1136, SHA256 `6d8d1f3f48a8…`, 14줄)은 middle 검수 요청이 아니라 **root에게 보내는 시험판 전달문**이다. middle은 이것을 처리할 수 없으므로(전달은 마일스톤 경계·root 몫), 파일이 남아 있는 한 middle 무실행 회차가 반복된다. lap1104/1105 선례도 같은 모양이었고 root가 00:21에 전달한 뒤 풀렸다.
- 이번 회차 초반에 이 교착을 끊으려고 원문을 byte 일치로 `docs/history/laps/`에 복사한 뒤 `loop/ESCALATE_SOL`을 지웠다. 그 직후 **root가 11:16:59에 `loop/STOP`(빈 파일)을 만든 것을 확인**했다. STOP이 있으면 이번 바퀴 뒤 루프가 내려가므로 교착은 이미 끊긴다. 그래서 root가 처리할 입력을 건드리지 않도록 `loop/ESCALATE_SOL`을 같은 바이트·mtime(`cp -p`, SHA256 `6d8d1f3f…` 일치)으로 되돌리고 중복 사본은 지웠다. 순변경 0.
- root에 남기는 제안(구현 아님): root 대상 전달문은 `ESCALATE_SOL` 대신 별도 이름을 쓰거나, root 드라이버가 `ESCALATE_SOL` 첫 줄의 수신자(`→ root`)를 보고 middle 재기동 대신 root 처리를 하도록 하면 같은 교착이 다시 생기지 않는다. `loop/loop.sh` 수정 여부는 root 판단이다.

## 2. root 전달 사전 확인(읽기만)

- 스테이징 공유 temp `20261007_lap1135_work_htr2/user_test_staging/` 4파일 SHA256 재계산 = ESCALATE_SOL 2항 값과 4/4 일치: `_inmm.dll` `6cbb12ac…`, `g1_trial_direct.bat` `2da323e8…`, `g1_trial_via_dxwnd.bat` `29a35d2e…`, 안내문 `f6593f5c…`.
- `260921_temp/`에는 lap1103판 `G1_1600x1200_시험판_20261007/`만 있고, 권장 새 폴더 `G1_1600x1200_시험판_20261007_lap1135/`는 아직 없다 = 전달 미처리. 디스크 여유 123G.

## 3. 무실행 3회째 판정(PROMPT ③, middle = Sol/Opus 역할)

- lap1136·1137·1138 middle은 모두 제품 코드·바이너리·실행 증거가 늘지 않았다. 원인은 G1 방향 문제가 아니라 §1 교착이다.
- **판정: G1 계속. 다음 회차는 work(Sonnet) H-TM0이며 middle 재계획을 끼우지 않는다.** 사양은 lap1137 §3 그대로이고, 아래 두 가지만 덧붙인다.
  1. **캐릭오픈방 외부 접속 가드.** 원본 EXE는 `WSOCK32.dll`·`DPLAYX.dll`을 정적 import한다(`objdump -p`). 캐릭오픈방이 DirectPlay/소켓 방을 여는 화면일 수 있다. 하네스에는 네트워크 격리가 없다(무권한 `unshare -n` 불가 확인). 그래서 캐릭오픈방은 4개 중 **마지막**에 돌리고, 클릭 1회 뒤 추가 입력 없이 관측만 한다. 서비스 공급자 선택·접속 창이 뜨면 그 화면 HD만 기록한다. probe 로그나 Wine trace에서 소켓 생성·접속 시도가 보이면 그 버튼은 `BLOCKED(외부 접속)`로 두고 다시 실행하지 않는다.
  2. **좌표 확인.** 하네스 상수 `LOAD_MENU = (296,505)`(`tools/g1_saved_scene_probe.py` 66행)와 lap1137 표의 불러오기 `(302,505)`는 6 px 다르다. 네 버튼 좌표는 첫 run의 PS9 캡처로 버튼 안쪽인지 확인한 뒤 쓴다(어긋나면 하네스 결함 → 고쳐서 재실행).
- 이번 STOP이 풀린 뒤 사용자 G1 시험 결과가 먼저 오면 그것이 최우선이다.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check` SKIP: 문서만 변경, C·하네스·테스트 source는 lap1133 full PASS 1786 그대로.

## 다음 행동

STOP 유지(사용자/root 해제 전 새 바퀴 없음). root: `loop/ESCALATE_SOL`(lap1136) 시험판 전달 처리. 재개 뒤 work(Sonnet): H-TM0(lap1137 §3 + 이 기록 §3 보강).

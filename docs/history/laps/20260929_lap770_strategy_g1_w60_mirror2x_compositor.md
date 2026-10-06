# 2026-09-29 | lap 770 | 목표 G1 (재착수 전략)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(effort 세션 비노출), 지정 역할 strategy
  (계약 모델 Fable/Astra 자리를 공개 대행). 게임 실행0, 제품/하네스 source·binary 변경0, 커밋0.
- 가설 / 사용자 관찰: 18:45 운영자 "G1 재착수 전략 1회 — lap607~612 기록과 DESIGN G1 조건을 읽고
  BLOCKED(attribution)를 넘는 새 구현 경로 1개를 work 카드로". 가설: 게임 논리 800 유지 + 렌더러 `0xE5BF18`
  픽셀 프리미티브를 버퍼 포인터 교체로 재호출해 1600 미러에 2배로 그리고, present를 caller가 아니라 내용으로
  골라 primary에 올리면 구도 동일성과 2배 디테일 경로를 동시에 얻는다(W60).
- 예상 PASS / FAIL 조건: 원본 bytes로 present thunk와 프리미티브의 버퍼/stride 접근이 확인되면 FEASIBLE 후보로
  work 카드 발행. 불일치·충돌이면 카드 없이 승격.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W60_MIRROR2X_COMPOSITOR_LAP770.md`
  (SHA256 `c02c9f8abd621840cb05d7683fd3e33f02abd0a309913b0b6bb1056a45d6728b`), 이 기록, `docs/STATUS.md` 압축·갱신
  (원문 `docs/history/20260929_status_lap770_precompaction.md` SHA256 `e966db8c…5fda`, 125줄),
  `docs/feedback/INBOX.md` 통지 1항. uncommitted. 진입 HEAD `a944d6ca`.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(read-only). 후보·실행·fixture 없음(SKIP).
- 실행 명령: `sha256sum`; `objdump -d -Mintel --start-address=0x00469350 --stop-address=0x0046937c`;
  `objdump -d | grep -A6 "mov ecx,0xe5bf18" | grep call | uniq -c`; 프리미티브 7개 진입부 0x160바이트에서
  `0x1514]`/`0x10]` 참조 계수; `grep` bridge `NATIVE_2X_PRESENT_RETURN`; 참고 `rendering.md` §3.3·§4.6~4.7,
  `FUN_004332f0_blit_primitives.md`, `g5_minimap_click_router_lap762.md` 읽기.
- 측정값 / 판정:
  - thunk `0x00469376: ff 50 1c`, `0x00469379: c2 18 00` — lap610~612 N224와 일치.
  - `mov ecx,0xe5bf18` 호출 773곳, 대상 함수 수십 개(상위 `0x464ec0`84·`0x465080`83·`0x463d30`70·`0x466d50`36…).
  - `0x466d50`(버퍼 1/stride 6), `0x4664d0`(3/8), `0x466540`(3/9), `0x466ea0`(1/6), `0x466280`(3/8),
    `0x465e80`(2/4), `0x465b30`(3→4/7): 매 호출 `[ecx+0x1514]`·`[ecx+0x10]`을 읽는다 → 버퍼 교체 재호출 가능.
  - bridge `SYW2_G1_NATIVE_2X_STRETCH` 조건이 `0x0049273F`(메뉴 PS5/7/9 present)에 묶여 있음 → N224 원인 재확인.
  - 마우스는 WndProc WM 메시지 + `GetCursorPos`(DirectInput 근거 없음) → 입력 1/2 변환은 bridge에서 가능.
  - **판정: W60 채택(정적 FEASIBLE 후보, 런타임 UNKNOWN).** 새 근거 N225: 프리미티브가 매 호출 버퍼 포인터를
    읽으므로 원본 코드를 재구현하지 않고 2배 미러를 만들 수 있다. N226: expected800 대조로 감싸지 않은 쓰기를
    자동 대체하므로 정확성이 프리미티브 완결성에 의존하지 않는다(커버리지는 지표).
  - Fast: 문서 반영 뒤 `python3 checks/context_limits.py` `CONTEXT_PASS`, `bash checks/safety.sh check`
    `SAFETY_PASS`. 게임 실행·source 변경0이라 전체 `make check`는 재실행하지 않았다(lap769 1136 passed가 현재 source).
  - APPROVALS 252줄 → 208줄 압축: 원문 `docs/history/20260929_approvals_lap770_precompaction.md`(SHA256
    `c352265a…c4bb6`, 252줄), 종결된 G5 lap762~763 정보제공 47줄(구간 SHA256 `d0f3ab16…1929`)만 포인터로 대체.
- 회귀 / 남은 위험 / 승인 상태: 입력 parity(N222)·재호출 부작용·하드웨어 커서·GDI 글자 stale·성능·1080p 표시
  정책이 미측정. W60 `FEASIBLE`도 G1 완료가 아니다(S3 디테일 증명·프리미티브 확장·실제 입력 대조·사용자 승인
  필요). 무증거 회차 lap769·770 2연속 → 다음은 반드시 work 실행. 사용자 승인 없음.
- 다음 한 가지: work(Sonnet5/Luna high)가 카드 §2 S1→S2를 구현·회귀·`make check`·격리 실행으로 §3 판정.

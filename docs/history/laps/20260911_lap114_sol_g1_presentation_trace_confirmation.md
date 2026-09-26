# 2026-09-11 | lap 114 | G1 presentation trace ABI confirmation

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier; `loopctl models`의 repo routing은
  Codex `gpt-5.6-sol`/high다. 현재 세션 backend의 별도 attestation은 없어 실제 model ID를
  추정하지 않았고 exit 0을 판정 근거로 쓰지 않았다. 게임 코드 hands-on 수정/runtime 재실행 없음.
- 가설 / 사용자 관찰: lap113의 ABI 수리와 native regression이 header/원본 caller/raw와 독립적으로
  일치하면 수리만 ACCEPT하고, 보존 run의 pointer timeout은 별도 측정 가능한 work 카드로 분리한다.
- 예상 PASS / FAIL 조건: source/private SHA·caller/IID·header·source/test/build/raw를 재현하고
  targeted/doctor/Fast/safety가 PASS하면 ABI 수리 ACCEPT. complete present chain/PS3가 없으면
  runtime/G1은 BLOCKED이며, 근거 충돌 또는 필수 gate 실패면 새 escalation으로 중단한다.
- 변경 파일 / source fingerprint / 커밋: 게임/helper/tests/binary/fixture/좌표/timeout 변경 없음.
  판정 문서 `docs/plans/20260911_lap114_g1_pointer_position_diagnostic_card.md`, `docs/STATUS.md`,
  본 이력만 추가·갱신하고 소진 marker `loop/ESCALATE_SOL` SHA
  `24fae6b945bbf78a6921232074bda9ec0da8b3953f817b3e039a6d2053ce03ba`는 아래 원문 보존 후 제거했다.
  최종 plan SHA `c896bc4f57380ffbb545a08dfcf2412482a11f6e2c123addc8fe16af7b8caa02`, STATUS SHA
  `123ddefd0462e0a13fb15a4802cf581c8b6c1211b0dc037bcf1cfa3d246ef086`; `LOOP_ALLOW_COMMITS=0`,
  uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / fixture: source/private/runtime-copy EXE 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, source/private `cmp=0`, PE32.
  lap113 whole copy/new Win32 prefix/private Xvfb run만 읽기 전용 검수했다. 새 runtime·후보·플레이어·
  지도·군대·fixture는 SKIP. 진단 bridge 사용은 명시된 observational fixture다.
- 실행 명령 / 로그 / 캡처: `sha256sum`, `cmp`, `file`, `objdump -d/-s`, MinGW `ddraw.h`, `jq`, `rg`,
  preserved PNG 2장 육안 대조, `pytest -q tests/test_direct_draw_abi.py`, 저장소 밖
  `/tmp/syw2_g1_lap114_sol_build.HeuqM9` fresh build, `make doctor`, `make check`, safety.
  live trace/24k/144k/멀티는 SKIP했다.
- 측정값 / 판정: 원본 caller는 arg2=`edi` output/arg3=`0x004E5928` IID이고 IID bytes와 header ABI,
  source typedef/hook/forwarding이 일치한다. source/test/manifest/raw/evidence/verdict/provenance SHA는
  lap113 기록과 전부 일치했다. targeted **3 passed**; fresh DLL build PASS SHA
  `fc381b62824e44f0d1f8737ea592ed9b3262fb1850b18b5e803d2bc3ef5cb77d`(기존 unrelated warnings),
  doctor top `ok=true`, `make check` **148 passed**, Ruff/compileall/mypy/context, safety PASS.
  raw 70 events의 IID=`15E65EC0-...`, DD=`0x01E6D080`, HRESULT=0은 수리를 지지한다.
- 판정 / 남은 위험: **ABI repair ACCEPT; runtime/G1 BLOCKED**. 화면은 PS9→PS7 및 800×600 content만
  증명한다. 두 Blt는 null-source clear형이고 summary/PS3/non-clear present/2x 후보가 없다.
  timeout 직전/직후 cursor 좌표가 없어 원인을 확정하지 않았으며 crash로 바꾸지 않았다.
- 다음 한 가지: 새 Luna/high가
  `docs/plans/20260911_lap114_g1_pointer_position_diagnostic_card.md`만 수행한다. exact pointer 좌표를
  관측·검증하는 helper와 회귀를 최소 구현하고, 필수 게이트 뒤 fresh private trace를 최대 1회 실행한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

lap111 ABI root-cause·lap112 gate recovery·lap113 repair evidence를 누적한 marker였으며, 다음 핵심
요청은 새 Sol/high가 lap113 source/test/build/raw를 독립 검수하고 runner/input automation 진단 카드의
필요 여부를 결정하라는 것이었다. 전체 byte-for-byte 입력 SHA는 위에 기록했고, marker의 lap113
evidence와 blocker 원문은 `docs/history/laps/20260911_lap113_luna_g1_presentation_trace_abi_repair.md`
및 이 기록의 검수 항목에 provenance를 보존했다.

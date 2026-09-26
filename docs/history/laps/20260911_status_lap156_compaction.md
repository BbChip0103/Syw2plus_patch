# STATUS pre-compaction snapshot — lap 156

dxwrapper 2배 출력·입력 성공과 실제 종료 실패 판정 직후 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `16794f485dd9eeb44b6e072f91011b74be5217da8840fe8667a37dd4d3905086`
- line count: `168`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

목표 G1~G4는 모두 제품 단위로 미완료다. 현재 최우선은 G1: 원본 800×600의 UI·스프라이트
구도를 유지한 1600×1200 정수 2배 출력과 입력 일치다. G2는 전비 5000 숫자 패치만 있으며
8인 부하/개체 풀·메모리 확장 증명이 없고, G3 16인과 G4 길찾기·AI는 구현 전이다.

lap146의 fresh diagnostic runtime은 PS9→PS3, owned WM_CLOSE→process exit→DLL detach,
최종 summary 1개, raw 보존, validator, cleanup을 모두 통과했고 lap147 middle이 독립 확인했다.
이 진단 경로는 원본 content 800×600이며 제품 2배 출력 자체는 아니었다.

lap148은 pinned `ddraw.dll`/`dxwrapper.dll`과 private config-only 후보를 사용해 실제 root/client
1600×1200, scale 2.0×2.0을 처음 확인했다. 논리 DirectDraw surface/게임 구도는 800×600으로
유지됐다. 하지만 입력을 `[184,560]→[368,1120]`으로 선변환한 클릭이 PS9→PS7을 만들지
못해 BLOCKED했다. 후보·원본·로그·trace는 보존했고 private config는 byte-exact 원복했다.

lap149 Opus/high는 증거 SHA, 적용 config, 원복, pinned DLL/EXE를 독립 재계산했다. 대조군은
800×600 child에서 `(184,560)` 클릭으로 PS7 PASS였고 후보는 1600×1200 client이지만 논리
surface가 800×600 그대로이며 wrapper가 mouse cursor를 hook한다. 따라서 프로필 폐기보다
**선변환 없는 논리 좌표 입력 계약을 1회 검증**하는 것이 다음 방향이다. Astra 분기는 아직
불필요하다. Opus 세션은 Fast/safety 실행 권한이 없어 이를 SKIP했고, 종료 후 STATUS 186줄
안전 위반이 발생했다. 원문은 아래 pre-compaction snapshot에 SHA와 함께 보존했다.

lap150 hands-on은 승인된 단일 입력 계약 변경을 구현했다. presentation trace는 client
800×600 또는 1600×1200을 허용하고, logical surface 800×600·마지막 mode·primary descriptor를
증거로 검사하며, `(184,560)`를 선변환 없이 보낸 뒤 효과 확인 전 `SENT`를 남긴다. targeted 80,
Fast 179, Ruff/compileall/mypy/context/safety는 PASS했다. 그러나 fresh helper/bridge 뒤
지정 source `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re`가 root에
`syw2plus_original.exe`를 갖지 않아 `prepare`가 RC2로 BLOCKED됐다. 실제 파일은 그 아래
`Syw2plus/syw2plus_original.exe`에 있어 source 계약의 중간 판정 없이는 재시도하지 않는다.

lap151 middle은 lap150 blocker를 독립 판정했다. `runtime_env.prepare`의 source 계약에는 결함이
없다. 계약은 "root가 `syw2plus_original.exe`를 직접 포함하는 게임 설치 디렉터리"이고 커밋된
`DEFAULT_SOURCE`(`tools/runtime_env.py:155`)가 이미 중첩 경로다. 성공한 과거 prepare(lap73/113/
115/136)는 모두 중첩 경로를 썼고, repo-root 문자열은 lap148·lap150 기록에만 있으며 저장소 어느
문서도 그것을 지시하지 않는다. 따라서 RC2는 **계약 결함이 아니라 호출 입력 오류**이며 코드 변경은
불필요하다. 승인된 입력은 `--source` 생략(= 커밋된 기본값)이다. lap150 변경 4개 파일 SHA는
재계산 결과 완전 일치했다. 이 세션은 실행 권한 거부로 Fast/safety/원본 해시를 SKIP했다.

lap152 hands-on은 승인된 기본 source로 fresh helper/bridge·private copy/prefix/display를 만들고
`g1-presentation-trace`를 정확히 1회 실행했다. 선변환 없는 `(184,560)`으로 PS9→PS7→PS3,
summary 1건, dropped 0, process exit/DLL detach/validator/owned cleanup은 PASS했다. 그러나
root/screen만 1600×1200이고 content child·physical client·캡처는 800×600, scale 1.0이었다.
private `dxwrapper.ini`는 old SHA 그대로여서 승인 candidate가 이 run에 적용되지 않았다. 제품 G1
physical 2x는 FAIL/BLOCKED이며, 중간 tier가 config 적용 경계를 판정할 때까지 재실행하지 않는다.

lap153 middle은 lap152가 요청한 config 적용 경계를 판정했다. old pin `918e…a5a2`는 기계 강제되고
3개 변경 라인은 각 1회·비중첩이며 `restore()`는 fail-closed여서 **바이트 계약은 승인**이다.
그러나 미적용은 호출 오류가 아니라 **하네스 결손**이다: `apply()`는 존재하는 target을 거부해
`game/dxwrapper.ini`에 적용할 수 없고, 커밋된 코드 어디에도 설치 경로가 없다. 게다가 커밋된 4개
런타임 경로가 `WINEDLLOVERRIDES=ddraw=b`를 고정하고 lap152 module map에는 Wine builtin ddraw만
매핑돼 있어, 설치했더라도 dxwrapper가 로드되지 않는다. candidate `f0ce…6785`는 아직 코드/테스트에
pin되어 있지 않다.

lap154 hands-on은 승인된 candidate를 fresh private copy에 설치하고 `--dxwrapper-2x` opt-in에서만
`WINEDLLOVERRIDES=ddraw=n,b`를 사용하도록 최소 배선을 구현했다. candidate `f0ce…6785` 설치 후
private `game/ddraw.dll` 로드, logical 800×600, client 1600×1200(scale 2×2), 선변환 없는
`(184,560)` 입력의 PS9→PS7→PS3와 1600×1200 capture를 PASS했다. 종료 시 ini는 old
`918e…a5a2`로 byte-exact 원복되고 sidecar 제거/owned cleanup도 PASS했다. 그러나 native
dxwrapper 실행은 event 384, summary 0, process exit 미관측으로 90초 finalization timeout이어서
G1 runtime은 BLOCKED이며 `loop/ESCALATE_SOL`에 승격했다. 같은 run 재실행 금지.

lap155 middle은 lap154 finalization blocker를 판정했다. **관측 결손이 아니라 실제 종료 실패다.**
실행 로그에 close helper `status PASS / match_count 1 / matched_thread 280`(게임 render thread)이
남아 있어 WM_CLOSE는 전달됐고, `surface_release`는 25건(상세 상한 256 미만 = 누락 아님)뿐이라
baseline의 종료 시 11,667건 해제 경로에 진입조차 못 했다. private `game/dxwrapper-*.log`는 close
직후 20:04:56.734–.735에 `Lock2 … DDERR_SURFACELOST` 100건을 남기고 멈췄고, 이후 약 78초간
trace·로그 무증가·프로세스 미종료였다. summary 요구는 옳으므로 완화/timeout 증가는 금지한다.
부수적으로 실패 경로가 close transport 증거와 wrapper 로그를 산출물에 남기지 않는 관측 결손이 있다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Astra는 큰 분기·반복 교착에서만 필요 시 high로 올리고 대략 10개 work/middle lap당 1회
이하를 운영 기준으로 삼으며 정기 자동 호출하지 않는다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료/BLOCKED | lap154 physical client 1600×1200(scale 2×2), 논리 800×600, 입력·PS3까지 PASS; lap155 판정=native dxwrapper 종료 실패(device lost 이후 teardown 미진입), 관측 결손 아님 |
| G2 8인 전비5000 안정성 | 미완료 | 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 구현·검증 없음 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

work tier(Luna/Sonnet5)가 승인된 **probe P1 한 개**만 구현하고 정확히 1회 실행한다: 실패 경로에
close transport 증거 기록, close 직후+5초 뒤 소유 프로세스 상태/CPU 표본 2회, private
`dxwrapper-*.log` 산출물 복사. 목적은 "살아서 재시도 spin"과 "차단/교착"을 가르는 것이다.
validator 완화·timeout 증가·config 프로필 변경·이전 run 재사용은 금지한다. 지시와 PASS/FAIL 분기는
`docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`에 있다.

## 지금 막힌 것 (Blockers)

- lap152는 입력 PS9→PS7→PS3와 finalization을 같은 run에서 통과했지만 client는 800×600이었다.
  제품 G1의 client 1600×1200 + scale 2×2는 여전히 미검증이다.
- lap148 inline runtime은 재사용 명령이 아니므로 다음 work가 최소 재현 가능한 경로를 남겨야 한다.
- 원본/제품 EXE·DLL/assets/baseline/golden 변경 금지. 보호 원본 EXE SHA256은
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다.
- 같은 run/prefix/display 재사용, 실패 후 임의 재시도, validator 완화, summary 합성 금지.
- 두 builder의 `--out-dir`은 호출 전에 존재하면 안 된다. fresh parent만 먼저 만든다.
- lap150 `prepare` BLOCKED는 lap151에서 해소됐다(입력 오류, 계약 결함 아님). 승인된 source 외
  다른 경로를 탐색하지 않는다. 남은 RC2 후보는 source 트리 내부 symlink이며 실행 전 확인한다.
- 기록된 명령 문자열을 커밋된 코드와 대조 없이 재현 근거로 쓰지 않는다. lap148의 부정확한
  `--source` 기록이 lap150 RC2로 전파됐다.
- G2 8인5000, G3 16인, G4 AI/pathfinding 및 사용자 마일스톤 승인은 모두 미검증이다.
- lap154에서 candidate pin, private-copy positive allow-list install/uninstall, opt-in `ddraw=n,b`,
  설치/로드/원복 증거는 PASS했다. 남은 blocker는 native dxwrapper에서 게임이 close 후에도 종료하지
  못하는 것이다(lap155 판정). config 프로필·입력 계약을 원인으로 의심해 되돌리지 않는다.
- 실패 경로가 close transport 결과와 wrapper 로그를 산출물에 남기지 않는다. P1에서 함께 수리한다.

## 검증 상태

- lap146~147(원문 `docs/history/laps/20260911_lap14*.md`): diagnostic runtime 651 events,
  summary 1, dropped 0, validator/process exit/DLL detach/cleanup PASS와 lap147 독립 확인;
  Fast 173 PASS. 모델 라우팅/console Wine fixture 관련 19 PASS, Ruff/compileall/mypy/context/safety PASS.
- lap148~149: config patcher pin `918e7043...a5a2`→`f0ce9e64...6785`(정확히 3 changes, hash 거부,
  byte-exact restore) PASS, fresh runtime root/client 1600×1200 PASS·논리 800×600·입력 FAIL;
  lap149가 SHA 재계산 후 방향을 **입력 좌표 계약 수리**로 판정. Fast 177/safety/doctor PASS
  (lap149는 실행 권한 부재로 Fast/safety/PNG hash SKIP).
- lap150~151: input-contract 변경에 targeted 80/`make check` 179/safety PASS, `prepare` RC2는
  lap151이 **호출 입력 오류**(계약 결함 아님, 4/4 SHA 일치, symlink·protected-root 재검토 PASS)로
  판정. lap150 runtime/doctor-runtime과 lap151 실행 검사는 SKIP.
- lap152: source symlink 빈 출력, 원본/private EXE SHA pin PASS; `make check` 179 passed,
  `make doctor`/`doctor-runtime`/safety PASS. fresh runtime 1회에서 root 1600×1200이나
  content/client/capture 800×600(scale 1×1), 입력 PS9→PS7→PS3, summary 1, dropped 0,
  validator/finalization/cleanup PASS. 제품 G1 2x는 BLOCKED; evidence와 raw 해시는
  `docs/history/laps/20260911_lap152_luna_g1_presentation_runtime_800x600_block.md` 및
  `loop/ESCALATE_SOL`에 보존.
- lap153 middle: private copy 재해시 `dxwrapper.ini` `918e7043...a5a2`(= 미적용 확인),
  `ddraw.dll` `3bc7230d...bd19`, `dxwrapper.dll` `96c44319...e8fe`; lap152 evidence module map은
  Wine builtin ddraw 7건/private 0건; `grep -rn dxwrapper_config tools/ checks/ tests/ Makefile`
  빈 출력. 실행 권한 거부로 `make check`/`safety.sh`/원본 EXE 해시/candidate 재계산은 SKIP.
- lap154: candidate install/loaded private ddraw/config restore PASS; fresh runtime client
  1600×1200(scale 2×2), logical 800×600, PS9→PS7→PS3 and 1600×1200 captures PASS. Native
  finalization BLOCKED (`event_count=384`, summary 0, process_exited false, timeout 90s), cleanup
  PASS. `make check` 182 passed, `SAFETY_PASS`, Ruff/compileall/mypy/context/doctor-runtime PASS.
  Evidence/raw/provenance/verdict and changed-file hashes are in
  `docs/history/laps/20260911_lap154_luna_g1_dxwrapper_install_finalization_block.md` and
  `loop/ESCALATE_SOL`.
- lap155 middle: lap154 산출물·변경파일 SHA 9/9 재계산 일치; provenance의 `ddraw=n,b`/installed
  `f0ce…6785`/원복 `918e…a5a2`/private `game/ddraw.dll` 로드/client 1600×1200·logical 800×600
  재확인 PASS. 1차 증거 2건 추가 확인: 실행 로그의 close helper PASS 1줄, private
  `game/dxwrapper-syw2plus_original.log`(15900 bytes, mtime 20:04:56.735, `DDERR_SURFACELOST` 100건).
  baseline lap152 summary는 `blt_fast` 256+1801, `surface_release` 256+11411, detach/flush complete.
  실행 권한 거부로 `make check`/`safety.sh`/작업 디렉터리 밖 원본 EXE 해시는 SKIP. 코드 변경 없음.
- STATUS pre-compaction SHA `9cd56fef4d7ad75c961a96d0ad87e58e070554ad40d400969657c2a5f9bfb39c`;
  snapshot 본문 SHA 동일 여부 확인 완료.

## 바퀴 기록

- lap2~141: `docs/history/laps/` 및 이전 STATUS compaction 원문.
- lap142~149: 각 `docs/history/laps/20260911_lap*.md` 원문.
- 최신 snapshot: `docs/history/laps/20260911_status_lap150_compaction.md`.
- lap148: `docs/history/laps/20260911_lap148_luna_g1_config_2x_block.md`.
- lap149: `docs/history/laps/20260911_lap149_middle_g1_config_2x_input_contract_confirmation.md`.
- lap150: `docs/history/laps/20260911_lap150_luna_g1_input_contract_prepare_block.md`.
- lap151: `docs/history/laps/20260911_lap151_middle_g1_source_root_contract_confirmation.md`.
- current handoff: `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md` (lap151 부록 포함).
- escalation: lap150 원문은 `docs/history/laps/20260911_lap150_escalate_sol_original.md`,
  lap152 원문은 `docs/history/laps/20260911_lap152_escalate_sol_original.md`에 보존했다.
  둘 다 판정 후 제거했으며 현재 미결 escalation은 없다.
- lap152: `docs/history/laps/20260911_lap152_luna_g1_presentation_runtime_800x600_block.md`.
- lap153: `docs/history/laps/20260911_lap153_middle_g1_dxwrapper_config_apply_boundary_verdict.md`.
- lap154: `docs/history/laps/20260911_lap154_luna_g1_dxwrapper_install_finalization_block.md`;
  원문 escalation은 `docs/history/laps/20260911_lap154_escalate_sol_original.md`에 보존하고
  lap155 판정 후 `loop/ESCALATE_SOL`을 제거했다. 현재 미결 escalation은 없다.
- lap155: `docs/history/laps/20260911_lap155_middle_g1_dxwrapper_finalization_verdict.md`;
  work tier 지시 `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`.
- model routing: `docs/history/20260911_model_routing_update.md`.

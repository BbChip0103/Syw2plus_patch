# 2026-09-11 | lap 155 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code / `claude-opus-5` / high;
  중간 tier(진단·계획·확인). 게임/하네스 코드는 이 바퀴에서 수정하지 않았다.
- 가설 / 사용자 관찰: lap154의 `summary 0 / process_exited=False`가 (H-A) trace finalization
  결선의 관측 결손인지, (H-B) native dxwrapper 경로에서 게임이 실제로 종료하지 못한 것인지 판정한다.
- 예상 PASS / FAIL 조건: 보존 산출물만으로 H-A/H-B를 가르는 독립 증거가 나오면 판정 PASS,
  근거가 갈리면 UNKNOWN으로 남기고 관측 추가 probe를 지정한다. 재실행/timeout 증가/validator 완화 금지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 코드 변경 없음. 문서만 추가·갱신
  (`docs/STATUS.md`, 본 기록, `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`,
  `docs/history/laps/20260911_lap154_escalate_sol_original.md`). commit 없음(`LOOP_ALLOW_COMMITS=0`).
  이번 바퀴 문서 SHA: `docs/STATUS.md` `16794f48…905086`,
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md` `fc9e54a0…8c1461`,
  `docs/history/laps/20260911_lap154_escalate_sol_original.md` `7dfd08dc…6aba5d`.
  판정 후 `loop/ESCALATE_SOL`은 원문 보존 뒤 제거했다(미결 escalation 없음).
  lap154 변경 4개 파일은 uncommitted 그대로 보존했고 SHA 4/4 재계산 일치:
  `patches/resolution/dxwrapper_config.py` `48d61a6c…37cbaa`,
  `patches/resolution/test_dxwrapper_config.py` `e4cf7ae4…2e1d04`,
  `tools/runtime_env.py` `05a6054e…01cf4b`, `tests/test_runtime_env.py` `782f74eb…2422f`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 재실행 없음.
  검수 대상은 lap154 run `local/runtime/20260911_200415_300054_0`(default two-player random game,
  diagnostic bridge, injection 없음)과 baseline PASS run `local/runtime/20260911_194932_189255_0`
  (lap152, Wine builtin ddraw, client 800×600). G2~G4 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 읽기 전용 재계산만 수행.
  lap154 산출물 5/5 SHA 일치(`trace_install.jsonl` `b50f0032…8c9a`, `trace_raw.jsonl` `8944ada6…1d9f`,
  `evidence.json` `905effd1…c221e`, `provenance.json` `163cdb03…08f5d`, `verdict.json` `5e9903a1…09ca`).
  새로 확인한 1차 증거 2건: 실행 로그 `local/runtime/20260911_200415_300054_0/output/g1-presentation-trace.log`
  의 close helper 결과 1줄, private 게임 디렉터리의
  `game/dxwrapper-syw2plus_original.log`(15900 bytes, mtime 2026-09-11 20:04:56.735).

## 판정 (중간 tier)

**H-B 채택: trace 관측 결손이 아니라 native dxwrapper 경로의 실제 종료 실패다.** 근거 5가지.

1. **close 전송은 성공했다.** 실행 로그에 helper 결과가 그대로 남아 있다:
   `{"status":"PASS","requested_pid":276,"matched_hwnd":"0x00020056","matched_thread":280,`
   `"match_count":1,"post_result":true,"post_error":0}`. `matched_thread=280`은 trace의
   DirectDraw 호출 thread(`thread_id:280`)와 같고 top-level 창은 정확히 1개였다. 즉 WM_CLOSE는
   게임 자신의 메인 창/스레드에 전달됐고, wrapper가 별도 창을 만들어 가로챈 정황은 없다.
   `_finalize_presentation_trace`는 close 실패 시 다른 예외를 던지므로(`owned Win32 close transport
   failed`), 관측된 timeout 문구 자체가 close 성공을 함의한다(`tools/runtime_env.py:894`).
2. **게임은 종료 teardown을 시작조차 하지 않았다.** 상세 기록 상한은 method당 256이다
   (baseline summary: `blt_fast` detailed 256 + aggregated 1801, `surface_release` detailed 256 +
   aggregated 11411). lap154의 `surface_release`는 **25건**으로 상한 미만이므로 누락이 아니라
   실제 호출 자체가 25건뿐이다. baseline은 종료 시 총 11,667건을 해제했다. 즉 lap154에서
   게임은 대량 surface 해제 경로에 진입하지 못했다.
3. **wrapper가 device lost를 자기 로그에 남겼다.** `game/dxwrapper-syw2plus_original.log`는
   20:04:46~48.8 사이 D3D9 device/texture/shader 생성·파괴 후 조용하다가,
   **20:04:56.734–.735에 `m_IDirectDrawSurfaceX::Lock2 Error: failed to lock texture surface!
   DDERR_SURFACELOST`를 100건 연속**으로 남기고 끝난다(100은 반복 메시지 상한으로 보이며
   프로세스 정지의 증거는 아니다). 이는 close 직후 시점이다.
4. **시간축이 일치한다.** live trace 마지막 기록 20:04:54.071(=PS3 캡처 시각), close 전송
   ≈20:04:54–56, SURFACELOST 폭주 20:04:56.73, 이후 20:06:15.27 실패 판정까지 **약 78초 동안
   trace·wrapper 로그 양쪽 모두 무증가, 프로세스 미종료**. bridge는 install gate PASS·384건 기록·
   raw 보존까지 정상 동작했으므로 기록 파이프라인 고장으로 설명되지 않는다.
5. **하네스 요구는 옳다.** `_trace_finalization_state`는 summary 정확히 1건과 그것이 마지막
   이벤트임을 요구하고(`tools/runtime_env.py:818`), summary는 bridge가 프로세스 종료 시 detach에서
   내보낸다(baseline `detach:"complete", flush:"complete"`). 프로세스가 살아 있는 한 summary가
   없는 것이 정상이다. **요구 완화·timeout 증가는 원인을 숨길 뿐이므로 금지한다.**

비판별 항목(오해 방지): trace 말미의 `program_state` 2는 종료 신호가 아니다. baseline도 종료 직전
3↔2↔5를 오갔다. 또한 `blt_fast`는 상한 256에 도달했으므로 **trace 침묵만으로 렌더 정지를 주장할 수
없다**. lap154가 "PS3"로 적은 것은 `evidence.capture.ps_after=3`(메모리 폴링)이며 raw trace의 마지막
tag와 다르지만, baseline도 같은 방식이라 회귀가 아니다.

남은 불확실성(1개): SURFACELOST 폭주가 (i) 게임의 종료 경로가 device lost에 걸려 재시도 루프에
갇힌 것인지, (ii) 종료와 무관하게 발생한 device lost로 렌더 루프가 갇힌 것인지는 보존 산출물만으로
가르지 못한다. 둘 다 "게임이 살아서 Lock 재시도에 갇혀 있다"는 동일 계열이며, 다음 probe의 목적은
이 한 가지를 관측으로 확정하는 것이다.

부수 결함(원인 아님, 별도 기록): 실패 경로에서 `evidence.json`에 `trace_finalization`/
`close_transport`가 기록되지 않아(`tools/runtime_env.py:914`의 예외 경로) 이번 판정은 close 결과를
실행 로그에서 복구해야 했다. wrapper 로그도 private 게임 디렉터리에만 있어 산출물로 수집되지 않는다.
이는 관측 결손이며, 다음 probe에서 함께 수리한다.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  lap154 산출물/변경파일 SHA 재계산 9/9 일치 **PASS**.
  `provenance.json` 재확인 **PASS**: `WINEDLLOVERRIDES=ddraw=n,b`, installed
  `f0ce9e64…2566785`, 원복 `918e7043…aeea5a2`, `loaded_ddraw_modules`=private `game/ddraw.dll`
  (`3bc7230d…62bd19`, 매핑 파일 재해시됨), client `[1600,1200]` / logical `[800,600]`, `ps_after=3`.
  finalization 원인 판정 **H-B 확정(관측 결손 아님)**.
  이 세션은 실행 권한 거부로 `make check`/`checks/safety.sh check`/`/home/dev_00/sharedfolder/
  260320_Syw2plus/Syw2plus_re/...` 원본 EXE 해시는 **SKIP**(작업 디렉터리 밖 해시는 도구가 차단).
  `checks/context_limits.py`도 실행 SKIP이나 그 규칙 2개는 수동 확인했다:
  `docs/STATUS.md` 168줄(상한 180), 필수 heading 5개 각 1회. 코드 변경이 없어 새 테스트 표면도 없다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 재실행·설정 변경 없음. lap154 산출물과
  uncommitted 변경은 그대로 보존했다. G1 제품 완료·G2·G3·G4·사용자 마일스톤 승인은 여전히 미검증이며,
  이번 판정은 기술 판정이지 마일스톤 승인이 아니다.
- 다음 한 가지: work tier(Luna/Sonnet5)가
  `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`의 **probe P1 한 개**만 구현·1회 실행한다.
  P1은 실패 경로 관측 3종(close_transport 증거 기록, close 이후 프로세스 상태/CPU 표본 2회,
  wrapper 로그 수집)을 추가하고 새 private copy/prefix/display에서 `--dxwrapper-2x`를 1회 실행해
  "spin 재시도(R 상태·CPU 증가)"와 "차단/교착(S·D 상태·CPU 정지)"를 가른다. validator 요구 완화,
  timeout 증가, config 프로필 변경은 금지한다.

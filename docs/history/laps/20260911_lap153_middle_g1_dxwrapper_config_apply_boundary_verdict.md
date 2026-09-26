# 2026-09-11 | lap 153 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / 중간 tier
  (진단·계획·확인). 게임·하네스 코드는 고치지 않았다. lap152 `loop/ESCALATE_SOL`이 요청한
  판정 세션이다.
- 가설 / 사용자 관찰: lap152에서 승인 candidate config가 적용되지 않은 것은 호출 입력
  오류(lap151형)이거나, 커밋된 하네스에 적용 경로가 없는 결손이다. 둘 중 무엇인지와
  `patches/resolution/dxwrapper_config.py`의 old/candidate 바이트·적용·원복 경계를 판정한다.
- 예상 PASS / FAIL 조건: 정적 근거만으로 (a) old 바이트 pin, (b) 3개 변경 라인의 유일성·비중첩,
  (c) 후보가 private copy에 도달하는 경로의 존재 여부, (d) 원복 계약의 fail-closed 여부를
  판정할 수 있으면 PASS. 근거가 충돌하거나 실행 없이는 판정 불가면 Astra/사용자로 승격.

## 판정 (근거와 함께)

1. **old 바이트 pin: PASS(기계 강제).** `dxwrapper_config.SOURCE_SHA256`
   `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`는 `build()`에서
   하드 실패로 강제된다. 이번 세션이 lap152 private copy
   `local/runtime/20260911_194932_189255_0/game/dxwrapper.ini`를 직접 `sha256sum`으로
   재계산해 같은 값을 얻었다. 즉 후보는 그 run에 적용되지 않았다는 lap152 기록이 맞다.
2. **candidate `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`:
   기계 강제 없음(FINDING).** 코드에도 `patches/resolution/test_dxwrapper_config.py`에도 이
   값이 pin되어 있지 않고, 문서/STATUS 서술에만 존재한다. 이번 세션은 실행 권한 거부로
   재계산을 SKIP했다. 승인 대상 바이트는 반드시 pin으로 고정되어야 한다.
3. **3개 변경 라인: PASS(정적).** private ini grep 결과 `LoadCustomDllPath`(8행),
   `DdrawIntegerScalingClamp = 0`(59행), `DdrawMaintainAspectRatio = 0`(60행)이 각각 1회이고
   서로 다른 섹션이라 비중첩이다. 프로필이 전제한 `Dd7to9 = 1`(20행),
   `DdrawUseNativeResolution = 1`(53행)은 이미 켜져 있다. `build()`는 매 단계
   `count(old)!=1`이면 거부하고 변경된 버퍼에서 offset을 다시 구하므로 1번 변경의 길이 감소
   (−10바이트)가 뒤 offset을 깨지 않는다.
4. **적용 경계: `apply()`는 "새 파일 생성" 계약이지 "private copy 설치" 계약이 아니다(핵심).**
   `apply()`는 `target.exists()`면 거부하고 테스트 `test_refuse_in_place_and_overwrite`가 이를
   고정한다. 게임이 실제로 읽는 `game/dxwrapper.ini`는 copytree 직후 이미 존재하므로 원리적으로
   적용 대상이 될 수 없다. 그리고 커밋된 어떤 코드도 후보를 private copy에 설치하지 않는다:
   `grep -rn dxwrapper_config tools/ checks/ tests/ Makefile` 빈 출력, `prepare`는 support DLL
   해시만 기록하고 ini는 다루지 않으며(`tools/runtime_env.py:506-515`), `prepare`/
   `g1-presentation-trace` CLI에도 해당 옵션이 없다(`tools/runtime_env.py:2809-2827`).
   → lap152의 미적용은 **작업자 입력 오류가 아니라 하네스 결손이다. lap151과 반대 판정이다.**
5. **두 번째 원인(독립적으로 충분): `WINEDLLOVERRIDES=ddraw=b`.** 커밋된 4개 런타임 경로
   (`tools/runtime_env.py:531, 1919, 2383, 2630`)가 builtin 전용 override를 고정한다. lap152
   `provenance.json`의 environment도 `ddraw=b`이고, 같은 run의 module map에는 Wine builtin
   `/usr/lib/i386-linux-gnu/wine/i386-windows/ddraw.dll`만 매핑돼 있으며 private
   `game/ddraw.dll`(`3bc7230d1a6023a8fc0ea52b18d7edda94fcb4c0ae3d178f6e1577d68a62bd19`),
   `dxwrapper.dll`(`96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe`),
   `syw2x.dll`은 0건이다. 즉 후보 ini를 설치했더라도 이 경로에서는 그것을 읽는 주체가 로드되지
   않는다. 1600×1200 client를 본 유일한 run(lap148)은 inline `ddraw=n,b`였고 그 조건은 커밋된
   하네스로 이관되지 않았다.
6. **원복 계약: PASS(fail-closed) + 한계.** `restore()`는 backup이 `SOURCE_SHA256`이고 target이
   manifest `patched_sha256`일 때만 복원한다. 한계는 (a) sidecar를 남기고, (b) 복원 후 재호출은
   실패하며(비멱등, 안전 방향), (c) `apply()`에 보호 경로 가드가 없어 참고/원본 트리 안에 새
   파일을 만들 수 있다는 점이다(현재 가드는 `source==target`과 `exists()`뿐).
   자동 경로에 배선하기 전에 positive allow-list 가드가 필요하다.

**결론:** 프로필과 바이트 계약은 폐기하지 않고 **승인**한다. 다만 "적용"은 아직 존재하지
않으므로, 같은 프로필을 지금 코드로 재실행하는 것은 반드시 같은 800×600을 다시 만든다.
다음 work 바퀴는 두 결손(설치 경로, ddraw override)을 메우는 최소 배선 후 정확히 1회 실행한다.
lap149 카드가 금지한 "추가 dxwrapper 설정 적층"은 그대로 유효하며, `ddraw=n,b`는 새 설정이
아니라 lap148에서 이미 성립했던 조건을 커밋된 하네스로 되돌리는 것이다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품·하네스 코드 변경 없음.
  `docs/STATUS.md`, `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md`(lap153 부록),
  본 기록, `docs/history/laps/20260911_lap152_escalate_sol_original.md`만 uncommitted로 갱신.
  `loop/ESCALATE_SOL`은 판정 완료로 제거(원문 위 파일에 보존).
  커밋 없음(`LOOP_ALLOW_COMMITS` 기본 0). uncommitted 파일 SHA256:
  `docs/STATUS.md` `f7bbdce38aee279587f743e594d24d5be7c5e70fb222fc23e68ccdc9417bf806`,
  handoff `2a0810f10e7b0908b7eb4e28390b90373f24d26f8f841c6e9c6bc59962a72ed0`,
  lap152 escalation 보존본 `f73bc8830d962738fb35094239a31e6a1cb0ed02bcdc59d7f07501715ec4fb74`
  (본 기록 자체의 해시는 이 줄을 쓴 뒤 바뀌므로 남기지 않는다).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 실행 없음. 검사 대상은
  lap152 산출물 `local/runtime/20260911_194932_189255_0`. 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 재계산하지 않았다
  (해당 run manifest/provenance 기록만 대조). G2~G4 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `sha256sum local/runtime/20260911_194932_189255_0/game/{dxwrapper.ini,ddraw.dll,dxwrapper.dll}`
  → `918e7043…a5a2`, `3bc7230d…bd19`, `96c44319…e8fe`.
  `grep -o "[^ ]*ddraw[^ \\]*" .../evidence.json | sort | uniq -c` → builtin ddraw 7건, private 0건.
  `grep -rn dxwrapper_config tools/ checks/ tests/ Makefile` → 빈 출력.
  `wc -l docs/STATUS.md` → 146행(`checks/context_limits.py` 상한 180 이내, 5개 필수 heading 각 1회).
  `python3 checks/context_limits.py` 자체는 실행 권한 거부로 SKIP. 새 PNG/런타임 산출물 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 위 판정 1·3·6 PASS(정적), 2 FINDING+SKIP,
  4·5 하네스 결손 확정. `make check`/`checks/safety.sh check`/원본 EXE 해시/candidate 재계산은
  이번 세션 실행 권한 거부로 **SKIP**(lap149·lap151과 동일 제약). exit 0이나 과거 179 PASS를
  이번 판정의 근거로 쓰지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 변경이 없어 회귀 없음. 남은 위험은
  (i) candidate SHA가 아직 기계 강제되지 않음, (ii) `apply()`의 보호경로 가드 부재,
  (iii) `ddraw=n,b`로 전환하면 진단 bridge가 보는 DirectDraw 구현이 바뀌어 event 수·surface
  identity가 lap152와 직접 비교되지 않을 수 있음(정상 기대치이며 숨기지 말고 기록할 것).
  사용자 마일스톤 승인 없음. 이 판정 자체는 다음 새 세션이 다시 검수할 수 있다.
- 다음 한 가지: work tier가 아래 부록
  (`docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md` lap153 부록)의 최소 배선 3개를
  구현하고, Fast/safety 통과 후 새 copy/prefix/display에서 `g1-presentation-trace`를 정확히
  1회 실행한다. 실패 시 재시도 없이 증거 보존 후 승격.

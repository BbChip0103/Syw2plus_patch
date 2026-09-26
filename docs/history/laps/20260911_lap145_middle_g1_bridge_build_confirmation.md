# 2026-09-11 | lap 145 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 현재 표면은 실제 model ID/effort attestation을 제공하지 않아 추정하지 않는다. 사용자 지정 middle-tier 진단·계획·확인 역할로 lap144 승격을 독립 검수했다.
- 가설 / 사용자 관찰: lap144 bridge 실패는 source/build 결함이 아니라 builder가 직접 생성해야 하는 out-dir을 호출자가 미리 만든 절차 오류다. 보존 증거와 계약이 일치하고 비존재 fresh child에서 build/Fast가 통과하면 재실행을 승인한다.
- 예상 PASS / FAIL 조건: lap144 failure log/helper/target/원본 SHA 일치, `exist_ok=False` 계약 확인, 비존재 child 확인 build RC0/PE32, lap143 source manifest byte-equal, Fast PASS면 MIDDLE CONFIRM PASS. 불일치나 예상 밖 필수 실패면 현재 근거를 보존하고 `loop/ESCALATE_SOL`을 유지·갱신한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/source/test/원본/제품/baseline/golden 변경 없음. builder `7b88ab9dccaa376a58c0b8d9aa43c4716295858fcdc1ee85203e79751fe255e0`, bridge source `0eedffedd9fcaa38be3b63c068ff1cb9199d4476ca0856368a558d4099917cea`, lap144 이력 `0df89e1db37758b44779f32696af2340d61e98bebd10c60769a703f051f9b98f`, 기존 handoff `6b0f944276e1afed841c5f0959ef374ef0f0619cc755d089af2b79917e14a103`, 검수 전 STATUS `85af66a3d39e866087def67f4ddda5bca2f82711423ba129e7cf04a31229c85b`, 처리 전 marker `2c65cc18ff9aa195eeb911c855b2fbb9e310d76883da9cd42958a7c50822bbef`. 변경 후 STATUS `54faacab5ee8bce4a332928674ffeb0cf9f2f63f95b685afc72cb3763c0f7ad7`, lap145 handoff `cc67a3cdabd3b2c1c1c4a8ece67f1a4b31d6bc2fb810b6a9633e8a03b8107134`; 본 기록의 자기참조 hash는 생략한다. `docs/STATUS.md`, 본 기록, lap145 handoff만 문서 변경하고 marker를 제거했다. `LOOP_ALLOW_COMMITS=0`, uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe`는 PE32/SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. lap144 helper/target PE32 SHA `31237342fa377dd9fb89d5ca314295aab52149178687a4385b8dc9a693bc7d82`/`14dca5e05ce671aea654166a11518c7a47945899220e40d06c70b3acfb4d97d8`. 확인 build `/tmp/syw2plus_lap145_bridge_confirm.4hvkWi/bridge/_inmm.dll` PE32 SHA `391c57a43f601825c10758672bdfb8495b7b2f2808eeb76b34ecf51567ab8768`; 실제 runtime/활성 플레이어/지도/군대/fixture N/A·SKIP.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`/`file`로 lap144 산출물·원본 확인; lap144 failure log `/tmp/syw2plus_lap144.PDPLBr/bridge_build.json` SHA `57cb5191c01c2fb7f023e8f194b7d53800cb07ee9a4d5129245dd6a52a05b417` 원문에서 동일 `FileExistsError` 확인. 비존재 `/tmp/syw2plus_lap145_bridge_confirm.4hvkWi/bridge`로 builder를 1회 실행해 RC0; build log SHA `d067a98315f9ca95961bebac6810f51ac69930cc0126c46e161110a4210d727a`, manifest SHA `91332c93c8b5c02c7d5dc747a8fb4cdf7312b6e3fe769605edd365a6a71c229f`. `jq -S`/`cmp`의 lap143 대 current source manifest 비교 RC0, canonical SHA 둘 다 `079b63a7616cf8567b2b70f5b1436634107b7ef689e99e1bf76c03a708ab2e4f`. `make check` 실행. 게임 실행/PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): lap144 기록·marker·failure log/helper/target/원본 SHA PASS; fresh bridge build RC0/PE32/imports 및 source manifest 비교 PASS; 기존 warning은 lap143과 같은 비치명 build warning으로 보존; Fast **173 passed**, Ruff/compileall/mypy/context PASS. actual game runtime/final summary/process exit/DLL detach/validator/cleanup은 SKIP. **MIDDLE CONFIRM PASS / RETRY AUTHORIZED**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 확인 build는 진단 산출물일 뿐 다음 work runtime에 재사용하지 않는다. 구현 미변경이 이번 lap으로 2회 연속이므로 다음 작업은 문서 확장이 아니라 새 같은-run finalization 수치를 만들어야 한다. G1 2배 제품 출력, G2~G4, 사용자 마일스톤 승인은 미검증이다.
- 다음 한 가지: 새 Luna/high work tier가 `docs/plans/20260911_lap145_g1_fresh_runtime_handoff.md`대로 새 helper/bridge/game copy/prefix/display를 만들고 presentation trace를 정확히 1회 실행한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
lap=144
role=Luna/high hands-on work
status=WORKER_BLOCKED

필수 fresh bridge build가 실패하여 지시대로 재시도하지 않고 승격한다.

실패 명령:
  python3 patches/population/build_runtime_bridge.py --out-dir /tmp/syw2plus_lap144.PDPLBr/bridge
결과:
  RC1 FileExistsError: [Errno 17] File exists: '/tmp/syw2plus_lap144.PDPLBr/bridge'
원인:
  호출자가 builder가 `exist_ok=False`로 생성해야 하는 출력 디렉터리를 미리 만들었다.
  bridge 산출물은 생성되지 않았다. 실패 로그는 `/tmp/syw2plus_lap144.PDPLBr/bridge_build.json`에 보존했다.

이미 성공한 증거:
  helper: /tmp/syw2plus_lap144.PDPLBr/helper/win32_close_helper.exe
    PE32 SHA256=31237342fa377dd9fb89d5ca314295aab52149178687a4385b8dc9a693bc7d82
  target: /tmp/syw2plus_lap144.PDPLBr/helper/win32_close_target.exe
    PE32 SHA256=14dca5e05ce671aea654166a11518c7a47945899220e40d06c70b3acfb4d97d8
  patch/reference original SHA256=b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac

Sol이 이어서 검증할 것:
1. 위 실패 로그와 lap144 기록, handoff를 독립 확인한다.
2. builder 계약상 출력 디렉터리가 존재하지 않아야 함을 확인하고, fresh bridge 재실행 여부를 판정한다.
3. 승인/판정 전에는 prepare, check, doctor-runtime, g1-presentation-trace를 실행하지 않는다.
4. bridge가 fresh로 생성된 경우에만 handoff의 새 전체 게임 복사본/prefix/display와 presentation trace를 정확히 1회 수행한다.

변경 없음: 게임/source/test/원본/제품/baseline/golden 변경 및 커밋/푸시 없음.
```

# 2026-09-11 | lap 29 | G1-A selector provenance middle 독립 확인

- 실제 provider/model/effort / 지정 역할: Codex 새 세션, 사용자 지정 middle 진단·계획·확인 역할.
  계약 대상은 `gpt-5.6-sol`/high이나 현재 런타임이 정확한 model ID/effort를 노출하지 않아 실제값은
  미확인. 게임 코드·하네스·EXE/DLL/asset hands-on 수정 및 게임 실행 없음.
- 가설 / 사용자 관찰: lap28의 callback-derived chain이 맞더라도 `0x004ED848`이 selector click의
  즉시 state인지, 연결 `확인` 뒤 commit되는 mode인지를 구분해야 lap26 FAIL의 최소 수리 범위를
  정할 수 있다.
- 예상 PASS / FAIL 조건: 고정 원본 SHA, object 생성 old bytes, `0x00405560`→`0x00404C20`
  vtable `+0x54`, `[object+0xA4]` state, `0x004B9341/0x004B9390` WORD write를 독립 재현하고
  selector object/label/confirm gate의 증거와 추론을 분리해 하나의 fail-closed work 수리를 정하면
  middle PASS. 필수 Fast 실패나 불해소 근거 충돌이면 marker를 유지·갱신하고 중단한다.
- 변경 파일 / source fingerprint / 커밋: 구현 변경 없음. 검수 source SHA256은
  `tools/runtime_env.py` `b091a8ae83e5332c1d5dc17cb979531fcafc19bdf3368f56b4c094d24560195c`,
  `tests/test_runtime_env.py` `d15a3580b2fd9d0bc209ca62015bc659f3a0d8982d33ea559b7645f1306baa75`,
  `tests/test_runtime_guards.py` `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`.
  문서만 `analysis/memory_maps/player_offsets.md`, 활성 카드, `docs/STATUS.md`, 이 기록을 갱신하고
  소진 marker `loop/ESCALATE_SOL` SHA256
  `d23fa60485d22f26e8ceadd8a86ddc03cd6ecc9119144ddd2982c5e35c35b30f`을 아래 원문 보존 후 제거했다.
  Git은 unborn HEAD, `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: source 원본과 lap26 private
  copy 모두 SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  바이너리/구현 후보 없음. lap26 보존 PNG는 historical captured evidence이며 새 fixture·Wine·display·
  active player·지도·군대 측정 없음. 원본 SPR와 private copy SHA는 둘 다
  `d124afe4e5e9ceb7b690a00dc07d6f641c7c6b441f3fad588ff3d4e5901776be`.
- 실행 명령 / 로그 / 캡처: `sha256sum`, `file`, `objdump -h/-s/-d -Mintel`, `.text` VMA/file
  offset 기반 `xxd`, `sed`/`rg`, 보존 PNG 시각 대조, `make doctor`,
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`, `make check`,
  `bash checks/safety.sh check`. 보존 PNG
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260911_025014_20260911_024939_418440_0_420371_lobby_selector_before_1789062614242968595.png`
  SHA256 `7f50c8b3203a3c9ca9053828566e931ef59e634f283afc876e4ccb9bd9b915ea`, 800×600.
  게임/`g1-baseline`/새 PNG/patch 생성·적용·원복은 실행하지 않았다.
- 측정값 / 판정: 원본/private copy SHA PASS. lap28 두 constructor 범위 raw bytes, callback wrapper,
  vtable `+0x54`, state reader/writer, WORD write raw bytes PASS. 정확히 dispatcher entry
  `0x00424A9F`는 NOP이고 call은 `0x00424AA0`. selector anchors `(294,152)`/`(412,152)`는
  보존 화면의 왼쪽 `여럿이하기`/오른쪽 `혼자하기`에 정렬되나 이는 static+historical evidence다.
  첫/둘째 selector state는 각각 `edi=1/0`을 만들고, global 0/1 write는 별도 confirm object
  `0x01071F18`의 `0x004B9309/0x004B9363` callback gate 뒤에서만 실행된다. 따라서 lap28 static
  chain은 **CONFIRMED**, immediate selector WORD 계약은 **HARNESS CONTRACT REVISE CONFIRMED**.
  `make doctor` top-level ok/original verified; canonical runtime manifest 없음은 새 runtime 금지 범위에서
  SKIP. targeted `19 passed in 0.05s`; Fast `89 passed in 10.46s`, Ruff/compileall/mypy8/context PASS;
  safety `SAFETY_PASS`. patch old/new bytes, unsupported-version reject, copy-only output, non-overlap,
  byte-exact restore는 후보가 없어 SKIP(N/A).
- 회귀 / 남은 위험 / 승인: exit 0이 아니라 SHA/raw control flow/화면 위치/회귀 gate를 함께 판정했다.
  lap26은 원본 게임 실패가 아니라 잘못된 관측 시점으로 중단된 과거 FAIL이며 입력 전달·PS5→PS3·
  전투·필수 입력5종·실제2배 출력은 계속 미검증이다. G1-A/G1~G4 및 사용자 마일스톤 승인 변화 없음.
  문서-only로 implementation-unchanged-streak=2이므로 다음은 추가 서술이 아닌 측정 가능한 코드 수리다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 허용된 runtime source/tests에서 selector를
  DWORD `0x0106A6A4`/`0x0106A86C` one-hot state로 검증하고, `0x004ED848` WORD는 연결 `확인`
  뒤 solo committed mode=1로만 검사하도록 최소 수리한다. global `1→0→1` 합성 테스트를 제거하고
  양쪽 초기 one-hot, 비 one-hot 거부, 정확 주소/폭, confirm-time 검사를 회귀로 고정한다.
  targeted/Fast/safety 후 새 Sol 독립 확인 전까지 게임 실행은 금지한다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
lap=28
reason=g1a_selector_static_provenance_found_but_ui_label_semantics_unproven
role_requested=Fresh Codex gpt-5.6-sol/high middle independent confirmation; do not rerun g1-baseline or edit harness/game.
required=On original SHA b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac, independently verify PS dispatcher 0x00424A9F -> 0x004B8A10, the two PS7 object construction ranges 0x004B8C16..0x004B8C70, poll 0x004B91E0 -> 0x00405560 -> 0x00404C20 vtable +0x54, object state [+0xA4] reader/writer, and 0x004B9341/0x004B9390 WORD writes to 0x004ED848. Decide whether the object order can establish Korean 여럿이하기/혼자하기 semantics from static evidence; if not, preserve that boundary as UNKNOWN/REVISE.
observed=Static chain is recorded in analysis/memory_maps/player_offsets.md lap28 with exact old bytes. Dispatcher enters PS7, constructs objects 0x0106A600 and 0x0106A7C8, callback path reaches virtual slot +0x54, state is stored/read at object+0xA4, and branch paths write WORD 0 or 1 to 0x004ED848. The binary does not expose the Korean labels, so the mapping 혼자=1/여럿=0 is not proven. Lap26 input delivery and post-click state series remain absent.
evidence=docs/history/laps/20260911_lap28_luna_g1a_selector_provenance.md; analysis/memory_maps/player_offsets.md lap28 section; original SHA above; prior run local/runtime/20260911_024939_418440_0 remains preserved and is not a new success.
candidate=No implementation or binary candidate. tools/runtime_env.py and tests/test_runtime_env.py were not changed. No old/new patch bytes, restore, commit, or push.
stop=This is the required work-to-middle boundary. Sol must independently confirm the static provenance and label-semantic boundary before any harness repair or new game run is authorized. Preserve current docs and all prior runtime artifacts.
```

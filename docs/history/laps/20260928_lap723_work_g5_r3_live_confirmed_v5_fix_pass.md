# 2026-09-28 | lap 723 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행). 게임 코드
  후보(v5)·진단 브리지(신규 op10)·probe 도구 구현 및 실행.
- 가설 / 사용자 관찰: 2026-09-28 01:30 사용자 지시("R3부터 해결해야겠는데?") — lap721 middle이 정적
  disasm으로만 제기한 R3(50선택 후 count≤20으로 줄고 생존 유닛이 배열 인덱스≥20에 있으면 v3/v4
  청크게이트의 `count<=20→원본20칸 본문` 경로가 그 생존 유닛에 명령을 못 보낼 것)를 ① 실제 게임에서
  raw로 확인하고, ② 예상대로 FAIL이면 v5(게이트를 "count>20 또는 entries[20:50]에 살아있는 칸이 있으면
  청크"로 확장)를 만들어 재측정한다.
- 예상 PASS / FAIL 조건: v4에서 인덱스0~29의 유닛을 실제로 죽여 count=20·생존 20기가 인덱스30~49에
  남는 상태를 만든 뒤 STOP·MOVE를 내리면 생존 전원 미수신(R3 CONFIRMED) 예상. v5는 같은 상태에서
  전원 수신(PASS) 예상. 원본은 자체 20칸 본문으로 같은 구조(count=10, 생존10 인덱스10~19)를 만들어도
  항상 PASS해야 방법론(죽이기+측정) 자체가 유효함을 확인하는 대조.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `patches/population/g5_r3_death_bridge.c` (신규) — `runtime_bridge.c`의 byte-for-byte 사본 +
    신규 진단 op 10(원본 사망처리 함수 `FUN_00409C70`을 thiscall로 직접 호출). 공유 `runtime_bridge.c`는
    무수정 — G2 lifecycle이 pin한 `G2_APPROVED_BRIDGE_SHA256`(컴파일된 DLL SHA)을 이 G5 작업으로
    건드리지 않기 위해 별도 파일로 분리했다(기본 빌드 경로의 `bridge_sha256`가 이 변경 전후 동일함을
    직접 재확인 — 아래 근거).
  - `patches/population/build_runtime_bridge.py` — 옵션 `--bridge-source`(기본값 없으면 기존
    `runtime_bridge.c`, 동작 100% 불변) 1개 추가, manifest에 `bridge_source` 필드 추가.
  - `patches/selection/g5_selection_cap50_v5.py` (신규) — v4 위에 R3 게이트 수정만 얹음(다른 전부
    byte-identical, 테스트로 확인).
  - `patches/selection/test_g5_selection_cap50_v5.py` (신규) — 결정론/SHA고정/cave여유/게이트구조(v4와
    구조 동일, 순서·상수만 대조)/스파스스캔구조(entries[20:50] 정확히 30칸)/청크본체 v4와 동일(모듈로
    relocation) 5개 pytest.
  - `tools/g5_r3_sparse_selection_probe.py` (신규) — R3 실측 도구(원본/v4/v5 공통, `--variant`로 선택).
  - 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0`). 임시 monkeypatch 드라이버(`/tmp/lap723_*.py`)는
    제품/저장소 파일이 아니며 세션 종료 시 사라진다(파일을 수정하지 않고 모듈 전역만 바꿔 재사용,
    lap682/684/717 선례와 동일 방식).
  - 신규/수정 파일 SHA256(uncommitted): `patches/population/g5_r3_death_bridge.c`
    `ab1606e5aa0cd1838a646391869bb1e57f51204cab1f98910820fb14b4a13768`,
    `patches/population/build_runtime_bridge.py`
    `438a1f4bc770e1625d84fc2ed3d1b8ea423d39a4319363606238842c0ed0a391`,
    `patches/selection/g5_selection_cap50_v5.py`
    `e13f094e14e1baf41dd2b0ae55dd566605feedd6bcf0a58eb832b164136e4ee0`,
    `patches/selection/test_g5_selection_cap50_v5.py`
    `d6a7778424182685bdb7ac01b4b83b5c0ccaa62030bb60d2ef4be074e9a9243d`,
    `tools/g5_r3_sparse_selection_probe.py`
    `536935dfee37b69070d9f38e087e4b6d04252a67fd1167c14ad863005bd52b18`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(모든 실행 전후 `source_unchanged=
  true`). v4 재빌드 `0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb`(lap717~721과
  일치). v5 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`(결정론, 3회 빌드 동일).
  기본(무수정) `build_runtime_bridge.py` 빌드의 `bridge_sha256`는 이 lap 변경 전후 동일(923fd1e1…,
  G2 실사용 경로 무영향 확인). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0 dense fixture worker(slot1198)
  앵커 7×8 grid 55기 SEED_TYPE=2(56기 선택 가능), world 앵커는 후보 실행 3회 모두 (93,56)(동일 지도/카메라
  절차, run간 결정론적).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact(JSON+캡처+probe.log)는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap723_r3_probe/`
  {candidate-v4,candidate-v5,original,shp-v5}/.
  1. `PYTHONPATH=. .venv/bin/python tools/g5_r3_sparse_selection_probe.py --variant candidate-v4
     --runtime-root local/runtime/lap723_r3_v4 --artifact-root .../candidate-v4`
  2. 동일 `--variant candidate-v5 --artifact-root .../candidate-v5`
  3. 동일 `--variant original --artifact-root .../original`
  4. `/tmp/lap723_v5_shp_driver.py`(임시, `tools/g5_stop_hold_patrol_v4_probe.py`의 모듈 전역 `g5`를
     v5로 monkeypatch, 파일 무수정) `candidate local/runtime/lap723_shp_v5 .../shp-v5`
  5. `make check` 포그라운드 완주(로그 `logs/gates/20260928_lap723_make_check.log`),
     `bash checks/safety.sh check`.
  6. `/tmp/lap723_v5_coverage_driver.py`(`g5_command_coverage_probe.py`를 v5로 monkeypatch) 2회 시도
     — 둘 다 자체 내부 ground-move 목적지 캘리브레이션(월드(93,56) 지형에서 7개 후보 중 1개만
     `move_ok`) 단계에서 `ProbeError`로 조기 종료. v5 게이트 이전 단계(로비/일꾼 이동 검증)에서
     실패하므로 내가 만든 v5 변경과 무관한 그 도구 자체의 기존 지형 의존 취약점으로 판단하고(동일
     세션 2회 반복 후 결론), ALT/Ctrl/Shift 드래그·공격·부대저장/로드 재측정은 이 lap에서 완결하지
     못했다(아래 회귀 항목 참고).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **v4 R3 실측 = CONFIRMED (FAIL, raw).** 50선택→인덱스0~29(29개 fixture+worker슬롯1198) 30기를
     신규 진단 op10으로 실제 사망 처리(원본 함수 `FUN_00409C70` 직접 호출)시킨 뒤 전체 버퍼 확인:
     `count_field=20`(50-30), `slots_all[:30]`전부0, `slots_all[30:50]`킬 이전과 완전 동일(생존20기
     그대로), 각 킬 리포트 전부 `selected_before=1→dead_flag_after=1→selected_after=0`(disasm이 예측한
     0x412D90 제거 경로가 실제로 매번 탔음을 확인). 이 상태에서 STOP 클릭 + 검증된 지면 우클릭(MOVE)을
     각각 내려 생존 20기(슬롯1147~1166) 전원을 3초 샘플 — **STOP·MOVE 모두 20/20 미수신**
     (`stop_missed_slots`/`move_missed_slots`가 생존 20기 전부와 정확히 일치). R3가 정적 PLAUSIBLE에서
     실측 CONFIRMED로 승격.
  2. **v5 R3 재측정 = PASS.** 완전히 동일한 절차(같은 킬 인덱스0~29, 같은 STOP/MOVE)에서
     `structural_ok=true`(버퍼 구조 v4와 동일하게 확인) 후 **STOP·MOVE 모두 생존 20/20 전원 수신**
     (`stop_missed_slots=[]`, `move_missed_slots=[]`) — `status=PASS_NO_SPARSE_GAP`.
  3. **원본 대조 = PASS.** 20선택→인덱스0~9(10기, worker슬롯1198 포함) 사망 처리→count=10, 생존10기
     (슬롯1177~1186)가 원본 자체 20칸 본문 안(인덱스10~19)에 남는 상태에서 STOP·MOVE 둘 다 10/10 수신 —
     "죽이기+측정" 방법론 자체가 유효함을 원본에서 확인(이 방법으로 생긴 인위적 아티팩트가 아님).
  4. **v5 STOP/HOLD/PATROL 회귀 = PASS(50/50 3종).** `g5_stop_hold_patrol_v4_probe.py`를 v5로
     monkeypatch(파일 무수정)해 재실행 — `pending_ever`에서 STOP(`0x1000002`)·HOLD(`0x1000027`)·
     PATROL(`0x1000023`) 각각 선택50/50 전원 관측, `status=COMPLETE`, 크래시0. lap717의 v4 결과와
     동일한 패턴.
  5. **정적 근거 — v5는 check_count 블록만 v4와 다름(전부 pytest로 확정):** 결정론 SHA 고정, cave
     여유(0x4e4f83+추가 ≤ limit), order-type 게이트 opcode·분기 구조 v4와 동일(심볼 매핑으로 비교,
     원시 바이트는 check_count 블록 길이차 때문에 다를 수 있음을 확인 후 이를 반영해 테스트를 고쳤다),
     스파스스캔이 정확히 `entries[20:50]`(`CHUNK1_OFFSET`부터 30칸=`ENTRIES+50*4`까지) 범위, do_chunk
     이후(청크빌드+백업+복원+relocate된 원본 본문)는 v4와 modulo relocation 완전 동일.
  6. `make check` **1106 passed(898.62s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS, `SAFETY_PASS`. 신규
     pytest 5개(v5) 전부 포함. cleanup 매회 프로세스 잔류 0(4회 게임 실행: v4·v5·original·shp-v5),
     원본 SHA 4회 전부 `source_unchanged=true`, EXE/원본 미변경.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **미완결(이 lap 예산 내):** ALT/Ctrl/Shift 드래그 변종·공격 판정·부대지정+저장/로드 라운드트립을
    v5로 직접 재측정하지 못했다(`g5_command_coverage_probe.py`의 자체 ground-move 목적지 캘리브레이션이
    이번 world(93,56) 지형에서 2회 연속 실패 — v5 변경과 무관한, 그 도구 자체가 로비/일꾼 이동 검증
    단계에서 그 지형에 취약한 기존 문제로 판단). v5가 `check_count` 블록만 v4와 다르고 나머지(드래그
    캡처/청크빌드/백업복원/relocated 본문/부대필드 훅/save-load 경로)는 byte-identical임을 pytest로
    확정했으므로, lap717·lap720의 v4 PASS(드래그3종·부대지정·저장로드·공격 N=5)가 그 경로들에 대해서는
    유효하게 이전된다고 추론하지만, **v5에 대한 직접 raw 재측정은 아니다** — 다음 middle/work가 확인
    필요.
  - R2(미측정 명령 버튼 opcode, lap719 후순위)는 여전히 미측정.
  - 멀티 동기화 `UNKNOWN` 유지.
  - 신규 진단 op10(`patches/population/g5_r3_death_bridge.c`)은 사망처리 함수만 호출하고 HP/존재
    테이블을 직접 쓰지 않는다 — 실측 결과 `hp_after`는 원래 값 그대로, `exists_after`는 0이 아닌 값(예:
    일꾼21, 그외 fixture 2)으로 남는다(사망 직후 다른 코드 경로가 나중에 정리하는 것으로 추정, 조사하지
    않음). 이 lap의 판정은 이 필드에 의존하지 않고 선택배열 구조(count/slots_all)와 각 킬의
    `selected_before/dead_flag_after/selected_after`로만 냈다.
  - 독립 검수: 아직 없음(work tier 산출, 다음 middle 요청).
  - 사용자 승인: 없음(v4→v5 교체·G1 재개는 사용자/운영자 판단 대기, `loop/ESCALATE_SOL` lap721 절 참고).
- 다음 한 가지: middle(Opus) 독립 검수 요청 — ① v4 R3 CONFIRMED·v5 PASS 실측 raw 재계산, ②
  `g5_selection_cap50_v5.py`가 check_count 외 전부 v4와 동일하다는 pytest 근거의 타당성, ③ 위 미완결
  회귀(드래그3종/공격/부대저장로드)를 "byte-identical이므로 이전됨" 추론으로 충분히 볼지 아니면 v5로
  직접 재측정을 요구할지, ④ 확정되면 v4→v5 교체·G1 재개 사용자 milestone 요청 여부.

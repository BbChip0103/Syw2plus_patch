# 2026-09-12 | lap 294 | G1/S1 missing-definition 수리 범위 재판정 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  중간 tier(진단·계획·확인). 게임 코드 hands-on 수정 없음. lap293 승격(`loop/ESCALATE_SOL`)의
  §4.5.3 범위 질문을 독립 판정하는 것이 이번 한 가지다.
- 가설 / 사용자 관찰: lap293이 거부한 `refs`의 `pinned[name]` 재인덱싱은 §4.5.3의 글자 범위
  밖이지만, 그 범위를 그대로 지키면 §4.5.3이 스스로 요구한 성공 조건을 만족할 수 없다.
  즉 사양이 자기모순이며 무방비 소비처가 하나가 아닐 것이다.
- 예상 PASS / FAIL 조건: (a) lap293의 정상 run 바이트 동일 주장이 fresh로 재현되면 ACCEPT.
  (b) 세 상수 정의를 각각 지운 mutant가 모두 같은 자리에서 0바이트로 죽으면 결함은 상수별이
  아니다. (c) `refs` 가드만 넣은 사본에서 한 상수라도 여전히 crash하면 §4.5.3 범위는 증명된
  불충분이며 middle이 범위를 정정해야 한다. 아니면 lap293 승격이 과도했던 것이다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap294_middle_missing_definition_scope_probe.py`
  SHA `8fe0d2575005b4d647e85c0c4377a2d132fc872a30a1e939e8b78171671ec469`;
  신규 `logs/lap294/middle_missing_definition_scope.json`
  SHA `3b1acbddb82591962a04e94f10eae73f6839304622daf391a7e99097ffd2a756`;
  `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`에 §4.6 추가(458→544줄);
  `docs/STATUS.md` 갱신; `loop/ESCALATE_SOL`은 아래 원문 보존 후 제거.
  **lap293이 수리한 target probe(`edefa0e4…7b47f61d`)는 건드리지 않았다.** 커밋 없음
  (`LOOP_ALLOW_COMMITS=0`). 구현 모듈 `tools/runtime_env.py` `dd2ad043…8500190`,
  `patches/population/runtime_driver.py` `ae4ff939…4e4291b5` 무변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변); 후보 EXE 없음.
  Linux `.venv`(Python 3.13.5) + `/usr/bin/objdump` 정적 분석, mutant는 `tempfile` 사본 트리
  (EXE는 symlink). 게임 fixture/활성 플레이어/지도/군대 **없음** — 이번 바퀴는 실행 증거가
  아니라 하네스 사양 판정이다. Wine/Xvfb/Stage B/runtime 예산/PNG 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
     → exit 0, stdout SHA `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126`,
     `logs/lap280/s1_crossverify_probe.json`과 바이트 동일 (lap293 주장 독립 재현).
  2. `.venv/bin/python docs/history/laps/probes/20260912_lap294_middle_missing_definition_scope_probe.py`
     → exit 0, `failures` 0, 보고서 `logs/lap294/middle_missing_definition_scope.json`
     SHA `3b1acbdd…ffd2a756`.
  3. `make check` → 292 passed (46.55s), `All checks passed!`, `CONTEXT_PASS`.
  4. `bash checks/safety.sh check` → `SAFETY_PASS`.
  5. 문서 갱신 후 재실행: `make check` 292 passed (45.68s)/`CONTEXT_PASS`, `SAFETY_PASS`.
     최종 `docs/STATUS.md` 130줄 SHA `316cb68398f99033cf0d98ddb81a9da587e1c45d333a53be29e0ae295ac388ab`;
     이전 원문(130줄, SHA `c2b7c7c6…c280de70`)은 `…_status_lap294_compaction.md`에 보존.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **as_is(lap293 상태):** control exit0 1,139 B `3d4fe307…`; `x`/`y`/`internal_id` 정의 삭제
  mutant 전부 exit1 **stdout 0바이트** `line 156 KeyError`. 결함은 상수별이 아니다.
  **refs 가드만 넣은 사본:** control exit0 보고서 **바이트 동일**(무해한 수리);
  `x` exit1 1,083 B 명명 failure; `y` exit1 1,083 B 명명 failure;
  `internal_id` exit1 **0바이트** `line 169`(저장소 파일 기준 **line 167**,
  accessor 검사의 `pinned['internal_id']`) `KeyError`.
  `scope_verdict = "refs guard alone is INSUFFICIENT; unguarded consumers remain"`.
  **판정: lap293 승격 ACCEPT(옳게 멈췄다) / §4.5.3 범위는 사실 오류로 정정(§4.6) / S1 카드
  종결은 REJECT 유지.** 하네스 판정 PASS, 제품 G1~G4 증거 SKIP(이번 범위 아님).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  무방비 `pinned` 인덱싱은 정확히 두 곳(line 156, 167)이며 line 189는 `.items()` 순회라 안전함을
  소스와 실행 양쪽으로 확인했다. lap292 review probe는 `y`만 mutate하므로 **line 156만 고친
  수리도 그 probe를 통과**한다 — 글자 범위를 지키면 lap290 결함 계열이 그대로 재발한다는 것이
  이번 바퀴의 핵심 증거다. 두 review probe의 `EXPECTED_SHA["target_probe"]` 고정값은 각 검수
  시점의 기록이므로 **편집 금지**로 못박고(§4.6.4 5항), 수리 후의 mismatch 한 줄을 예상 결과로
  재정의했다. §4.5.4의 reader 이름 사각(`x=i(...)`)은 여전히 열려 있고 범위 밖이다.
  이번 판정 자체는 다음 새 세션의 독립 검수 대상이며 사용자 마일스톤 승인은 없다.
- 다음 한 가지: work tier가 §4.6.4 사양대로 line 156과 line 167 두 자리만 수리하고,
  정상 보고서 바이트 동일 + 동행 4종 + lap294 scope probe의 `as_is` 세 mutant 전부 명명 failure를
  fresh 실행으로 보인 뒤 `make check`를 돌린다. 그 전에 S1 카드 종결/Stage B/runtime 실행/
  제품 G1~G4 승격은 하지 않는다.

## 부록 A — lap293 `loop/ESCALATE_SOL` 원문 보존 (판정 후 파일 제거)

```
# ESCALATE_SOL — lap 293 G1/S1 missing-definition guard 범위 충돌

## 현재 상태

lap292 middle의 §4.5.3 지시에 따라 lap280 cross-verify probe의 튜플 가드만
`pinned.get` 기반으로 수리했다. 정상 정적 probe는 exit 0이고 보존 report와 바이트 동일하지만,
정의 누락 mutant는 뒤의 `refs` 생성부에서 `pinned[name]`을 다시 인덱싱해 stdout 0바이트로
`KeyError: 'y'`가 난다. 필수 독립 검수 조건을 충족하지 못했으며, 이 추가 인덱싱은 지시된
"정의 누락 분기와 그 직후 튜플 가드만" 범위 밖이므로 억지로 확장하지 않았다.

## 보존된 근거

- 변경 파일: `docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`.
  이전 SHA `100f991b3abfa6d075a35facf9a9e479c1d2092ebb4d6245688cfe73cb999f84`;
  현재 SHA `edefa0e4b82d39034ddd14055e09a651998d2a8c93e5d27ab0f168bc7b47f61d`.
- 정상 run: `.venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
  exit 0; stdout SHA `3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126`;
  `logs/lap280/s1_crossverify_probe.json`과 바이트 동일.
- fresh missing-definition mutant: exit 1, stdout 0바이트, traceback은
  `line 156: abs_addr = UNIT_BASE + pinned[name]`, `KeyError: 'y'`.
- 동행 4종 SHA는 lap292 기록과 일치: `e848c940…`, `e0f07f3a…`, `28703830…`,
  `7381b5f7…`. 구현 모듈 `tools/runtime_env.py` SHA
  `dd2ad0439111d6b1e098d0ea771db172847dfa42f04ed085c4567f2ac8500190`,
  `patches/population/runtime_driver.py` SHA
  `ae4ff9393247ce31eab7c953b040f7d3c5aa8b0386af025046382c7d4e4291b5`, 원본 EXE SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 불변.
- 게임/Wine/Xvfb/Stage B/runtime 예산/PNG/원본·구현 모듈 쓰기/`make check` 재실행은 0.

## 승격 작업자가 이어서 검증할 것

1. `refs` 생성부의 `pinned[name]` 재인덱싱을 §4.5.3의 허용 범위에 포함할지, 또는 현재
   튜플 가드 수리만 보존하고 새 middle이 별도 범위를 정할지 독립 판정한다.
2. 허용 범위가 확정되면 missing-definition mutant가 traceback 없이 명명된 failure를 내는
   최소 수리를 하고, lap292 review의 stale `target_probe` SHA fixture를 새 probe SHA와
   어떻게 보존·갱신할지 결정한다.
3. 그 뒤 정상 report 바이트 동일성, 동행 4종, 자체 mutant, `make check`를 fresh 실행한다.
   그 전에는 S1 카드 종결, Stage B/runtime 실행, 제품 G1~G4 승격을 하지 않는다.
```

원문 SHA: 82d8ec12179f441f16626e8ded8f3040f482597b1e1db8c3ce507f6d6cf045f1

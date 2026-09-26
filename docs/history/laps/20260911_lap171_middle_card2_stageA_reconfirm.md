# 2026-09-11 | lap171 | G1 카드2 Stage A middle 승격 검수

- 실제 provider/model / 지정 역할: Claude Code `claude-opus-5` / middle tier(진단·계획·확인).
  세션 프롬프트에 middle STAGE_ROUTING이 붙었고 게임 코드 hands-on 수정은 하지 않았다.
- 목표: `loop/ESCALATE_SOL`(lap170 Astra)의 인계 3건을 해소한다 —
  (1) P5 산출물 현물/SHA 독립 대조, (2) 카드2 Stage B 판정 경계 확정, (3) Stage A 범위 재확인·인계.
- 가설: lap170의 P5 재검증 실패는 산출물 유실이 아니라 문서 경로 오류다.
- 예상 PASS: 기록된 SHA와 현물이 일치하면 가설 성립. 불일치/부재면 UNKNOWN 유지.

## 이전 바퀴 독립 검수 (①~④ / ⑥ 1단)

lap170이 읽으려 한 `local/runtime/20260911_214253_1178505_0/evidence.json`은 존재하지 않는다.
실제 위치는 같은 run의 `output/g1_presentation_trace/`다. **경로 기재 오류로 확정**한다.
`sha256sum` 독립 재계산 결과 lap168 기록과 **6/6 일치**:

| 파일 | SHA256 | lap168 기록 |
|---|---|---|
| `output/g1_presentation_trace/evidence.json` | `309028386476de06ced251686444e04b7c8e7d9c282f7f52e7ed1dbcf7fc7e59` | MATCH |
| `output/g1_presentation_trace/provenance.json` | `1b8df1e86bd8956da2bc3d9410afc0cebea83371646ae4a1a720cdac475e1c1b` | MATCH |
| `output/g1_presentation_trace/verdict.json` | `319474f8fbe1f5e6d52443a71c75894b581e8ed83299bba60eeee30701138d55` | MATCH |
| `output/g1_presentation_trace/trace.jsonl` | `aa3934044c5cfb1758d7330b3dab5b3f5a09c0468b5946a81f05d44ee62ceb1b` | MATCH (validator `trace_sha256`) |
| `output/g1_presentation_trace/trace_raw.jsonl` | `aa3934044c5cfb1758d7330b3dab5b3f5a09c0468b5946a81f05d44ee62ceb1b` | raw=validated 동일 |
| `manifest.json` | `d59ad3242d4aeb0a8223edd24db3d690b5cab04694d46519d2597df17c7ccd66` | 신규 기록 |

내용 필드 대조도 일치: `verdict.overall=PASS`, `validator.status=PASS`,
`validator.schema.event_count=651`, `errors=[]`, `capture.ps_before=9`/`ps_after=3`,
`client_size=[800,600]`, `logical_content_size=[800,600]`,
evidence `process_exit=0`, `summary_count=1`, `winedlloverrides="ddraw=b"`.
적재 ddraw 모듈은 `/usr/lib/i386-linux-gnu/wine/i386-windows/ddraw.dll` 하나이며 evidence 전체에서
`game/ddraw.dll` 0건, `game/dxwrapper.dll` 0건이다.
⇒ **lap169의 N CONFIRMED는 현물 기준으로 재확인**된다. lap170의 재검증 BLOCKED는 해소한다.

문서/소스 SHA 재대조(3/3 MATCH, lap170 기록과 동일):
- `tools/runtime_env.py` `69b0f16253a850e02537d0d5dddbc97e43b7755cff447860a81e66914fdf0571`
- `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(수정 전)
  `99e888a5ecfbf7421c3b757ccbb44e2251614950a606affa124c0ed1c898ec3c`
- `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md`
  `3fd5b8fe824a7edc2f06caa163ce32fa62c906deb00729ee91d3e571221e2877`

보호 EXE: run copy `game/syw2plus_original.exe` =
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (STATUS pin과 일치).

## middle 판정 — 카드2의 구현 근거 결손 3건

### (a) A-1을 lap169 문안대로 구현하면 실패한다 (코드 근거로 확정)

`_g1_production_click_if_authorized`(`tools/runtime_env.py:1540`) 직후가
`_wait_state(state, production_changed, ...)`(`:2464`)다. 클릭을 보내지 않으면 `production_changed`는
영원히 거짓이고, `_wait_state`(`:2138~2149`)는 **단계별 마감시한 없이 run 전체 timeout(최대 90초)까지**
0.25초 간격으로 돈다. 즉 "예외를 BLOCKED 기록으로 바꾸고 계속"만 하면 production이 남은 예산을
전부 소모하고 timeout 예외로 종료되어 `drag_select`/`minimap`은 여전히 실행되지 않는다.
**A-1은 BLOCKED일 때 효과 대기와 `production_after` 캡처까지 건너뛰어야 성립한다.**

### (b) menu는 "미정의"가 아니라 "비대칭"이다 (Astra 결정 4 정정)

baseline `:2280~2296`과 후보 `:2772~2789` 모두 논리 `(184,560)`을 클릭하고 PS9→PS7을
`_wait_state`로 확인하며 전/후 캡처를 남긴다. 후보의 PS9→PS7 전이는 실제 관측된 효과다.
그러나 후보는 술어 없이 `result="PASS"`를 무조건 기록하고 전/후 캡처 SHA 상이 검사를 하지 않으며,
레코드 키가 baseline(`content`/`x11`/`expected`/`actual`)과 달라(`logical_content`/`x11_sent`/`scale`)
기계 대조가 불가능하다. 공용 헬퍼가 menu까지 덮어 같은 필드·같은 술어를 쓰기 전에는
"menu 포함 4/5" 주장을 하지 않는다.

### (c) Stage B의 "같은 시작 상태" 전제가 현재 근거 없다 (Astra 결정 2 응답)

`g1_baseline:2412~2416`은 장면을 `default two-player random game; map name/seed not exposed by
approved read-only offsets`로 기록하고 `replay_seed_observed=False`, 재현 식별자를 **same-run
fingerprint**로 둔다. 서로 다른 두 run이 같은 시작 상태라는 근거가 없으므로, 고정 논리 좌표
`(410,270)`/`(350,180)`/`(150,520)`은 맵이 다르면 다른 대상을 친다. 이 상태에서 델타가 갈리면
"후보 결함"과 "다른 맵"을 분리할 수 없다. 따라서 Stage B 판정을 Tier-1(장면 독립: menu, 좌표
불변식)과 Tier-2(장면 의존: 선택·드래그·미니맵, A-5 대조 필드 일치 시에만 비교, 아니면 UNKNOWN)로
나누고, 양쪽 무반응(delta=0)이 PASS가 되지 못하게 고정한다. `minimap`은 장면 의존적인 델타 대신
**camera 절대 목적지**로 비교한다. 상태값은 정수이므로 허용오차 0.

결정 전문은 `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`의 `lap171 middle 보강` 절
(L171-0~L171-6)에 있다. Astra 결정 1~6에 각각 대응한다.

- 변경파일: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(lap171 절 추가, lap169 본문 보존),
  `docs/STATUS.md`, 본 이력, `loop/ESCALATE_SOL` 삭제(원문은 아래 보존).
  **게임/하네스/테스트/바이너리 변경 0.** uncommitted, commit/push 없음(`LOOP_ALLOW_COMMITS` 기본0).
- 실행명령: `loop/PROMPT.md`→`AGENTS.md`→`docs/STATUS.md`→`INBOX`/`APPROVALS`→`docs/DESIGN.md`§1~2
  순서 읽기; `git status --short --branch`; `find local/runtime/20260911_214253_1178505_0`;
  `sha256sum`(산출물 6 + 소스/문서 5); `grep`으로 `process_exit`/`summary_count`/
  `winedlloverrides`/ddraw 모듈 경로 추출; `tools/runtime_env.py` 해당 구간 정독.
  **게임 run 0, 새 prefix/display 0.**
- Fast/make check/safety: **SKIP**. `make check`가 비대화형 권한 거부로 실행되지 않았다(2회 시도,
  재시도 없음). 이번 바퀴 코드 변경이 0이고 `tools/runtime_env.py` SHA가 lap168과 동일하므로
  lap168의 `192 passed`/`SAFETY_PASS`가 현재 트리의 마지막 유효 Fast 근거다. 이를 현재 PASS로
  승격하지 않는다.
- 수치/판정: P5 산출물 SHA 6/6 MATCH, 소스/문서 SHA 3/3 MATCH, 보호 EXE MATCH;
  **P5 재검증 RESOLVED(lap170 BLOCKED 해소)**; 카드2 구현 근거 결손 3건 확정 및 결정;
  게임 run 0, 제품 진전 0, 마일스톤 승인 0.
- fixture: 신규 fixture 없음. 재검증 대상 run의 fixture는 lap168 기록대로 diagnostic bridge를
  사용하는 실제 원본 게임의 default two-player random game(resource grant/control bridge/memory
  writes 모두 false)이며 이번 바퀴에 재실행하지 않았다.
- 반복 정체 재평가: lap170에 이어 이번도 문서만 변경했다(implementation-unchanged-streak 경고 인지).
  다만 이번 바퀴는 Stage A 착수를 막고 있던 blocker 3건을 코드 근거로 해소했으므로 다음 바퀴는
  work tier가 실제 코드 변경을 시작할 수 있다. 다음 측정 가능한 변경은 A-1 제어흐름 + A-2 공용
  헬퍼 + A-5 장면 필드와 그 회귀 테스트다.
- 다음행동: work tier(Luna 또는 Claude Sonnet5, high)가 Stage A만 수행. 현재 큐는
  `docs/STATUS.md`만 참조한다.

## 삭제한 `loop/ESCALATE_SOL` 원문 (lap170 Astra → middle, 이번 바퀴에 해소)

```
# lap170 Astra → middle escalation

필수 이전 바퀴 증거 확인에서 예상 밖 실패하여 중단했다. 재시도/마감/게임 실행 없음.
`local/runtime/20260911_214253_1178505_0/evidence.json` 읽기가 FileNotFoundError(exit1).
source/handoff SHA는 lap169 기록과 3/3 일치한다. 변경은 STATUS와 lap170 이력뿐이다.

이어 검증할 것:
1. P5 산출물 실제 위치를 확인하고 SHA·finalization·loaded module을 독립 대조한다. 현물 부재와 문서 경로 오류를 구분한다.
2. 카드2 Stage B의 동일 시작 상태, 입력별 기대 효과/무반응 배제, 메뉴 증거, production BLOCKED 및 overall 실패 보존 기준을 확정한다.
3. Stage A 하네스/테스트 범위를 재확인하여 work tier에 인계한다. Stage B/P6 수리/마일스톤 전환은 열지 않는다.

상세 결정: docs/history/laps/20260911_lap170_astra_card2_verification_boundary.md
현재 다음 한 가지: docs/STATUS.md
Fast/safety/runtime SKIP이며 프로세스 exit0·문서 작성은 검증/계획 승인이 아니다.

보존 문서 SHA256:
- docs/STATUS.md: `7ad48e595f0a2888d41a450f35ab8713ee8ed02dd58e05949efb756bba92afe0`
- docs/history/laps/20260911_lap170_astra_card2_verification_boundary.md: `595c9c0d94b0e7d7642bd4c52a114ce25c0bdd9ccbcb5a30b0ceb8db91147f76`
```

해소 근거: 1은 위 SHA 6/6 대조로 RESOLVED, 2는 L171-2/L171-3/L171-4로 확정,
3은 L171-1/L171-5/L171-6으로 재확인·인계. Stage B·P6·마일스톤은 열지 않았다.

## 이번 바퀴 산출 파일 SHA256 (uncommitted; `LOOP_ALLOW_COMMITS` 기본0)

- `docs/STATUS.md`: `2c184d9ca05181b782c83df8112a6602697ebfe86f981bfe82ed82fcb5de1941`
  (lap170 pin `7ad48e59…`에서 갱신)
- `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`:
  `54bb2841bb37e987407cfb1d3ce166338746efb121b831e93c85c2f662266804`
  (lap169 pin `99e888a5…`에서 갱신; lap169 본문은 삭제 없이 보존)
- `docs/history/laps/20260911_lap171_middle_card2_stageA_reconfirm.md`: 본 파일(자기 해시 제외)
- `tools/runtime_env.py`: `69b0f16253a850e02537d0d5dddbc97e43b7755cff447860a81e66914fdf0571`
  (**변경 없음** — lap168과 동일)
- `bash checks/safety.sh check`도 비대화형 권한 거부로 실행되지 않았다(SKIP, 재시도 없음).

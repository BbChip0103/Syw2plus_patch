# 2026-10-02 KST | lap 850 | G1 W70 P3 fixed-window 독립 확인·경계 승격

- 실제 provider/model/effort / 지정 역할: Codex native 새 세션, 사용자 지정 일반 middle(진단·계획·확인). 실제 서비스 model ID/effort는 검증 가능한 도구 정보가 없으며 모델 전환·승격 실행을 주장하지 않는다. `loop/.lap_counter=850` 읽기만 수행했다.
- 목표/가설: STATUS의 lap849 계측/bbox 결과를 독립 확인한다. 원본/save/build/raw SHA가 맞고 raw endpoint rate와 전체 histogram이 기록을 재현하면 성능 FAIL 근거를 수용한다. 성공 조건은 기존 3 fresh pair 각각 rate ratio≥0.95, p95 delta≤16ms이며 임의 완화하지 않는다. P3→P4 경계에서는 승인·구현 대신 승격 인계 후 종료한다.
- 현행 계약: PROMPT→AGENTS/INBOX/APPROVALS→STATUS→DESIGN §1~4→W70 카드/lap849 순으로 확인. 최신 사용자 결정대로 G1 최우선, G2 5000 유지·10000 종료, G3 중단, G4 보류, G5 승인·종료다. PROMPT의 옛 목표 문구로 종료 목표를 재개하지 않았다. 문서 추가 전 STATUS73/INBOX244/APPROVALS144줄로 소프트 한도 내였다.
- 변경 파일: 이 기록, `docs/history/20261002_lap850_prior_lap849_escalate_sol_archive.md`, `docs/STATUS.md`, `loop/ESCALATE_SOL`. 문서/인계만 변경, 게임/하네스 source·바이너리 수정0, 신규 게임 실행0, 커밋0(uncommitted). 원본/참고/다른 세션·기존 raw·runtime를 쓰거나 정리하지 않았다.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. save006 SHA: `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`, non-synthetic. fixture 원본·EXE를 직접 재해시했다. 과거 lap849는 private copy/prefix/display, scene player record8/unit558이며 이번 확인은 활성8인 부하시험이 아니다.
- 후보 DLL SHA(pair5/6/7): `ccae70dea70441aaec560b0302452b66f1b63caf8716e7fb646e437fb022c471` / `5fc047e653a03cd301eb88eb6fba536f0b2e1eefa785d56c6bc24e1ad2163223` / `a78c3314db8509fb6a48fed8742071143ab8c072edb0053161ef623b034ddaa6`. 각 build 입력40개는 현재 source와 MATCH, 복사본은 builder의 명시적 두 변환(inmm_stub.c poll 삽입·Makefile SRCS 추가)을 재현한 뒤 MATCH. generated runtime_bridge SHA와 manifest DLL도 MATCH.
- 실행 명령: `.venv/bin/python - <<'PY'` 독립 JSON/SHA/Pillow 검수(raw histogram nearest-rank p95 및 endpoints 산식; 제품 validator helper import 없음), `rg`/`sed`/`nl`로 지정 G1 source 열람, `view_image`로 pair5 원본800×600/후보1600×1200 loaded를 나란히 비교. 신규 PNG 생성0. 원본 화면 구도/HUD 배치는 일치하며 이 관찰은 전체 HD coverage·입력 검증이 아니다.
- 새 근거: 공유 temp `lap850_middle_review/review.json` SHA `af21055ab0ddf73093d7d5971446cf648fdecd563c626ffdac1b2f978574e32a`; `source-sha256.json` SHA `2dba3d52b8dfeb0d7556c8bcfad4a9b885881ed784a13c8a29a7fb5ac07c587a`. 둘의 절대 루트는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/`다. 각 pair/raw/capture·원본·fixture·DLL SHA와 세부 수치는 review.json에 보존했다.

## 독립 확인 결과

| lap849 pair | baseline Hz | candidate Hz | rate ratio | rate delta | present p95 delta | 성능 |
|---|---:|---:|---:|---:|---:|---|
| 5 | 19.999622 | 10.249722 | 0.512496 | −48.750422% | +9ms | FAIL |
| 6 | 19.999595 | 10.349779 | 0.517499 | −48.250059% | +10ms | FAIL |
| 7 | 19.999603 | 10.099781 | 0.504999 | −49.500090% | +11ms | FAIL |

- 전체 histogram의 중복 bin0/drop0/count 일치, 후보102/102/99 samples와 19,992/19,937/19,653ms span을 재계산했다. rate는 `Δstate.tick / Δmonotonic`; runtime_driver.py:294의 `0x8924B8`을 쓰며 옛 trace `game_tick`을 쓰지 않는다. endpoint PS3/동일 camera·no-input marker 제거를 확인했다. **중간 state samples는 raw에 저장되지 않았다.** 연속 PS3/tick-monotonic은 기록된 boolean과 코드 경로까지만 확인 가능하며 독립 재구성 PASS로 선언하지 않는다. camera도 시작/끝만 측정한다.
- scene state equality/source unchanged·cleanup 기록과 game 사본 실제 부재를 확인했다. prefix 무프로세스는 과거 cleanup 기록이며 이번 프로세스 전수 재조사 결과는 아니다.
- 후보 Scale2x present383/372/366, mask 내부 diff1,941,419/1,953,850/1,924,163·외부0, palette/miss/invalid0을 독립 집계했다. 모든 capture 경로/공유 원본 경로 SHA·dimensions를 재검산했다. post-bbox loaded SHA가 세 pair에서 같은 것은 현 장면 재현성 근거이며 **bbox 전후 불변을 단독 증명하지 않는다.** 정적 safe-bounds/full fallback 확인 외에 bbox 전후 일반 경계 회귀를 이번 세션이 새로 실행하지 않았다.
- 후보 first-to-last marker-window present의 inclusive reinvoke elapsed delta17,169/16,987/16,780ms, calls8,586/8,585/8,333, refresh333/333/322, inserts398/397/385, cache hits8,521/8,521/8,270, Scale2x blocks170,119,588/170,117,588/164,837,196을 재현했다. 이는 첫 present 이전 일을 제외한 cumulative counter 차이며 정확한 marker edge interval 총합이라고 확대하지 않는다.
- inclusive timer(`g1_mirror2x.c:670~706`)는 scratch 초기화·원본2회·hash/key lookup·frame 비교/복사/HD build·compose를 함께 센다. 따라서 re-render/cache 경로 비용이 크다는 사실은 수용하나 Scale2x가 단독 원인이라고 확정하지 않는다. bind의 full-frame fallback800×600(`g1_hd_asset.c:323~324`)·mismatch free/rebuild(`:337~358`, `:301`)가 큰 재생성 후보지만 writer/size별 원인 비중은 미계측이다.
- input 비교 HOLD(selection/empty만 true; drag_exact/minimap_gate_restore/production_effect false), minimap diagnostic `ORIGINAL_PARITY_UNKNOWN`, production UNKNOWN, GDI/전체 HD coverage/사용자 승인 미충족을 유지한다. 성능 p95만 통과했다고 P3 gate를 PASS하지 않는다.
- 검수 도구 오류2건은 해소: 비용 event를 종료 `mirror2x_metrics`로 잘못 고른 IndexError는 window의 `mirror2x_present`로 수정했다. copied stub==original을 요구한 검수 assertion은 builder의 위 두 정상 변환을 누락한 것이므로 변환을 직접 재현해 일치 확인했다. 필수 gate 실패나 게임 결함으로 분류하지 않는다.

## 승격 및 work-tier handoff 제안 — 승인 아님

- 판정: **P3_PERFORMANCE_FAIL_CONFIRMED / G1 HOLD / P4 금지**. lap849 기록과 raw의 실질 충돌은 발견하지 않았다. 사용자 호출의 “현재 작업이 마일스톤을 마감하거나 다음 마일스톤으로 넘기는 경계”에 해당해 `ESCALATE_SOL`을 갱신하고 종료한다. 일반 middle이 작업 범위 최종 승인/마감하지 않는다.
- 승격 middle은 review.json의 입력40개·DLL·histogram·rate 실패와 위 증거 한계를 확인하고 **한 bounded work 수리 범위**를 판정한다. 동일 raw의 일반 middle 재요약 회차를 추가하지 않는다.
- work-tier 제안 범위: `tools/inmm_stub/g1_mirror2x.c`, `g1_hd_asset.c/.h`, 필요 시 `direct_draw_trace.c`, `tools/g1_saved_scene_probe.py`와 해당 tests의 **P3 cache/reinvoke 비용 분해 및 확인된 병목 최소 수리만**. EXE/게임 로직·G2/G5·legacy validator·pin/golden·P4는 제외한다. 코드를 이 middle 세션이 변경하지 않았다.
- opt-in 고해상도 timer로 scratch fill/original 두 호출/hash+lookup/frame compare+copy+allocation/Scale2x build/compose의 포함 관계를 명시하고 배타 구간별 count/time/processed bytes를 같은 window ID에 남긴다. writer·full-frame/bbox·cache hit/insert/refresh별 원인/size를 bounded 집계한다. timing 토글 대조로 계측 overhead를 밝힌다. endpoint/state 샘플 tick·PS3·monotonic과 window 경계를 raw에 저장해 다시 독립 검산 가능하게 한다.
- 큰 frame refresh 원인이 확인되면 같은 work lap에서 최소 수정→빌드→격리 paired 재실행을 반복한다. full-key lookup/변경 frame invalidation/negative fail-closed를 삭제하거나 content compare를 무근거 생략하지 않는다. safe bbox fallback, mask 밖 diff0·팔레트/키/invalid0, scene/source/cleanup과 input 한계가 회귀하지 않아야 한다. 원본/save/옵션/하드웨어 조건을 고정한 새3 pair 모두 ratio≥0.95·p95≤baseline+16ms로 통과해야 중간 재검수 가능하다. 큰 구조 변경이나 2회 work 연속 FAIL이면 W70 §4에 따라 strategy로 보고한다.
- Fast/runtime: **SKIP_THIS_LAP**. 사용자 경계 stop 지시가 `patch-validation`의 `make doctor`/`make check` 및 PROMPT 일반 검증보다 우선한다. doctor/lint/typecheck/targeted pytest/full Fast/game·24k/144k를 새로 시작하지 않았다. lap849 Fast1218 passed/5 skipped는 과거 기록이며 이번 fingerprint PASS로 재사용하지 않는다. 기록 완료 뒤 안전/문서 한도·scoped diff만 확인하고 결과를 STATUS에 보강한다.
- 이전 ESCALATE_SOL14줄·SHA `0603d9e4509a4c117a62e121c7422b618d9edb9b9294fa5cf217ce98bfa7c746`는 위 archive에 byte-exact 보존했다. 새 기록/marker가 fingerprint를 바꾸므로 전체 Fast 미검증 상태를 명시한다. 현재 다음 한 가지는 STATUS만 따른다.

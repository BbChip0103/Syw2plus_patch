# 2026-09-28 | lap 746 | 목표 G5 ((F) H-STALE-TAIL 런타임 재현 + v8 최소 수정)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행). lap745
  middle 핸드오프(`docs/history/laps/20260928_lap745_middle_g5_a_h_independent_review_hold_stale_tail.md`)의
  "다음 한 가지"(S1~S3 paired probe, FAIL이면 최소 v8) 그대로 수행.
- 가설 / 사용자 관찰: lap745가 정적으로만 확인한 H-STALE-TAIL(v7 `LOAD_WRAPPER`가 새 선택 배열
  entries[20:50]을 로드 후에도 비우지 않음)을 런타임에서 재현한다. 예상: 50 선택 유지한 채 로드하면
  count≤20인데 entries[20:50]은 로드 직전 값 그대로 남아 count/실제 비0 칸 수 불변식이 깨지고, v5
  청크 게이트가 그 잔여 칸으로 명령을 흘려보내며, 전체 해제 시 count가 비정상값(음수 가능)이 된다.
- 예상 PASS / FAIL 조건: 모든 시점에서 count == 비0 칸 수, 로드된 선택(entries[0:count]) 밖 유닛에
  명령 0건, 해제 후 count==0·50칸 전부 0, 크래시 0, 원본 대비 동작 차이 없음(원본은 항상 ≤20).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`):
  - `tools/g5_stale_tail_probe.py` (신규, S1/S2/S3 paired 런타임 probe, `--candidate-version v7|v8`)
  - `patches/selection/g5_selection_cap50_v8.py` (신규, v7의 `LOAD_WRAPPER` zero-fill 폭을
    `STOCK_CAPACITY`(20)에서 `TARGET_CAPACITY`(50)로 넓히는 1바이트 수정)
  - `patches/selection/test_g5_selection_cap50_v8.py` (신규, v7→v8 바이트 diff가 정확히 1바이트이고
    그 오프셋이 LOAD_WRAPPER 캐이브 안이며 값이 0x14→0x32임을 고정하는 회귀 4종)
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`Syw2plus_re/Syw2plus`, 4회 실행
  전후 재확인 전부 불변). v7 `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`(기존
  lap740/743/745 기록과 재빌드 일치). **v8**
  `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`(v7과 정확히 1바이트만 다름,
  오프셋 1028541, `0x14`→`0x32`, `test_g5_selection_cap50_v8.py`로 고정). 솔로 로비, worker(slot 1198)
  앵커 7×8 dense fixture(55기 SEED_TYPE=2, 기존 G5 probe와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 4회 synchronous 격리 실행(`kill -0` 폴링, 세션 유지, 각
  `game`(~2.7GB) 사본은 직후 삭제·output/manifest/prefix/로그만 보존):
  1. `python3 tools/g5_stale_tail_probe.py --variant original --runtime-root
     local/runtime/lap746_stale_tail_original --artifact-root
     .../20260928_lap746_g5_h_stale_tail/original` → `PASS_NO_STALE_TAIL_EFFECT`.
  2. 같은 도구 `--variant candidate`(기본 v7) → `FAIL_STALE_TAIL_CONFIRMED`.
  3. 같은 도구 `--variant candidate --candidate-version v7`(재현성 확인, deselect 직후 count<0이면
     즉시 저장하는 추가 분기 포함) → 재현, 이번엔 count=-30에서 저장 시도 후 `resume_after_
     deselect_save` 45초 타임아웃으로 `FAIL`(아래 상세).
  4. 같은 도구 `--variant candidate --candidate-version v8 --attempt-menu-exit` →
     `PASS_NO_STALE_TAIL_EFFECT`.
  전체 artifact·캡처·probe-result.json은
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap746_g5_h_stale_tail/`에
  보존. `make check` 로그 `/tmp/lap746_make_check.log`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **원본(paired baseline): PASS.** 20선택 유지 로드 전후 내내 `count==nonzero_count`(20/20),
    해제 후 0/0, 재드래그 20/20, 우클릭 이동 후 19/20 fixture(+worker 1) 전원 정상 command 변화,
    `commanded_outside_legit_selection=[]`, 재저장 크래시 없음(`ps=23` pause 상태에서 process_alive
    유지, 이후 정상 재개).
  - **v7 후보: FAIL_STALE_TAIL_CONFIRMED(런타임 최초 확인, 기존 정적 예측 3건 전부 적중).**
    - ① 불변식 붕괴: 로드 직후 `count=20`인데 `nonzero_count=50`(entries[20:50] 전부 로드 직전
      값 그대로 잔존, `stale_tail_slots_after_load`=`[1147..1176]` 30개).
    - ② 명령 유출: 우클릭 이동 후 `commanded_slots_after_move`=49개(정상 19 + 잔존 꼬리 30 전부),
      `commanded_outside_legit_selection`=`[1147..1176]`(30개 전부) — 로드된 20선택 밖 유닛이
      실제로 명령을 받았다(v5 청크 게이트가 잔여 비0 칸으로 트리거된 것과 정확히 일치).
    - ③ 음수 count: 빈 지면 클릭 전체 해제 후 `count=-30`(재현 2/2, 두 번째 실행에서도 동일하게
      -30) — 해제 루틴이 count 기반 배열이 아니라 유닛별 "selected" 플래그(byte+0=1인 유닛 50개
      전부)를 순회하며 제거마다 count를 1씩 감소시키는 것으로 보인다는 정적 추정과 일치.
    - ④ **치명적 결과(런타임에서 새로 확인, 정적 예측보다 구체적):** count=-30 상태에서 즉시
      저장을 시도하자 `SAVE_ACTION_POINT` 클릭 후 게임이 **`ps=23`(저장 화면)에 무한정 멈추고
      8인 플레이어 레코드 전부(쌀/나무/유닛수/cap 등)가 0으로 초기화**됐다(45초 타임아웃 동안
      `resume_after_deselect_save` 미도달, `players[*].used/count/rice/wood` 전부 0). 프로세스
      자체는 죽지 않았지만(`poll()==None`) 응답 없는 무한 루프 또는 대규모 메모리 손상으로
      정적 분석이 예측한 "`rep movsd`가 음수 count를 부호없는 ~40억 dword 반복으로 읽어 크래시"
      위험의 실제 발현 형태로 판단한다(즉시 세그폴트 대신 행+데이터 파괴).
    - `source_unchanged` 4/4, 원본 EXE/보호 원본 0 변경.
  - **v8 후보(수정 후): PASS_NO_STALE_TAIL_EFFECT.** 로드 직후 `count=20, nonzero_count=20`(꼬리
    완전히 0), `legacy_after_load.count=20`(레거시 미러 동일 유지, 저장 호환 회귀 없음),
    `stale_tail_slots_after_load=[]`, `commanded_outside_legit_selection=[]`, 해제 후 `count=0`
    (음수 아님 → `negative_count_save_crash_check.attempted=False`), 재드래그 `50/50`, 재저장
    process_alive 유지(크래시 없음). `source_unchanged=True`.
  - **정적 회귀 범위 증명:** `test_build_is_v7_plus_exactly_one_changed_byte`가 v8과 v7의 바이트
    차이를 정확히 1바이트(오프셋 1028541, LOAD_WRAPPER 캐이브 안, `0x14`→`0x32`)로 고정 — 드래그/
    이동/공격/그룹지정·호출/사망후호출 정리(H4)/SAVE_WRAPPER 등 v7의 기존 PASS 경로는 코드 수준에서
    원천적으로 손댈 수 없다.
  - `pytest -q patches/selection/test_g5_selection_cap50_v8.py
    patches/selection/test_g5_selection_cap50_v7.py tests/test_g5_selection_inventory.py
    tests/test_g5_stock_selection_array_xrefs.py tests/test_g5_command_packer_xrefs.py` →
    **17 passed(17.25s)**. `make check` **1115 passed, 5 skipped(823.25s)**, ruff/compileall/mypy
    전부 PASS, `checks/context_limits.py` `CONTEXT_PASS`, `checks/safety.sh check` `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **S3(50선택 유지한 채 메인메뉴→새게임 이월)은 미해결로 남았다.** 일시정지 메뉴 7번째 항목
    "초기메뉴"(400,342, 35px 행 간격 추정) 클릭 후 화면이 `ps=23`에서 바뀌지 않아(확인 대화상자
    추정 좌표(400,300) 클릭도 무반응) `S3_INCONCLUSIVE_UNEXPECTED_SCREEN`으로 종료(v7/v8 둘 다
    동일). 캡처는 `s3-after-menu-exit-click.png`/`s3-after-confirm-guess.png`에 보존. 이 화면의
    실제 레이아웃(확인 대화상자 유무·좌표)은 다음 work가 스크린샷을 먼저 판독해 좌표를 재확정해야
    한다 — 추측 클릭을 추가로 반복하지 않았다(handoff 대상).
  - **(F) 재검수 범위:** 이번 lap은 F(원본 세이브 호환·양방향 crossload)를 다시 실행하지 않았다
    (lap740이 이미 양방향 PASS 확인, v8은 그 경로를 건드리지 않는다 — `test_load_wrapper_old_bytes_
    are_the_pinned_v7_encoding`가 저장 경로/`SAVE_WRAPPER`는 완전히 동일함을 고정). 다음 middle이
    F 재검수 시 필요하면 crossload 1회를 v8로 재확인할 수 있다.
  - S2의 "체력바 표시"·"개별 클릭 재선택 가능 여부"는 이번 lap에서 재드래그(전체 재선택 성공)로만
    간접 확인했고, 21~50번째 개별 유닛 단위 클릭 테스트나 스크린샷 육안 대조는 하지 않았다(시간
    예산, lap745의 "핵심 무결성 불변식"이 이미 결정적으로 FAIL/PASS를 가르므로 우선순위를 낮춤).
  - 제품 코드 변경은 v8 1바이트뿐이며 원본은 0 변경. `LOOP_ALLOW_COMMITS=0`이라 전부 uncommitted —
    다음 세션이 `git status`/해시로 검수한다. 사용자 milestone 재확인 여전히 없음.
- 다음 한 가지: middle(Opus5/Sol)이 (F)만 독립 재검수한다 — v8 재빌드 SHA 일치, v7→v8 1바이트 diff
  범위 확인, 이번 lap의 원본/v7/v8 raw 3세트 재계산, `make check`/`SAFETY_PASS`/`CONTEXT_PASS` 확인.
  PASS면 G5 체크리스트를 v8 기준으로 (F)=PASS로 갱신하고 S3(메인메뉴 이월)만 별도 미해결로 명시한 뒤
  사용자 milestone 재상정 여부를 판단한다. S3는 다음 work가 스크린샷 판독으로 좌표를 재확정해 마저
  채운다.

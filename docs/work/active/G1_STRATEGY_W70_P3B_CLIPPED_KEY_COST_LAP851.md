# G1 W70 P3b — P3 성능 FAIL 전략 판정: 지속 `FEASIBLE`, bounded 수리 1회 (lap851 strategy, 2026-10-02)

> **종결(lap853 strategy):** lap852가 §2를 수행했고 §4-1 승격은 `G1_STRATEGY_W70_P3C_ENV_LATCH_COMPOSE_LAP853.md`가
> 해소·대체한다. §1의 시간 귀속(full-frame 캐시)은 그 카드 §0.5에서 정정됐다. 아래 원문은 보존용이다.

- 발행: lap851 strategy. 실제 모델 Claude Code `claude-fable-5-1`(세션 지정 strategy 역할, effort 세션 비노출).
  러너가 이 세션을 strategy로 호출했고 자동 폴백이 아니다. 게임 실행0, 제품/하네스 source·binary 변경0, 커밋0.
- 호출 사유: W70 카드 §4 "같은 단계 work 2회 연속 FAIL" 조건 충족 — lap844 P3 성능 PASS는 lap847에서 무효화됐고
  (trace `game_tick`=시간값, 실제 sim tick `0x8924B8` 아님), lap849 통제 3 pair는 ratio 0.505~0.517로 FAIL(lap850 독립 확인).
- 입력 근거(이 세션이 직접 읽음): `docs/history/laps/20261002_lap849_*.md`, `..._lap850_*.md`,
  `docs/history/20261002_lap850_confirmed_p3_perf_fail_handoff_archive.md`, 공유 temp `lap849_perf_pair5/6/7/pair-result.json`,
  현재 source `tools/inmm_stub/g1_mirror2x.c`(`mirror_reinvoke` 659~711, `compose_sentinel` 371~427, `copy_present` 429~592),
  `tools/inmm_stub/g1_hd_asset.c`(`g1_hd_asset_begin` 179~237, `bind_identity_frame` 312~413, `build_scale2x` 247~286),
  `tools/inmm_stub/g1_scratch_bounds.h`, W70 카드 `G1_STRATEGY_W70_FULLSCREEN_HD_LAP819.md` §0.3·§3.5·§4.

## 0. 판정 요약

1. **P3 지속 = `FEASIBLE`. P3 중단/NOT_FEASIBLE 판정 없음, 성능 기준 §3.5 완화 없음, P4 전환 금지 유지.**
2. 근거: 성능 FAIL의 지배 비용이 **구조적 한계가 아니라 카드 §0.3 설계와 어긋난 구현 결함**(클립된 프리미티브를
   800×600 full-frame 키로 캐시)에 귀속될 가능성이 raw 산술로 높다(§1). 원본 2회 재호출+sentinel 합성만의 바닥 비용은
   lap817-r5 실측 0.246ms/call(당시 full clear 포함)로 예산 안이다.
3. 다음 work 1 lap = **P3b**: 배타 구간 계측(§2-A)을 먼저 넣고 같은 lap 안에서 클립 키 수리(§2-B)를 구현→빌드→격리
   fresh 3 pair→원인 수리 반복(최대 3회, INBOX 2026-09-29 20:11 규칙). ESCALATE는 §4 조건에서만.
4. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 독립 검수·3단 사용자 승인은 그대로 남는다.

## 1. raw에서 직접 도출한 비용 구조 (lap849 pair5/6/7, 20초 고정창, 후보 lane)

| 항목 | pair5 | pair6 | pair7 | 해석 |
|---|---:|---:|---:|---|
| baseline primary present / window | 400 | 400 | 400 | 20Hz = tick당 present 1회 |
| candidate primary present / window | 102 | 102 | 99 | ≈5fps, tick 10Hz |
| reinvoke calls / window(delta) | 8,586 | 8,585 | 8,333 | present당 ≈84 primitive |
| reinvoke elapsed(delta, inclusive) | 17,169ms | 16,987ms | 16,780ms | window 벽시계의 84~86% |
| 평균 inclusive / call | 2.00ms | 1.98ms | 2.01ms | lap817-r5 sentinel-only 0.246ms의 ≈8배 |
| identity cache refresh | 333 | 333 | 322 | |
| Scale2x blocks(delta) | 170,119,588 | 170,117,588 | 164,837,196 | |
| **blocks ÷ refresh** | **510,869** | **510,863** | **511,917** | ≈ 800×600=480,000 + 신규 insert 몫 |
| 전 run 단일 call 최대 | 461ms | 465ms | 467ms | full-frame rebuild 또는 첫 할당 의심 |

- `bind_identity_frame`은 `full_frame`(원점이 `800-w`/`600-h`를 넘는 **클립된** 프리미티브) 키를 800×600 전체로
  캐시한다(`g1_hd_asset.c:323~325`). 클립된 스프라이트/타일이 한 픽셀이라도 움직이면 같은 source 포인터라도 전체 프레임
  내용이 달라져 mismatch→evict→480k 바이트 복사+480k 블록 Scale2x 재생성이 일어난다(`:337~358`, `:301`). 위 산술은
  refresh 1회당 ≈ 전체 프레임 Scale2x이며 **Scale2x 블록의 ≥94%가 이 경로**임을 뜻한다(159.8M/170.1M).
- 같은 키의 hit 경로도 매 call 480k 바이트 비교(`:330~336`)이고, `mirror_reinvoke`의 scratch clear도 클립 시
  832×600×2 전체 fallback(`g1_mirror2x.c:686~691`)이다. 즉 클립된 프리미티브 1회 = clear 1MB + 비교 480KB
  (+mismatch 시 복사 480KB + Scale2x 480k 블록 + HeapAlloc/Free 2회).
- W70 카드 §0.3은 원래 "키 첫 등장 시 원본 함수를 private scratch(dst=(0,0), viewport 전체)에 한 번 더 호출해
  **클립 없는 디코딩 프레임**을 얻고 Scale2x→캐시"로 정했다. 현 구현은 이 대신 full-frame 캐시를 택했고 그것이 비용의
  근원이다. 따라서 **설계 변경이 아니라 설계 복귀**다.
- 한계: 위는 cumulative counter 산술이며 writer/크기별 배타 시간은 미계측(lap850 지적 유지). 그래서 §2-A 계측을 수리보다
  먼저 넣고, 수리 전/후를 같은 계측으로 남긴다.

## 2. P3b work 범위 (한 lap, 구현 우선)

### A. 배타 구간 계측 (opt-in `SYW2_G1_PERF_SECTIONS=1`, 기본 OFF)
1. `QueryPerformanceCounter` 기반(GetTickCount 해상도 불충분) 배타 구간: `scratch_clear` / `original_call_a` /
   `original_call_b` / `hash_lookup`(readable_source+hash+find_key) / `bind_compare` / `bind_copy_alloc` /
   `scale2x_build` / `compose` / `negative_probe`. 각 구간 count·ns 합·max, 처리 바이트(비교/복사/블록).
2. 결과 분류 카운터: `full_frame` vs `bbox` call 수, cache `hit`/`insert`/`refresh`별 call 수와 프레임 바이트,
   writer(a/b)별 분리. 같은 window ID의 `perf_window_meta`/histogram 이벤트와 함께 raw(trace.jsonl)에 기록.
3. probe(`tools/g1_saved_scene_probe.py`)는 window 동안 **중간 state sample**(sim tick `0x8924B8`, PS, camera,
   monotonic)을 ≥1초 간격으로 raw에 보존한다(lap850 "중간 samples 미보존" 해소). 계측 ON/OFF 각 1회로 계측 overhead를 밝힌다.
4. 수리 전 계측 pair 1회(현재 source) → 수리 후 fresh 3 pair. 수리 전 pair는 "pre" 라벨로 raw 보존.

### B. 클립 키 수리 (카드 §0.3 설계 복귀)
1. `full_frame` 캐시 경로 제거. 클립된 프리미티브(원점이 음수/프레임 밖, 또는 `x+w>800`/`y+h>600`)는 키를
   `(writer, source, w, h, digest)`로 통일하고 **clip 없는 w×h 프레임**을 캐시한다: insert 시에만 원본 함수를 private
   scratch에 `dst=(0,0)`(필요 시 viewport 전체로 임시 설정 후 즉시 원복)로 1회 더 호출해 디코딩 프레임을 얻는다.
   `w>800`/`h>600`은 기존대로 invalid(nearest 잔여, 카운트 공개).
2. lookup은 signed offset(`p − origin`)으로 캐시 프레임 안 좌표를 계산한다. 가시 영역 밖 좌표는 miss.
3. 내용 비교(fail-closed)는 **가시 교집합 영역만** 캐시 프레임의 해당 부분과 비교한다. 삭제·샘플링·생략 금지
   (lap837이 실제 2450 mismatch를 잡은 경로). negative probe·full-key search·변경 frame invalidation 유지.
4. scratch clear/compose도 클립 교집합 사각형으로 한정(현재는 전체 fallback). 교집합을 증명 못 하면 기존 전체 fallback.
5. (0,0) 재호출의 게임 상태 부작용0을 기존 state/scene hash parity로 검사한다. 렌더러 viewport 필드를 바꾼다면
   old 값 저장→호출→정확 원복, 예외 시 원복 보장.
6. 금지: EXE 패치, 임계값 변경, legacy validator 완화, G2/G5 source·`local/runtime/g2_*`·`*g5_esl2608*` 접촉,
   P4 코드, 새 의존성. 새 코드는 새 파일 또는 `g1_hd_asset.c`에 두고 `g1_mirror2x.c`(896줄)는 연결만.

### C. 합격 (§3.5 불변 + P3 기존 gate)
- fresh 3 pair 모두: `tick_rate_ratio ≥ 0.95`, `present p95 ≤ baseline + 16ms`, scene equal·source unchanged·cleanup PASS,
  Scale2x validator(마스크 밖 diff 0, palette/miss/invalid 0), selection/empty/drag parity 기존 수준 유지,
  loaded 캡처 non-black·1600×1200.
- 추가 보고(gate 아님, 판정 근거): candidate present/window(기대 ≥0.95×baseline≈380), refresh/window, full-frame
  call 0, 배타 구간 표, 평균 inclusive/call. 운영 추정치: present당 ≈84 call이므로 **평균 ≤0.35ms/call·present당 mirror
  총 overhead ≤ ~40ms**가 ratio 0.95의 대략적 필요조건이다(baseline은 20Hz 고정 타이머로 sleep 여유를 쓰므로 정확한
  바닥은 계측이 정한다).

## 3. 다음 middle 검수 조건

- 수리 후 raw/pair/DLL SHA, build 입력, 배타 구간 표와 tick rate·p95 독립 재계산. full-frame 경로 제거와 fail-closed 비교
  유지(코드 열람). (0,0) 재호출 부작용 parity. 통과 시 P3 2단 수용 → **P4 구조 판정 회차**로 전환 가능(사용자 승인 아님).
- "수리 대상이 명확한 구현 결함"이면 middle은 짧게 확인만 하고 work로 되돌린다(INBOX 2026-09-29 20:11).

## 4. 정지/승격 규칙 (strategy 재호출 조건)

1. work가 3회 반복 후에도 FAIL이고 배타 계측이 **원본 2회 호출 + compose만으로 예산 초과**를 보이면 `BLOCKED(structure)`로
   승격 — 그때 strategy가 sentinel 1회화/dirty-rect present 등 구조 대안을 판정한다. 그 전에는 재호출 안 함.
2. 3회 반복 후 FAIL이되 다른 단일 구간(예: present compose ≈10ms, hash/VirtualQuery)이 최대 비중이면 **같은 카드로 work 1회
   추가**(§2 범위 안, 총 2 work lap). 2회째도 FAIL이면 strategy.
3. (0,0) 재호출이 상태 hash를 바꾸거나 크래시하면 즉시 ESCALATE(안전·근거 충돌).
4. 입력 parity(selection/empty/drag) 회귀도 FAIL이며 수리 대상이다.

## 5. 남은 위험

- 클립 프리미티브가 정말 지배 비용인지는 §2-A 계측으로만 확정된다. 아니면 §4-2 경로.
- (0,0) 재호출은 렌더러 상태(viewport/clip 필드)를 건드릴 수 있다. 필드 주소 미확정이면 "dst=(0,0)으로 호출하되 클립은
  그대로"가 먼저 시도할 최소안이고, 그래도 원점 이동 시 프레임이 변하면 그 비율을 보고한다.
- present compose(`copy_present`, 800×600 3회 순회+1600×1200 hash) ≈ p95 +9~11ms는 별도 비용. 이번 범위 밖이되
  §4-2 후보 1순위로 기록한다.
- 측정은 Xvfb/Wine 환경이며 사용자 하드웨어 수치가 아니다.

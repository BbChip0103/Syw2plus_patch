# G2 work 카드 W5 — 재배치 목적지 **섹션 커버리지** 수리 + W4 §5 실행

발행: lap402 middle (Claude Code `claude-opus-5` / high), 2026-09-20 KST
수행: work tier (`claude-sonnet-5` / high 또는 Luna/high), **다음 work 회차**
상한: **한 work 회차 또는 60분 중 먼저 도달하는 시점, 실패 가설 2개**
승인: **불필요** — 기존 격리 사본 + 기존 save000 fixture. 새 fixture·새 시나리오 없음.

W4(`G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md`)를 **대체하지 않는다.** W4의 §1 배치 설계(꼬리 재배치),
§2 B-2 상수 4개, §3 B-3 fixup 필수 카운트, §5 실행 순서, §6 범위 경계는 **전부 그대로 살아 있다.**
이 카드는 lap402 검수가 찾은 결함 하나(§1)와 그것을 막을 게이트 하나(§2)만 추가하고,
그 뒤의 순서를 §3에 다시 적는다.

> **재조사 금지.** lap397(정적 표면)·lap398(FO 3건)·lap399(패처 골격)·lap400(충돌 스캔)·
> lap401(재배치 구현)·lap402(검수)가 낸 바이트 사실은 확정이다. 이 회차는 **수리와 실행**만 한다.
>
> **lap401에서 유지되는 것(재작업 금지):** `tail_relocation_storage_layout_v1`의 배치 계산
> (`layout()`), N=1200 항등, B-2 4상수, B-3 재스캔, `_patch_literal` 재디코드 수리는 lap402가
> 독립 대조로 **ACCEPT**했다(명령 경계 드리프트 0, 변경 명령 1,056 == 기대 1,056, 기대 밖 0,
> 누락 0, `old+delta` 아닌 값 0). **손대지 말 것.**

## 0. 왜 lap401 후보 `2571d6a2…`를 기동하면 안 되는가 (lap402 확정)

재배치된 세 배열 `[0x0108C000, 0x012B88D8)`(2,279,640 B) 중 **17,360 B(0.76%)만** 후보 자신의
섹션 테이블 안에 있다. 후보 `.data`는 `VA 0x004EC000 / VirtualSize 0x00BA43D0` ⇒ 가상 끝 `0x010903D0`,
다음 섹션 `.rsrc`는 `0x012B9000`. 블록은 그 구멍에 놓인다 — SizeOfImage 안이지만 **모든 섹션의
`[VA, VA+VirtualSize)` 밖**이다. **unit_pool slot 10부터, existence/age는 전부** 매핑 밖이다.

원인: `tail_relocation_storage_layout_v1.build_layout_artifact`의

```python
total_growth = sum(region.delta for region in result.regions)   # 18,840 B
new_data_vsz = data_vsz + total_growth
```

`RegionLayout.delta`는 `base_preserving_storage_layout_v1`의 정의대로 **배열 성장량이지 주소 이동량이
아니다**(그 모듈 주석이 명시). 제자리 성장에서는 둘이 같아서 옳았지만, **재배치에서는 배열이 통째로
옮겨가므로 확보해야 할 공간은 성장량이 아니라 블록 전체 크기**다. 바로 아래 가드
`if data_va + new_data_vsz > new_rsrc_rva: raise`는 **과확장만** 막고 미확장은 통과시킨다.

재현: `docs/history/laps/probes/20260920_lap402_middle_g2_tail_relocation_review_probe.py`(rc1, D1),
산출물 `.../out/20260920_lap402_middle_g2_tail_relocation_review.json`,
기록 `docs/history/laps/20260920_lap402_middle_g2_tail_relocation_review.md`.

## 1. 수리 — `.data` VirtualSize를 블록 끝까지 확장

`build_layout_artifact`에서 `.data`의 새 VirtualSize를 **성장량이 아니라 재배치 블록 끝에서** 산출한다:

```
new_data_vsz = result.regions[-1].new_end - (IMAGE_BASE + data_va_rva)
```

N=1210에서 이 값은 **`0x00DCC8D8`**(원본 `0x00B9FA38` 대비 +2,281,120 B)이고,
기존 `.rsrc` 비침범 가드를 **1,832 B 여유로 통과**한다(lap402 `d2_repair_fits_under_existing_rsrc_guard`).

- `n == STOCK_CAPACITY`(1200) 경로는 **조기 return이라 손대지 않는다** — 항등 앵커 불변.
- 배치 설계는 바꾸지 않는다. 새 섹션 추가·`.rsrc` 재배치 방식 변경·N 변경 **금지**.
  (새 섹션 생성은 섹션 테이블 확장이 헤더 크기를 건드려 훨씬 큰 변경이다. 지금은 불필요.)
- `.data`의 `SizeOfRawData`는 **바꾸지 않는다**(BSS 확장이므로 raw 바이트는 움직이지 않는다).
  `if len(out) != len(original)` 단언은 그대로 통과해야 한다.
- 수리 후 후보 SHA는 반드시 `2571d6a2…`와 **달라진다**. 새 SHA를 기록에 남긴다.

## 2. 새 필수 게이트 G-c — 기동 전 정적 통과

W4 §4의 G-a/G-b는 그대로 두고, 아래를 **추가**한다. 실패하면 기동하지 않는다.

- **G-c 커버리지:** 후보 **자신의 섹션 테이블**에서, `[pool.new_start, age.new_end)`의 **모든 바이트**가
  어떤 섹션의 `[VA, VA+VirtualSize)` 안에 있다. 부분 커버리지는 FAIL.

G-a/G-b와 마찬가지로 **재사용 가능한 pytest 회귀 앵커**로 넣는다
(`test_tail_relocation_storage_layout_v1.py`). lap402 probe의 `D1` 블록이 그대로 옮겨 쓸 수 있는
구현이다. **N=1200 항등 회귀와 W4 §3 필수 카운트 회귀는 반드시 함께 유지한다.**

교훈 일반화(같은 계열 결함 재발 방지): 재배치 계산기에서 `RegionLayout.delta`를 **주소 이동량으로
읽으면 안 된다**. 주소 이동은 `new_start - old_start`이며, 패처(`g2_unit_pool_expansion_v1`)는
이미 그렇게 계산한다 — 헤더 쪽만 성장량을 쓰고 있었다.

## 3. 실행 — W4 §5 그대로, 다만 P-0는 D1과 무관

- **P-0(양성 대조군)은 원본 바이너리만 쓰므로 §1 수리와 독립이다.** 먼저 하거나 병행해도 된다.
  새 prepare run에서 `syw2plus_original.exe`를 그대로 기동해 PS9 도달 확인.
  PS40 정지면 **환경 회귀**이므로 패치·파일명 트랙을 멈추고 `wine_dll_overrides`·private `ddraw.dll`
  로드 단언부터 진단한다(W4 §5 1번 그대로, 배제된 가설도 그대로 — 재조사 금지).
- **S-1은 §1 수리 + G-c PASS 전에는 착수 금지.** 미수리 후보의 S-1 결과는 "패치 결함"과
  "환경/파일명"을 구분하지 못해 해석 불가다.
- S-1 이후 S-2~S-5는 W3 §A 표 그대로 판정한다.
- 각 run의 `driver_out`은 **run마다 다른 디렉터리**를 쓴다(lap399 provenance 사각 재발 금지).

## 4. 범위 경계 (W4 §6 그대로 유지)

- 저장/LAN은 PASS 조건이 아니지만 **후속 필수 blocker**다. 꼬리 재배치가 existence/age를 bulk blob
  밖으로 빼내므로 **저장 파일 호환성은 반드시 깨진다** — 기록에 명시한다.
- lap385/388 저장포맷 통합 blocker, lap389 owner-transfer NO_GO, `ESCALATE_SOL` §5~§10(F4 포함)을
  **뒤집지 않는다**.
- 원본/참고 저장소 쓰기 금지. 메모리 쓰기 0(`process_vm_readv` 폴링만). baseline/golden 수정 금지.
- 결과는 **다음 새 middle 세션이 독립 검수**한다. work는 자기 결과를 최종 승인하지 않는다.

## 5. 부수(낮음, 이 카드의 PASS 조건 아님)

`docs/history/laps/probes/`의 lap400·lap401 probe는 `REPO_ROOT = Path(__file__).resolve().parents[3]`로
잡는데 실제 루트는 `parents[4]`다. 기록된 `python3 docs/…/probe.py` 명령이 그대로는
`ModuleNotFoundError: No module named 'patches'`로 죽는다(저장소 루트 CWD + `PYTHONPATH=.`면 rc0 재현).
**과거 probe 파일과 기록은 고쳐 쓰지 않는다**(provenance 보존). 새로 쓰는 probe만 `parents[4]`를 쓴다.
필수 게이트 영향 없음(lap339).

# G2 work 카드 W4 — UnitStruct 풀 **재배치**(relocation) 스파이크

발행: lap400 middle (Claude Code `claude-opus-5` / high), 2026-09-20 KST
수행: work tier (`claude-sonnet-5` / high 또는 Luna/high), **다음 work 회차**
상한: **한 work 회차 또는 60분 중 먼저 도달하는 시점, 실패 가설 2개**
승인: **불필요** — 기존 격리 사본 + 기존 save000 fixture. 새 fixture·새 시나리오 없음.

W3(`G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`)를 **대체**한다. W3의 §A 합격식·§C 봉투·§E 범위경계는
그대로 살아 있고, **§B-1의 목적지 선택과 도구 지정만** 이 카드가 정정한다.

> **재조사 금지.** lap397(정적 표면)·lap398(FO 3건)·lap399(패처 골격·B-2 4상수)·lap400(충돌 스캔)이
> 낸 바이트 사실은 확정이다. 이 회차는 **구현과 실행**만 한다.

## 0. 왜 lap399 후보 `303c78f8…`를 실행하면 안 되는가 (lap400 확정)

`base_preserving_storage_layout_v1`은 **unit_pool의 base가 움직이지 않는** 계산기다. lap399가 B-1을
여기에 위임한 결과 `deltas["unit_pool"] == 0`이고 `b3_fixup_site_counts["unit_pool"] == 0` —
수집한 1,014건이 **0건 적용**됐다. 풀은 제자리에서 위로 자라 N=1210에서
`[0x00892410, 0x00896D80)` 18,800 B를 차지하는데, 그 구간은 `.text` 리터럴 **1,311건**(disp 1,072 /
imm 239, 그중 bulk base `0x892410` 정확 일치 179건)이 읽고 쓰는 **live state·bulk blob의 머리**다.
후보는 그중 **0건**을 고친다. ⇒ S-6는 실행 전에 이미 설계로 위반. 상세·재현:
`docs/history/laps/20260920_lap400_middle_g2_pool_overrun_reject.md`,
`docs/history/laps/probes/20260920_lap400_middle_g2_pool_overrun_probe.py`(rc0, `failures=[]`).

**lap399의 `N<=1217` 상한은 안전 상한이 아니다.** 제자리 성장에서는 `N>1200`인 모든 N이 깨진다.

## 1. 정정된 B-1 — 세 배열 전부 **이미지 꼬리 virgin BSS로 재배치**

lap400 D4 스캔: `.data` BSS 끝 `0x0108BA38`부터 2.18 MB 구간 `[0x0108BA38, 0x012B8310)`의 `.text`
리터럴은 **1건**뿐이고(`0x00401402 push 0x1100007`), 주소가 아닌 플래그 즉치로 보인다.
**1,311 대 1.** 이 꼬리가 W3 §B-1이 원래 요구한 목적지다.

| 영역 | 원본 base | 새 base(권고) | delta | 크기(N=1210) |
|---|---|---|---|---|
| unit_pool | `0x0066B790` | 꼬리 정렬 base `P` | `P - 0x66B790` (**0이 아니어야 한다**) | `0x758 × N` |
| unit_existence | `0x008990C8` | `E` | `E - 0x8990C8` | `2 × N` |
| unit_age | `0x00899A28` | `E + 2N` | — | `2 × N` |

- **`새_age_base == 새_existence_base + 2N` 인접 배치는 그대로 필수**(할당자 `[ecx-0x960]` 변위, §2).
- 세 배열을 전부 꼬리로 옮기면 bulk blob 내부는 **한 바이트도 움직이지 않는다** ⇒ catA/catB/
  active/PlayerStruct/`0x892410` 별칭 179건은 W3대로 계속 **손대지 않는다**.
- PE 기하(`.data` VirtualSize, `.rsrc` RVA, SizeOfImage, 9개 resource `OffsetToData`)를 늘리는 방법
  자체는 `base_preserving_storage_layout_v1.build_layout_artifact`가 이미 검증한 절차다(lap388 ACCEPT).
  **그 절차는 재사용하되, 세 배열의 새 base를 꼬리로 주는 layout 공급자를 새로 쓴다.** 이름이
  "base preserving"인 계산기를 B-1 목적지 결정에 그대로 쓰면 이 카드가 금지하는 제자리 성장이 된다.
- `N`은 작게 유지한다. **N = 1210** 권고(slot 1200~1209 열 칸이면 S-2~S-5에 충분).
  꼬리 재배치에서는 catA/catB/FO-3 gap 충돌이 사라지므로 `N<=1217` 제약은 적용되지 않는다.

## 2. B-2 상수 4개 — lap399 구현 유지

`0x00442FAC`(스캔 시작 = `새_age_base + 2`) / `0x00442FB1`(existence 상대 변위 = `-2N`) /
`0x00442FD1`(스캔 배타적 끝 = `새_age_base + 2N`) / `0x0044317D`(전멸 루프 상한 = `N`).
old bytes 확인 후 교체하는 lap399 구현이 옳다. `0x0044317D` 단독 변경은 여전히 **금지**.

## 3. B-3 fixup — lap399 구현 유지, 다만 **적용 수를 반드시 보고**

`patches/population/g2_unit_pool_expansion_v1.py`의 재스캔·bucket0 검증·`_patch_literal` 유일성
검증·`BuildAbortedError` 골격은 **그대로 좋다**(lap400이 독립 재유도해 ACCEPT). FO-4
(`0x00421349`/`0x0048F4B4`)·B-2 4사이트 하드 제외도 유지.

변경점은 delta가 0이 아니게 되는 것뿐이며, 그 결과 적용 수는 다음이어야 한다:

```
b3_fixup_site_counts == {"unit_pool": 1014, "unit_existence": 34, "unit_age": 4}
```

**`unit_pool`이 0이면 그 회차는 즉시 FAIL이다.** lap 기록에 이 딕셔너리를 기계 산출 그대로 인용한다.

## 4. 실행 전 필수 게이트 (새로 추가 — 이번 회차의 핵심 안전장치)

후보를 **기동하기 전에** 아래 두 가지를 정적으로 통과시킨다. 실패하면 실행하지 않는다.

- **G-a 침범 0:** 새 pool/existence/age가 차지하는 세 구간 각각에 대해, 원본 `.text`가 그 구간을
  가리키는 리터럴 사이트 수가 **0**이거나, 0이 아니면 **각 건을 개별 분류해 주소가 아님을 보인다**
  (lap400 D4의 `push 0x1100007` 1건이 유일한 알려진 후보).
- **G-b 원상 보존:** 후보에서 `[0x00892410, 0x00975D8C)` bulk blob의 **모든 바이트 의미가 원본과
  동일**함을 보인다 — 즉 세 배열이 그 안에 있지 않고, 그 안을 가리키는 리터럴이 원본과 동일함.

두 게이트를 그대로 검사하는 재사용 가능한 assert를 pytest에 추가한다(회귀 앵커).
**N=1200 항등 회귀(lap399 최강 앵커)는 반드시 유지한다.**

## 5. 실행 — S-1 재시도 전에 **양성 대조군 먼저**

lap399가 확정한 것: 바이트 동일 원본을 `control_renamed_original.exe`로 개명하면 `PS=40`에서 정지
(31표본/30초, `trace.jsonl` 보존). **아직 확정되지 않은 것:** 같은 prepare run에서 원래 이름
`syw2plus_original.exe`가 PS9에 도달하는가. 이 양성 대조군이 없으면 "파일명 의존"과 "이 run 환경
회귀"가 구분되지 않는다(lap400 §3).

배제된 가설(재조사 금지): `runtime_driver.SUPPORTED_EXECUTABLES`의 profile 문자열은 기동 절차를
바꾸지 않는다(SHA 게이트 라벨). `dxwrapper.ini`의 `IncludeProcess`/`ExcludeProcess`는 비어 있어
래퍼는 exe 이름으로 게이트하지 않는다.

순서:

1. **P-0 양성 대조군** — 새 prepare run에서 `syw2plus_original.exe`를 그대로 기동해 PS9 도달 확인.
   - PS9 도달 ⇒ 환경 정상, 파일명 가설 확정. 2번으로 간다.
   - PS40 정지 ⇒ **환경 회귀**다. 패치·파일명 트랙을 멈추고 `wine_dll_overrides`(manifest는 `ddraw=b`,
     lap334 봉투는 `ddraw=n,b`)·private `ddraw.dll` 로드 단언부터 진단한다. 실패 가설 1회 소진.
2. **S-1** — 후보를 원본 파일명 `syw2plus_original.exe`로 배치해 기동(원본은 별도 이름으로 보존).
   `SUPPORTED_EXECUTABLES`를 "파일명 → 허용 SHA **집합**"으로 넓히는 편이 실행 스크립트 신설보다
   작다. PS9 도달 후 save000 로드 → PS3.
3. **S-2~S-5** — `새_existence_base`로 slot 1200~1209의 existence/age/pool을 직접 read.
   W3 §A 표 그대로 판정한다. **S-2 관측은 S-6가 PASS인 후보에서만 의미가 있다**(lap400 §1).

각 run의 `driver_out`은 **run마다 다른 디렉터리**를 쓴다 — lap399는 후보 run 로그가 control run에
덮여 provenance 사각을 남겼다. 재발시키지 않는다.

## 6. 범위 경계 (W3 §E 그대로 유지)

- 저장/LAN은 PASS 조건이 아니지만 **후속 필수 blocker**다. 꼬리 재배치는 세 배열을 bulk blob 밖으로
  빼내므로 **저장 파일 호환성은 반드시 깨진다** — 이 사실을 lap 기록에 명시한다.
- lap385/388 저장포맷 통합 blocker, lap389 owner-transfer NO_GO, `ESCALATE_SOL` §5~§10(F4 포함)을
  **뒤집지 않는다**. 이 스파이크는 그 blocker의 부분집합을 건드릴 뿐이다.
- 원본/참고 저장소 쓰기 금지. 메모리 쓰기 0(`process_vm_readv` 폴링만). baseline/golden 수정 금지.
- 결과는 **다음 새 middle 세션이 독립 검수**한다. work는 자기 결과를 최종 승인하지 않는다.

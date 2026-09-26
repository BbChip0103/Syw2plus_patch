# 2026-09-20 | lap 401 | 목표 G2 (전역 UnitStruct 풀 확장 — W4 B-1 재배치 구현)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, **work(실무) 역할**.
  work 카드 `docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md`(W4) §1~§4를 구현.
- 가설 / 사용자 관찰: lap400이 REJECT한 원인(§B-1을 `base_preserving_storage_layout_v1`에
  위임 ⇒ `unit_pool` delta 0, fixup 0/1,014 적용, 풀이 제자리에서 live state 18,800B 침범)을
  새 layout 공급자로 고치면 `b3_fixup_site_counts == {"unit_pool":1014,"unit_existence":34,
  "unit_age":4}`(W4 §3 필수치)를 만족하면서 N=1200 항등·G-a·G-b를 모두 통과할 것.
- 예상 PASS / FAIL 조건: 위 카운트 불일치(특히 `unit_pool`==0)·N=1200 비항등·G-a 미분류
  참조·G-b 신규/변경 참조 중 하나라도 있으면 FAIL. 전부 충족하면 이 회차의 구현 PASS
  (제품/게임 실행 승인 아님 — S-1~S-6는 다음 회차).

## 구현 및 신규 발견

1. **신규 모듈** `patches/population/tail_relocation_storage_layout_v1.py`: `unit_pool`/
   `unit_existence`/`unit_age`를 `.rsrc` 바로 아래(원본 `RSRC_BASE_VA`)에 한 덩어리로
   재배치하는 `layout(n)`/`build_layout_artifact(original, n)`. N==1200이면 완전 항등
   (재배치 없음, `.rsrc` 불변) — W4 §4 필수 회귀 앵커. N>1200이면 세 배열이 existence/age
   인접성(`age.new_start == existence.new_end`)을 지키며 꼬리에 packed. `base_preserving_
   storage_layout_v1`은 lap388 ACCEPTED·종결 모듈이라 **손대지 않고**, 절차만 복제했다
   (모듈 docstring에 사유 명시).
2. `g2_unit_pool_expansion_v1.py`를 이 새 모듈로 재배선(import만 교체, B-2/B-3 로직 무변경).
3. **신규 결함 발견 및 수리(실패가설 1회 소진 후 해결):** `unit_pool` delta가 처음으로
   0이 아니게 되자 `_patch_literal`의 고정 16바이트 윈도우가 인접 명령까지 스캔해
   read-modify-write 3종 세트(`mov edi,[ecx*8+lit]; add edi,eax; mov [ecx*8+lit],edi`)의
   같은 리터럴을 두 번 찾아 `BuildAbortedError`(허위 비유일)를 냈다. 대상 명령을 캡스톤으로
   재디코드해 그 명령 **자신의 길이**로 윈도우를 자른 뒤 재검사하도록 수리 —
   base-preserving 시절에는 pool 리터럴을 한 번도 패치한 적이 없어 잠복해 있던 버그.
4. `test_tail_relocation_storage_layout_v1.py`(신규 10건) + `test_g2_unit_pool_expansion_v1.py`
   1건 추가(N=1210 카운트가 카드 필수치와 정확히 일치함을 고정) — G-a/G-b를 **재사용 가능한
   pytest 회귀**로 구현(W4 §4 요구).
5. 별도 확인용 probe `docs/history/laps/probes/20260920_lap401_work_g2_pool_tail_relocation_probe.py`
   (SHA `73efeb2b392ee04581a69c83cd9744ebd92fac7b8b5ab5f7d6e3215e804e8ec8`)로 R1/R2/Ga/Gb를
   독립 재확인, 산출물 `docs/history/laps/probes/out/20260920_lap401_work_g2_pool_tail_relocation.json`
   (SHA `33f0c66efb7dd48b449f179c604d15856ea8455020c283a71148c3f6298e2118`, rc0 `failures: []`).

## 측정값 (기계 산출 인용, 손 전사 아님)

- `r2_n1210_b3_fixup_site_counts`: `{"unit_pool": 1014, "unit_existence": 34, "unit_age": 4}` — **W4 §3 필수치와 정확 일치**.
- `r1_n1200_identity`: `true` (candidate_sha256 == original_sha256).
- Ga: `ga_hits` 1건뿐, `0x401402`(`push 0x1100007`) — lap400 D4의 그 비주소 즉치와 동일 사이트.
- Gb: `gb_before_count` 3172 → `gb_after_count` 3132, `removed` 40(existence/age 재배치 38건 +
  B-2 두 상수 자신의 old-value가 blob 안이었던 2건), `added`/`changed` **0건** — catA/catB/
  active_slot_list는 손대지 않았음을 바이트로 확인.
- N=1210 candidate SHA `2571d6a2d07396215dadc323a42e1c763ff332132463e5b049fb2135b9d264de`(메모리
  재생성, 파일로 쓰지 않음). deltas: pool `0xa20870`/existence `0xa1e528`/age `0xa1e53c`.

## 변경 파일 / source fingerprint / 커밋

- 신규: `patches/population/tail_relocation_storage_layout_v1.py`
  (`80383562678e5327c2974761dd442d1f019c700d9159fe769d60396dfa57b8d2`),
  `patches/population/test_tail_relocation_storage_layout_v1.py`,
  probe + 산출물(위 SHA 기재).
- 수정: `patches/population/g2_unit_pool_expansion_v1.py`
  (`e468a1caa99338ed5426d32ae12bc7a04ffd76310b01e836422bd7fb02fa85b6`,
  import 재배선 + `_patch_literal` 윈도우 재디코드 수리),
  `patches/population/test_g2_unit_pool_expansion_v1.py`(카운트 회귀 1건 추가),
  `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`(W3, 변경 없음 재확인만),
  `docs/STATUS.md`.
- 커밋 없음(`LOOP_ALLOW_COMMITS=0`). uncommitted 보존.

## 원본 SHA / 환경 / fixture

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — **읽기만**,
  회차 전후 및 `Syw2plus/`·`Syw2plus_re/Syw2plus/` 양쪽 재해시 불변 확인.
- fixture: 없음(게임 미실행). 메모리 쓰기 0.

## 실행 명령 / 로그

```
python3 -m pytest patches/population/test_tail_relocation_storage_layout_v1.py \
    patches/population/test_g2_unit_pool_expansion_v1.py -q   # 24 passed
make check   # rc0, 739 passed 225.45s (728+11 신규), Ruff/compileall/mypy10 Success, CONTEXT_PASS
checks/safety.sh check   # SAFETY_PASS
python3 docs/history/laps/probes/20260920_lap401_work_g2_pool_tail_relocation_probe.py \
    --output docs/history/laps/probes/out/20260920_lap401_work_g2_pool_tail_relocation.json  # rc0
```

## 판정

- **B-1 재배치 구현 PASS(정적)**: 카드 §3 필수 카운트 정확 일치, N=1200 항등 유지, G-a/G-b
  전부 충족. lap400이 지목한 결정적 결함(제자리 성장 → live state 침범)은 **해소됐다**.
- 게임 실행 0회 — S-1(원본과 같은 지점까지 정상 구동)~S-6는 **아직 검증하지 않았다**.
  이 회차는 §5의 "실행" 단계(P-0 양성 대조군 → S-1 → S-2~S-5)에 착수하지 않았다: 구현+정적
  게이트만으로도 실패가설 1회(윈도우 버그)를 소진했고, 이번 발견(read-modify-write 리터럴
  중복)은 향후 다른 사이트에서도 재발할 수 있어 실행 전 정적 결과를 먼저 기록해 독립 검수를
  받는 편이 안전하다고 판단했다.
- 저장/LAN 호환은 W4 §6대로 여전히 후속 필수 blocker(재배치가 existence/age를 bulk blob
  밖으로 빼내므로 저장 포맷은 반드시 깨진다) — 이 회차가 새로 깬 것은 없다(아직 실행 안 함).

## 회귀 / 남은 위험 / 독립 검수

- lap385/388 저장포맷 통합 blocker, lap389 NO_GO, `ESCALATE_SOL` §5~§10(F4 포함)은 **뒤집지
  않는다**. 이 lap은 그중 어느 것도 닫지 않았다.
- **다음 새 middle 세션의 독립 검수 대상**: (1) 이 probe의 rc0 재현, (2) `_patch_literal`
  재디코드 수리가 다른 B-2/B-3 사이트에서 회귀를 만들지 않았는지(fixup 카운트 재검증으로
  이미 간접 확인됨), (3) P-0 양성 대조군 실행 이전 착수 여부 판단.

## 다음 한 가지

**다음 work 회차가 W4 §5를 실행한다**: (1) P-0 — 같은 prepare run에서 `syw2plus_original.exe`
그대로 PS9 도달 확인(양성 대조군, 아직 미실행). (2) PS9 확인되면 이 회차의 N=1210 후보를
`syw2plus_original.exe` 이름으로 배치해 S-1(save000 로드, PS35→PS3) 시도. (3) 통과하면
S-2~S-5(slot≥1200 관측/필드/사망/재사용)를 W3 §A 표대로 판정.

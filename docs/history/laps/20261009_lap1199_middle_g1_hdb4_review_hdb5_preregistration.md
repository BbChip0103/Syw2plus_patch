# 2026-10-09 | lap 1199 | G1 middle — H-HDB4 검수 · H-HDB5(테스트 공백 4 + 직렬화 실패 표기) 사전등록 · 효과 갈래 마감 판정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 하위 독립 검수 2개(Opus): 원본 역어셈블(architect), 변이 재현·독립 변이(test-engineer). 게임 실행 0, C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1198 work → middle). 원문을 byte 일치로 보존한 뒤 삭제했다: `docs/history/laps/20261009_lap1199_preserved_lap1198_escalate_sol.txt`(SHA256 `00a05d4bbbb6f1e7…`). `loop/STOP` 없음. INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 러너 lap = 1199.
- 목표: G1 효과(반투명) 갈래. lap1198 H-HDB4(7인자 `0x4678C0`·반전 `0x468360` HD 키 경로)를 독립 검수하고 다음 work를 정한다.
- 산출물(공유 temp `20261009_lap1199_middle_review/`, SHA256 앞 16자):
  - `recalc_lap1199.py` `7f0e331bde06588d` · `.json` `a62fcfd013f88eff` · `.out` `9bf0ad03c6745057`(lap1197 middle 스크립트 기반, work `w_metrics/attrib/asym` 미사용)
  - `mut/repro_work_lap1199.txt` `e9e0ddfea3988219` · `mut/mutation_lap1199.py` `733d5e743fac7cb2` · `mut/mutation_lap1199.txt` `3541d97726386227`
  - 원본 역어셈블(`../syw2plus_original.exe`, SHA `b56986e0…` 일치, 읽기 전용): `orig_4654d0` `8c86597322894801` · `orig_4655b0` `9019bb03d44e979f` · `orig_4678c0` `9a82be1d39ed27a4` · `orig_468360` `0faf64d3f642f81a` · `orig_4685c0` `76263a0d4b67c24c` · `orig_41a7d0` `7550b8b5d7e35e69` · `orig_4782b0` `34415abefc7357f7` · `orig_478a42` `00e26cd6811273bd` · `orig_478c88` `c5712ee27d6a8f13` · `orig_48d549` `c461872ac4b37969` · `orig_411a00` `e341ad6d9e0c6e16` · `orig_40f4b0` `198acb3859af5bf6`(모두 `_lap1199.asm`)

## 1. source·DLL 동일성

source SHA 8개(`g1_blend_key.h 4d2b0884…`·`g1_mirror2x.c 89838938…`·`.h 73113806…`·`g1_hd_asset.c fcf6e976…`·`.h 61173d6b…`·`direct_draw_trace.c 63172d37…`·`test_g1_blend_key.py 83c37e87…`·`test_g1_rect_fill.py 15ecb5fc…`)와 저장소 `_inmm.dll ef21d7bb…`가 lap1198 기록과 일치한다.

## 2. 원본 독립 역어셈블(작업 1)

- **`0x4654D0` 표 구성: 확인.** 포인터 `lea eax,[ecx+0x43ca0]`(4654DF)는 루프 전에 1회만 잡는다. 바깥 v = 0..90 step 10(46558A/46558D/465594), 중간 d(465579 `cmp 0x40`), 안쪽 s(46556B), DWORD 진행. 10슬라이스 = `+0x43CA0..+0x6BCA0`. 항목 = `max(d, max(0, s − ⌊v·s/100⌋))`.
- `0x43ca0` 참조는 .text 전체 13곳(원시 바이트 검색과 같음): 쓰기 1(4654DF), 읽기 12 = `0x467410` 3·`0x4678C0` 3·`0x467E60` 3·`0x468360` 3. 다른 코드가 이 범위를 쓰지 않는다.
- **`0x4678C0`·`0x468360`: 확인.** 쓰기 열 `x + (int16)(w − col − 1)`(46847A~4684B4), 클립 4비교(4683A6/4683C9/4683D1/4683E3, 반전 때문에 열 조건이 바뀐 것까지 `0x4685C0`과 같음), remap `[esp+0x44]`→ebx·`mov dl,[eax+ebx]`(4684C5), level `movsx [esp+0x48]`·`shl 6`(4684B9/4684E5), 표 읽기 468512/468531/46855A, `ret 0x1c`. 표 인덱스 바깥 = 목적지, 안쪽 = 원천(코어의 `[d][s]`와 같음).
- **level 출처(보강 1, work "정적으로 못 묶음"을 좁힘):**
  - 호출자(예: 478579~4785BC)는 `level = movsx BYTE [obj + slot + 0x62]`, slot = `BYTE [0x956775 + [0xB63FC4]·0x3ABC]`(현재 플레이어 슬롯)이다. 0이면 level 없는 경로(`0x467410`/`0x467E60` 계열 래퍼)로 간다. work의 "클래스 바이트"는 실제로는 **플레이어 슬롯 바이트**다(정정 1, 판정 영향 없음).
  - 쓰기 지점은 3곳이다. 객체 초기화 `rep stos` 0(411A1A). 틱 루프 48D549~48D56E: 8슬롯마다 가시 바이트 `[+0x5a+k]==1`이면 `level≠0`일 때 −1, 아니면 `level≠9`일 때 +1 → **0과 9에서 포화**한다(이번 회차에 직접 열람). 세이브 로드 `0x40F4F0`(40F511)는 0x758 B를 검증 없이 fread한다.
  - 그러므로 **정상 경로에서 level ∈ 0..9로 정적으로 묶인다.** 세이브에서 들어온 범위 밖 값은 원본도 표 밖을 읽는다. work의 런타임 거부(0..9 밖이면 키 경로만 거부, 원본은 그대로)는 그 경우에만 작동하는 안전한 방어다. 사전등록 BLOCKED 조건에는 해당하지 않는다.
  - 의미: level은 플레이어별 시야 페이드(0 = 보임 ↔ 9 = 숨김)이고, 표는 "원천을 (100−10L)%로 줄인 뒤 lighten"이다.
- 남는 UNDETERMINED: slot 바이트가 0..7이라는 보장, 멀티 동기화 경로(G3/LAN은 현재 범위 밖).

## 3. 코어·asset 검토(작업 2)

- `blend_key_apply` remapped 분기: level 슬라이스→int16 변환·거부는 디코드·begin 전에 return하므로 asset 상태를 건드리지 않는다. 자기 검사는 remap 평면(현재 remap)으로 하고 identity bind는 스트림 색이다. `g_blend_key_remap`은 호출 직후 NULL로 해제된다. level·digest는 남지만 remapped 경로가 remap≠NULL을 요구하고 setter가 항상 먼저 실행되므로 무해하다. 재진입은 없다(set과 clear 사이에 훅이 없고, 렌더러는 단일 스레드).
- **캐시 재사용 위험(사전등록 B4-1 "잘못된 level로 그리지 않음"): 현재 코드에서는 안전하다.** 캐시된 HD 프레임은 팩 위에 LUT(remap)만 적용한 것이라 level과 무관하고, level은 호출마다 weights로 바뀌어 `g1_blend_apply_hd`에만 들어간다. remap은 키에 aux 포인터와 FNV digest가 같이 들어간다(`g1_hd_asset.c` `find_key_for_request` 604~608).
- `PACK_TINTED=0`은 capture와 build 양쪽에서 팩을 끈다. 결정이 타당하다(LUT 경로는 tinted와 같은 의미).
- 트레이스 줄 버퍼 수리 타당: D0 metrics 줄 10,233 B < 10,240, S3 10,243 B > 10,240(직접 측정). 새 버퍼 16,384로 여유는 약 6.1 KB다. 변이 m17·m18(되돌림)은 용량 테스트가 RED로 잡는다.
- **정정 2(판정 영향 없음):** 첫 run 손실은 S1·S2 두 개뿐이다(summary `dropped_count` 1·overflow 1). **Q0는 metrics 1개·dropped 0으로 손실이 없었다.** Q0를 제외한 것은 DLL이 달라서 보수적으로 한 조치로 본다. 또 손실은 "조용히" 일어난 것이 아니다. `dropped_count` 1로 보였지만 overflow `scope`가 `event_limit`으로 잘못 붙었다(직렬화 실패를 개수 상한으로 표기) → H-HDB5에서 고친다.

## 4. 변이(작업 3, 격리 `/tmp` 사본, 저장소 무변경)

- **work 28종 재현: 28/28 RED.** 실패 수 "1 failed, N passed"까지 work 결과와 전부 같다. base 149 GREEN.
- **독립 19종(`-x` 없이 5파일, base 239 GREEN): RED 11 · 생존 8.**
  - RED 11: slice stride 오독·절반 복사·flip7 remap 제외·NULL remap 허용·flip7 remap 미해제·digest 0·키 비교 digest 제거(m12, `-Werror` 경고로만 잡힘)·PACK_TINTED 무시·키 픽셀 LUT·`mirror_details`/줄 버퍼 되돌림.
  - 동등 4: int8 항목 검사·투명 칸 remap·평면 개수·`0x467B00` LUT 집합(모두 실제 값이나 게이트 때문에 결과가 같음).
  - **실제 테스트 공백 4:**
    - **m12b(상):** 키 비교에서 `auxiliary_digest`를 무시해도(경고 없는 형태) 239 GREEN이다. 같은 주소의 remap 내용이 바뀌면 옛 LUT 색으로 HD를 그린다. 1x 자기 검사는 현재 remap을 쓰므로 통과해 버린다. tinted writer에도 원래 있던 같은 공백이다. 현재 코드는 옳다(회귀 보호 공백).
    - m01(중): level 상한 `≤10` 허용. 경계 테스트가 10슬라이스 표 밖 바이트가 int16에 안 맞아서 우연히 통과한다.
    - m08(중): level이 첫 호출 값에 고정. 틀린 픽셀은 없지만 자기 검사 불일치 → Scale2x 폴백으로 HD가 조용히 사라진다.
    - m16(하): trace에서 두 writer의 `keyed_pixels` 맞바꿈(진단 표기만 틀림).
  - 그 밖: 래퍼(clip7/flip7)·setter는 문자열 계약으로만 잡힌다(m06/m07/m09/m11/m13).
- focused 5파일 저장소 **239 passed/22.63s**(로그 `logs/gates/lap1199-middle-focused.log` `c12f9ab8baad0fbd`).

## 5. run raw 새 스크립트 재계산(작업 3)

| run | PS3·s | p95 | stale 최대(군집) | 안전 7종·summary dropped | `0x4678C0` 화면 안 = keyed+폴백 · cut · 불일치/px · level 거부 | `0x468360` 같은 항목 | 키 로그 두 writer | pair |
|---|---|---|---|---|---|---|---|---|
| S3 켬 | 409·20 | 7/7 | 0 | 0·0 | 184 = 184+0 · 184 · 0/249,736 · 0 | 8 = 8+0 · 8 · 0/6,446 · 0 | `lut_hit` 15·5 digest, 미귀속 0, `char/cannon2c1·2`, 비대칭 15/15·5/5 | HOLD, 게이트 31 |
| S4 켬 | 410·20 | 7/7 | 0 | 0·0 | 같음 | 같음 | 같음 | HOLD, S3 대비 차이 0 |
| Q1 끔 | 410·20 | 7/7 | 0 | 0·0 | 184 화면 안, 키 시도 0 | 8, 시도 0 | 항목 0 | HOLD, 차이 0 |
| D0 발견 | 410·20 | 7/7 | 0 | 0·0 | 184 = 0+184(팩 없음) | 8 = 0+8 | `miss` 15·5 | HOLD, 차이 0 |
| F1 new-game | 6,017·301 | 6/6 | 92(140.9~141.1 s 2개, 225.4 s 1개) | 0·0(aggregate 45) | 호출 0 | 호출 0 | — | — |

- 비회귀: save000 네 기존 writer의 S3/S4 값은 D0와 같다(`0x467B00` 2,120/2,123 keyed·폴백 654, `0x467580` 폴백 504, `0x467FD0` 폴백 102). F1은 `0x467B00` 1,025/1,027(빈 창 2)·`0x467580` 470/470·`0x4685C0` 309/309(빈 창 10)·`0x467FD0` 152/152이고, 전부 불일치 0이다.
- **판정 영향 불일치 0.** 키 로그 digest 수(15·5)는 work의 줄 수(16·5)와 다르다. 같은 digest가 두 줄에 나온 것이라 모순이 아니다.
- F1 aggregate 45 손실: present·metrics는 무손실이고 개수 상한(8,192)에 따른 것이다. 기존 backlog(lap1146 trace 8192 상한)와 같은 하네스 한계로 수용한다.

## 6. 판정

**H-HDB4 `PASS(partial, 기술·격리)` 수용.** 집계: 판정 영향 불일치 0 · 정정 2 · 보강 1 · 테스트 공백 4.
- 정정 2: level 출처는 플레이어 슬롯 바이트, Q0는 손실 없음(손실 표기 scope 오표기)
- 보강 1: level 정상 경로 0..9 정적 확정(포화 루프 `0x48D549`), 런타임 거부는 세이브 이상값 방어
- 테스트 공백 4: m12b·m01·m08·m16

기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

**디스크 판단(작업 6):** 지금 여유는 11 GB다. `local/runtime` 223개 run(260 GB)에 `game` 사본은 없다. prefix archive 회수는 archive·restore 검증 비용이 크다. 그리고 2026-10-08 root 정리(INBOX 12:05)처럼 대량 삭제는 사용자 승인 사안이다. 그래서 이번 회차에는 회수하지 않는다. 다음 H-HDB5는 게임 run이 없다. run이 필요한 work는 5 GB 미만이면 시작하지 않는다. **여유가 8 GB 미만이 되면 middle이 root 대상 ESCALATE_SOL로 디스크 확보(사용자 승인)를 요청한다.**

**효과 갈래 마감 판정(작업 7):** 남은 혼합 writer는 `0x467410`(무클립 7인자)·`0x467E60`(무클립 반전 7인자)이고, 둘 다 level=0 경로(호출자가 level 0일 때 고르는 래퍼)다. 과거 trace 1,476개에서 화면 안 호출은 각 2 run뿐이다. `0x467E60`은 lap1081 hl1·hl2의 candidate throttle(인위 감속) run에서만 나왔고, 정상 속도에서는 호출 0이다. diff 미러가 정확성을 지키고 있으므로, 키 경로화는 측정 수단(인위 감속)에 비해 사용자 가치가 낮다. → **두 writer는 명시 잔여(Scale2x 화질)로 두고, H-HDB5 검수 뒤 효과 갈래를 마감한다.** 새로 관측되면 재개한다.

## 7. 다음 work 사전등록(Sonnet) — H-HDB5: 효과 키 경로 테스트 공백 4개 + 직렬화 실패 표기

**게임 run 0**(디스크 절약). C 변경은 진단 표기 1곳뿐이다.

- **B5-1(m12b, 상):** asset 호스트 테스트를 추가한다. 같은 remap 포인터에서 내용 A로 키를 만든 뒤 내용을 B로 바꿔 다시 요청하면 새 키가 생기고(또는 A 키를 재사용하지 않고), 팩 프레임에 B의 LUT 색이 적용되는지 확인한다. tinted writer(`0x466EA0`·`0x466540`, `is_tinted_pack_writer`)에도 같은 테스트를 둔다. 독립 변이 m12b(`(key->auxiliary_digest == auxiliary_digest || 1)`)가 RED여야 한다.
- **B5-2(m01):** 11슬라이스 크기의 정상 값 표(int16에 맞는 값)로 `g1_blend_level_weights(table, 10, out)`가 0을 반환하는지 확인한다. m01(`≤10` 허용)이 RED여야 한다.
- **B5-3(m08):** `blend_key_set_remap`(또는 그것을 쓰는 래퍼 흐름)의 동작 테스트를 추가한다. 서로 다른 두 level을 번갈아 넣었을 때 코어가 각 호출의 level 슬라이스를 쓰는지 확인한다(문자열 계약이 아니라 호스트 실행). m08(첫 값 고정)이 RED여야 한다.
- **B5-4(m16):** trace 필드 이름과 접근자의 대응 테스트를 추가한다. 두 writer의 8개 필드가 각각 자기 writer 통계에서 나오는지 확인한다(예: 통계 값을 서로 다르게 넣고 직렬화 결과 대조). m16이 RED여야 한다.
- **B5-5(정정 2):** `trace_event`에서 `trace_event_raw` 실패(직렬화·쓰기 실패)와 개수 상한 초과를 구분한다. 직렬화 실패는 overflow `scope` `serialize`(또는 같은 의미의 이름)로 표기한다. 호스트 테스트로 고정한다. 기존 필드·이벤트 의미는 바꾸지 않는다.
- 변이 확인: m12b·m01·m08·m16·B5-5 되돌림 5종 RED, 기존 lap1198 28종과 lap1199 RED 11종은 그대로 RED.
- **측정식(합격):** 위 5개 RED→GREEN, focused 5파일 GREEN, `make lint`·`make typecheck` → `make check` 1회 PASS, 원본 EXE SHA 불변. DLL이 바뀌어도 게임 run은 하지 않는다(진단 표기만; 다음 run 회차에서 자연 확인).
- **비목표:** `0x467410`·`0x467E60` 키 경로(명시 잔여), 실제 업스케일 화질, 기본 켬·사용자 전달.
- **중단:** 실패 가설 2회 또는 60분. 테스트 추가 중 현재 코드의 실제 결함이 드러나면 수리하지 말고 근거를 남긴 뒤 ESCALATE_SOL로 판정을 요청한다.

**그다음(H-HDB5 검수 뒤 middle 판단 후보):** 효과 갈래 마감 → backlog(lap1189) "기본 켬 전 전체 팩(`pack_hdf1`+로고+효과) 동시 실게임 확인" 1회 → 사용자 시험판 재스테이징 여부 판단(마일스톤 경계이므로 root 전달).

## 8. 검사

- `checks/safety.sh check`·CONTEXT 결과는 STATUS 검증 줄에 보강한다.
- 이번 회차는 문서와 공유 temp 스크립트·역어셈블만 바꿨다. tools·tests·C source는 lap1198 full PASS(2036 passed) 그대로다. 그래서 전체 `make check`는 SKIP한다.
- 원본 EXE SHA `b56986e0…` 일치. 디스크 여유 11 GB.

## 다음 행동

work(Sonnet) H-HDB5(§7)를 진행한다. 사용자 G1 시험 결과가 오면 그것이 최우선이다.

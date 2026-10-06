# 2026-10-06 | lap1041 | G1 work H-S — 남은 유닛 크기 stale 덩어리 writer 귀속(진단 전용, 제품 동작 불변)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work 1 lap. 제품 source 변경 0, commit 0.
- 가설(lap1040 사전등록 §H-S): 마지막40 중앙값 26(p388 가장자리)·p399 덩어리·p6/p12/p144/p174/p204 유닛 크기 덩어리의 마지막 writer는 표본 watch로 귀속되고, 기후킹/미후킹으로 분류하면 다음 수리 대상이 정해진다.
- 변경 파일: 없음(진단 하네스 `--drift-samples`만 사용, opt-in 기존 기능). 스크립트·산출물은 공유 temp `20261006_lap1041_work_hs/`.
- 원본/후보 SHA: 원본 EXE `b56986e0…8ac` 읽기 전용 재확인, pair-result `source_unchanged` 7/7 true. `g1_mirror2x.c` `4c4a4152…ef5421`(= lap1039 product, 실행 전후 동일), `CONTROL-TEMP` 0.
- 실행: `run_s.sh` `0c97e3e6…`(세트 S1·S2·S3 × save000 watch pair 2회, 인자는 lap1039 w와 같고 `--drift-samples`만 변경: `--performance-window --layer-drift --screen-watch --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`), 각 run 직전 load ≤8 대기, 단일 인스턴스(`pgrep` 0 확인 뒤 기동·종료까지 1개). 전 run exit 2 = 기존 pair HOLD(V2s raw gate), 로그 `logs/gates/lap1041_hs_*`.
  - **무효 처리:** s1_r1은 외부 프로세스(다른 세션의 ffmpeg/hyperframes 렌더)로 load가 10 이상 오르며 후보 p95 41 ms·ps3 272(정상 410)로 중도 종료 → S-0 불만족이라 귀속 판정에서 제외하고 `run_s_rerun.sh` `127e8b27…`로 s1_r3 재실행(정상 410). s1_r1 수치는 참고 기록만(귀속 EIP 구성은 r2/r3와 일치).
  - 분석 `analyze_s.py` `4d9f9015…`(sum_*.json), `hooked_w.py` `93cbad1e…`; 정적 `od_466000_46a000.txt`·`od_text_all.txt`(읽기 전용 objdump).

## S-0 (동작 불변)
- 유효 6 run(s1_r2·r3, s2_r1·r2, s3_r1·r2): selftest PASS·무장 fail 0·좌표 3/3(arm_xy = 표본)·dropped/overflow 0·안전 7종 0·cleanup true·항등식 `flip_rle_466B50`/`blend_4678C0`/`blend_467FD0`/`blend_467B00` `invocations = mirrored + reject_*` 전부 성립·**마지막40 중앙값 26 전 run 재현**(s1_r1만 27, 무효 run). → **PASS**.

## S-1 귀속 (9점, 2 run 동일 EIP·값 일치 100%)
| 표본 | stale present 수(run 1/2) | 마지막 writer EIP(두 run 동일 분포) |
|---|---|---|
| S1 (795,470) p388 가장자리 | 20/20 (140..394) | `0x466D15` 12, `0x468571` 5, `0x46884E` 2, `0x467CCF` 1 |
| S1 (628,409) p6 | 1/1 | `0x46884E` |
| S1 (599,367) p12 | 1/1 | `0x46884E` |
| S2 (779,467) p144 | 8/8 | `0x466D15` 6, `0x46884E` 2 |
| S2 (718,452) p174 | 3/3 | `0x46884E` 2, `0x467692` 1 |
| S2 (788,391) p204 | 2/2 | `0x467692` 2 |
| S3 (786,220) p399 | 1/1 | `0x46884E` |
| S3 (783,377) p366 | 5/5 | `0x468A28` 3, `0x467692` 2 |
| S3 (568,483) p6 둘째 | 3/3 | `0x466D15` 3 |
- 귀속 9/9(≥6/9 기준 PASS, 귀속 실패 `none` 0). stale present마다 마지막 writer 값 = 화면 값(value_match = stale 수, 100%). S1 r2/r3·S2 r1/r2·S3 r1/r2 쌍은 present 위치까지 같거나 ±1 present.
- **마지막40 중앙값 26을 정하는 writer:** 덤프 p386~392 구간 S1(795,470)의 마지막 writer가 `0x468571`(r2 p388..392, r3 p386..390), p394~396은 `0x467CCF`(기후킹 `0x467B00`). p399 덩어리(S3 (786,220))는 `0x46884E`, p366은 `0x468A28`.

## S-2 분류
| EIP | 소속 함수(objdump, 원본 SHA 확인) | 후킹 | 인자·클립·호출처 | 표본 기여 |
|---|---|---|---|---|
| `0x466D15` | `0x466BE0..0x466D4F` | **미후킹** | `sub esp,0x18` 시작(5B 경계 `83 EC 18 33 C0`), `ret 0x18`(6인자), 클립 참조 `+0x4D0..` 5곳, 호출처 `0x419FB0`·`0x41A54A`, 내부 분기가 앞 5바이트를 겨냥하지 않음 | 3점(p6 둘째·p144·p388 일부) |
| `0x468571` | `0x468360..0x4685BF` | **미후킹** | `sub esp,0x1c; push ebx; push ebp`(5B 경계), `ret 0x1c`(7인자), 클립 5곳, 호출처 `0x41A8E7`·`0x41AA5F` | S1 p388 가장자리(마지막40 중앙값 26 직접 원인) |
| `0x46884E` | `0x4687F0..0x46886F` | **미후킹** | `push ecx; mov edx,[esp+0xc]`(5B 경계), `ret 0x18`(6인자), 클립 없음, 호출처 `0x41A190` 1곳 | 6점(p6·p12·p144·p174·p399) |
| `0x468A28` | `0x4689C0..0x468A4F` | **미후킹** | `push ecx/ebx/ebp/esi/edi`(5B 경계), `ret 0x18`(6인자), 클립 없음, 호출처 `0x41A250` 1곳 | S3 p366 |
| `0x467692` | `0x467580` 내부 | **기후킹**(H-B) | `w` 레코드에 같은 present의 `mirrored`/`clipped` 다수(예: S3 (783,377) p185~186, S2 (718,452) p174), 표본 값 `scr`=writer 값이나 `snap` 불변 → 거부 계수(reject_*) 아님(`blend_467580_reject_*` 전부 0, invocations = mirrored)·원인 UNKNOWN(팝업 구간 p150~205 중첩 writer 여러 개) | S2 p174·p204·S3 p366 일부 |
| `0x467CCF` | `0x467B00` 내부 | **기후킹**(H-B4) | S1 p394/396 단발(기록 1회), 원인 UNKNOWN | 1 |
- 새 미후킹 함수 4개(`0x466BE0`·`0x468360`·`0x4687F0`·`0x4689C0`)는 모두 기존 후킹 형제의 클립/파생 변형이다: `0x466BE0` ↔ `0x466B50`(좌우반전 RLE, 호출처 인접), `0x468360` ↔ `0x467FD0`·`0x4678C0`(반전 반투명, 7인자 클립), `0x4687F0`·`0x4689C0`는 단일 호출처(`0x41A190`·`0x41A250`).
- **판정 FEASIBLE:** 모두 5바이트 명령 경계·내부 분기 없음·호출처 확인. 다음 수리는 표본 기여가 큰 순서로 (1) `0x468360`(마지막40 중앙값 직접 원인 — H-P `mirror_blend_clip7`을 좌우반전으로 바꾼 diff 미러), (2) `0x46884E` 함수 `0x4687F0`(6점), (3) `0x466BE0`(3점), (4) `0x4689C0`.

## 수치 요약
- 마지막40 중앙값 26(전 유효 run), 표본 stale present 수 위 표, 안전 0, p95는 watch run 11~12 ms(watch 계측 포함, 판정 아님).
- 항등식·좌표·dropped 상세는 `sum_*.json`.

## 회귀 / 남은 위험 / 독립 검수
- 제품 변경 0이라 회귀 없음. 환경 로드: s1_r1 외부 load 10+로 무효(위 처리).
- 남은 위험: 후킹 함수 내 stale(`0x467692`·`0x467CCF`)의 원인 UNKNOWN(거부 아님 → diff 미러는 적용됐으나 `snap` 갱신 안 됨, popup 중첩 의심). 표본 9점은 8 run 결정적 재현 점뿐이라 덩어리 전체의 writer 분포가 아니다.
- 독립 검수(middle)가 확인할 것: (1) 새 스크립트로 6 유효 run 재계산(표 9점·EIP 분포·항등식·마지막40 26), (2) s1_r1 무효 처리 타당성, (3) objdump `0x468360`·`0x4687F0`·`0x466BE0`·`0x4689C0` 시작 5B 경계·분기·호출처, (4) 다음 work 사전등록(H-U: `0x468360` 미러).
- 사용자 승인 상태: 진단 결과이며 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격은 비차단 대기.
- 다음 한 가지: middle 독립 검수 → work H-U(`0x468360` 클립 반전 반투명 diff 미러, 마지막40 26 → 감소 기대).

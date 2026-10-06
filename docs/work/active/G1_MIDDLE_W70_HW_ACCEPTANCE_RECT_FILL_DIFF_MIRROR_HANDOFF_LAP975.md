# G1 middle lap975 — lap974 H-W 수용 · `0x466B50` 반환 정정 · 다음 work = `0x466070` 호출 전후 diff 미러(H-F)

- 작성: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). 게임/source/실행/commit 0.
- 입력(읽기 전용): 공유 temp `20261005_lap974_work_delayed_watch/{hp,unit}/census/census_raw.jsonl`, 보호 원본 EXE
  `Syw2plus/syw2plus_original.exe`(SHA256 `b56986e0…08a8ac` 직접 재계산 MATCH).
- 산출(공유 temp `20261005_lap975_middle_review/`, 제품 helper import 없음, stdlib+capstone):
  `recalc_lap975.py` `29e5f581…3e1b` → `recalc_lap975.json` `1942385b…dbc4`; `disasm_lap975.py` `0054c36e…6e75` →
  `disasm_lap975.txt` `d28b5132…70b4`; `xref_lap975.py` `f1c89b78…1852` → `xref_lap975.txt` `8e3066bf…bcc6`.

## 1. 독립 재계산 (lap974 주장 대비 불일치 0)

| 항목 | HP 바 (442,155) | 유닛 (701,237) |
|---|---|---|
| raw SHA256 / 줄 | `61bb4a1d…c36a1` / 2,206 | `70c29c80…e701f` / 2,206 |
| present_skip / watch_armed / selftest | 300→301 / 301 / PASS·1 | 같음 |
| watch_hit / hit present 범위 | 126 / 302~364(63개, 각 2 hit) | 같음 |
| present 안 순서 | 63/63 모두 hook 안 → hook 밖 | 같음 |
| hook 안 EIP | `0x4662DE`(block_copy) 63, 값 84 | `0x4662DE` 63, 값 92 |
| **hook 밖 EIP** | **`0x466114` 63 (50%)**, 값 68 | **`0x466BB3` 63 (50%)**, 값 66 |
| hook 밖 스택 상위 | `0x479044 0x478E21 0x433B8C` 63(외곽 `0x410101` 52·`0x437CA3` 11) | `0x41A4FF 0x478A0C 0x433B8C` 63(59/4) |
| overflow / 기타 watch | 0 / summary 1 | 같음 |

- source fingerprint 4개(`g1_census.c` `341a16c3…71b4`·`g1_census_contract.h` `acbdd310…5b94`·`g1_saved_scene_probe.py`
  `e9093262…0fa5`·`tests/test_g1_census.py` `fb585037…4846`)가 lap974 기록과 일치(uncommitted). `local/runtime/lap974_{hp,unit}`에는
  `census`만 남아 game 사본 정리 확인. skip 경로는 한도 게이트 뒤·`++g_present_count` 앞에서 return(기록 그대로).

## 2. EXE 역어셈블 (함수 경계·기존 hook과 별개 확인)

- `0x466070`: 앞 함수 끝 `0x466069 ret 0x14`+nop, 본체 끝 `0x466127 ret 0x14`. 인자 5개 = x1·y1·x2·y2(양끝 포함, 뒤집힌 쌍 교환)·색
  (`[esp+0x24]`의 1바이트). 클립 `renderer+0x4D0/4D4/4D8/4DC`(xmin·ymin·xmax·ymax, 포함), 완전 밖이면 바로 return. 쓰기
  `0x466111 mov [ebx+ebp],dl`(`ebp=[renderer+0x1514]`, `ebx=y*[renderer+0x10]+x`) → 다음 명령 `0x466114` = 포획 EIP.
  prologue `8B 44 24 04 | 53` = 정확히 5바이트 명령 경계. 호출 8곳(xref). 기존 `rect_fill 0x465E80`(`8B 41 10 53 55 …`)과 다른 함수.
- `0x466B50`: **본체 끝 `0x466BD4 ret 0x18`(인자 6개)** — lap974의 `ret 0x1c`·7개는 앞 함수 끝(`0x466B4A`)을 옮긴 전사 오류로,
  `analysis/memory_maps/g1_unhooked_writers_466070_466b50_lap974.md` §3에 정정을 기록했다. 인자 = x·y·width·height·RLE source·리맵 LUT
  (tinted RLE와 같은 배치), **클립 없음**, 대상 `[x,x+w)×[y,y+h)`를 행마다 오른쪽→왼쪽으로 쓴다(`0x466BAF mov [ebx+ebp-1],al` →
  EIP `0x466BB3`). prologue 8바이트 `51 53 56 57 8B 7C 24 18`(=`rle_tinted_clip 0x466540`과 byte 동일). 호출 2곳.
- 두 함수 모두 `g1_mirror2x.c` hook 대상(rle_clip·rle_plain·panel RLE·tinted 2·cache copy·terrain 5)에 없다.

## 3. 판정

- **H-W PASS(partial) 수용.** 사전등록(hook 밖 같은 EIP ≥50%, mirror 미대상 writer) 충족, FAIL (i)(ii)(iii) 해당 없음.
  present마다 "block_copy 캐시 복사 → 미후킹 writer 덮어쓰기" 한 쌍이라 stale 원인 설명과 맞는다(mirror는 캐시 값만 안다).
- 한계 유지: 픽셀 1개씩의 표본. 유닛은 애니메이션이라 `0x466B50` 외 변형 writer 가능성. 제품 수치 변화 없음, pair HOLD(V2s raw)·
  사용자 마일스톤 승인은 그대로.

## 4. 다음 work 가설 H-F (Sonnet work 1 lap, FEASIBLE — 최소 구현 + fresh pair 2회)

`0x466070` 먼저(HP 바 423px, 단색·5바이트 prologue·클립 사각형이 인자로 결정). `0x466B50`(유닛 961px)은 H-F 결과를 본 뒤 다음 가설.

- 변경(제품 mirror, H-T 선례와 같은 범위): `0x466070` exact-5-byte hook(old bytes `8B 44 24 04 53` 확인 후 설치·원복, 기존
  `install_one`/`restore_hook` 경로). wrapper(thiscall, 5 DWORD 인자, 원본 trampoline 호출)는
  1. 재진입 guard(`g_primitive_guard`) 중이거나 `[renderer+0x1514]`가 화면 frame이 아니면(=`G1_CACHE_BASE`, panel bound buffer,
     stride <800 또는 height≠600, mirror/expected 미준비 — 기존 `mirror_reinvoke`의 대상 판별과 같은 값) 원본만 호출하고
     사유별 `rect_fill_466070_rejects`++.
  2. 원본과 같은 순서로 사각형을 계산: 쌍 정렬 → 클립 사각형(포함 경계)과 교집합 → 빈 사각형이면 원본만 호출.
     이 계산은 host gcc로 시험할 수 있는 순수 header 함수로 둔다(예: `g1_rect_fill.h`).
  3. 크기가 `g1_overlay_blt_accepts` 한도(≤320×128, 화면 안) 밖이면 reject 계수 후 원본만. 안이면 호출 전 사각형 사본 →
     원본 호출 → `g1_overlay_blt_apply(before, frame, stride, …)`로 바뀐 픽셀만 Scale2x 미러·expected·covered 갱신
     (H-T와 같은 helper·scratch 재사용, 새 alloc 금지). 계수 `rect_fill_466070_calls/mirrored_pixels/rejects`를 trace 요약에 추가.
- 회귀 테스트(먼저 작성, RED→GREEN): 사각형 계산(정상·뒤집힌 쌍·부분 클립·완전 밖·한 점) host gcc 시험, 설치 표 정적 계약(주소
  `0x466070`·len 5·old bytes·`ret 0x14` 인자 5), 기존 `test_g1_overlay_blt.py`·`test_g1_mirror2x.py`·`test_g1_panel_layer.py` 유지.
- 실행: lap969/972와 같은 fresh save006 scale2x pair 2회(`tools/g1_saved_scene_probe.py` 같은 lane·stale-mask 일정). 끝나면 game 사본만 정리.
- 비교는 **공통 덤프 집합** 기준(lap973 §2 한계: 880 덤프 누락 가능). 기준 = lap972 r1(공통 덤프 교집합).
- PASS(사전등록, 두 run 모두):
  - F-1: HP 바 영역(x401~494·y153~159) steady 교집합 423 → **≤42**(≥90% 제거).
  - F-2: 영역 밖 신규 stale(후보 교집합 − 기준 교집합) **0**, 전체 교집합 = 기준 − (HP 바 감소분) ± 0.
  - F-3: hook 설치 PASS·old bytes 일치, `rect_fill_466070_mirrored_pixels` > 0, steady present당 호출 ≥1(HQ 선택 뒤).
  - F-4: 안전 7종 0·V1/V2/V2q/Scale2x/minimap/input PASS·present ≥850·p95 ≤12ms·cov p50 ≥98.4%. V2s raw는 기록만(pair HOLD는 기존 사용자 판단 큐).
- FAIL/반증:
  - (i) 호출·mirrored_pixels > 0인데 HP 바 stale >380 → 같은 present에서 뒤에 또 다른 writer/전송이 덮음 → `--census-skip-presents 300
    --census-watch` 다른 HP 바 픽셀(예: 401,153·494,159)로 middle 재분석.
  - (ii) 화면 frame 대상 호출 0(전부 reject) → reject 사유별 계수로 대상 buffer 판별 실패 위치 기록, middle.
  - (iii) 안전 counter >0·크래시·영역 밖 신규 stale >0·p95 >12ms → hook 비활성 상태로 되돌리고 원인 기록, `loop/ESCALATE_SOL`.
- 범위 밖: `0x466B50`(다음), P6 로고 2,102(명시 잔여), validator·gate·V2s 정의 변경, G2/G5/G3/G4. 커밋 0.

## 5. 그 뒤

- H-F PASS면 같은 방식을 `0x466B50`에 적용(8바이트 steal, 6인자, 사각형 = 인자 그대로·클립 없음 → 화면 밖이면 reject)하는 H-R을
  다음 middle이 사전등록한다. 대안(기존 `mirror_reinvoke`에 tinted처럼 writer 추가)은 HD asset identity 결합이 커서 H-F 결과 뒤 비교한다.
- strategy 재호출 조건 추가 없음.

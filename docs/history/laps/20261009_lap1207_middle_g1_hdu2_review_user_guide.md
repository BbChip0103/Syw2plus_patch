# 2026-10-09 | lap 1207 | G1 middle — H-HDU2(업스케일러 입력 묶음) 독립 검수 · 사용자 안내

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 run 0·C/tools/tests 변경 0·커밋 0.
- 입력: lap1206 work `loop/ESCALATE_SOL`(4줄 745 B, 원문 byte 일치 보존 `docs/history/laps/20261009_lap1207_preserved_lap1206_escalate_sol.txt` SHA256 `0e2bb358…cdea4957`, `cmp` 일치 확인 뒤 삭제). `loop/STOP` 없음. INBOX 최신 = 2026-10-09 13:52 사용자 결정 "입력 묶음 만들어줘". APPROVALS 새 반려·사용자 G1 시험 결과 없음. `loop/.lap_counter` = 1207.
- 가설: lap1206 묶음(W = 공유 temp `20261009_lap1206_work_hdu2`)은 사전등록(lap1205 §3) U2-0~U2-5를 실제로 만족하고, 사용자가 실제 업스케일러(부드러운 확대·RGBA·일부만)로 돌려줘도 `convert`→`check`→`pack`이 받는다.
- 원본 SHA: EXE `b56986e0…08a8ac` MATCH(읽기만). 환경 `.venv/bin/python -I`. 디스크 여유 235 GB. fixture 없음.
- 검수 산출(공유 temp `20261009_lap1207_middle_review/`): 스크립트 `recalc_u2.py` `a87f3c86…`·`sim_realistic.py` `a3caebd8…`·`bleed_diff.py` `6fe96799…`, 결과 `recalc_u2.json` `ec841c4e…`·`bleed_diff.json` `d0efd2ac…`·`pack_partial.json` `23947d22…`·convert/check json 6개. 모의 그림(sim·sim_hd_*·pack_partial, 약 20 MB)은 검사 뒤 삭제.

## 1. 독립 재계산 (저장소 도구 import 없이 새 스크립트)

| 항목 | work 주장 | middle 재계산 | 판정 |
|---|---|---|---|
| `ref/manifest.json` SHA256 | `4f65df5d…dad10` | 같음, summary rle 2,763·ytl 425·raw 152·bmp 27·unsupported 7 | 일치 |
| 렌더 파일 / `fc` 합 | 840 / 43,622 | 840 / 43,622(char rle 20,598·fnt rle 5,794·fnt raw 49·tile ytl 17,062·tile rle 112·tile raw 7) | 일치 |
| 입력 폴더 파일 | 43,622·다른 파일 0·폴더 840 | 43,622·비프레임 0·폴더 840, manifest 기대 집합 대비 누락 0·초과 0 | 일치 |
| SHA | ref와 불일치 0, 목록 `007bc9d7…` | 전 파일 ref와 불일치 0, 목록을 다시 만들어 **byte 동일**(`007bc9d7…`) | 일치 |
| 형식 | P·팔레트 `imjin2.pal`×4·tRNS 254만·크기 fw×fh·마스크 위반 0 | 팔레트는 원본 `pal/imjin2.pal`(`5ba2c020…`)에서 직접 ×4로 기대값 계산, 위반 0. 추가: 프레임별 불투명 화소 수 = 파일별 manifest `opaque` 전부 일치(합 59,678,581) | 일치(보강 1) |
| 하드링크 | 0 | 0 | 일치 |
| 전부-투명 | 10,782 | 10,782 | 일치 |
| 크기 | 191 MB | 파일 바이트 합 94.5 MB(191 MB는 `du` 블록 크기) | **정정 1(표기)** |

## 2. 돌려받기 규칙 현실 모의 (work는 최근접 2배만 확인)

시드 1207, 불투명 있는 100프레임, 모두 LANCZOS 2배(실제 업스케일러처럼 색이 섞임):
- `rgb_pink`(알파 무시 = 투명 자리가 분홍 252,224,252), `rgba`(tRNS→알파), `rgba_black`(투명 자리 RGB 검정): 셋 다 `convert` converted 100·errors 0·ignored 0, `check` 위반 0 → **RGB·RGBA 모두 받는다** 확인.
- 일부만 돌려줌: `rgba` 100프레임만으로 `pack --ref W/ref --hd-dir` → exit 0·`pass` true·named 43,064·**no_hd 42,964(= 100프레임만 HD)**·nonconforming 0·no_reference 0 → **일부만 돌려줘도 된다** 확인(빠진 프레임은 기존 Scale2x).
- **분홍 번짐 실측(보강 2, 공개 위험의 크기):** 같은 프레임 `rgb_pink` vs `rgba` 변환 결과가 실루엣 화소 820,692 중 152,089(18.5%) 다르고, 그중 83,199(10.1%)는 알파 무시 쪽이 분홍에 더 가깝다(54,601은 실루엣 가장자리, 100프레임 중 99). `convert`가 실루엣 밖은 지우지만 안쪽 가장자리 색 오염은 그대로 남는다 → 사용자 안내에 **알파(투명) 유지 모드 권장**을 넣는다. `rgba`와 `rgba_black`은 결과 화소가 같다(PIL LANCZOS가 RGBA를 premultiply). 실제 업스케일러가 premultiply하지 않으면 투명 자리 색이 다시 섞일 수 있음(UNKNOWN, 첫 실제 결과에서 측정). 처음 쓴 "분홍 근처 색 개수" 지표(`bleed.json`)는 정상 색 혼합과 구분이 안 돼 쓰지 않는다.
- 팩이 받지 못하는 프레임(공개 보강 3): `pack` 대상 RLE·ytl 43,566 중 `tail_short` 502(파일 끝 128 B 미만, lap1168부터 알려진 엔진 digest 한계)·raw 56은 업스케일해도 이 경로로는 쓰이지 않는다. 이름 충돌 3개 106프레임도 그대로(lap1202).

## 3. 판정

**H-HDU2 `PASS(partial, 기술·격리)` 수용.** 집계: 판정 영향 불일치 0 · 정정 1(크기 표기) · 보강 3(불투명 수 대조, 현실 모의·일부 팩, 분홍 번짐 크기·팩 미소비 558). 사용자 마일스톤 승인 아님. 실제 업스케일 결과는 아직 없다.

## 4. 사용자 안내(APPROVALS lap1203 항목에 기록, 안내문 txt 없음)

- 위치: 공유 `temp/Syw2plus_patch/20261009_lap1206_work_hdu2/upscaler_input_1x/` (char·tile·fnt 폴더, 파일 43,622개, 약 95 MB). 옆 `ref/`는 루프 참조라 건드리지 않는다.
- 규칙: 2배 정확히, 같은 폴더 구조·같은 이름 `NNNN.png`, PNG RGB/RGBA 모두 가능, 알파 유지 권장, 일부만 가능(전부 투명 10,782는 건너뛰어도 됨), 결과 폴더 위치를 알려 주면 루프가 변환·팩·격리 확인·시험판.
- `260921_temp` 배치 여부·사용자 통지는 root 몫 → root 대상 `loop/ESCALATE_SOL`(마일스톤 경계: 사용자 작업 대기).

## 5. 다음 한 가지 (사용자 결과 대기 동안, 게임 run 0)

사용자 업스케일 결과가 오면 그것이 최우선(middle이 H-HDU3 변환·팩·격리 실게임 사전등록). 그 전 work = **H-TR15**(lap1201 i15 테스트 공백, lap1203/1204 메모가 지정한 backlog):

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| T15-1 | `tests/test_g1_presentation_trace.py`(또는 같은 호스트 실행 방식의 B5-5 테스트)에 경우 추가: `g_event_count == TRACE_MAX_EVENTS − 2`에서 `summary` 이벤트의 `trace_event_raw` 실패 → overflow 이름 `serialize` | 새 테스트 GREEN |
| T15-2 | 변이 i15(`direct_draw_trace.c` 578줄 기준을 `< TRACE_MAX_EVENTS − TRACE_RESERVED_EVENTS`로) | 새 테스트 RED, 원복 뒤 GREEN |
| T15-3 | C 제품 소스 변경 0 확인, lint·typecheck → `make check` 1회 | PASS(exit 0) |

하지 않는 것: 게임 run, C 동작 변경, 시험판. 끝나면 work는 `loop/ESCALATE_SOL`(middle 검수).

## 6. 검증

- focused `tests/test_g1_hd_extract.py`·`tests/test_g1_hd_convert.py` 결과와 `checks/safety.sh check`는 STATUS에 보강한다. 전체 `make check` SKIP(문서만 변경, source는 lap1200 full PASS 2042 그대로).

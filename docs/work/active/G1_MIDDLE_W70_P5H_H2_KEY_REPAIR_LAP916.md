# G1 P5-H H2 누락 수리 인계 — lap916 middle, 2026-10-04

- 판정: **실행·화면 `PASS(partial)` / H2 계약 `HOLD_IMPLEMENTATION_MISSING_PANEL_ASSET_KEY` / G1 HOLD**.
- 지정 middle 역할. 실제 API model/effort 메타데이터 미노출; Sol/high 실행이나 다른 모델 호출을 주장하지 않는다.
- 근거: lap914 카드 §2 H2·§3·§5, lap915 소스와 6개 실행. 제품/하네스/테스트 수정·게임 실행·커밋 없음.

## 확인 결과

48개 build 입력 × 6개 실행 모두 현재 소스와 일치한다. DLL·raw·캡처·원본 EXE/save SHA와 cleanup도 일치한다.
독립 재계산은 공유 temp `20261004_lap916_middle_review/recalculate.py` 및 `recalculation.json`에 있다.
PH-a 오류 0, PH-b 800×143 frame SHA 일치, PH-d 키 subpixel 0, V1 6,730 present 위반 0,
V2/V2s/V2q 30 tag 통과, GREEN/B′ 30 completed snapshot 상태·owner 불변식·기준 일치,
C 3회 tick ratio ≥0.95·p95 delta ≤16ms를 수용한다. HUD 캡처 6쌍 직접 확인: 키 색 얼룩/분리/패널 구멍 결함 없음.
C1/C2의 선택 초상화·내용은 두 lane이 다르므로 동일 입력 결과를 승인하지 않는다. 기존 입력 HOLD 유지.

PH-c의 독립 표본은 **전체 PS3 `mirror2x_present`**다. GREEN/B′1/B′2/C1/C2/C3 중앙값은
`0.8333520833/0.8333552083/0.8333500000/0.8255333333/0.8255125000/0.8255083333`.
lap915 기록의 다른 중앙값은 표본 범위가 없어 재현하지 못했다. 수치는 삭제하지 않으며 동일 표본이라고 주장하지 않는다.
두 수치열 모두 PH-c 범위 안이고, 이 검수는 명시된 전체 PS3 raw의 재계산에 근거한다. 90% coverage는 미달이다.

## 추적 가능한 구현 누락

- H2는 `(writer, src 포인터, w, h, 원천 digest)` 자산 키와 같은 키의 `SYW2_G1_HD_PACK` 슬롯을 요구한다.
- `g1_mirror2x.c:1425`의 `panel_capture_frame(renderer,width,height)`는 source/writer/key를 받거나 저장하지 않는다.
  buffer에서 800×h를 복사하고 `g1_panel_build_scale2x`로 바로 확대한다.
- `mirror_panel_rle`은 원본에 source를 넘기지만 capture에는 넘기지 않는다. panel frame SHA는 결과 프레임 해시이며 요구한 자산 키가 아니다.
- `g1_panel_layer.h`에도 key/HD-pack 입력이 없다. 기존 `g1_hd_asset.c`는 key를 갖지만 패널 경로가 호출하지 않는다.
  저장소 C/H 전체에 `SYW2_G1_HD_PACK` 소비 구현도 없다. 기존 공통 pack 기능을 사용한다고 가정하지 않는다.
- 따라서 Scale2x 자산 단위 출력 증거는 유효하지만 H2의 키·교체 계약 완료는 아니다. 사용자 HD 그림을 넣어 출력 디테일을 보존하는 것은 미검증이다.
- 기존 테스트의 비패널 반환 주소/Lock 불일치 검사는 주로 소스 문자열 검사다. 실제 분기 fixture 검증이라고 확대 해석하지 않는다.

## 다음 work 한 가지 — H2 최소 수리

1. lap914 H1~H5·기존 gate/임계값을 유지하고, 패널 경로에 실제 원천 source·writer·831×h·원천 digest를 보존한다.
   자산 키의 831폭과 folded frame의 800폭을 구분한다. 공통 ledger의 `width<=800` guard를 전역 완화하지 않는다.
2. 해당 키로 선택하는 HD 교체 슬롯을 연결한다. HD-pack 소비 코드가 없으므로 없는 유틸리티를 있다고 전제하지 말고,
   W70 §3-1(b)의 2w×2h idx8 슬롯·정확한 크기 확인·키 처리·Scale2x fallback을 필요한 범위만 구현한다.
   키/파일 대응과 831→800 folding을 기록한다. 잘못된 키/크기/없는 슬롯은 안전한 기존 fallback이다.
3. RED→GREEN: 원천 key 필드가 다른 자산을 거부함, 같은 자산 재사용, 831→800 folding,
   유효 pack의 네 subpixel 디테일이 panel HD 및 screen 전사까지 보존됨, 없는/잘못된 pack fallback,
   E 비키 subpixel에 FE가 없음, 실제 non-panel return 및 pointer/pitch 불일치 분기를 fixture로 검증한다.
   slot fixture는 local/·공유 temp에만 생성하고 원본 frame/데이터/golden은 수정하지 않는다.
4. 새 source build → fresh Scale2x GREEN → B′ 연속2 → C3, PH-a~d·V1/V2/V2s/V2q·전체 PS3 표본 정의 유지.
   명시한 slot fixture를 켠 격리 probe로 디테일 전달도 별도 확인한다. PH-b는 **원본 identity frame** SHA로 유지한다.
5. 기록을 먼저 확정하고 lint/typecheck/full Fast를 완주한다. 새 middle이 수리와 새 source-matched 결과를 독립 검수한다.

이는 기존 카드의 수리 범위이며 상위 설계 변경·P5-T 재계획·제품/마일스톤 승인이 아니다.
P5-H H2 수리 다음에 기존 P5-T 순서로 연결한다. 게임 hands-on 수리는 work tier가 수행한다.
명확한 구현 누락으로 lap914 §5→lap911 §6에 따라 직접 work 인계한다. 설명되지 않는 실행 실패나 실제 근거 충돌은 발견되지 않아
`ESCALATE_SOL`을 만들지 않는다. 후속 수리에서 사용자 승격 조건이 생기면 현행 지시대로 보존·승격한다.

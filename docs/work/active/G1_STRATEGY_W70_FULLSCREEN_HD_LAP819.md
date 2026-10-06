# G1 W70 — 화면 전체 2배 그리기 경로 + HD 그림 출처 (lap819 strategy 발행, 2026-09-30)

- 발행: lap819 strategy. 실제 모델 Claude Code `claude-opus-5-5`(effort 세션 비노출). 계약 strategy 모델
  Fable/Astra 자리를 lap770과 같이 **공개 대행**한다(자동 폴백 아님, 러너가 이 세션을 strategy로 호출).
  게임 실행0, 제품/하네스 source·binary 변경0, 커밋0.
- 근거: INBOX 2026-09-30 22:2x 사용자 결정("G1 = 고해상도 그림까지"), DESIGN §2 G1, W60 카드
  `G1_STRATEGY_W60_MIRROR2X_COMPOSITOR_LAP770.md`, lap817/818 raw 수치, 현재 `tools/inmm_stub/g1_mirror2x.c`,
  참고 `Syw2plus_re/analysis/disasm/rendering.md` §4.3~4.7·§6(일부 `[추정]` 표기 — 사실로 승격하지 않음),
  `ingame_render_pipeline.md`(타일 렌더 `0x403B20`, SPR RLE `0xFE,count`, 팔레트 `imjin2.pal`+night1~4).
- 이 카드는 lap818 work handoff(profile-only baseline + 남은 primitive measurement-only 분류)를 **P1로 흡수·확대**한다.
  W60 카드는 기반으로 유지하며, W60의 S1/S2/S3 PASS와 입력 parity 결과는 그대로 전제로 쓴다.

## 0. 결정 요약

1. **G1 완료 지표를 "HD 가능 coverage"로 바꾼다.** 현재 `covered`(sentinel 2×2 복제)는 nearest와 같은 그림이라
   몇 %여도 사용자 기준을 못 넘는다. 새 지표 = PS3 한 프레임 논리 픽셀 중 **최종 1600 값이 원본 자산 키에 묶인
   2배 자산에서 온 픽셀 비율**. 자산이 없는 동적 그리기(선·채우기·미니맵 점)는 "원천 그림 없음" 클래스로
   따로 세고 nearest 허용(디테일 원천이 없으므로 DESIGN 위반 아님).
2. **HD 그림 출처 기본값 = (a) 자동 업스케일, 알고리즘은 Scale2x(EPX/AdvMAME2x), 팔레트 인덱스 공간.**
   - 이유: 8bpp 팔레트 primary·night1~4 팔레트 교체와 충돌하지 않고(새 색을 만들지 않음, 결과가 원본 인덱스만
     사용), 색상키 투명을 그대로 보존하며, 결정적이고 외부 의존성이 없다(C 수십 줄). 결과가 nearest와 **자산
     가장자리에서만 다르므로** "800을 거치지 않은 2배 디테일"을 합성 체커(S3)가 아닌 실제 원본 그림으로 증명한다.
   - xBRZ/hqx/ESRGAN은 새 RGB를 만든다 → 32bpp present 또는 팔레트 양자화가 필요하다. 기본값에서 제외하고,
     아래 (b) 팩 슬롯으로 같은 키에 나중에 끼울 수 있게만 둔다(지금 도입·다운로드 금지).
   - **(b) 사용자 HD 자산 슬롯:** `SYW2_G1_HD_PACK=<dir>`의 `<key>.idx8`(2w×2h 8bpp 인덱스 + 투명키) 파일이
     있으면 Scale2x 대신 사용. 생성물은 `local/g1_hd_pack/`(Git 제외)에만 둔다. 원본 데이터는 읽기 전용.
   - **자산 단위 적용이 필수다.** 최종 800 프레임 전체에 Scale2x를 거는 것은 "800 최종 버퍼 확대"이므로
     G1 합격 경로가 아니다(DESIGN §2). 키는 원천 프레임 단위다.
3. **구조 = W70: W60 + 마스크 유도 자산 치환 + 지속 미러.**
   - **어디(WHERE)는 원본 코드가, 무엇(WHAT)은 자산이 정한다:** 기존 sentinel 재호출이 주는 "원본이 쓴 논리
     픽셀 마스크"(클립·viewport·색상키를 원본 코드가 처리, 재구현 금지 유지)를 그대로 쓰고, 마스크 안 각 논리
     픽셀 p의 미러 2×2 블록 값만 HD 프레임의 `2·(p − dst원점 + src오프셋)` 블록으로 채운다. HD 블록 안 투명키
     서브픽셀은 미러의 이전 값을 유지한다.
   - **HD 프레임 생성은 원본 프리미티브로 한다:** 키 첫 등장 시 원본 함수를 private scratch(dst=(0,0), viewport
     전체로 임시 설정 후 즉시 원복)에 한 번 더 호출해 **클립 없는 디코딩 프레임+투명 마스크**를 얻고 Scale2x →
     캐시. SPR RLE 디코더를 재구현하지 않는다. renderer viewport 임시 변경은 렌더 상태이며 게임 상태가 아님 —
     state hash로 부작용 0을 검사한다.
   - **지속 미러:** 지금은 매 present마다 `g_covered`를 0으로 지운다. 지형은 dirty flag(`0x432954`
     `[esi+0x597D/597C]`, 참고문서 `[추정]`)로 부분 재그리기일 수 있으므로 covered/expected를 프레임 간
     유지하고, present의 기존 픽셀 검증(`expected==800[p]`)으로만 무효화한다. 스크롤 복사로 밀린 영역은 stale로
     계측되며, P4에서 스크롤 복사 경로를 미러에도 같은 shift로 적용할지 판정한다.

## 1. 고정 사실 (이번 lap read-only 재확인, 원본 `[HQ]Syw2plus 2002.exe` SHA `b56986e018b43293…`)

- `ret` 크기(인자 바이트): `0x466d50` 0x14, `0x4664d0` 0x14, `0x466280` 0x14, `0x465e80` 0x14, `0x465b30` 0x14
  (5인자, 현재 wrapper 형식과 같음); **`0x466540`·`0x466ea0` 0x18(6인자 — 현 5인자 wrapper로 감싸면 스택 파손)**;
  `0x464ec0`·`0x465080`·`0x463d30` 0x4(1인자 — 픽셀 프리미티브가 아닌 상태/로드 계열로 보임, P1에서 확인).
- 타일 렌더 `0x403B20`(`ret 0x1c`, 7인자)는 `call 0x465250`과 `call [edx+0x30]`(vtable)을 부른다 → 지형 픽셀
  writer가 위 프리미티브인지 다른 경로인지는 **미확정**. P1 census가 정한다.
- UI 이미지는 DirectDraw `BltFast`(참고문서 29곳, 투명색) 경로가 있다 → renderer 프리미티브 밖의 writer다.
  GDI 텍스트(`GetDC` 58곳)도 밖의 writer다.
- 현재 `g1_mirror2x.c`는 802줄로 이미 800줄 한도를 넘었다. **새 코드는 새 파일**(`g1_census.c`,
  `g1_hd_asset.c` 등)에 둔다. 기존 파일은 연결만 추가하고, 줄이기 위한 무관 리팩터는 하지 않는다.
- lap817-r5 기준 수치: covered max 27.05%, primitive 0.246ms/call, present p50/p95/p99 4/8/11ms.
  재호출마다 832×600 버퍼 2장을 전체 채운다(`mirror_reinvoke`) → 확장 전 dst bbox 한정 채우기가 필요하다.

## 2. 단계 (각 단계 = work 1회차, 구현 우선: 구현→빌드→격리 실행→원인 수리→재실행)

공통: 기본 OFF opt-in env, EXE 파일 불변, old bytes 대조 후 설치·불일치 skip 기록·부분 설치 rollback,
save006 same-save fresh pair(baseline 800 / W70 1600), private 사본·prefix·Xvfb, 게임 사본 삭제, raw 덮어쓰기 금지.

### P1 — writer census (measurement-only, 다음 work)
1. `SYW2_G1_CENSUS=1`: 논리 800×600 **last-writer id 맵**(1바이트/픽셀)과 writer별 unique 픽셀 수를 present마다
   집계. writer = 5인자 `0x466d50 0x4664d0 0x466280 0x465e80 0x465b30`, 6인자 `0x466540 0x466ea0`(6인자 전용
   wrapper), `0x4658e0` SetPixel(ret 확인 후), DirectDraw BltFast/Blt의 PS3 offscreen 대상, GDI TextOut 계열.
   `0x403B20`은 writer가 아니라 **호출 문맥 태그**(이 안에서 일어난 쓰기를 terrain으로 표시).
2. 마스크는 sentinel 재호출로 얻되 채우기는 **dst bbox(인자에서 계산, 없으면 전체)** 로 한정. 값이 목적지에
   의존하는 writer(A/B 결과가 sentinel 외 값에서도 서로 다름)는 `dest_read=true`로 분류.
3. 인자 표본: writer별 첫 N회 인자 튜플(x,y,w,h,src 포인터 후보)과 src 포인터가 가리키는 바이트 앞 16B를 raw에
   남겨 P2 키 설계(src 오프셋·flip 플래그)를 확정.
4. 같은 census를 baseline(미러 OFF)에도 켜서 writer별 원본 elapsed·present cadence·tick rate를 비교 기준으로 남긴다.
- **P1 PASS:** 3회 fresh pair 모두 PS3 프레임 attribution ≥95%(미귀속 픽셀 bbox·영역 표기), writer별
  %·dest_read·인자 표본 raw, census ON/OFF state hash 일치, crash0, tick≥300, cleanup PASS.
  미귀속 >5%면 그 bbox를 다음 writer 후보로 적고 같은 회차 안에서 1회 더 추적한다(구현 우선).

### P2 — 마스크 유도 자산 치환 (identity 자산으로 배관 증명)
- `SYW2_G1_HD_SOURCE=identity`: HD 프레임 = 디코딩 프레임의 nearest 2배. P1 인자 표본으로 src 매핑을 고정하고,
  기존 두 hook + P1에서 `dest_read=false`인 writer로 확장, 지속 미러 적용.
- **P2 PASS:** 최종 1600 = 같은 프레임 800의 nearest 2배 ≥0.999(=매핑 정확성 오라클), HD 가능 coverage(키로
  치환된 픽셀) 보고, state hash 일치, 스크롤 전후 stale 수 보고.

### P3 — Scale2x HD (실제 원본 그림 기반 디테일)
- `SYW2_G1_HD_SOURCE=scale2x`(+ 선택 `SYW2_G1_HD_PACK`). 캐시 키 = (writer, src 포인터, w, h, 원천 바이트 FNV).
- **P3 PASS:** HD 마스크 밖 최종 1600 = nearest 2배 완전 일치(diff0), 마스크 안 nearest와 다른 서브픽셀 >0이고
  그 값이 모두 원천 프레임에 존재하는 팔레트 인덱스, 원본/후보 나란히 캡처 visual-verdict, 동일 입력
  selection/drag/minimap(진단 gate) parity 유지, 성능 기준(§3) 계측.

### P4 — 지형/타일 (구조 판정 회차)
- P1이 지형 writer를 감싼 프리미티브로 귀속하면 P2/P3를 그대로 확장한다. 타일 캐시 `rep movsd` 복사
  (참고 `0x405B36` 계열) 등 프리미티브 밖이면 그 복사를 미러에서 같은 shift/복사로 재현하는 가능성을 조사한다.
  **60분 또는 실패 가설 2회에서 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`**(PROMPT ③). NOT_FEASIBLE이면 strategy 재판정.

### P5 — HUD/메뉴 이미지 (DirectDraw 표면)
- UI 원천 표면(BltFast source)마다 2배 **쌍둥이 표면**(Scale2x 또는 팩)을 두고, primary/offscreen 대상 BltFast를
  미러에 2배 좌표로 재실행. 메뉴(PS9/7/5) 배경도 같은 경로. PASS 형식은 P3와 같다.

### P6 — 목적지 읽기 writer(색조·반투명 6인자 blit) / P7 — GDI 텍스트
- P6: 원본이 쓰는 혼합 테이블/색조 LUT를 정적 확인 후 미러에서 같은 LUT로 HD 혼합. 불가하면 nearest 잔여로
  명시하고 비율을 보고. P7: TextOut 계열을 2배 폰트로 미러 DC에 재그리기. 둘 다 P3·P5 뒤 우선순위.

## 3. G1 합격 기준안 (사용자 3단에 제출할 형식, 임의 PASS 금지)

1. census 전 writer가 **HD 가능**(identity 오라클 + Scale2x 차이 증명) 또는 **원천 그림 없음**(선·채우기·미니맵
   점, 목록·비율 공개) 또는 **명시 잔여**(P6/P7 미완 시, 비율 공개)로 분류된다.
2. PS3 save006 장면과 두 번째 장면(메뉴 PS9 또는 다른 save)에서 HD 가능 coverage ≥90%(원천 그림 없음 클래스 제외
   분모), 명시 잔여 ≤5%.
3. HD 픽셀은 구조상 800 버퍼를 거치지 않는다: 최종 1600이 nearest(800)와 HD 마스크 안에서만 다르다는 raw.
4. 입력·구도 parity 유지(선택/빈땅/드래그/진단 gate 미니맵/메뉴 PASS 재확인), production은 `UNKNOWN(original parity)`.
5. 성능: 3회 fresh pair에서 게임 tick rate가 baseline 대비 −5% 이내, present p95 ≤ baseline p95 + 16ms.
6. 원본/후보 나란히 캡처 + 사용자 3단 승인. 모델 exit0·S3 합성 패턴은 근거가 아니다.

## 4. 운영

- 다음 work = **P1**. 이후 순서 P2→P3→P4→P5→P6/P7. 각 단계 PASS 후 새 middle이 raw 독립 검수(2단)하되,
  lap773 규칙대로 "수리 대상이 명확한 구현 결함"이면 middle은 짧게 확인만 하고 work로 넘긴다.
- strategy 재호출은 P4 판정이 `NOT_FEASIBLE/BLOCKED`이거나 같은 단계 work 2회 연속 FAIL일 때만.
- 금지: 원본/참고 저장소 쓰기, EXE 파일 패치, legacy validator 완화, 기존 raw 재사용, G2/G5 소스·`local/runtime/g2_*`·
  `g2shift*` 변경, 외부 업스케일러 다운로드/새 의존성, 커밋.

## 5. 남은 위험

- src 포인터/flip 의미가 P1 표본으로 확정되지 않으면 P2 매핑 오라클이 실패한다 → 해당 writer만 제외·기록.
- 지형이 프리미티브 밖(캐시 복사·스크롤 memmove)이면 P4 비용이 커진다. 이것이 이 계획의 최대 불확실성이다.
- Scale2x는 "HD 그림 경로"를 증명하지만 미적 품질은 사용자 판단이다. 더 나은 그림은 (b) 팩 슬롯으로 받는다.
- 1080p 모니터 표시 정책(DESIGN §2)은 여전히 미정. Xvfb 1600×1200에서만 측정한다.

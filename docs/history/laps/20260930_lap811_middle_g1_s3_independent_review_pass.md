# 2026-09-30 | lap 811 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex native 세션(backend model ID·effort 비노출) / 사용자 지정
  middle `gpt-5.6-sol`/high, 진단·계획·확인. 게임·bridge·EXE hands-on 수정 없음.
- 가설 / 사용자 관찰: lap810의 S3 raw와 최종 PNG를 원본 `resource.spr` frame0에서 독립 재계산하면,
  W60이 800 최종 버퍼를 단순 2배한 결과와 달리 원본 실루엣 안에 1600 출력 전용 세부 픽셀을 보존할 수
  있음을 좁게 수용할 수 있다.
- 예상 PASS / FAIL 조건: 원본 EXE SHA와 detour old bytes가 pin과 일치하고, raw에 S3 event 정확히 1건·
  summary1/drop0·PS3/5/7/9 converted가 있으며, reference SPR의 315 opaque mask가 pattern PNG의 비균일
  2x2 block과 좌표별 완전 일치하고 마스크 밖은 nearest 기준 차이0이면 PASS. 전체 PNG 직접 pair나
  G1 제품 PASS로 과장되면 HOLD.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이번 middle은 이 기록과
  `docs/STATUS.md`만 수정. 제품/하네스 source와 binary 변경 없음, 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  검수 당시 `g1_mirror2x.c 1f5b9b80…ee9`, `.h 125858fc…f56`, `direct_draw_trace.c
  f8844332…aea`, `runtime_env.py 1abd0d8f…5ea`, `g1_s3_probe.py f8813768…f98`, 관련 테스트
  `f6444d65…726`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본과 두 manifest EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; S3 bridge
  `f3163e2074644f9d54b73ff5df8ebf82820731e507adf9d04b4c976f7393476a`, control bridge
  `6b8f825a…c9ce`(서로 같은 DLL이 아니므로 whole-image A/B로 사용하지 않음). Wine32/private prefix/Xvfb
  1600x1200, default two-player random, synthetic=false, diagnostic render bridge. 원본
  `fnt/resource.spr` SHA `04a2c160…f40`, frame0 20x24 RLE mask가 fixture다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; `sha256sum`·`jq -s` raw 독립 집계;
  `xxd`/`objdump` 원본 old-byte 확인; Pillow read-only 재계산; `pytest -q
  tests/test_g1_s3_pattern.py tests/test_g1_mirror2x.py tests/test_g1_presentation_trace.py
  tests/test_runtime_env.py` = **199 passed**. raw SHA control `59a3e922…28a8`, pattern
  `17a1ea03…fce9`; PS3 PNG SHA control `f38b16b2…9d9b`, pattern `7287bcb6…af3d`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): pattern raw 1672 events·S3 event1(id36/frame0,
  x10/y3,20x24,315px)·converted246(states3/5/7/9)·mirror545·primitive21233·oracle min
  `0.99934375`·summary1/drop0. SPR decode 409B→480px, opaque315/transparent165; pattern PNG는
  opaque 315 block 전부 비균일, 각 block의 좌상 픽셀 nearest 기준 내부 diff `315*3=945`, transparent
  165 block 비균일0/diff0, mask 좌표 mismatch0. control은 같은 rect 전체 비균일0/diff0.
  **판정 `PASS(S3 detail-path evidence) / G1 overall HOLD`.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 두 PS3 PNG는 랜덤 카메라가 달라 직접 비교하면
  전체 diff1,110,473·resource rect밖 diff1,109,528이다. lap810의 `outside diff0`은 pattern 캡처를
  자체 좌상 픽셀 nearest 기준과 비교한 마스크 밖 수치로만 수용하며 whole-image paired equality가 아니다.
  generic verdict는 production UNKNOWN 때문에 BLOCKED이고, primitive 전체 범위·결정적 동일 장면의
  원본/후보 입력 및 시각 비교·1080p 표시 정책·사용자 3단 승인은 미완료다.
- 다음 한 가지: work tier가 결정적 동일 save/장면을 원본 800과 W60 후보 1600 private run에 각각 로드해
  메뉴·선택·드래그·미니맵·생산 입력 결과와 2x 구도, primitive coverage/성능을 fresh paired로 측정한다.
  S3 합성 패턴은 실제 HD 자산으로 표시하지 않고 별도 opt-in 진단으로 유지한다.

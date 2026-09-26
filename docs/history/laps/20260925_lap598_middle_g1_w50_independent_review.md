# 2026-09-25 | lap 598 | 목표 G1 W50 독립 검수

- 실제 provider/model/effort / 지정 역할: Codex native middle; 실제 model ID·effort 비노출, 지정 역할은 Sol/high 중간 진단·컨펌. 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap597의 `0x76FAA750` owner/export mismatch가 실제 native export 불일치인지, 혹은 Wine rebasing 오판인지 A1/A3 raw와 모듈/PE 증거로 독립 판정한다.
- 예상 PASS / FAIL 조건: raw slot·factory/device·install event를 summary 없이 재계산하고, target의 module containment/export identity를 확인한다. native export면 lap597 `BLOCKED`를 ACCEPT; DxWrapper 내부 target이면 계획 전제를 REJECT하고 strategy에 승격한다.
- 변경 파일 / source fingerprint / 커밋: 문서만 변경. `analysis/memory_maps/g1_w50_d3d9_wrapper_chain_20260925.md`, 이 lap 기록, STATUS/INBOX/`loop/ESCALATE_SOL`; 제품·하네스 source 변경0, 커밋0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…a8ac`, DxWrapper `96c44319…e8fe`, Wine d3d9 `97d381c2…ae1`; lap597의 두 격리 run을 읽기 전용 재검수. 새 게임/fixture/입력0.
- 실행 명령 / 로그 / 캡처: `jq`로 두 final trace와 `evidence.json.modules.maps_raw` 대조, `i686-w64-mingw32-objdump -D/-p`로 DxWrapper call chain과 Wine d3d9 export table 확인, `sha256sum`으로 raw/원본/DxWrapper/캡처 재계산. 입력은 lap597 history에 고정된 두 run/capture 경로와 동일하다.
- 측정값 / 판정: A1 `source=cache=0x76FAA750`, factory `0x020B1350`; A3 source/cache 동일, factory/device 0, owner gate skip을 재확인. DxWrapper loaded base `0x76FA0000` + RVA `0xA750` = target. Wine d3d9 base `0x76D60000` + export RVA `0x3A40` = `0x76D63A40`. target은 DxWrapper 내부 redirector이고, 실제 native lazy chain은 source/cache/guard RVA `0x1BAC60/0x1BACC0/0x1BACC4`. **`REJECT / BLOCKED(plan_contract)`**; raw 및 fail-closed는 ACCEPT, G1 불가능성 아님.
- 회귀 / 남은 위험 / 승인: `make doctor` 원본 verified·side effects false(선택적 runtime manifest 없음은 이번 read-only 범위 밖), `make check` **838 passed in 500.93s**, Ruff/compileall/mypy/`CONTEXT_PASS`, `SAFETY_PASS`. inner slot의 런타임 값·owner/export는 아직 raw 미수집이며 top redirector hook은 계약 변경이다. Fast일 뿐 W51/G1 PASS/마일스톤·사용자 승인 아님.
- 다음 한 가지: strategy가 W50R inner-slot audit work 1회를 허용할지, 아니면 W50 카드 §6대로 G1 대안/G4 전환할지 판정한다. G1 계속 시 work handoff는 inner source/cache/guard+owner/export audit 추가→fresh 1회→native 일치 때만 별도 opt-in CAS이며 재실행·구현은 strategy 판정 전 금지한다.

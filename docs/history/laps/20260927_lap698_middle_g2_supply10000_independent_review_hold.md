# 2026-09-27 | lap 698 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code Opus 5.5(`claude-opus-5-5`), 중간 tier(진단·계획·확인).
  게임 코드/도구 hands-on 수정 없음(문서·승격 파일만 작성).
- 가설 / 사용자 관찰: STATUS "다음 한 가지" = lap691~697 누적 G2 8인×10000 후보의 middle 독립 검수.
  검수 질문: (1) 후보/원본/raw 결과가 재현·일치하는가, (2) 그 결과가 DESIGN §G2와 00:05 운영자 판정
  ("고비용 타입으로 10000을 채우는 것은 실제 플레이를 대표하지 않아 기각", "개인 상한 부족하면 500→1250
  등으로 올리되 8×개인 ≤ 풀")을 충족하는가.
- 예상 PASS / FAIL 조건: 재빌드 SHA·raw JSON·테스트·safety가 기록과 일치하고, 대표 군대 구성에서도
  8×10000이 구조적으로 가능하면 2단 PASS 후보. 구조적 한계로 대표 구성이 불가능하면 HOLD + 방향 판정 승격.
- 변경 파일 / source fingerprint / 커밋: 코드 변경 없음. 신규 이 파일, STATUS/INBOX 갱신,
  `loop/ESCALATE_SOL`에 lap698 절 추가. 전부 uncommitted(LOOP_ALLOW_COMMITS=0).
  검수 대상 해시: `patches/population/g2_supply10000_pool4092_owner500.py` `1c301c71…6faf14a99`(lap695 기록과
  일치), `tools/g2_supply10000_pool4092_eight_owner_probe.py` `640ba51e…2e309fcb9`(lap697 수정본),
  `patches/population/runtime_driver.py` `6b227017…3d0385bb`, `verification_0910/type_costs.json` `520e581a…e3ae24`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e0…c9c08a8ac`
  (`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`) 재해시 일치. **후보를 이번 세션에서 원본 바이트로 독립 재빌드
  (`build_candidate`) → `11aa9e796805d3e0c29b55de957d003c521e74f9aeddf4e3478bd743842e5b53`**, lap695/696/697
  probe JSON 3개의 `candidate_sha256`과 byte-identical. 활성 8인 seed42, 지도 100×100, owner당 type103(cost65)×153
  + type5(cost35)×1 + HQ/worker = 156기.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 게임 실행 없음(기존 artifact 검수).
  lap697 `temp/Syw2plus_patch/g2_capacity/20260927_lap697_pool4092_global_live/probe-result.json`
  SHA256 `95cb79cbcdabd7fcee0363ed4d8481da84bc5a5c59dd7bc18e6ceda16754ff27` 직접 파싱.
  `PYTHONPATH=. .venv/bin/python -m pytest -q patches/population/test_g2_supply10000_pool4092_owner500.py
  patches/population/test_runtime_driver_pool4092_global_live.py patches/population/test_fixed_supply_10000.py`
  → **22 passed (88.16s)**. `checks/safety.sh check` → **SAFETY_PASS**. 전체 `make check`는 코드 무변경이라
  이번 회차 미실행(lap697 로그 1025 passed 참조, 현재 성공으로 승격하지 않음).
- 측정값 / 판정:
  - **확인(PASS):** raw JSON에서 owner0~7 `used=10000,count=156,count_cap=500,cap=10000`, `final_global_live=1248`,
    active_slot_list=exists bitmap=owner합=1248, 중복0, 저장/로드 후 동일, cleanup ok, `source_unchanged=true`.
    후보 재빌드 일치. 편집 raw: 전비 `0x1B576` `66c7008813→66c7001027`·`0x3FFD4` `b888130000→b810270000`,
    개인 cap `0x1B56E` `b0040000(1200)→f4010000(500)`(stock은 `fa000000`=250), 6-영역 fixup 합 1323곳.
  - **결함 1 — 대표성(판정 핵심, 근거 충돌):** type_costs(200종 중 비용>0 83종) 분포 min10/중앙값15/max65,
    비용<20인 종 59/83. fixture의 type103(65)은 **게임 전체에서 가장 비싼 단일 타입**이다. 개인 cap 500이면
    1인 10000은 평균 비용≥20일 때만 가능하고, 중앙값 15 구성은 약 667기(×8=5336), 비용10 구성은 1000기
    (×8=8000)가 필요하다. 전역 풀은 명령 wire 형식이 슬롯을 **하위 12비트**로 압축(`0x004AE613 shl edx,12`,
    복원 `and 0x0FFF`; `analysis/memory_maps/g2_esl2606_command_slot12_boundary_20260925.md`, N=4097/4098
    실측 명령 무시)하므로 현재 구조의 상한이 4095다. 즉 **개인 cap을 1250으로 올려도 8인 합 ≤4092라
    1인 평균 ~511기가 천장**이며 평균 비용≥~20인 군대만 8×10000에 도달한다. 이것은 00:05 판정이 기각한
    "고비용 타입 우회"와 같은 범주다 → 현재 PASS는 **고비용 fixture의 회계·풀 무결성 PASS**일 뿐 대표 구성
    8×10000 증거가 아니다. 방향(비용 하한 수용 vs wire 형식 확장)은 middle 권한 밖 → strategy/사용자 판정.
  - **결함 2 — 안정성 미측정:** 전 구간 게임 tick 3→21(약 18 tick). 전투·생산·사망·재생산·시간 경과가 없다.
  - **결함 3 — 저장/로드 비판별:** 저장 후 상태 변경 없이 바로 로드(`probe.py` 313~367행). no-op 로드도
    동일 결과를 낸다. 유일한 로드 흔적은 tick 21→20 복귀(약한 신호).
  - **결함 4(경미, provenance):** lap695/697 문서의 bridge SHA `28980e42…`는 JSON(`51168d40…`/`bb3ae221…`/
    `42d2eda1…`, 회차마다 다름)과 불일치. 진단 브리지라 제품 판정엔 영향 없으나 문서 정정 필요.
  - 미검증 유지: category_slot_list_a/b, 24k/144k, 멀티 동기화, 건물/효과 혼합.
  - **판정: 2단 `CONDITIONAL PARTIAL PASS`(용량·회계·풀 무결성 단계, 고비용 fixture 한정) / G2 제품 `HOLD`.**
    제품 G2 PASS·사용자 milestone 승인 요청 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 무변경이라 회귀 없음. 결함1은 G2 목표 해석과
  구조 한계가 충돌하는 방향 경계라 `loop/ESCALATE_SOL`로 승격했다.
- 다음 한 가지: strategy(Astra/Fable)/운영자가 방향을 판정한다 — (A) "8×10000은 평균 비용≥20 군대 기준"을
  사용자에게 올려 현 후보(4092/500)로 안정성 단계 진행, 또는 (B) 명령 wire 슬롯 12비트 확장(13비트 이상,
  모든 생산자·소비자·저장·멀티 호환)으로 풀 ≥8000~10000 + 개인 cap ~1250. 판정 대기 중 비차단 work 1건
  (A/B 공통으로 필요): 현 후보 8인 fixture에서 **① 대표 혼합(비용10/15/20/35/65 혼합) 1인 주입으로 cap500
  도달 시 used 실측(천장 수치 확정), ② 저장→유닛 1기 제거/추가→로드로 판별형 복원 확인, ③ 수천 tick 진행
  후 무결성 재확인**. 게임 EXE 변경 없이 probe만 확장한다.

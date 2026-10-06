# 2026-10-04 | lap946 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(세션 시스템 표시), middle(진단·계획·확인). effort는 런처 argv 기준 high이며 이 세션에서 별도 확인 불가. 게임·하네스·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 946 읽기만.
- 가설 / 사용자 관찰: lap945 work의 production K1~K6 PASS(partial)가 raw·PNG로 독립 재현되는가(lap944 카드 §7).
- 예상 PASS / FAIL 조건: 두 lane `prev/a/b`가 command1→15·queue31·progress 감소·`(−800,−300,+10)` EXACT, spec 10/800/300, control_global_delta 비은닉, 120초 내 type31 +1·command15 해제, PNG 생산 표시 동일(P-6), cleanup·source SHA MATCH. 하나라도 재계산 불일치면 HOLD.
- 변경 파일 / source fingerprint / 커밋: 새 문서 `docs/work/active/G1_MIDDLE_W70_PRODUCTION_ACCEPTANCE_CENSUS_CLASS_HANDOFF_LAP946.md`, 본 기록, `docs/STATUS.md`. probe `65fd7f6b22d1fd7627b67408917d3574c9304faa87f74c683e8f2e647c562e29`·test `2648368612d884ab92aa32f9f665ef31c43a0bece522cc6bc3e52e82cdb6b139` 현재 = lap945 실행 before/after. uncommitted.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(원천 game.exe 재해시 MATCH), 비합성 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` MATCH. 원본 800×600 / Scale2x 1600×1200. 활성8인 부하 아님.
- 실행 명령 / 로그 / 캡처: `python3 temp/Syw2plus_patch/20261004_lap946_middle_review/recalculate.py`(SHA `64ea42485b751e1f6f3aa68a9f341e37ba2a455f7c0acca4cb02dcb05bd5369b`) → `recalculation.json` SHA `8ef8c7a2eccf0ab1046a8b1e110277f052b9f28ae0c2d57d4873d19c5591f5b6`. 같은 폴더에 PNG 비교 crop(`b_hud.png`/`c_hud.png`/`sbs_*.png`). `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py` → 175 passed/5.98s.
- 측정값 / 판정:
  - pair SHA `cfb34227…eb8f` MATCH. 원본 prev/a/b tick 24650/24653/24654, 후보 24670/24673/24673. a: command15·queue31·progress 0(원본)/1(후보), 쌀 96807→96007·나무 30031→29731·`+0x1C` 423→433 두 lane EXACT(prev→a, prev→b 모두). K1·K3·K4·K5 **PASS**.
  - K2 control: 원본 1.372초 건물 필드 불변, 쌀 +640 `control_global_delta`에 기록·재계산 일치. 후보 1.377초 delta0. **PASS**(은닉 없음).
  - K6: 두 lane type31 14→15, 새 slot1079(클릭 전 빈 slot, (164,83)), 소실0, slot1199 command1/100 복귀, 다른 type31 생산 건물 1163·1177 전후 불변. **PASS**.
  - P-1 camera `[158,101]→[165,87]`·gate `00→01→00` exact 두 lane **PASS**(진단 gate=1 아래 parity, 정상 gate=0 N/A).
  - P-6 PNG(원본 `6ebf641b…076a7`, 후보 `ab159bc5…6bf`, 저장·captures 사본 MATCH): 자원 HUD·F칸 강조·선택 패널 동일, 후보만 `일본 농부 1%` 생산 패널. **UNKNOWN(캡처 시점)** — 두 캡처 모두 before+0.37초, a progress 0 vs 1. 후보는 원본 표면 미러라 패널 생성 불가 → 렌더 결함 귀속 안 함, 증명도 안 됨.
  - 후보 mirror_validator BLOCKED(nearest oracle 1104건)는 Scale2x용 gate 아님(lap853·lap940 그대로). Scale2x/V1/V2/V2s/V2q PASS.
  - cleanup 두 lane ok, private game 경로 부재 확인. 다른 세션 Xvfb/wine 프로세스는 건드리지 않음.
  - 종합: lap945 생산 발행·완료 parity **PASS(partial) 수용**. lap943 r4 소급 PASS 아님. G1 HOLD.
- 회귀 / 남은 위험 / 승인 상태: 생산 패널 시각 parity(P-6) 미확인, GDI·두 번째 장면·전체HD coverage·D-2·lap913 census 결함·동적 API 실패 주입·사용자 승인 미완료. 모델 기술 컨펌이며 사용자 마일스톤 아님. ESCALATE_SOL 조건 없음(충돌·미설명 실패·milestone 경계 없음).
- 다음 한 가지: work(Sonnet)가 lap946 카드대로 lap913 census 결함 두 건 수리 + fresh save006 `--census-only`로 lap819 §3 기준1 writer 분류 표(HD 가능/원천 그림 없음/명시 잔여/unknown 비율) 산출.

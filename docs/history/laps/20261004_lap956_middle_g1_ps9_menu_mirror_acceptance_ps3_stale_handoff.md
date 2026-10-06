# 2026-10-04 | lap 956 | G1 W70 lap955 PS9 메뉴 block_copy 미러 독립 수용 · PS3 stale 구성 측정 인계

- 실제 provider/model/effort / 지정 역할: middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 956 읽기만.
- 가설: lap955 r1/r2/id/idoff raw는 제품 helper 없이 재현되고, PS9 상승은 메뉴 분기에만 귀속되며(idoff 대조), 후보 메뉴 PNG는 baseline 프레임의 Scale2x와 일치한다.
- 예상 PASS / FAIL 조건(lap954 카드 §5 그대로, 새 임계 없음): PASS = PS9 모든 present ≥90%·V1 0·identity PS9 inside diff 0·소스 hash 불변·PS3 비하락, 재계산이 기록과 일치. FAIL = 불일치·SHA 불일치·PS3 하락의 분기 귀속.
- 변경 파일 / 커밋: 새 카드 `docs/work/active/G1_MIDDLE_W70_P5MENU_ACCEPTANCE_PS3_STALE_HANDOFF_LAP956.md`, 이 기록, STATUS. uncommitted. source 4파일 SHA = lap955 기록(카드 §1).
- 원본 SHA / 후보 SHA / 환경 / fixture: `Syw2plus/game.exe b56986e0…a8ac`·`save/save006.dat 616b7997…d064` read-only 재해시 MATCH. 네 pair PASS·`source_unchanged` true·non-synthetic, `local/runtime/lap955_menu_*` game 사본만 없음(manifest/output/prefix 보존). bridge 사본 diff = 기록된 r1/id 직렬화 차이·idoff 호출 비활성 한 줄과 정확히 일치. 8 player records는 활성8인 부하증명 아님.
- 실행 명령 / 산출(공유 temp `20261004_lap956_middle_review/`): `recalc_lap956.py`(SHA256 `de3e73cfe37e05113f5137eb1468b7f193a051e8a59a106892953418d7ea93b1`) → `recalc_lap956.json`(`223ba38938bff76d6d39bb9479d446e3e889cbf87543fa890b7ea3d2cb877fb6`); `png_cmp_lap956.py`(`4da84233…93b1`) → `png_cmp_lap956.json`(`6ea29d214271c93c73021f9988f176076596d75b0569e8f79220870659393144`); `png_resid_lap956.py`(`d479a5a8…c5b9`) → `png_resid_lap956.json`(`a7659b0641847e5e4b9ec69a44326463f8a6649b9177bf36bf2a30620943dc5f`); `png_ring_lap956.txt`(`654f4e38…c9`); `ps3_dip_lap956.txt`(`23850fcf…961`).
- 측정값 / 판정:
  - PS9: r1 48·r2 46·id 55 present 전부 99.454%(last 99.464), V1 0, id inside diff 0, menu_copy present당 +1·hash `1777000796` 196회 불변·changes 0. idoff PS9 5.677/5.731 = lap945와 정확히 같음 → 상승은 분기 귀속. **PS9 HD coverage PASS(partial) 수용.**
  - PS3: r1 min 89.793·p50 90.413·미달 idx 6~12 = lap945(89.793/90.419/6~12) → 비하락. r2(579~630, 86.67%)·idoff(429~468, 87.03%) transient burst는 covered 불변·stale +16~17.7k·2~2.6s, 분기 OFF에도 존재 → 분기 무관(미측정 원인, 다음 work 범위).
  - PNG: 후보 vs Scale2x(baseline) 3,984 서브픽셀(0.21%), vs 최근접 118,028 → Scale2x 렌더 확인. 후보 자기 프레임 기준 잔여 1,518(0.079%) = stale fallback 1,152(버튼 글자·TextOutA, P7) + 366(0.019%, 그중 94는 stale 이웃 링). 구성은 커서 위치 617px 외 일치.
  - PS35 2.2→8.9%는 메뉴 covered 이월(PS35 menu_copy Δ0) → PS35 진척 아님.
  - source 검토: 가드·Scale2x 인자·stale 보호·버퍼 최악 길이(359+1 ≤ 400, present 줄 최대 2,723B < 5,000) 이상 없음.
- 회귀 / 남은 위험: 단일 fixture·메뉴 한 장면, non-(0,0,800,600) block copy 미지원, 경계 링 소량, 동적 API 실패 주입 미검증. 기준2 전체 미합격(PS3 경계·PS35·HUD/tinted/P6/P7 HD·D-2·사용자승인). ESCALATE·strategy 재호출 조건 없음.
- 다음 한 가지: work(Sonnet) 1 lap — opt-in PS3 stale mask dump 구현(기본 raw 불변 pin) + fresh save006 scale2x run, census last-writer map과 정렬해 정상·초기 idx 6~12·burst stale을 writer 클래스로 분류(카드 §6).

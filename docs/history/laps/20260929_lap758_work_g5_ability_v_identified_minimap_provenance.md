# 2026-09-29 | lap 758 | 목표 G5 (사용자 항목(2) 착수 — "v" 능력 명칭/조건, 미니맵 provenance)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high effort; 지정 역할 work(실무) — 승인된
  범위의 실측/코드/실행만 수행, milestone 판정이나 G5 종료 선언은 하지 않음.
- 가설 / 사용자 관찰: 2026-09-29 10:35 운영자 지시 — "특수능력 v"는 더 이상 맹목적 오프셋 탐색(lap735/lap737,
  실패 가설 2회 소진, UNKNOWN 유지) 대신 **설명서·툴팁 텍스트로 기능과 대상 조건을 확인**하라는 지시.
  이 lap의 가설: (1) 원본 EXE에는 버튼이 보여줄 텍스트 라벨을 저장한 문자열 테이블(`Text_kor.dat`)이
  있고 커맨드 메뉴 버튼 ID는 그 테이블 인덱스와 100 단위로 대응한다(참고 저장소 `Syw2plus_re`의
  `command_menu.h`/`unit_ai_dispatch.md`가 이미 Stop=0x01/Move=0x02/Attack=0x03 ↔ `Text_kor.dat`
  10900/11000/11100 대응을 2026-08-24 정정본으로 문서화해 뒀다). (2) worker 유닛 struct의
  `+0x532..+0x57A` 3-parallel-array(btn/enabled/count, 각 12×uint16)를 그대로 읽으면 클릭 없이
  "v"/"i"/"f" 버튼의 raw ID를 알 수 있다.
- 예상 PASS / FAIL 조건: worker 커맨드 메뉴 슬롯 table을 읽어 slot0/1이 알려진 Stop(1)/Move(2)와
  일치하면 오프셋이 이 빌드에서도 유효(PASS), 불일치면 참고 저장소 오프셋이 이 EXE에 안 맞음(FAIL,
  추가 조사 필요). "v"/"f" 버튼 클릭 시 게임 자체가 버튼 라벨을 한글 텍스트로 표시하면(스크린샷으로
  직접 확인) 그것이 정답이며 외부 문서 대조가 불필요해진다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `tools/g5_command_menu_slot_probe.py`
  (SHA256 `0cdc2ea9ca6b56889a1ea29af41495950e8f9c2d000e9586aee3696887af6afa`) — 조사용 read-only 도구,
  제품 코드(EXE 패치) 0 변경. uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(3회 실행 전후 `source_unchanged=true`).
  후보 없음(원본만, 순정 EXE 읽기 전용 조사). 격리 Wine prefix/Xvfb 1600x1200, 솔로 로비(시드 미고정,
  world (93,56) 또는 (10,49) — 기존 관측과 일치하는 두 spawn 중 하나), 기존 워커(slot1198)+HQ(exclusion
  스캔). 별도 fixture 스폰 없음(op=5 브릿지 미사용, 순정 `build_runtime_bridge.py` 진단 DLL만).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python -m tools.g5_command_menu_slot_probe
  --runtime-root local/runtime/lap758_cmdmenu_slot_probe --artifact-root
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260929_lap758_cmdmenu_slot_probe`
  (3회 반복 실행하며 스크립트를 점진 수정 — 최초 2회는 드래그 선택 버그로 FAIL, 3회째부터 COMPLETE).
  최종 `probe-result.json` SHA256 `73486f26a9d852457c263010c1bf60036a42a1d9a5a0c31bfda38b1413349e5d`.
  캡처: `00-worker-selected-command-grid.png`(S/M/V/F 4버튼, "I" 없음 — 이 스폰의 nation은 4버튼만
  가짐), `02-button-v-after-click.png`(V 슬롯이 "수확( )" 텍스트로 바뀜), `02-button-f-after-click.png`
  (F 슬롯이 "옮기기( )" 텍스트로 바뀜), `03-button-{v,f}-last-attempt.png`, `04-plain-field-rclick-no-button.png`.
  게임 사본(~800MB)은 실행 직후 삭제(output/manifest/prefix/log는 `local/runtime/lap758_cmdmenu_slot_probe/`에 보존).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **오프셋 검증: PASS.** worker(`unit_type=31`, world 예: (93,56)) 커맨드 메뉴 슬롯 배열
    `btn=[0x1, 0x2, 0x5, 0x6, 0,0,0,0,0,0,0,0]`, `enabled=[1,1,1,1,0,...]`, `sub_index=4`,
    `command_kind=0x13`. slot0=0x1, slot1=0x2 — `command_menu.h`의 2026-08-24 정정본
    (`Stop=0x01`·`Move=0x02`, `kBaseCombatCommandSlots` 순서 Stop→Move→Attack→Patrol→Hold)과
    정확히 일치해 이 오프셋이 이 EXE 빌드에서도 유효함을 확인했다(참고 저장소 W6.2의 구버전
    `unit_ai_dispatch.md`는 Move/Stop이 뒤바뀐 미정정 문서이므로 command_menu.h 쪽을 신뢰).
  - **"V" = 수확(Harvest), raw button ID 0x05 — 직접 확인(PASS, 게임 자체 UI 텍스트).** V 버튼을
    클릭하면 그 슬롯 아이콘이 즉시 "수확( )" 한글 텍스트로 바뀐다(`02-button-v-after-click.png`).
    `Text_kor.dat`(`analysis/asset_maps/text_kor.json`, `Syw2plus_re` 참고 저장소, 958개 엔트리)에서도
    10900=정지, 11000=이동, 11100=공격, **11300=건설, 11400=해체**로 100 단위 순열이 확인되지만(공식:
    `text_id = 10800 + 100*button_id` 가설), 이 lap은 그 문자열표 추론 대신 **게임이 클릭 시 스스로
    라벨을 보여주는 것을 직접 캡처**해 "수확"임을 확정했다(문자열표 공식이 맞다면 button 5는
    `10800+500=11300`="건설"이어야 하는데 실측은 "수확"이다 — **문자열표 공식은 틀렸거나 이 항목엔
    안 맞는다는 뜻**, 아래 "회귀/남은 위험"에 기록).
  - **"F" = 옮기기(Move/Relocate), raw button ID 0x06 — 직접 확인(PASS).** F 버튼 클릭 시 슬롯이
    "옮기기( )" 텍스트로 바뀐다(`02-button-f-after-click.png`). 대상 조건 부분 확인: F를 armed한 뒤
    근처 밭 타일을 **우클릭**하면 worker의 `+0x290`(명령) 값이 1(정지/유휴)→**3**(이동중, lap677
    coverage raw의 "이동 3" 관례와 일치)으로 바뀐다(2/2 우클릭 시도 재현, 좌클릭 3회는 불변) —
    "옮기기"가 실제로 이동형 명령을 발주함을 실측으로 확인했다. `+0x384`(pending)는 두 시도 모두
    `0x1000001`로 불변이었다(기존 "신선한 이동"이면 `0x1000003`이 될 것으로 기대되는 값과 다름 —
    **미해결 세부사항**, 아래 참고).
  - **"V"(수확) 대상 좌표: 미확정(UNKNOWN 유지, 그러나 근거는 좁혀짐).** armed 후 밭 타일 4곳×좌/우
    클릭 조합 5회 전부 `+0x290`/`+0x384` 불변 — 어떤 시도도 발주되지 않았다. 원인 후보: (a) 시도한
    화면 좌표가 실제 벼 스프라이트 픽셀이 아니라 갈아엎은 흙/그 사이 여백을 짚었을 가능성(정밀 타일
    좌표 미보정), (b) 순정 우클릭이 이미 암묵적으로 수확류 명령(`command`→8, 아래 baseline 참고)을
    발주하므로 명시적 "수확" 버튼이 요구하는 대상이 밭이 아닌 다른 것(예: 이미 채집 중인 다른 유닛,
    또는 곳간/시장)일 가능성. **이번 lap에서 해소하지 않음** — 다음 work가 이어받을 구체 대상.
  - **baseline(비교용): 버튼 없이 같은 밭 타일 순정 우클릭 → `command` 1→**8**.** (`pending`은
    `0x1000001`로 불변) — lap677/lap727이 이미 문서화한 "밭 우클릭 시 이동이 type8(수확류)로 바뀐다"는
    관찰과 일치. 즉 암묵적 수확은 살아 있고 재현됐다(회귀 없음); 그 위에 명시적 "V=수확" 버튼이
    무엇을 추가로 하는지는 여전히 미상.
  - "I" 버튼은 **이번 fixture의 worker 커맨드 그리드에 존재하지 않았다**(slot 배열이 4개만 활성,
    S/M/V/F). `tools/g5_worker_ability_hq_ui_survey_probe.py`의 기존 주석(S,M,V,I,F 5버튼, lap726
    관측)은 **다른 nation/부팅에서 관측된 구성**이었을 가능성이 높다 — nation에 따라 커맨드 그리드
    구성이 다르다는 근거(이 lap의 worker `unit_type=31`·`command_kind=0x13`, 과거 다른 lap은 다른
    unit_type/국가). "I"의 raw ID/명칭은 이번 lap에서 확인하지 못함(다른 국가 부팅이 필요).
  - **미니맵 provenance(신규 확인, 조사만 — 실행 없음):** 참고 저장소 `Syw2plus_re`(별도
    reverse-engineering 프로젝트, 읽기 전용 참고, 이 프로젝트의 큐/상태 아님)를 조사한 결과, 그
    프로젝트도 **원본 미니맵 렌더 함수 VA를 끝내 찾지 못했다**(`analysis/disasm/ingame_render_pipeline.md`
    §7.4.2 "결과: dead-end 유지" — 문자열 리터럴, 팔레트 인덱스 249/160, 플레이어루프+스트라이드
    조합, 화면좌표 상수 4가지 탐색 전부 실패). 이는 이 프로젝트의 lap677/lap710이 각각 두 위젯(다이아몬드,
    나침반)+Tab/m/M 토글 전부에서 원본조차 미니맵 우클릭 이동이 재현되지 않은 것과 **독립적으로 부합**한다
    — 즉 "이 3가지 UI 요소를 못 찾았다"가 아니라 "완전히 별개의 RE 프로젝트가 원본 바이너리를 처음부터
    다시 뒤져도 미니맵 렌더 진입점 자체를 못 찾는다"는 훨씬 강한 negative 증거다. 새 단서(미실행,
    다음 lap 후보): 네이버 카페 커뮤니티 실측 주소(`analysis/memory_maps/cafe_community_offsets.md`,
    §13) `0x451C12`(미니맵 X좌표)·`0x451C19`(미니맵 Y좌표), §9 `0x4F2E8B`(미니맵 점 IFF 기본값 0xEF) —
    이 프로젝트에서 한 번도 읽어본 적 없는 주소. 다음 lap이 이 주소들을 격리 실행 중 실시간으로 읽어
    (a) 값이 초기화되는지(서브시스템이 살아있는지), (b) 렌더 관련 플래그가 있는지 확인하면 "완전
    비활성"과 "렌더만 실패"를 가를 수 있다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(제품 코드 0 변경, 순정 EXE만 읽음,
  3회 실행 전부 `source_unchanged=true`). 남은 위험: (1) `Text_kor.dat` 100-단위 공식(`10800+100*id`)이
  1~3번 버튼에는 맞지만 5번(수확 실측 vs 건설 예측)에는 틀렸다 — **이 공식으로 다른 버튼 ID를 추론하지
  말 것**(6번="해체" 추측도 검증되지 않았고, 실측 결과 F=6="옮기기"이므로 마찬가지로 틀렸다). 앞으로는
  게임 자체의 클릭-후-라벨 방식(이번 lap이 입증한 방법)만 신뢰한다. (2) "V=수확"의 정확한 발주 대상은
  미해결 — 다음 work가 이어받는다. (3) "I"는 이번 국가에 없어 미확인. (4) 미니맵은 실행 증거 추가 없음
  (조사만). middle 독립 검수 요청 없음(work tier, 정보 제공용). 사용자 승인 대기 없음.
- 다음 한 가지: (a) "V"(수확)의 정확한 발주 대상 특정 — 밭 스프라이트 정밀 좌표 보정 또는 다른 대상
  유형(창고/시장/다른 유닛) 시도. (b) 다른 국가 부팅으로 "I" 버튼 raw ID/라벨 확인. (c) 미니맵:
  `0x451C12`/`0x451C19`/`0x4F2E8B` 실시간 읽기로 서브시스템 활성 여부 1차 확인 — 성공하면 원본에서
  먼저 렌더 살리는 다음 단계로, 실패(주소가 전혀 안 바뀜)하면 미니맵 자체가 이 빌드/환경에서
  완전 비활성이라는 훨씬 강한 BLOCKED 근거로 2026-09-29 10:35 지시 항목①을 마감한다.

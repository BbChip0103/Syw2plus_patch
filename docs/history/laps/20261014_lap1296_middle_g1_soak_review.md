# 2026-10-14 KST | lap1296 middle | H-G1ON2614 raw/coverage 독립 검수

- 역할: 사용자 지정 middle(진단·계획·확인), fresh Codex App 세션. 실제 model/effort의 launch argv는 이 표면에서 확인하지 못해 추측하지 않음. 게임/하네스 구현·새 게임 실행·전달·커밋0. 검증용 소스 사본·독립 DLL 빌드는 공유temp에서만 생성.
- 읽기 순서: loop/PROMPT → AGENTS·최신 INBOX·APPROVALS → STATUS 전체 → DESIGN1~4·MODEL_ROUTING → lap1294/1295·검수대상 소스/raw. STOP 없음. runtime lap1296은 읽기만 했고 변경0. 오래된 full-test는 source_match=no라 재사용하지 않음.
- 목표/가설/종료 조건: lap1294의 중첩trace FAIL 결합·로그예산·PS3 실제시간 수리와3×160초 근거를 독립 대조. raw와구현·관련회귀가 일치하면 이 수리 범위만 기술수용하고 다음 실제시험을work에 넘긴다. G1 마일스톤을 마감하지 않는다.
- 이전 바퀴: lap1295는 새구현/검증 없이 fresh middle을 요청한 회차다. 그 요청2364B·SHA256 `90eda25331b4524f2cb2ed3018155b624554b59309f1c7a5d845693c8cdc71d6`를 `20261014_lap1296_preserved_lap1295_escalate_sol.md`에 byte-exact 보존한 뒤 완료된요청파일을소비한다. 재승격조건(미설명반복실패·실질근거충돌·마일스톤마감)은 이번검수에서발생하지않았다.

## 독립 확인 / 판정

- 공식 EXE SHA256 `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`, 기존 WINMM DLL SHA256 `0e5ef5fdb1b191957ad61e5c5976271a82c19156028f0b068722f770b4f9d728` 재계산 MATCH. 원본 입력·실제게임후보는 수정하지 않았다.
- 현재 C/헤더/exports/Makefile 사본을 공유temp/build에서독립빌드. 새 DLL SHA256 `5c4f275f98a24b73154ca8782f0abe6583057b78ddeb605b150e436b3aca3f88`. 원후보와길이561368B 동일·차이6byte는COFF TimeDateStamp/Export TimeDateStamp/CheckSum 위치만; 세 필드의4B를0으로정규화하면전체바이트일치. .text/.data/.rdata/.idata/.reloc 등동일. 초기진단스크립트는Export TimeDateStamp를빼먹어assert실패했으나원인확인후진단만바로잡음(제품결함/실질근거충돌아님).
- 소스검수:2614 lane_passed가lane status뿐아니라trace_close·trace_summary PASS와PS3 dwell시간/상태를함께요구. close summary는expected run_id·detached/flush·drop/aggregate loss/overflow를검사. C예산65536·install metadata동일상수·상태전환예약·aggregate output loss가failure/drop에반영됨. 관련회귀에과거drop10932/nestedFAIL·부족시간·PS29전환거부가포함된다. 기존mirror nearest validator FAIL은Scale2x의알려진oracle불일치로유지하며이를새PASS로바꾸지않는다.
- 원시재계산:3경기각PS3 dwell만160.976/161.215/161.312초(3193/3214/3182 presents), 합483.503초. 해당window의모든raw상태PS3·present최대간격109/117/172ms, HD min100%·stale/fallback/safety0, event_limit65536·drop/aggregate loss/overflow0, final summary detached/flush complete. 원본·후보·result·manifest의2614필드MATCH. prefix trace와보존trace전체일치,24capture SHA MATCH. 기존cleanup기록PASS이며현재도각ownedprefix PID0·game사본부재확인.
- **PASS(scoped, 기술·보존Wine증거 독립검수).** 이는3개의새단일경기에서입력없이시작화면에머문display soak 합계다. 한경기연속480초/고부하/자연전투장기안정성/Windows/사용자G1완료로표현하지않는다. save006은복사된과거fixture일뿐이soak는new-game경로이며저장로드시험이아니다. 활성8인·지도/군대별안정성수용없음.
- 세prefix MCI로그0B확인. 음악/효과음실재재생·G1-off 동일조건MCI계측비교·Windows/DxWnd·사용자입력/화질UNKNOWN/SKIP 유지. lap1289의기록손실/패배후시간포함FAIL은과거그후보의FAIL로유지한다.

## 명령 / 결과 / 근거

- `make doctor` → setup PASS·보호원본SHA MATCH. 기본runtime/manifest 미존재로optional runtime.ok=false는새실행검증이아니며이번보존run은개별manifest로확인했다.
- `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py tests/test_g1_presentation_trace.py tests/test_g1_winmm_proxy.py` →273 passed/28.16s, exit0, `logs/gates/lap1296-middle-targeted.log`.
- `make typecheck` →12 sources PASS; scoped7파일Ruff PASS. `make lint` 최초exit2는별도세션 `patches/esl2614/g2_port_2614.py:12` F401로설명됨. 수정하지않고보존;검수중INBOX02:07 root가기존사용자분리결정에따라Makefile FOREIGN_PATHS에별도2614파일을추가했다. 최신 `make lint` 재실행exit0 PASS(`lap1296-middle-lint-after-root.log`). 최초FAIL로그도보존.
- `make -C ../temp/Syw2plus_patch/20261014_lap1296_middle_soak_review/build default-on-winmm` →exit0,기존compiler cast/unused/stdcall경고만. `logs/gates/lap1296-middle-build.log`.
- `.venv/bin/python ../temp/Syw2plus_patch/20261014_lap1296_middle_soak_review/recalculate.py` →PASS_SCOPED_WINE_DISPLAY_SOAK. 공유temp의 `review.json` SHA256 `bb03f99b8140503f76c6a25000a2724720e13449d9377b9e0ebeca91b283f41d`; 후속metadata는lint root수정/현재PID확인/정규화필드를주석성판정으로추가했다. script는실행raw핵심지표를재계산한다.
- source-before/after.json:검수대상Python/테스트·C/헤더/export 소스 SHA동일. 전체repo fingerprint불변은주장하지않음(root의Makefile/loop분리설정변경존재). 이회차제품수정0;과거full-test를현재source PASS로승격0. 전체 `make check` SKIP(사용자전달직전만).
- 결과파일final_r1/r2/r3 SHA256: `cf8de0bcdc68436be144f7e8128af402b535fc437f7f770668347f1b61842637` / `7f751f95eb84c12945f2d32a34ee1ffded6a44f537cd9ddbd4071511dd4dd6ec` / `afba3fe2824527e8fcdd75e019bd25ffdfe37f5d056640a6153b1ea6b82baada`.
- 최종trace SHA256: `5c65fb8bae336888987528e251cfb4ac83b0e1e64f5b2c4e41db3011b74daa2b` / `cec49ed861b4aef9c83bd1276b75e60d185030a050b3280186a1c96fd34b28fd` / `d3e9f4773937d33e0c5ca48350fa47e1da1a49d9720ef4465e8718122083da9d`.lap1294가적은4e7be32b/e7975443/27fa1fc3은최종전체trace가아닌WM_CLOSE 요청전owned event_count까지의prefix SHA이며독립대조일치(전사라벨보완·raw충돌아님).
- 변경파일:docs/STATUS.md·docs/feedback/APPROVALS.md·본lap·lap1295요청전문보존. loop/ESCALATE_SOL의완료된검수요청소비. 공유temp의검수스크립트/JSON·빌드사본과logs만추가. 원본/후보/전달물/golden/G5/다른세션소스비접촉;uncommitted 유지.

## 명시 work handoff / 다음 한 가지

- **다음은INBOX00:57에이미배정된MCI G1-off/on 동일조건실제시험이다.** lap1295/1296은제품실행이늘지않은2회이므로추가카드·middle 재검수·장부만의회차로연장하지말고work가실제probe로복귀한다. 기존483.503초시험반복이나추가480초를새합격조건으로요구하지않는다.
- Work는기존2614EXE·동일후보winmm.dll·동일음악설정/새단일경기/관측구간으로쌍을만든다. off에서도WINMM/MCI logging을유지해야한다. DLL을빼서로그가안생기는baseline을0call로세지말것. 현재default-on은명시env를보존하므로 `SYW2_G1_NATIVE_2X_BLIT=0`·`SYW2_G1_MIRROR2X=0`·`SYW2_G1_HD_SOURCE=off`를명시하고off800×600·G1render 비활성화를실측한다. 하네스가이구성을덮어쓰면이비교를위한최소옵션만work가수리한다(현재middle은수정하지않음).
- PASS/UNKNOWN:같은계측조건의on/off에서호출수/명령/반환값을비교. 둘다0이면“이조건에서G1을꺼도MCI0”까지만판정하고실재오디오/Windows는UNKNOWN. off만호출하거나반환이달라지면구체native path를추적해work가최소수리후관련회귀→재실행한다. force-music fixture를쓰면두조건에동일적용하고자연음악과구분해공개한다.
- 전체게임사본/privateprefix/빈display/소유PID종료·game사본정리/raw보존을유지. G5·별도두EXE이식재개0. 사용자승인대기·G1마일스톤은유지하고새전달경계에서root에인계한다.

## 최종 문서·안전 확인

- `.venv/bin/python checks/context_limits.py` →CONTEXT_PASS; STATUS80/INBOX319/APPROVALS102줄로130/350/250이하, Blockers절정확히1개. `.venv/bin/python checks/safety.py check --require-game` →SAFETY_PASS, `git diff --check` →exit0.
- 검수대상source-before SHA재대조변경0·실제후보DLL SHA불변·runtime lap1296불변. 완료된lap1295검수요청은byte-exact보존후소비했고새ESCALATE_SOL은필요하지않음(실질충돌/미설명실패/마일스톤마감없음). 이번종료는기술검수범위완료이며G1제품완료가아니다.

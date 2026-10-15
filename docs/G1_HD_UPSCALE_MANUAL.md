# G1 HD 업스케일 매뉴얼

원본 그림을 뽑아 GPU 업스케일러로 2배로 키우고, 게임이 읽는 원본 형식 `<이름>_hd.<확장자>` 파일로 되돌리는 절차다.
공식 판이 그림을 바꾸거나 새로 넣었을 때 그 그림만 다시 돌리는 데 쓴다.

## 0. 한눈에

| 단계 | 어디서 | 도구 |
|---|---|---|
| ① 원본 → 1배 인덱스 PNG | 로컬 | `tools/g1_hd_extract.py extract` |
| ② 1배 PNG → 2배 RGBA | GPU 인스턴스 | `run_fakefaith_full.py`(2x-FakeFaith-Lite) |
| ③ 2배 RGBA → 팔레트 인덱스 PNG(실루엣·팀색 강제) | 로컬 | `tools/g1_hd_convert.py convert` → `check` |
| ④ 인덱스 PNG → 팩 → 원본 형식 `_hd` 파일 | 로컬 | `g1_hd_convert.py pack` → `native-layout` |
| ⑤ 실게임 확인·전달 | 로컬 Wine → 사용자 | `tools/g1_saved_scene_probe.py` 등, 루프 middle 검수 |

명령은 2026-10-09~14 실제 실행 기록에서 옮겼다. 처음 다시 돌리는 회차가 실제로 실행해 보고 틀린 곳을 이 문서에서 고친다.
모든 로컬 명령은 저장소 루트(`Syw2plus_patch/`)에서 실행한다. 원본 게임 폴더는 **읽기만** 한다. 산출물은 `../temp/Syw2plus_patch/<날짜>_<이름>/` 아래 새 폴더에 둔다.

## 1. GPU 인스턴스

- 접속: `ssh dit_251107_lww_comfyUI_00` (runpod, RTX 4090 24 GB; `~/.ssh/config`에 있음)
- **같은 GPU에서 다른 작업(vLLM 등)이 늘 돌고 있다.** 남의 프로세스를 죽이지 않는다. 실행 전 `nvidia-smi`로 남은 메모리를 확인하고, 실행기의 `--gpu-fraction`(기본 0.25)으로 자기 몫만 쓴다. 메모리가 모자라면 실행기가 CPU로 다시 시도한다(느리지만 결과는 같다).
- 원격 작업 루트: `/workspace/syw2_upscale_setup/`
  - `20261010_193000_fakefaith_full/` — 현재 HD의 원천이 된 전체 실행(799 파일·39,805 프레임, 오류 0). `local_models/2x-FakeFaith-Lite.pth`, `scripts/run_fakefaith_full.py`가 있다.
  - `20261010_032319_pixel_style_compare/`, `20261010_000449_five_model_compare/` — 모델 비교 실행(2x-FaithfulSPSR, 4x-NXbrz, 4x-PixelPerfectV4, 4x-PocketMonsters-Alpha 등 보관).
- 원격 실행 결과 사본(로컬): `../temp/Syw2plus_patch/20261009_lap1206_work_hdu2/upscaler_output_2x/_intermediate/20261010_193000_fakefaith_full/`
  - `logs/runner_snapshot.py` = 실행기 사본, `scripts/build_manifest.py`·`package_job.py`·`audit_full.py`, `task_plan.json`

### 모델·처리 방식(바꾸면 기존 HD와 화풍이 달라진다)

- 모델 `2x-FakeFaith-Lite.pth`, SHA256 `51ee3b4b05422f1e48aee115c05dc6dca8fd5ff7b8341e7f6b84be820696c9db` (실행기가 SHA 불일치면 멈춘다)
- Spandrel `ModelLoader`, scale 2, float32, 타일 128 + 겹침(halo) 24
- 전처리: 팔레트 PNG → RGBA, 실루엣 밖 화소는 가장 가까운 보이는 색으로 채움(가장자리 분홍 번짐 방지)
- 알파: 원본 알파를 최근접 2배로 그대로 씀(`sourceNN2`) — 업스케일 뒤 배경 제거를 하지 않는다
- 속도: 4090에서 약 20 프레임/초(전체 39,805 프레임 약 35분)

## 2. 단계별 명령

### ① 입력 뽑기

```bash
G="../[ESL]Syw2plus - ESL2614/[ESL]Syw2plus"        # 지금 정본 게임 폴더(바뀌면 고친다)
W=../temp/Syw2plus_patch/<날짜>_hd_reupscale_input
# --out 은 추출 기록(ref): 파일별 manifest.json + 프레임 NNNN.png. 기본 --image-dirs 는 char,tile,BattleSpr,portrait 이므로 필요한 폴더를 적는다.
# 주의: --only 는 목록 필터일 뿐이다. 폴더가 --image-dirs 에 없으면 rendered=false 로 PNG 없이 끝나고 exit 0 이다(lap1302).
#       뽑을 파일의 폴더(fnt, yfnt …)를 반드시 --image-dirs 에 넣고, 끝나면 manifest 의 rendered=true 를 확인한다.
.venv/bin/python tools/g1_hd_extract.py extract --game "$G" --out "$W/ref" --image-dirs char,tile,BattleSpr,fnt,yfnt \
    --only fnt/portrait_plus.spr --only yfnt/title.spr --only tile/normal/castle2.ytl     # 파일마다 --only 반복, 전체면 생략
# 업스케일러 입력은 ref 에서 프레임 PNG만 복사(SHA 목록 함께 생성; 두 번째 인자는 imjin2.pal)
python3 ../temp/Syw2plus_patch/20261009_lap1206_work_hdu2/scripts/u2_copy_verify.py "$W" "$G/pal/imjin2.pal"
#   → $W/upscaler_input_1x/  +  $W/upscaler_input_1x.manifest.sha256
```

입력 형식: `char/ad1.SPR/0000.png`처럼 원본 파일마다 폴더, 프레임마다 `NNNN.png`. 원본 1배 크기, 256색 인덱스 PNG(팔레트 `imjin2.pal`), **투명 = 색 254**(`tRNS`).
전부 투명한 프레임도 개수를 맞추려고 들어 있다(실행기가 건너뛴다). `_online`이 들어간 폴더는 업스케일 대상에서 뺀다.

### ② GPU 업스케일

```bash
# 로컬: 매니페스트와 업로드 묶음 만들기 (원격 실행 폴더 이름은 새로 정한다)
J=<새 실행 폴더, 예: 20261014_hhmmss_reupscale>
L=../temp/Syw2plus_patch/$J ; mkdir -p "$L/logs" "$L/scripts"
cp ../temp/Syw2plus_patch/20261009_lap1206_work_hdu2/upscaler_output_2x/_intermediate/20261010_193000_fakefaith_full/logs/runner_snapshot.py "$L/scripts/run_fakefaith_full.py"
python3 ../temp/Syw2plus_patch/20261009_lap1206_work_hdu2/upscaler_output_2x/_intermediate/20261010_193000_fakefaith_full/scripts/build_manifest.py "$W/upscaler_input_1x" "$L/input_manifest.json"   # 실행기는 job 최상위 input_manifest.json 을 읽는다
# 모델은 원격에 이미 있으므로 묶음에는 입력+매니페스트+실행기만 넣어도 된다(package_job.py는 모델까지 넣는다)

# 원격: 새 폴더에 올리고 모델 링크 후 실행
ssh dit_251107_lww_comfyUI_00 "mkdir -p /workspace/syw2_upscale_setup/$J/local_models && \
  ln -sf ../../20261010_193000_fakefaith_full/local_models/2x-FakeFaith-Lite.pth /workspace/syw2_upscale_setup/$J/local_models/"
# 원격 /workspace 는 소유자 변경이 막혀 rsync -a 가 실패(exit 23)한다 → -rt 로 올린다
rsync -rt "$W/upscaler_input_1x/" dit_251107_lww_comfyUI_00:/workspace/syw2_upscale_setup/$J/input/
rsync -t  "$L/input_manifest.json" dit_251107_lww_comfyUI_00:/workspace/syw2_upscale_setup/$J/
rsync -rt "$L/scripts/" dit_251107_lww_comfyUI_00:/workspace/syw2_upscale_setup/$J/scripts/
ssh dit_251107_lww_comfyUI_00 "nvidia-smi; cd /workspace/syw2_upscale_setup/$J && \
  nohup python3 scripts/run_fakefaith_full.py --job . --device auto --gpu-fraction 0.08 > logs/run.log 2>&1 < /dev/null &"   # 0.08≈2 GB: vLLM 이 ~21.6 GB 를 쓰고 남는 게 ~2.2 GB
# 진행: logs/run.log 의 {"event":"progress",...} 줄 (errors_this_run 0 확인)

# 결과 내려받기: 원격 staged_results/ (input과 같은 구조, NNNN.png RGBA 2배)
rsync -rt dit_251107_lww_comfyUI_00:/workspace/syw2_upscale_setup/$J/staged_results/ "$L/upscaler_output_2x/"
```

결과 규칙: 가로·세로 **정확히 2배**, 폴더 구조와 `NNNN.png` 이름 그대로(꼬리 붙으면 무시됨), RGB/RGBA 모두 가능하지만 RGBA 권장.

### ③ 팔레트로 되돌리기·검사

```bash
PAL="$G/pal/imjin2.pal"
REF="$W/ref"                                  # ①의 추출 기록(원본 실루엣·팀색 자리)
.venv/bin/python tools/g1_hd_convert.py convert --pal "$PAL" --ref "$REF" --out "$L/hd" "$L/upscaler_output_2x"
.venv/bin/python tools/g1_hd_convert.py check   --pal "$PAL" --ref "$REF" --json "$L/check.json" "$L/hd"   # 위반 0
```

`convert`가 하는 일: `imjin2.pal` 양자화, 원본 실루엣을 2×2로 키워 강제(밖 = 투명 254, 안 = 불투명), 팀색(236~239) 자리를 원본 기준으로 복구.

### ④ 원본 형식 `_hd` 파일 만들기

```bash
# --game 을 꼭 준다: 기본값은 옛 2608 폴더(../[ESL]Syw2plus)라 2614 그림과 이름이 어긋난다. --image-dirs 는 ①과 같은 폴더.
.venv/bin/python tools/g1_hd_convert.py pack --game "$G" --pal "$PAL" --ref "$REF" --hd-dir "$L/hd" --image-dirs char,tile,fnt --out "$L/pack"
.venv/bin/python tools/g1_hd_convert.py native-layout --game "$G" --pal "$PAL" --out "$L/native_layout" "$L/pack"
```

결과는 게임 폴더 구조 그대로 `char/archerk_hd.spr`, `tile/normal/castle2_hd.ytl`처럼 원본 옆에 놓일 파일이다. 형식은 원본과 같고 프레임만 2배다.
기존 전체 팩에 일부만 바꿔 넣을 때는 바뀐 파일의 `_hd`만 교체한다. **일부만 돌리면 native-layout이 대상 밖 파일도 만든다**(같은 프레임을 공유하는 `castle0_hd.ytl`·`button_hd.spr` 등, 나머지 프레임은 기본 확대로 채움 — 2026-10-14 14개 → 391파일). 이것들은 기존 전체판보다 나쁘므로 **대상 파일만 골라** 기존 전체판에 합치고, `g1_hd_sources.sha256`(원본 SHA 색인, H-HDGUARD DLL이 읽음)도 합친 파일 전체에 대해 다시 만든다(줄 형식 `<원본 SHA256>  <_hd 상대경로>`, 원본 = 이름에서 `_hd`를 뺀 게임 파일).
`BattleSpr/`·`yfnt/`의 `_hd`는 2026-10-14까지 전달판에 넣은 적이 없다(`yfnt/title`은 DLL의 H-HDF0 전용 경로). 넣으려면 실게임에서 따로 확인한다.

### ⑤ 확인과 전달

- 실게임: 2614는 G1 DLL이 `winmm.dll`(게임 폴더)로 들어간다. 하네스 `tools/g1_esl2614_display_probe.py`·`tools/esl2614_runtime.py`(격리 Wine 사본).
- 원본이 바뀐 그림의 옛 `_hd`는 쓰면 안 된다(바뀐 그림 위에 옛 HD가 나옴). 원본 SHA 확인 장치(H-HDGUARD)가 들어가면 DLL이 자동으로 무시한다.
- 루프 규칙대로: work → fresh middle 검수 → root가 전달 직전 전체 `make check` 1회 → 사용자 확인 후 `260921_temp/`로 전달(txt 없음, 이전 판은 `archive/`).

## 3. 모델 시험 이력 (2026-10-09~10)

기록 폴더: `../temp/Syw2plus_patch/20261009_lap1206_work_hdu2/upscaler_output_2x/_intermediate/<실행>/`. 모두 대표 샘플(15개 그림·22프레임 수준) 비교였고, 전체 적용은 FakeFaith-Lite 하나뿐이다.

| 실행 | 방식·모델 | 결과 |
|---|---|---|
| `20261009_155904_pilot` | 생성형 시트 편집 — topview `gpt-image-2.5-sunburst` (16요청) | **탈락.** 시트 전체를 다시 그려 프레임 위치·모양이 바뀜(기하 불변 아님). v1 12·v3 2 반려 |
| `20261009_195415_bria_resolution` | 유료 API `bria/increase-resolution` (Replicate, 8요청 약 $0.32) | 2배 정확·알파 유지. 전체 적용은 안 함 |
| `20261009_202030_2k_provider_split` | 전체 적용 비용 산정: 투명 있는 그림 → Bria 770요청(약 $30.8), 불투명 → GPT Image 2 21요청 | 계획만, 실행 안 함 |
| `20261010_000449_five_model_compare` | 로컬 GPU 5종: `4x_UltraFArt_v3`·`4x_HDCube`·`2x_Gen5_Alpha`·`4x_PocketMonsters_Alpha`·`1x_PixelSharpen` | UltraFArt v3 균형(일반 후보), HDCube 가장 선명하나 흰 테두리·과샤픈, Gen5 Alpha 부드럽고 윤곽 변형, PocketMonsters 만화풍, PixelSharpen 노이즈. **원본 투명 화소의 숨은 분홍 RGB가 테두리 번짐의 원인** → 이후 “실루엣 밖 가장 가까운 색 채우기 + 원본 알파 최근접 2배”를 표준으로 삼음 |
| `20261010_032319_pixel_style_compare` | 픽셀 아트용 6종: MMPX(알고리즘)·`2x-FakeFaith-Lite`·`2x-FaithfulSPSR`·`4x-NXbrz`·`4x-PixelPerfectV4`·`4x-PocketMonsters-Alpha` (PixelLab API는 키가 없어 시도 안 함) | MMPX 원본 도트 가장 충실(거의 최근접 확대), **FakeFaith-Lite 중간 정도 정리 — 절충안**, FaithfulSPSR 뚜렷한 이득 없음, NXbrz·PixelPerfectV4·Pocket은 매끈한 재해석 |
| `20261010_193000_fakefaith_full` | **채택: `2x-FakeFaith-Lite` 전체 799파일·39,805프레임** | 현재 `_hd`의 원천 |

4배 모델은 결과를 2배로 줄여 쓴다(Lanczos, 또는 phase 0 화소 선택). 다른 모델로 바꿔 다시 돌리면 기존 HD와 화풍이 섞이므로, 바뀐 그림만 다시 돌릴 때는 FakeFaith-Lite를 그대로 쓴다.

## 4. 기록

- 2026-10-09 입력 묶음: `../temp/Syw2plus_patch/20261009_lap1206_work_hdu2/upscaler_input_1x/` (840 파일·43,622 프레임, 매니페스트 SHA `007bc9d7…`)
- 2026-10-10 전체 실행: 위 `20261010_193000_fakefaith_full` (19:33~20:27 KST, 4090, 오류 0)
- 2026-10-14 2614 변경분: 바뀐 12개(`fnt/portrait_plus.spr`·`fnt/button_plus.Spr`·`yfnt/title.spr`·`tile/{bright,dark,green,normal,brown,volcano,snow}/castle2.ytl`·`BattleSpr/ICON.Spr`·`BattleSpr/BANNER.Spr`)·새 3개(`eft/codex_poisonfield.yav`·`fnt/poisonfield.SPR`·`fnt/poisonfx.spr`) — 입력만 `../temp/Syw2plus_patch/20261014_hd_reupscale_input/`(lap1301), 업스케일 미실행

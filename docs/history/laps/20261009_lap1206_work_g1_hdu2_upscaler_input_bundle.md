# 2026-10-09 | lap 1206 | G1 work — H-HDU2 업스케일러 입력 묶음(U2-0~U2-5)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 게임 run 0·저장소 소스/테스트 변경 0·커밋 0.
- 가설: 기존 `g1_hd_extract`·`g1_hd_convert`만으로 `char,tile,fnt` 1배 입력 묶음을 만들고, 돌려받기 규칙이 도구 동작과 일치한다(lap1205 사전등록 §3).
- 예상 PASS: manifest SHA = lap1202 `4f65df5d…`, 복사 43,622·SHA 불일치 0·형식 위반 0, 가짜 업스케일 200 convert/check 위반 0, 음성 대조 2 거부.
- 변경 파일 / fingerprint: 저장소 변경 0(스크립트 `W/scripts/u2_copy_verify.py`·`u2_sim.py`는 공유 temp). W = `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261009_lap1206_work_hdu2`.
- 원본 SHA / 환경: EXE `b56986e0…08a8ac` 실행 전후 MATCH(`sha256sum`), `.venv/bin/python -I` numpy 2.4.3·Pillow 12.1.1, 디스크 여유 236 GB. fixture 없음(게임 run 0).
- 실행: `tools/g1_hd_extract.py extract --game ../[ESL]Syw2plus --out W/ref --image-dirs char,tile,fnt`(86 s, exit 0) → `u2_copy_verify.py` → `u2_sim.py` + `g1_hd_convert.py convert/check`. 로그 `W/extract.log` `7c5653c5…`, `W/u2_verify.json` `c44cbb59…`, `W/u2_sim.log` `0da565e4…`, `W/upscaler_input_1x.manifest.sha256` `007bc9d7…`.
- 측정값:
  - U2-1 PASS: `source_unchanged` true, summary rle 2,763·ytl 425·raw 152·bmp 27·unsupported 7, 렌더 840 파일·`fc` 합 43,622, `ref/manifest.json` SHA256 `4f65df5df49fc222c9fc6460f176253217f57d6cf5430d913d75a8eb802dad10` = lap1202 일치(결정론).
  - U2-2 PASS: 복사 43,622 = ref FRAME_RE 43,622 = manifest `fc` 합, 폴더 안 다른 파일 0, SHA 불일치 0, 하드링크 0, 폴더 840개.
  - U2-3 PASS: 43,622 전부 모드 P·팔레트 = `imjin2.pal`×4·`tRNS` 254만·크기 = `fw×fh`·마스크 0↔254/1↔≠254 위반 0. 전부-투명(불투명 0) 프레임 **10,782**(공개).
  - U2-4 PASS: 200프레임 최근접 2배 RGB → convert converted 200·errors 0·ignored 0(tie 4,260 중 draft 해소 4,034), check 위반 0. 음성 (a) 4배 크기 → errors 1 `size 352x256 != required 176x128`, (b) `0000_out.png` → ignored_files 1. 규칙 문장과 도구 동작 일치.
  - U2-5: `upscaler_input_1x` 191 MB, `ref` 603 MB, `sim_*` 삭제(결과 json·로그만 보존).
- 판정: **H-HDU2 `PASS(partial, 기술·격리)`** 후보. 공개 한계: 알파 무시 업스케일러의 분홍(252,224,252) 번짐 위험, 전부-투명 10,782프레임은 사용자가 업스케일할 필요 없어도 1:1 개수 유지로 포함, raw 56프레임 실사용 미증명, 중복 제거 안 함, 실제 업스케일 결과는 아직 없음.
- 회귀 / 독립 검수: 소스 변경 0. middle 독립 재계산·APPROVALS 사용자 안내 미수행(역할 경계, `loop/ESCALATE_SOL`).
- 다음 한 가지: middle이 새 스크립트로 개수·SHA·형식을 재계산하고 APPROVALS lap1203 항목에 사용자 안내(txt 금지)를 적는다.

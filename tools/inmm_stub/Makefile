CC      = i686-w64-mingw32-gcc
# -fno-stack-protector: __stack_chk_fail 참조 제거
CFLAGS  = -m32 -shared -Wall -Wextra -O2 -fno-stack-protector -mno-stack-arg-probe
# msvcrt.dll 의존성 완전 제거:
#   -nostartfiles: dllcrt2.o (msvcrt 의존 CRT 스타트업) 제외
#   -nodefaultlibs: 기본 라이브러리 전부 제외
#   -Wl,-e,_DllMain@12: PE 진입점을 직접 DllMain으로 설정 (CRT 래퍼 우회)
# -luser32: wvsprintfA / wsprintfA 사용
LDFLAGS = -nostartfiles -nodefaultlibs -Wl,-e,_DllMain@12 \
          -lkernel32 -luser32 -lwinmm -ldsound -lmsvfw32 -lmsacm32
TARGET  = _inmm.dll


.PHONY: all default-on default-on-winmm clean

all: $(TARGET)

SRCS = inmm_stub.c control_logging.c control_protocol.c control_registry.c control_state_bridge.c control_executor.c control_input_bridge.c control_handler_bridge.c asset_hook.c sfx_hook.c direct_draw_trace.c g1_mirror2x.c g1_screen_watch.c g1_hd_asset.c g1_perf_sections.c g1_census.c g1_state_snapshot.c final_d3d9_trace.c ai_shadow.c trace_record_serializer.c

$(TARGET): $(SRCS) g1_census_contract.h g1_census_residual.h g1_census_watch.h g1_stale_mask.h g1_layer_drift.h g1_screen_watch.h g1_scratch_bounds.h g1_state_snapshot.h g1_panel_layer.h g1_overlay_blt.h g1_frame_copy.h g1_pause_snapshot.h g1_primary_readback.h g1_bar_copy.h g1_briefing_compose.h g1_scratch_bltfast.h g1_rect_fill.h g1_cache_fill.h g1_blend_key.h g1_sha256.h inmm_stub.def
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS) inmm_stub.def $(LDFLAGS) \
		-Wl,--out-implib,lib_inmm.a
	@echo "✅ Built: $(TARGET)"
	@i686-w64-mingw32-objdump -p $(TARGET) | grep -A10 "The Export Tables" || true

# Shipped G1 build: same sources with SYW2_G1_DEFAULT_ON, written to _G1MM.dll.
# Module name inside stays _inmm (inmm_stub.def); only the file name differs.
G1MM_TARGET = _G1MM.dll

default-on: $(G1MM_TARGET)

$(G1MM_TARGET): $(SRCS) $(wildcard *.h) inmm_stub.def
	$(CC) $(CFLAGS) -DSYW2_G1_DEFAULT_ON -o $(G1MM_TARGET) $(SRCS) inmm_stub.def $(LDFLAGS) \
		-Wl,--out-implib,lib_g1mm.a
	@echo "✅ Built: $(G1MM_TARGET)"

# ESL2614 imports WINMM.dll directly. This app-local proxy keeps the stock
# G1 hooks for the four game imports and forwards the complete WINMM export
# table to the system copy for the rest of the process.
WINMM_TARGET = winmm.dll

default-on-winmm: $(WINMM_TARGET)

$(WINMM_TARGET): $(SRCS) g1_winmm_proxy.c g1_winmm_forwarders.S $(wildcard *.h) g1_winmm_proxy.def Makefile
	$(CC) $(CFLAGS) -DSYW2_G1_DEFAULT_ON -DSYW2_WINMM_PROXY -o $@ $(SRCS) g1_winmm_proxy.c g1_winmm_forwarders.S g1_winmm_proxy.def $(filter-out -lwinmm,$(LDFLAGS)) -Wl,--exclude-all-symbols -Wl,--out-implib,lib_g1winmm.a
	@echo "✅ Built: $(WINMM_TARGET)"

clean:
	rm -f $(TARGET) lib_inmm.a $(G1MM_TARGET) lib_g1mm.a $(WINMM_TARGET) lib_g1winmm.a

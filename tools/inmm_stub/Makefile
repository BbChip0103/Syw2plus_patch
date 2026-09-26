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


.PHONY: all clean

all: $(TARGET)

SRCS = inmm_stub.c control_logging.c control_protocol.c control_registry.c control_state_bridge.c control_executor.c control_input_bridge.c control_handler_bridge.c asset_hook.c sfx_hook.c direct_draw_trace.c final_d3d9_trace.c ai_shadow.c trace_record_serializer.c

$(TARGET): $(SRCS) inmm_stub.def
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS) inmm_stub.def $(LDFLAGS) \
		-Wl,--out-implib,lib_inmm.a
	@echo "✅ Built: $(TARGET)"
	@i686-w64-mingw32-objdump -p $(TARGET) | grep -A10 "The Export Tables" || true

clean:
	rm -f $(TARGET) lib_inmm.a

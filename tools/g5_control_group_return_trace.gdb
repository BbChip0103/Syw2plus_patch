set pagination off
set confirm off
set debuginfod enabled off
set architecture i386
handle SIGILL stop print pass
handle SIGSEGV stop print pass
handle SIGBUS stop print pass
handle SIGABRT stop print pass

# FUN_0040F7D0 returns with ret 0xc at 0x0040F7F6.  This breakpoint is
# observational: it records eax and the caller stack before the return.
break *0x0040f7f6
commands
  silent
  printf "RETURN_0040F7D0\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  printf "return_address: "
  x/wx $esp
  printf "slot_arg: "
  x/wx $esp+4
  printf "mode_arg: "
  x/wx $esp+8
  printf "flag_arg: "
  x/wx $esp+12
  printf "selection_count: "
  x/wx 0x0108c000
  continue
end

shell touch "$G5_UI_TRACE_CONTROL/armed.json"
shell while [ ! -f "$G5_UI_TRACE_CONTROL/probe_ready.json" ]; do sleep 0.1; done
shell touch "$G5_UI_TRACE_CONTROL/continue.flag"
continue

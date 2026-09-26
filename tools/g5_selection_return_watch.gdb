set pagination off
set confirm off
set debuginfod enabled off
set architecture i386
set can-use-hw-watchpoints 1
handle SIGILL stop print pass
handle SIGSEGV stop print pass
handle SIGBUS stop print pass
handle SIGABRT stop print pass

watch *(unsigned int*)0x31fa40
condition 1 *(unsigned int*)0x31fa40 > 0x01000000
watch *(unsigned int*)0x31fa44
condition 2 *(unsigned int*)0x31fa44 > 0x01000000
watch *(unsigned int*)0x31fa48
condition 3 *(unsigned int*)0x31fa48 > 0x01000000
watch *(unsigned int*)0x31fa4c
condition 4 *(unsigned int*)0x31fa4c > 0x01000000

commands 1
  silent
  printf "\n=== RETURN_SLOT_WATCH_HIT address=0x31fa40 value_gt=0x01000000 ===\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  printf "watch_slot_value: "
  p/x *(unsigned int*)0x31fa40
  printf "pc_symbol: "
  info symbol $pc
  x/16i $pc
  x/48wx 0x31fa00
  bt 20
  info frame
  shell touch "$G5_SELECTION_TRACE_CONTROL/watch-hit.flag"
  shell touch "$G5_SELECTION_TRACE_CONTROL/continue.flag"
  detach
  quit
end

commands 2
  silent
  printf "\n=== RETURN_SLOT_WATCH_HIT address=0x31fa44 value_gt=0x01000000 ===\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  printf "watch_slot_value: "
  p/x *(unsigned int*)0x31fa44
  printf "pc_symbol: "
  info symbol $pc
  x/16i $pc
  x/48wx 0x31fa00
  bt 20
  info frame
  shell touch "$G5_SELECTION_TRACE_CONTROL/watch-hit.flag"
  shell touch "$G5_SELECTION_TRACE_CONTROL/continue.flag"
  detach
  quit
end

commands 3
  silent
  printf "\n=== RETURN_SLOT_WATCH_HIT address=0x31fa48 value_gt=0x01000000 ===\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  printf "watch_slot_value: "
  p/x *(unsigned int*)0x31fa48
  printf "pc_symbol: "
  info symbol $pc
  x/16i $pc
  x/48wx 0x31fa00
  bt 20
  info frame
  shell touch "$G5_SELECTION_TRACE_CONTROL/watch-hit.flag"
  shell touch "$G5_SELECTION_TRACE_CONTROL/continue.flag"
  detach
  quit
end

commands 4
  silent
  printf "\n=== RETURN_SLOT_WATCH_HIT address=0x31fa4c value_gt=0x01000000 ===\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  printf "watch_slot_value: "
  p/x *(unsigned int*)0x31fa4c
  printf "pc_symbol: "
  info symbol $pc
  x/16i $pc
  x/48wx 0x31fa00
  bt 20
  info frame
  shell touch "$G5_SELECTION_TRACE_CONTROL/watch-hit.flag"
  shell touch "$G5_SELECTION_TRACE_CONTROL/continue.flag"
  detach
  quit
end

shell touch "$G5_SELECTION_TRACE_CONTROL/armed.json"
shell while [ ! -f "$G5_SELECTION_TRACE_CONTROL/probe_ready.json" ]; do sleep 0.1; done
shell touch "$G5_SELECTION_TRACE_CONTROL/gdb_continuing.flag"
continue

printf "\n=== RETURN_SLOT_WATCH_NO_HIT_OR_INFERIOR_EXIT ===\n"
info registers
info proc mappings
detach

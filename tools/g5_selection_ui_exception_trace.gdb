set pagination off
set confirm off
set debuginfod enabled off
set can-use-hw-watchpoints 0
set architecture i386
handle SIGILL stop print pass
handle SIGSEGV stop print pass
handle SIGBUS stop print pass
handle SIGABRT stop print pass

break *0x0043877a if *(int*)0x0108c000 >= 20
commands
  silent
  printf "\nBREAK hit_append_limit 0x0043877a\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x004384b0 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK hit_test 0x004384b0\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x0041e03b if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK hit_test_return_path 0x0041e03b\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x0041e114 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK selection_post_hit_test 0x0041e114\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x0041e1d6 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK selection_loop 0x0041e1d6\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x00412d90 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK selection_writer 0x00412d90\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x0041dc40 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK selection_consumer 0x0041dc40\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x00498f4f if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK ui_refresh 0x00498f4f\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x00498e60 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK ui_unit 0x00498e60\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x0049933c if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK ui_loop 0x0049933c\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x004998b3 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK ui_slot_scan 0x004998b3\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x0049a995 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK ui_selection_case 0x0049a995\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x0049a9f0 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK ui_selection_case2 0x0049a9f0\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

break *0x004a4240 if *(int*)0x0108c000 > 20
commands
  silent
  printf "\nBREAK ui_selected_lookup 0x004a4240\n"
  info registers eax ebx ecx edx esi edi esp ebp eip
  x/24wx $esp
  bt 8
  continue
end

shell touch /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap647_g5_exception_trace_gate/armed.json
shell while [ ! -f /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap647_g5_exception_trace_gate/probe_ready.json ]; do sleep 0.1; done
continue
echo \\n=== EXCEPTION SNAPSHOT ===\\n
info registers
info proc mappings
x/128wx $esp
bt 20
x/16i $pc
info frame
detach

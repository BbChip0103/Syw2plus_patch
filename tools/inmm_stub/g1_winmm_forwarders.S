.text
.extern _g1_winmm_resolve
.extern _g1_winmm_resolve_ordinal
.globl _g1_forward_CloseDriver
_g1_forward_CloseDriver:
    pushl $_g1_forward_CloseDriver_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_CloseDriver_missing
    jmp *%eax
_g1_forward_CloseDriver_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_CloseDriver_name:
    .asciz "CloseDriver"
.text
.globl _g1_forward_DefDriverProc
_g1_forward_DefDriverProc:
    pushl $_g1_forward_DefDriverProc_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DefDriverProc_missing
    jmp *%eax
_g1_forward_DefDriverProc_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DefDriverProc_name:
    .asciz "DefDriverProc"
.text
.globl _g1_forward_DriverCallback
_g1_forward_DriverCallback:
    pushl $_g1_forward_DriverCallback_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DriverCallback_missing
    jmp *%eax
_g1_forward_DriverCallback_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DriverCallback_name:
    .asciz "DriverCallback"
.text
.globl _g1_forward_DrvClose
_g1_forward_DrvClose:
    pushl $_g1_forward_DrvClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DrvClose_missing
    jmp *%eax
_g1_forward_DrvClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DrvClose_name:
    .asciz "DrvClose"
.text
.globl _g1_forward_DrvDefDriverProc
_g1_forward_DrvDefDriverProc:
    pushl $_g1_forward_DrvDefDriverProc_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DrvDefDriverProc_missing
    jmp *%eax
_g1_forward_DrvDefDriverProc_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DrvDefDriverProc_name:
    .asciz "DrvDefDriverProc"
.text
.globl _g1_forward_DrvGetModuleHandle
_g1_forward_DrvGetModuleHandle:
    pushl $_g1_forward_DrvGetModuleHandle_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DrvGetModuleHandle_missing
    jmp *%eax
_g1_forward_DrvGetModuleHandle_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DrvGetModuleHandle_name:
    .asciz "DrvGetModuleHandle"
.text
.globl _g1_forward_DrvOpen
_g1_forward_DrvOpen:
    pushl $_g1_forward_DrvOpen_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DrvOpen_missing
    jmp *%eax
_g1_forward_DrvOpen_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DrvOpen_name:
    .asciz "DrvOpen"
.text
.globl _g1_forward_DrvOpenA
_g1_forward_DrvOpenA:
    pushl $_g1_forward_DrvOpenA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DrvOpenA_missing
    jmp *%eax
_g1_forward_DrvOpenA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DrvOpenA_name:
    .asciz "DrvOpenA"
.text
.globl _g1_forward_DrvSendMessage
_g1_forward_DrvSendMessage:
    pushl $_g1_forward_DrvSendMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_DrvSendMessage_missing
    jmp *%eax
_g1_forward_DrvSendMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_DrvSendMessage_name:
    .asciz "DrvSendMessage"
.text
.globl _g1_forward_GetDriverFlags
_g1_forward_GetDriverFlags:
    pushl $_g1_forward_GetDriverFlags_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_GetDriverFlags_missing
    jmp *%eax
_g1_forward_GetDriverFlags_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_GetDriverFlags_name:
    .asciz "GetDriverFlags"
.text
.globl _g1_forward_GetDriverModuleHandle
_g1_forward_GetDriverModuleHandle:
    pushl $_g1_forward_GetDriverModuleHandle_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_GetDriverModuleHandle_missing
    jmp *%eax
_g1_forward_GetDriverModuleHandle_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_GetDriverModuleHandle_name:
    .asciz "GetDriverModuleHandle"
.text
.globl _g1_forward_OpenDriver
_g1_forward_OpenDriver:
    pushl $_g1_forward_OpenDriver_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_OpenDriver_missing
    jmp *%eax
_g1_forward_OpenDriver_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_OpenDriver_name:
    .asciz "OpenDriver"
.text
.globl _g1_forward_OpenDriverA
_g1_forward_OpenDriverA:
    pushl $_g1_forward_OpenDriverA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_OpenDriverA_missing
    jmp *%eax
_g1_forward_OpenDriverA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_OpenDriverA_name:
    .asciz "OpenDriverA"
.text
.globl _g1_forward_PlaySound
_g1_forward_PlaySound:
    pushl $_g1_forward_PlaySound_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_PlaySound_missing
    jmp *%eax
_g1_forward_PlaySound_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_PlaySound_name:
    .asciz "PlaySound"
.text
.globl _g1_forward_PlaySoundA
_g1_forward_PlaySoundA:
    pushl $_g1_forward_PlaySoundA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_PlaySoundA_missing
    jmp *%eax
_g1_forward_PlaySoundA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_PlaySoundA_name:
    .asciz "PlaySoundA"
.text
.globl _g1_forward_PlaySoundW
_g1_forward_PlaySoundW:
    pushl $_g1_forward_PlaySoundW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_PlaySoundW_missing
    jmp *%eax
_g1_forward_PlaySoundW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_PlaySoundW_name:
    .asciz "PlaySoundW"
.text
.globl _g1_forward_SendDriverMessage
_g1_forward_SendDriverMessage:
    pushl $_g1_forward_SendDriverMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_SendDriverMessage_missing
    jmp *%eax
_g1_forward_SendDriverMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_SendDriverMessage_name:
    .asciz "SendDriverMessage"
.text
.globl _g1_forward_auxGetDevCapsA
_g1_forward_auxGetDevCapsA:
    pushl $_g1_forward_auxGetDevCapsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_auxGetDevCapsA_missing
    jmp *%eax
_g1_forward_auxGetDevCapsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_auxGetDevCapsA_name:
    .asciz "auxGetDevCapsA"
.text
.globl _g1_forward_auxGetDevCapsW
_g1_forward_auxGetDevCapsW:
    pushl $_g1_forward_auxGetDevCapsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_auxGetDevCapsW_missing
    jmp *%eax
_g1_forward_auxGetDevCapsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_auxGetDevCapsW_name:
    .asciz "auxGetDevCapsW"
.text
.globl _g1_forward_auxGetNumDevs
_g1_forward_auxGetNumDevs:
    pushl $_g1_forward_auxGetNumDevs_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_auxGetNumDevs_missing
    jmp *%eax
_g1_forward_auxGetNumDevs_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_auxGetNumDevs_name:
    .asciz "auxGetNumDevs"
.text
.globl _g1_forward_auxGetVolume
_g1_forward_auxGetVolume:
    pushl $_g1_forward_auxGetVolume_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_auxGetVolume_missing
    jmp *%eax
_g1_forward_auxGetVolume_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_auxGetVolume_name:
    .asciz "auxGetVolume"
.text
.globl _g1_forward_auxOutMessage
_g1_forward_auxOutMessage:
    pushl $_g1_forward_auxOutMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_auxOutMessage_missing
    jmp *%eax
_g1_forward_auxOutMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_auxOutMessage_name:
    .asciz "auxOutMessage"
.text
.globl _g1_forward_auxSetVolume
_g1_forward_auxSetVolume:
    pushl $_g1_forward_auxSetVolume_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_auxSetVolume_missing
    jmp *%eax
_g1_forward_auxSetVolume_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_auxSetVolume_name:
    .asciz "auxSetVolume"
.text
.globl _g1_forward_joyConfigChanged
_g1_forward_joyConfigChanged:
    pushl $_g1_forward_joyConfigChanged_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyConfigChanged_missing
    jmp *%eax
_g1_forward_joyConfigChanged_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyConfigChanged_name:
    .asciz "joyConfigChanged"
.text
.globl _g1_forward_joyGetDevCapsA
_g1_forward_joyGetDevCapsA:
    pushl $_g1_forward_joyGetDevCapsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyGetDevCapsA_missing
    jmp *%eax
_g1_forward_joyGetDevCapsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyGetDevCapsA_name:
    .asciz "joyGetDevCapsA"
.text
.globl _g1_forward_joyGetDevCapsW
_g1_forward_joyGetDevCapsW:
    pushl $_g1_forward_joyGetDevCapsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyGetDevCapsW_missing
    jmp *%eax
_g1_forward_joyGetDevCapsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyGetDevCapsW_name:
    .asciz "joyGetDevCapsW"
.text
.globl _g1_forward_joyGetNumDevs
_g1_forward_joyGetNumDevs:
    pushl $_g1_forward_joyGetNumDevs_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyGetNumDevs_missing
    jmp *%eax
_g1_forward_joyGetNumDevs_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyGetNumDevs_name:
    .asciz "joyGetNumDevs"
.text
.globl _g1_forward_joyGetPos
_g1_forward_joyGetPos:
    pushl $_g1_forward_joyGetPos_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyGetPos_missing
    jmp *%eax
_g1_forward_joyGetPos_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyGetPos_name:
    .asciz "joyGetPos"
.text
.globl _g1_forward_joyGetPosEx
_g1_forward_joyGetPosEx:
    pushl $_g1_forward_joyGetPosEx_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyGetPosEx_missing
    jmp *%eax
_g1_forward_joyGetPosEx_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyGetPosEx_name:
    .asciz "joyGetPosEx"
.text
.globl _g1_forward_joyGetThreshold
_g1_forward_joyGetThreshold:
    pushl $_g1_forward_joyGetThreshold_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyGetThreshold_missing
    jmp *%eax
_g1_forward_joyGetThreshold_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyGetThreshold_name:
    .asciz "joyGetThreshold"
.text
.globl _g1_forward_joyReleaseCapture
_g1_forward_joyReleaseCapture:
    pushl $_g1_forward_joyReleaseCapture_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joyReleaseCapture_missing
    jmp *%eax
_g1_forward_joyReleaseCapture_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joyReleaseCapture_name:
    .asciz "joyReleaseCapture"
.text
.globl _g1_forward_joySetCapture
_g1_forward_joySetCapture:
    pushl $_g1_forward_joySetCapture_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joySetCapture_missing
    jmp *%eax
_g1_forward_joySetCapture_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joySetCapture_name:
    .asciz "joySetCapture"
.text
.globl _g1_forward_joySetThreshold
_g1_forward_joySetThreshold:
    pushl $_g1_forward_joySetThreshold_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_joySetThreshold_missing
    jmp *%eax
_g1_forward_joySetThreshold_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_joySetThreshold_name:
    .asciz "joySetThreshold"
.text
.globl _g1_forward_mciDriverNotify
_g1_forward_mciDriverNotify:
    pushl $_g1_forward_mciDriverNotify_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciDriverNotify_missing
    jmp *%eax
_g1_forward_mciDriverNotify_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciDriverNotify_name:
    .asciz "mciDriverNotify"
.text
.globl _g1_forward_mciDriverYield
_g1_forward_mciDriverYield:
    pushl $_g1_forward_mciDriverYield_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciDriverYield_missing
    jmp *%eax
_g1_forward_mciDriverYield_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciDriverYield_name:
    .asciz "mciDriverYield"
.text
.globl _g1_forward_mciExecute
_g1_forward_mciExecute:
    pushl $_g1_forward_mciExecute_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciExecute_missing
    jmp *%eax
_g1_forward_mciExecute_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciExecute_name:
    .asciz "mciExecute"
.text
.globl _g1_forward_mciFreeCommandResource
_g1_forward_mciFreeCommandResource:
    pushl $_g1_forward_mciFreeCommandResource_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciFreeCommandResource_missing
    jmp *%eax
_g1_forward_mciFreeCommandResource_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciFreeCommandResource_name:
    .asciz "mciFreeCommandResource"
.text
.globl _g1_forward_mciGetCreatorTask
_g1_forward_mciGetCreatorTask:
    pushl $_g1_forward_mciGetCreatorTask_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetCreatorTask_missing
    jmp *%eax
_g1_forward_mciGetCreatorTask_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetCreatorTask_name:
    .asciz "mciGetCreatorTask"
.text
.globl _g1_forward_mciGetDeviceIDA
_g1_forward_mciGetDeviceIDA:
    pushl $_g1_forward_mciGetDeviceIDA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetDeviceIDA_missing
    jmp *%eax
_g1_forward_mciGetDeviceIDA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetDeviceIDA_name:
    .asciz "mciGetDeviceIDA"
.text
.globl _g1_forward_mciGetDeviceIDFromElementIDA
_g1_forward_mciGetDeviceIDFromElementIDA:
    pushl $_g1_forward_mciGetDeviceIDFromElementIDA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetDeviceIDFromElementIDA_missing
    jmp *%eax
_g1_forward_mciGetDeviceIDFromElementIDA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetDeviceIDFromElementIDA_name:
    .asciz "mciGetDeviceIDFromElementIDA"
.text
.globl _g1_forward_mciGetDeviceIDFromElementIDW
_g1_forward_mciGetDeviceIDFromElementIDW:
    pushl $_g1_forward_mciGetDeviceIDFromElementIDW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetDeviceIDFromElementIDW_missing
    jmp *%eax
_g1_forward_mciGetDeviceIDFromElementIDW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetDeviceIDFromElementIDW_name:
    .asciz "mciGetDeviceIDFromElementIDW"
.text
.globl _g1_forward_mciGetDeviceIDW
_g1_forward_mciGetDeviceIDW:
    pushl $_g1_forward_mciGetDeviceIDW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetDeviceIDW_missing
    jmp *%eax
_g1_forward_mciGetDeviceIDW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetDeviceIDW_name:
    .asciz "mciGetDeviceIDW"
.text
.globl _g1_forward_mciGetDriverData
_g1_forward_mciGetDriverData:
    pushl $_g1_forward_mciGetDriverData_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetDriverData_missing
    jmp *%eax
_g1_forward_mciGetDriverData_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetDriverData_name:
    .asciz "mciGetDriverData"
.text
.globl _g1_forward_mciGetErrorStringA
_g1_forward_mciGetErrorStringA:
    pushl $_g1_forward_mciGetErrorStringA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetErrorStringA_missing
    jmp *%eax
_g1_forward_mciGetErrorStringA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetErrorStringA_name:
    .asciz "mciGetErrorStringA"
.text
.globl _g1_forward_mciGetErrorStringW
_g1_forward_mciGetErrorStringW:
    pushl $_g1_forward_mciGetErrorStringW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetErrorStringW_missing
    jmp *%eax
_g1_forward_mciGetErrorStringW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetErrorStringW_name:
    .asciz "mciGetErrorStringW"
.text
.globl _g1_forward_mciGetYieldProc
_g1_forward_mciGetYieldProc:
    pushl $_g1_forward_mciGetYieldProc_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciGetYieldProc_missing
    jmp *%eax
_g1_forward_mciGetYieldProc_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciGetYieldProc_name:
    .asciz "mciGetYieldProc"
.text
.globl _g1_forward_mciLoadCommandResource
_g1_forward_mciLoadCommandResource:
    pushl $_g1_forward_mciLoadCommandResource_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciLoadCommandResource_missing
    jmp *%eax
_g1_forward_mciLoadCommandResource_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciLoadCommandResource_name:
    .asciz "mciLoadCommandResource"
.text
.globl _g1_forward_mciSendCommandW
_g1_forward_mciSendCommandW:
    pushl $_g1_forward_mciSendCommandW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciSendCommandW_missing
    jmp *%eax
_g1_forward_mciSendCommandW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciSendCommandW_name:
    .asciz "mciSendCommandW"
.text
.globl _g1_forward_mciSendStringA
_g1_forward_mciSendStringA:
    pushl $_g1_forward_mciSendStringA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciSendStringA_missing
    jmp *%eax
_g1_forward_mciSendStringA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciSendStringA_name:
    .asciz "mciSendStringA"
.text
.globl _g1_forward_mciSendStringW
_g1_forward_mciSendStringW:
    pushl $_g1_forward_mciSendStringW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciSendStringW_missing
    jmp *%eax
_g1_forward_mciSendStringW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciSendStringW_name:
    .asciz "mciSendStringW"
.text
.globl _g1_forward_mciSetDriverData
_g1_forward_mciSetDriverData:
    pushl $_g1_forward_mciSetDriverData_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciSetDriverData_missing
    jmp *%eax
_g1_forward_mciSetDriverData_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciSetDriverData_name:
    .asciz "mciSetDriverData"
.text
.globl _g1_forward_mciSetYieldProc
_g1_forward_mciSetYieldProc:
    pushl $_g1_forward_mciSetYieldProc_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mciSetYieldProc_missing
    jmp *%eax
_g1_forward_mciSetYieldProc_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mciSetYieldProc_name:
    .asciz "mciSetYieldProc"
.text
.globl _g1_forward_midiConnect
_g1_forward_midiConnect:
    pushl $_g1_forward_midiConnect_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiConnect_missing
    jmp *%eax
_g1_forward_midiConnect_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiConnect_name:
    .asciz "midiConnect"
.text
.globl _g1_forward_midiDisconnect
_g1_forward_midiDisconnect:
    pushl $_g1_forward_midiDisconnect_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiDisconnect_missing
    jmp *%eax
_g1_forward_midiDisconnect_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiDisconnect_name:
    .asciz "midiDisconnect"
.text
.globl _g1_forward_midiInAddBuffer
_g1_forward_midiInAddBuffer:
    pushl $_g1_forward_midiInAddBuffer_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInAddBuffer_missing
    jmp *%eax
_g1_forward_midiInAddBuffer_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInAddBuffer_name:
    .asciz "midiInAddBuffer"
.text
.globl _g1_forward_midiInClose
_g1_forward_midiInClose:
    pushl $_g1_forward_midiInClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInClose_missing
    jmp *%eax
_g1_forward_midiInClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInClose_name:
    .asciz "midiInClose"
.text
.globl _g1_forward_midiInGetDevCapsA
_g1_forward_midiInGetDevCapsA:
    pushl $_g1_forward_midiInGetDevCapsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInGetDevCapsA_missing
    jmp *%eax
_g1_forward_midiInGetDevCapsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInGetDevCapsA_name:
    .asciz "midiInGetDevCapsA"
.text
.globl _g1_forward_midiInGetDevCapsW
_g1_forward_midiInGetDevCapsW:
    pushl $_g1_forward_midiInGetDevCapsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInGetDevCapsW_missing
    jmp *%eax
_g1_forward_midiInGetDevCapsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInGetDevCapsW_name:
    .asciz "midiInGetDevCapsW"
.text
.globl _g1_forward_midiInGetErrorTextA
_g1_forward_midiInGetErrorTextA:
    pushl $_g1_forward_midiInGetErrorTextA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInGetErrorTextA_missing
    jmp *%eax
_g1_forward_midiInGetErrorTextA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInGetErrorTextA_name:
    .asciz "midiInGetErrorTextA"
.text
.globl _g1_forward_midiInGetErrorTextW
_g1_forward_midiInGetErrorTextW:
    pushl $_g1_forward_midiInGetErrorTextW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInGetErrorTextW_missing
    jmp *%eax
_g1_forward_midiInGetErrorTextW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInGetErrorTextW_name:
    .asciz "midiInGetErrorTextW"
.text
.globl _g1_forward_midiInGetID
_g1_forward_midiInGetID:
    pushl $_g1_forward_midiInGetID_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInGetID_missing
    jmp *%eax
_g1_forward_midiInGetID_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInGetID_name:
    .asciz "midiInGetID"
.text
.globl _g1_forward_midiInGetNumDevs
_g1_forward_midiInGetNumDevs:
    pushl $_g1_forward_midiInGetNumDevs_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInGetNumDevs_missing
    jmp *%eax
_g1_forward_midiInGetNumDevs_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInGetNumDevs_name:
    .asciz "midiInGetNumDevs"
.text
.globl _g1_forward_midiInMessage
_g1_forward_midiInMessage:
    pushl $_g1_forward_midiInMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInMessage_missing
    jmp *%eax
_g1_forward_midiInMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInMessage_name:
    .asciz "midiInMessage"
.text
.globl _g1_forward_midiInOpen
_g1_forward_midiInOpen:
    pushl $_g1_forward_midiInOpen_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInOpen_missing
    jmp *%eax
_g1_forward_midiInOpen_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInOpen_name:
    .asciz "midiInOpen"
.text
.globl _g1_forward_midiInPrepareHeader
_g1_forward_midiInPrepareHeader:
    pushl $_g1_forward_midiInPrepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInPrepareHeader_missing
    jmp *%eax
_g1_forward_midiInPrepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInPrepareHeader_name:
    .asciz "midiInPrepareHeader"
.text
.globl _g1_forward_midiInReset
_g1_forward_midiInReset:
    pushl $_g1_forward_midiInReset_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInReset_missing
    jmp *%eax
_g1_forward_midiInReset_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInReset_name:
    .asciz "midiInReset"
.text
.globl _g1_forward_midiInStart
_g1_forward_midiInStart:
    pushl $_g1_forward_midiInStart_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInStart_missing
    jmp *%eax
_g1_forward_midiInStart_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInStart_name:
    .asciz "midiInStart"
.text
.globl _g1_forward_midiInStop
_g1_forward_midiInStop:
    pushl $_g1_forward_midiInStop_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInStop_missing
    jmp *%eax
_g1_forward_midiInStop_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInStop_name:
    .asciz "midiInStop"
.text
.globl _g1_forward_midiInUnprepareHeader
_g1_forward_midiInUnprepareHeader:
    pushl $_g1_forward_midiInUnprepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiInUnprepareHeader_missing
    jmp *%eax
_g1_forward_midiInUnprepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiInUnprepareHeader_name:
    .asciz "midiInUnprepareHeader"
.text
.globl _g1_forward_midiOutCacheDrumPatches
_g1_forward_midiOutCacheDrumPatches:
    pushl $_g1_forward_midiOutCacheDrumPatches_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutCacheDrumPatches_missing
    jmp *%eax
_g1_forward_midiOutCacheDrumPatches_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutCacheDrumPatches_name:
    .asciz "midiOutCacheDrumPatches"
.text
.globl _g1_forward_midiOutCachePatches
_g1_forward_midiOutCachePatches:
    pushl $_g1_forward_midiOutCachePatches_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutCachePatches_missing
    jmp *%eax
_g1_forward_midiOutCachePatches_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutCachePatches_name:
    .asciz "midiOutCachePatches"
.text
.globl _g1_forward_midiOutClose
_g1_forward_midiOutClose:
    pushl $_g1_forward_midiOutClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutClose_missing
    jmp *%eax
_g1_forward_midiOutClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutClose_name:
    .asciz "midiOutClose"
.text
.globl _g1_forward_midiOutGetDevCapsA
_g1_forward_midiOutGetDevCapsA:
    pushl $_g1_forward_midiOutGetDevCapsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutGetDevCapsA_missing
    jmp *%eax
_g1_forward_midiOutGetDevCapsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutGetDevCapsA_name:
    .asciz "midiOutGetDevCapsA"
.text
.globl _g1_forward_midiOutGetDevCapsW
_g1_forward_midiOutGetDevCapsW:
    pushl $_g1_forward_midiOutGetDevCapsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutGetDevCapsW_missing
    jmp *%eax
_g1_forward_midiOutGetDevCapsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutGetDevCapsW_name:
    .asciz "midiOutGetDevCapsW"
.text
.globl _g1_forward_midiOutGetErrorTextA
_g1_forward_midiOutGetErrorTextA:
    pushl $_g1_forward_midiOutGetErrorTextA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutGetErrorTextA_missing
    jmp *%eax
_g1_forward_midiOutGetErrorTextA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutGetErrorTextA_name:
    .asciz "midiOutGetErrorTextA"
.text
.globl _g1_forward_midiOutGetErrorTextW
_g1_forward_midiOutGetErrorTextW:
    pushl $_g1_forward_midiOutGetErrorTextW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutGetErrorTextW_missing
    jmp *%eax
_g1_forward_midiOutGetErrorTextW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutGetErrorTextW_name:
    .asciz "midiOutGetErrorTextW"
.text
.globl _g1_forward_midiOutGetID
_g1_forward_midiOutGetID:
    pushl $_g1_forward_midiOutGetID_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutGetID_missing
    jmp *%eax
_g1_forward_midiOutGetID_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutGetID_name:
    .asciz "midiOutGetID"
.text
.globl _g1_forward_midiOutGetNumDevs
_g1_forward_midiOutGetNumDevs:
    pushl $_g1_forward_midiOutGetNumDevs_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutGetNumDevs_missing
    jmp *%eax
_g1_forward_midiOutGetNumDevs_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutGetNumDevs_name:
    .asciz "midiOutGetNumDevs"
.text
.globl _g1_forward_midiOutGetVolume
_g1_forward_midiOutGetVolume:
    pushl $_g1_forward_midiOutGetVolume_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutGetVolume_missing
    jmp *%eax
_g1_forward_midiOutGetVolume_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutGetVolume_name:
    .asciz "midiOutGetVolume"
.text
.globl _g1_forward_midiOutLongMsg
_g1_forward_midiOutLongMsg:
    pushl $_g1_forward_midiOutLongMsg_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutLongMsg_missing
    jmp *%eax
_g1_forward_midiOutLongMsg_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutLongMsg_name:
    .asciz "midiOutLongMsg"
.text
.globl _g1_forward_midiOutMessage
_g1_forward_midiOutMessage:
    pushl $_g1_forward_midiOutMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutMessage_missing
    jmp *%eax
_g1_forward_midiOutMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutMessage_name:
    .asciz "midiOutMessage"
.text
.globl _g1_forward_midiOutOpen
_g1_forward_midiOutOpen:
    pushl $_g1_forward_midiOutOpen_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutOpen_missing
    jmp *%eax
_g1_forward_midiOutOpen_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutOpen_name:
    .asciz "midiOutOpen"
.text
.globl _g1_forward_midiOutPrepareHeader
_g1_forward_midiOutPrepareHeader:
    pushl $_g1_forward_midiOutPrepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutPrepareHeader_missing
    jmp *%eax
_g1_forward_midiOutPrepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutPrepareHeader_name:
    .asciz "midiOutPrepareHeader"
.text
.globl _g1_forward_midiOutReset
_g1_forward_midiOutReset:
    pushl $_g1_forward_midiOutReset_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutReset_missing
    jmp *%eax
_g1_forward_midiOutReset_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutReset_name:
    .asciz "midiOutReset"
.text
.globl _g1_forward_midiOutSetVolume
_g1_forward_midiOutSetVolume:
    pushl $_g1_forward_midiOutSetVolume_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutSetVolume_missing
    jmp *%eax
_g1_forward_midiOutSetVolume_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutSetVolume_name:
    .asciz "midiOutSetVolume"
.text
.globl _g1_forward_midiOutShortMsg
_g1_forward_midiOutShortMsg:
    pushl $_g1_forward_midiOutShortMsg_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutShortMsg_missing
    jmp *%eax
_g1_forward_midiOutShortMsg_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutShortMsg_name:
    .asciz "midiOutShortMsg"
.text
.globl _g1_forward_midiOutUnprepareHeader
_g1_forward_midiOutUnprepareHeader:
    pushl $_g1_forward_midiOutUnprepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiOutUnprepareHeader_missing
    jmp *%eax
_g1_forward_midiOutUnprepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiOutUnprepareHeader_name:
    .asciz "midiOutUnprepareHeader"
.text
.globl _g1_forward_midiStreamClose
_g1_forward_midiStreamClose:
    pushl $_g1_forward_midiStreamClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamClose_missing
    jmp *%eax
_g1_forward_midiStreamClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamClose_name:
    .asciz "midiStreamClose"
.text
.globl _g1_forward_midiStreamOpen
_g1_forward_midiStreamOpen:
    pushl $_g1_forward_midiStreamOpen_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamOpen_missing
    jmp *%eax
_g1_forward_midiStreamOpen_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamOpen_name:
    .asciz "midiStreamOpen"
.text
.globl _g1_forward_midiStreamOut
_g1_forward_midiStreamOut:
    pushl $_g1_forward_midiStreamOut_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamOut_missing
    jmp *%eax
_g1_forward_midiStreamOut_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamOut_name:
    .asciz "midiStreamOut"
.text
.globl _g1_forward_midiStreamPause
_g1_forward_midiStreamPause:
    pushl $_g1_forward_midiStreamPause_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamPause_missing
    jmp *%eax
_g1_forward_midiStreamPause_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamPause_name:
    .asciz "midiStreamPause"
.text
.globl _g1_forward_midiStreamPosition
_g1_forward_midiStreamPosition:
    pushl $_g1_forward_midiStreamPosition_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamPosition_missing
    jmp *%eax
_g1_forward_midiStreamPosition_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamPosition_name:
    .asciz "midiStreamPosition"
.text
.globl _g1_forward_midiStreamProperty
_g1_forward_midiStreamProperty:
    pushl $_g1_forward_midiStreamProperty_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamProperty_missing
    jmp *%eax
_g1_forward_midiStreamProperty_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamProperty_name:
    .asciz "midiStreamProperty"
.text
.globl _g1_forward_midiStreamRestart
_g1_forward_midiStreamRestart:
    pushl $_g1_forward_midiStreamRestart_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamRestart_missing
    jmp *%eax
_g1_forward_midiStreamRestart_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamRestart_name:
    .asciz "midiStreamRestart"
.text
.globl _g1_forward_midiStreamStop
_g1_forward_midiStreamStop:
    pushl $_g1_forward_midiStreamStop_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_midiStreamStop_missing
    jmp *%eax
_g1_forward_midiStreamStop_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_midiStreamStop_name:
    .asciz "midiStreamStop"
.text
.globl _g1_forward_mixerClose
_g1_forward_mixerClose:
    pushl $_g1_forward_mixerClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerClose_missing
    jmp *%eax
_g1_forward_mixerClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerClose_name:
    .asciz "mixerClose"
.text
.globl _g1_forward_mixerGetControlDetailsA
_g1_forward_mixerGetControlDetailsA:
    pushl $_g1_forward_mixerGetControlDetailsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetControlDetailsA_missing
    jmp *%eax
_g1_forward_mixerGetControlDetailsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetControlDetailsA_name:
    .asciz "mixerGetControlDetailsA"
.text
.globl _g1_forward_mixerGetControlDetailsW
_g1_forward_mixerGetControlDetailsW:
    pushl $_g1_forward_mixerGetControlDetailsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetControlDetailsW_missing
    jmp *%eax
_g1_forward_mixerGetControlDetailsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetControlDetailsW_name:
    .asciz "mixerGetControlDetailsW"
.text
.globl _g1_forward_mixerGetDevCapsA
_g1_forward_mixerGetDevCapsA:
    pushl $_g1_forward_mixerGetDevCapsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetDevCapsA_missing
    jmp *%eax
_g1_forward_mixerGetDevCapsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetDevCapsA_name:
    .asciz "mixerGetDevCapsA"
.text
.globl _g1_forward_mixerGetDevCapsW
_g1_forward_mixerGetDevCapsW:
    pushl $_g1_forward_mixerGetDevCapsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetDevCapsW_missing
    jmp *%eax
_g1_forward_mixerGetDevCapsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetDevCapsW_name:
    .asciz "mixerGetDevCapsW"
.text
.globl _g1_forward_mixerGetID
_g1_forward_mixerGetID:
    pushl $_g1_forward_mixerGetID_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetID_missing
    jmp *%eax
_g1_forward_mixerGetID_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetID_name:
    .asciz "mixerGetID"
.text
.globl _g1_forward_mixerGetLineControlsA
_g1_forward_mixerGetLineControlsA:
    pushl $_g1_forward_mixerGetLineControlsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetLineControlsA_missing
    jmp *%eax
_g1_forward_mixerGetLineControlsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetLineControlsA_name:
    .asciz "mixerGetLineControlsA"
.text
.globl _g1_forward_mixerGetLineControlsW
_g1_forward_mixerGetLineControlsW:
    pushl $_g1_forward_mixerGetLineControlsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetLineControlsW_missing
    jmp *%eax
_g1_forward_mixerGetLineControlsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetLineControlsW_name:
    .asciz "mixerGetLineControlsW"
.text
.globl _g1_forward_mixerGetLineInfoA
_g1_forward_mixerGetLineInfoA:
    pushl $_g1_forward_mixerGetLineInfoA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetLineInfoA_missing
    jmp *%eax
_g1_forward_mixerGetLineInfoA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetLineInfoA_name:
    .asciz "mixerGetLineInfoA"
.text
.globl _g1_forward_mixerGetLineInfoW
_g1_forward_mixerGetLineInfoW:
    pushl $_g1_forward_mixerGetLineInfoW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetLineInfoW_missing
    jmp *%eax
_g1_forward_mixerGetLineInfoW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetLineInfoW_name:
    .asciz "mixerGetLineInfoW"
.text
.globl _g1_forward_mixerGetNumDevs
_g1_forward_mixerGetNumDevs:
    pushl $_g1_forward_mixerGetNumDevs_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerGetNumDevs_missing
    jmp *%eax
_g1_forward_mixerGetNumDevs_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerGetNumDevs_name:
    .asciz "mixerGetNumDevs"
.text
.globl _g1_forward_mixerMessage
_g1_forward_mixerMessage:
    pushl $_g1_forward_mixerMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerMessage_missing
    jmp *%eax
_g1_forward_mixerMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerMessage_name:
    .asciz "mixerMessage"
.text
.globl _g1_forward_mixerOpen
_g1_forward_mixerOpen:
    pushl $_g1_forward_mixerOpen_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerOpen_missing
    jmp *%eax
_g1_forward_mixerOpen_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerOpen_name:
    .asciz "mixerOpen"
.text
.globl _g1_forward_mixerSetControlDetails
_g1_forward_mixerSetControlDetails:
    pushl $_g1_forward_mixerSetControlDetails_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mixerSetControlDetails_missing
    jmp *%eax
_g1_forward_mixerSetControlDetails_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mixerSetControlDetails_name:
    .asciz "mixerSetControlDetails"
.text
.globl _g1_forward_mmGetCurrentTask
_g1_forward_mmGetCurrentTask:
    pushl $_g1_forward_mmGetCurrentTask_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmGetCurrentTask_missing
    jmp *%eax
_g1_forward_mmGetCurrentTask_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmGetCurrentTask_name:
    .asciz "mmGetCurrentTask"
.text
.globl _g1_forward_mmTaskBlock
_g1_forward_mmTaskBlock:
    pushl $_g1_forward_mmTaskBlock_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmTaskBlock_missing
    jmp *%eax
_g1_forward_mmTaskBlock_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmTaskBlock_name:
    .asciz "mmTaskBlock"
.text
.globl _g1_forward_mmTaskCreate
_g1_forward_mmTaskCreate:
    pushl $_g1_forward_mmTaskCreate_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmTaskCreate_missing
    jmp *%eax
_g1_forward_mmTaskCreate_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmTaskCreate_name:
    .asciz "mmTaskCreate"
.text
.globl _g1_forward_mmTaskSignal
_g1_forward_mmTaskSignal:
    pushl $_g1_forward_mmTaskSignal_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmTaskSignal_missing
    jmp *%eax
_g1_forward_mmTaskSignal_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmTaskSignal_name:
    .asciz "mmTaskSignal"
.text
.globl _g1_forward_mmTaskYield
_g1_forward_mmTaskYield:
    pushl $_g1_forward_mmTaskYield_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmTaskYield_missing
    jmp *%eax
_g1_forward_mmTaskYield_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmTaskYield_name:
    .asciz "mmTaskYield"
.text
.globl _g1_forward_mmioAdvance
_g1_forward_mmioAdvance:
    pushl $_g1_forward_mmioAdvance_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioAdvance_missing
    jmp *%eax
_g1_forward_mmioAdvance_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioAdvance_name:
    .asciz "mmioAdvance"
.text
.globl _g1_forward_mmioAscend
_g1_forward_mmioAscend:
    pushl $_g1_forward_mmioAscend_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioAscend_missing
    jmp *%eax
_g1_forward_mmioAscend_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioAscend_name:
    .asciz "mmioAscend"
.text
.globl _g1_forward_mmioClose
_g1_forward_mmioClose:
    pushl $_g1_forward_mmioClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioClose_missing
    jmp *%eax
_g1_forward_mmioClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioClose_name:
    .asciz "mmioClose"
.text
.globl _g1_forward_mmioCreateChunk
_g1_forward_mmioCreateChunk:
    pushl $_g1_forward_mmioCreateChunk_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioCreateChunk_missing
    jmp *%eax
_g1_forward_mmioCreateChunk_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioCreateChunk_name:
    .asciz "mmioCreateChunk"
.text
.globl _g1_forward_mmioDescend
_g1_forward_mmioDescend:
    pushl $_g1_forward_mmioDescend_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioDescend_missing
    jmp *%eax
_g1_forward_mmioDescend_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioDescend_name:
    .asciz "mmioDescend"
.text
.globl _g1_forward_mmioFlush
_g1_forward_mmioFlush:
    pushl $_g1_forward_mmioFlush_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioFlush_missing
    jmp *%eax
_g1_forward_mmioFlush_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioFlush_name:
    .asciz "mmioFlush"
.text
.globl _g1_forward_mmioGetInfo
_g1_forward_mmioGetInfo:
    pushl $_g1_forward_mmioGetInfo_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioGetInfo_missing
    jmp *%eax
_g1_forward_mmioGetInfo_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioGetInfo_name:
    .asciz "mmioGetInfo"
.text
.globl _g1_forward_mmioInstallIOProc16
_g1_forward_mmioInstallIOProc16:
    pushl $_g1_forward_mmioInstallIOProc16_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioInstallIOProc16_missing
    jmp *%eax
_g1_forward_mmioInstallIOProc16_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioInstallIOProc16_name:
    .asciz "mmioInstallIOProc16"
.text
.globl _g1_forward_mmioInstallIOProcA
_g1_forward_mmioInstallIOProcA:
    pushl $_g1_forward_mmioInstallIOProcA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioInstallIOProcA_missing
    jmp *%eax
_g1_forward_mmioInstallIOProcA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioInstallIOProcA_name:
    .asciz "mmioInstallIOProcA"
.text
.globl _g1_forward_mmioInstallIOProcW
_g1_forward_mmioInstallIOProcW:
    pushl $_g1_forward_mmioInstallIOProcW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioInstallIOProcW_missing
    jmp *%eax
_g1_forward_mmioInstallIOProcW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioInstallIOProcW_name:
    .asciz "mmioInstallIOProcW"
.text
.globl _g1_forward_mmioOpenA
_g1_forward_mmioOpenA:
    pushl $_g1_forward_mmioOpenA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioOpenA_missing
    jmp *%eax
_g1_forward_mmioOpenA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioOpenA_name:
    .asciz "mmioOpenA"
.text
.globl _g1_forward_mmioOpenW
_g1_forward_mmioOpenW:
    pushl $_g1_forward_mmioOpenW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioOpenW_missing
    jmp *%eax
_g1_forward_mmioOpenW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioOpenW_name:
    .asciz "mmioOpenW"
.text
.globl _g1_forward_mmioRead
_g1_forward_mmioRead:
    pushl $_g1_forward_mmioRead_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioRead_missing
    jmp *%eax
_g1_forward_mmioRead_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioRead_name:
    .asciz "mmioRead"
.text
.globl _g1_forward_mmioRenameA
_g1_forward_mmioRenameA:
    pushl $_g1_forward_mmioRenameA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioRenameA_missing
    jmp *%eax
_g1_forward_mmioRenameA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioRenameA_name:
    .asciz "mmioRenameA"
.text
.globl _g1_forward_mmioRenameW
_g1_forward_mmioRenameW:
    pushl $_g1_forward_mmioRenameW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioRenameW_missing
    jmp *%eax
_g1_forward_mmioRenameW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioRenameW_name:
    .asciz "mmioRenameW"
.text
.globl _g1_forward_mmioSeek
_g1_forward_mmioSeek:
    pushl $_g1_forward_mmioSeek_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioSeek_missing
    jmp *%eax
_g1_forward_mmioSeek_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioSeek_name:
    .asciz "mmioSeek"
.text
.globl _g1_forward_mmioSendMessage
_g1_forward_mmioSendMessage:
    pushl $_g1_forward_mmioSendMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioSendMessage_missing
    jmp *%eax
_g1_forward_mmioSendMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioSendMessage_name:
    .asciz "mmioSendMessage"
.text
.globl _g1_forward_mmioSetBuffer
_g1_forward_mmioSetBuffer:
    pushl $_g1_forward_mmioSetBuffer_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioSetBuffer_missing
    jmp *%eax
_g1_forward_mmioSetBuffer_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioSetBuffer_name:
    .asciz "mmioSetBuffer"
.text
.globl _g1_forward_mmioSetInfo
_g1_forward_mmioSetInfo:
    pushl $_g1_forward_mmioSetInfo_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioSetInfo_missing
    jmp *%eax
_g1_forward_mmioSetInfo_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioSetInfo_name:
    .asciz "mmioSetInfo"
.text
.globl _g1_forward_mmioStringToFOURCCA
_g1_forward_mmioStringToFOURCCA:
    pushl $_g1_forward_mmioStringToFOURCCA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioStringToFOURCCA_missing
    jmp *%eax
_g1_forward_mmioStringToFOURCCA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioStringToFOURCCA_name:
    .asciz "mmioStringToFOURCCA"
.text
.globl _g1_forward_mmioStringToFOURCCW
_g1_forward_mmioStringToFOURCCW:
    pushl $_g1_forward_mmioStringToFOURCCW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioStringToFOURCCW_missing
    jmp *%eax
_g1_forward_mmioStringToFOURCCW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioStringToFOURCCW_name:
    .asciz "mmioStringToFOURCCW"
.text
.globl _g1_forward_mmioWrite
_g1_forward_mmioWrite:
    pushl $_g1_forward_mmioWrite_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmioWrite_missing
    jmp *%eax
_g1_forward_mmioWrite_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmioWrite_name:
    .asciz "mmioWrite"
.text
.globl _g1_forward_mmsystemGetVersion
_g1_forward_mmsystemGetVersion:
    pushl $_g1_forward_mmsystemGetVersion_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_mmsystemGetVersion_missing
    jmp *%eax
_g1_forward_mmsystemGetVersion_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_mmsystemGetVersion_name:
    .asciz "mmsystemGetVersion"
.text
.globl _g1_forward_sndPlaySoundA
_g1_forward_sndPlaySoundA:
    pushl $_g1_forward_sndPlaySoundA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_sndPlaySoundA_missing
    jmp *%eax
_g1_forward_sndPlaySoundA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_sndPlaySoundA_name:
    .asciz "sndPlaySoundA"
.text
.globl _g1_forward_sndPlaySoundW
_g1_forward_sndPlaySoundW:
    pushl $_g1_forward_sndPlaySoundW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_sndPlaySoundW_missing
    jmp *%eax
_g1_forward_sndPlaySoundW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_sndPlaySoundW_name:
    .asciz "sndPlaySoundW"
.text
.globl _g1_forward_timeGetDevCaps
_g1_forward_timeGetDevCaps:
    pushl $_g1_forward_timeGetDevCaps_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_timeGetDevCaps_missing
    jmp *%eax
_g1_forward_timeGetDevCaps_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_timeGetDevCaps_name:
    .asciz "timeGetDevCaps"
.text
.globl _g1_forward_timeGetSystemTime
_g1_forward_timeGetSystemTime:
    pushl $_g1_forward_timeGetSystemTime_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_timeGetSystemTime_missing
    jmp *%eax
_g1_forward_timeGetSystemTime_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_timeGetSystemTime_name:
    .asciz "timeGetSystemTime"
.text
.globl _g1_forward_timeKillEvent
_g1_forward_timeKillEvent:
    pushl $_g1_forward_timeKillEvent_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_timeKillEvent_missing
    jmp *%eax
_g1_forward_timeKillEvent_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_timeKillEvent_name:
    .asciz "timeKillEvent"
.text
.globl _g1_forward_timeSetEvent
_g1_forward_timeSetEvent:
    pushl $_g1_forward_timeSetEvent_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_timeSetEvent_missing
    jmp *%eax
_g1_forward_timeSetEvent_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_timeSetEvent_name:
    .asciz "timeSetEvent"
.text
.globl _g1_forward_waveInAddBuffer
_g1_forward_waveInAddBuffer:
    pushl $_g1_forward_waveInAddBuffer_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInAddBuffer_missing
    jmp *%eax
_g1_forward_waveInAddBuffer_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInAddBuffer_name:
    .asciz "waveInAddBuffer"
.text
.globl _g1_forward_waveInClose
_g1_forward_waveInClose:
    pushl $_g1_forward_waveInClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInClose_missing
    jmp *%eax
_g1_forward_waveInClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInClose_name:
    .asciz "waveInClose"
.text
.globl _g1_forward_waveInGetDevCapsA
_g1_forward_waveInGetDevCapsA:
    pushl $_g1_forward_waveInGetDevCapsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInGetDevCapsA_missing
    jmp *%eax
_g1_forward_waveInGetDevCapsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInGetDevCapsA_name:
    .asciz "waveInGetDevCapsA"
.text
.globl _g1_forward_waveInGetDevCapsW
_g1_forward_waveInGetDevCapsW:
    pushl $_g1_forward_waveInGetDevCapsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInGetDevCapsW_missing
    jmp *%eax
_g1_forward_waveInGetDevCapsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInGetDevCapsW_name:
    .asciz "waveInGetDevCapsW"
.text
.globl _g1_forward_waveInGetErrorTextA
_g1_forward_waveInGetErrorTextA:
    pushl $_g1_forward_waveInGetErrorTextA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInGetErrorTextA_missing
    jmp *%eax
_g1_forward_waveInGetErrorTextA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInGetErrorTextA_name:
    .asciz "waveInGetErrorTextA"
.text
.globl _g1_forward_waveInGetErrorTextW
_g1_forward_waveInGetErrorTextW:
    pushl $_g1_forward_waveInGetErrorTextW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInGetErrorTextW_missing
    jmp *%eax
_g1_forward_waveInGetErrorTextW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInGetErrorTextW_name:
    .asciz "waveInGetErrorTextW"
.text
.globl _g1_forward_waveInGetID
_g1_forward_waveInGetID:
    pushl $_g1_forward_waveInGetID_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInGetID_missing
    jmp *%eax
_g1_forward_waveInGetID_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInGetID_name:
    .asciz "waveInGetID"
.text
.globl _g1_forward_waveInGetNumDevs
_g1_forward_waveInGetNumDevs:
    pushl $_g1_forward_waveInGetNumDevs_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInGetNumDevs_missing
    jmp *%eax
_g1_forward_waveInGetNumDevs_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInGetNumDevs_name:
    .asciz "waveInGetNumDevs"
.text
.globl _g1_forward_waveInGetPosition
_g1_forward_waveInGetPosition:
    pushl $_g1_forward_waveInGetPosition_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInGetPosition_missing
    jmp *%eax
_g1_forward_waveInGetPosition_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInGetPosition_name:
    .asciz "waveInGetPosition"
.text
.globl _g1_forward_waveInMessage
_g1_forward_waveInMessage:
    pushl $_g1_forward_waveInMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInMessage_missing
    jmp *%eax
_g1_forward_waveInMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInMessage_name:
    .asciz "waveInMessage"
.text
.globl _g1_forward_waveInOpen
_g1_forward_waveInOpen:
    pushl $_g1_forward_waveInOpen_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInOpen_missing
    jmp *%eax
_g1_forward_waveInOpen_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInOpen_name:
    .asciz "waveInOpen"
.text
.globl _g1_forward_waveInPrepareHeader
_g1_forward_waveInPrepareHeader:
    pushl $_g1_forward_waveInPrepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInPrepareHeader_missing
    jmp *%eax
_g1_forward_waveInPrepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInPrepareHeader_name:
    .asciz "waveInPrepareHeader"
.text
.globl _g1_forward_waveInReset
_g1_forward_waveInReset:
    pushl $_g1_forward_waveInReset_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInReset_missing
    jmp *%eax
_g1_forward_waveInReset_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInReset_name:
    .asciz "waveInReset"
.text
.globl _g1_forward_waveInStart
_g1_forward_waveInStart:
    pushl $_g1_forward_waveInStart_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInStart_missing
    jmp *%eax
_g1_forward_waveInStart_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInStart_name:
    .asciz "waveInStart"
.text
.globl _g1_forward_waveInStop
_g1_forward_waveInStop:
    pushl $_g1_forward_waveInStop_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInStop_missing
    jmp *%eax
_g1_forward_waveInStop_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInStop_name:
    .asciz "waveInStop"
.text
.globl _g1_forward_waveInUnprepareHeader
_g1_forward_waveInUnprepareHeader:
    pushl $_g1_forward_waveInUnprepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveInUnprepareHeader_missing
    jmp *%eax
_g1_forward_waveInUnprepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveInUnprepareHeader_name:
    .asciz "waveInUnprepareHeader"
.text
.globl _g1_forward_waveOutBreakLoop
_g1_forward_waveOutBreakLoop:
    pushl $_g1_forward_waveOutBreakLoop_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutBreakLoop_missing
    jmp *%eax
_g1_forward_waveOutBreakLoop_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutBreakLoop_name:
    .asciz "waveOutBreakLoop"
.text
.globl _g1_forward_waveOutClose
_g1_forward_waveOutClose:
    pushl $_g1_forward_waveOutClose_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutClose_missing
    jmp *%eax
_g1_forward_waveOutClose_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutClose_name:
    .asciz "waveOutClose"
.text
.globl _g1_forward_waveOutGetDevCapsA
_g1_forward_waveOutGetDevCapsA:
    pushl $_g1_forward_waveOutGetDevCapsA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetDevCapsA_missing
    jmp *%eax
_g1_forward_waveOutGetDevCapsA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetDevCapsA_name:
    .asciz "waveOutGetDevCapsA"
.text
.globl _g1_forward_waveOutGetDevCapsW
_g1_forward_waveOutGetDevCapsW:
    pushl $_g1_forward_waveOutGetDevCapsW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetDevCapsW_missing
    jmp *%eax
_g1_forward_waveOutGetDevCapsW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetDevCapsW_name:
    .asciz "waveOutGetDevCapsW"
.text
.globl _g1_forward_waveOutGetErrorTextA
_g1_forward_waveOutGetErrorTextA:
    pushl $_g1_forward_waveOutGetErrorTextA_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetErrorTextA_missing
    jmp *%eax
_g1_forward_waveOutGetErrorTextA_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetErrorTextA_name:
    .asciz "waveOutGetErrorTextA"
.text
.globl _g1_forward_waveOutGetErrorTextW
_g1_forward_waveOutGetErrorTextW:
    pushl $_g1_forward_waveOutGetErrorTextW_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetErrorTextW_missing
    jmp *%eax
_g1_forward_waveOutGetErrorTextW_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetErrorTextW_name:
    .asciz "waveOutGetErrorTextW"
.text
.globl _g1_forward_waveOutGetID
_g1_forward_waveOutGetID:
    pushl $_g1_forward_waveOutGetID_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetID_missing
    jmp *%eax
_g1_forward_waveOutGetID_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetID_name:
    .asciz "waveOutGetID"
.text
.globl _g1_forward_waveOutGetNumDevs
_g1_forward_waveOutGetNumDevs:
    pushl $_g1_forward_waveOutGetNumDevs_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetNumDevs_missing
    jmp *%eax
_g1_forward_waveOutGetNumDevs_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetNumDevs_name:
    .asciz "waveOutGetNumDevs"
.text
.globl _g1_forward_waveOutGetPitch
_g1_forward_waveOutGetPitch:
    pushl $_g1_forward_waveOutGetPitch_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetPitch_missing
    jmp *%eax
_g1_forward_waveOutGetPitch_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetPitch_name:
    .asciz "waveOutGetPitch"
.text
.globl _g1_forward_waveOutGetPlaybackRate
_g1_forward_waveOutGetPlaybackRate:
    pushl $_g1_forward_waveOutGetPlaybackRate_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetPlaybackRate_missing
    jmp *%eax
_g1_forward_waveOutGetPlaybackRate_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetPlaybackRate_name:
    .asciz "waveOutGetPlaybackRate"
.text
.globl _g1_forward_waveOutGetPosition
_g1_forward_waveOutGetPosition:
    pushl $_g1_forward_waveOutGetPosition_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetPosition_missing
    jmp *%eax
_g1_forward_waveOutGetPosition_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetPosition_name:
    .asciz "waveOutGetPosition"
.text
.globl _g1_forward_waveOutGetVolume
_g1_forward_waveOutGetVolume:
    pushl $_g1_forward_waveOutGetVolume_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutGetVolume_missing
    jmp *%eax
_g1_forward_waveOutGetVolume_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutGetVolume_name:
    .asciz "waveOutGetVolume"
.text
.globl _g1_forward_waveOutMessage
_g1_forward_waveOutMessage:
    pushl $_g1_forward_waveOutMessage_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutMessage_missing
    jmp *%eax
_g1_forward_waveOutMessage_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutMessage_name:
    .asciz "waveOutMessage"
.text
.globl _g1_forward_waveOutOpen
_g1_forward_waveOutOpen:
    pushl $_g1_forward_waveOutOpen_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutOpen_missing
    jmp *%eax
_g1_forward_waveOutOpen_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutOpen_name:
    .asciz "waveOutOpen"
.text
.globl _g1_forward_waveOutPause
_g1_forward_waveOutPause:
    pushl $_g1_forward_waveOutPause_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutPause_missing
    jmp *%eax
_g1_forward_waveOutPause_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutPause_name:
    .asciz "waveOutPause"
.text
.globl _g1_forward_waveOutPrepareHeader
_g1_forward_waveOutPrepareHeader:
    pushl $_g1_forward_waveOutPrepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutPrepareHeader_missing
    jmp *%eax
_g1_forward_waveOutPrepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutPrepareHeader_name:
    .asciz "waveOutPrepareHeader"
.text
.globl _g1_forward_waveOutReset
_g1_forward_waveOutReset:
    pushl $_g1_forward_waveOutReset_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutReset_missing
    jmp *%eax
_g1_forward_waveOutReset_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutReset_name:
    .asciz "waveOutReset"
.text
.globl _g1_forward_waveOutRestart
_g1_forward_waveOutRestart:
    pushl $_g1_forward_waveOutRestart_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutRestart_missing
    jmp *%eax
_g1_forward_waveOutRestart_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutRestart_name:
    .asciz "waveOutRestart"
.text
.globl _g1_forward_waveOutSetPitch
_g1_forward_waveOutSetPitch:
    pushl $_g1_forward_waveOutSetPitch_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutSetPitch_missing
    jmp *%eax
_g1_forward_waveOutSetPitch_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutSetPitch_name:
    .asciz "waveOutSetPitch"
.text
.globl _g1_forward_waveOutSetPlaybackRate
_g1_forward_waveOutSetPlaybackRate:
    pushl $_g1_forward_waveOutSetPlaybackRate_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutSetPlaybackRate_missing
    jmp *%eax
_g1_forward_waveOutSetPlaybackRate_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutSetPlaybackRate_name:
    .asciz "waveOutSetPlaybackRate"
.text
.globl _g1_forward_waveOutSetVolume
_g1_forward_waveOutSetVolume:
    pushl $_g1_forward_waveOutSetVolume_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutSetVolume_missing
    jmp *%eax
_g1_forward_waveOutSetVolume_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutSetVolume_name:
    .asciz "waveOutSetVolume"
.text
.globl _g1_forward_waveOutUnprepareHeader
_g1_forward_waveOutUnprepareHeader:
    pushl $_g1_forward_waveOutUnprepareHeader_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutUnprepareHeader_missing
    jmp *%eax
_g1_forward_waveOutUnprepareHeader_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutUnprepareHeader_name:
    .asciz "waveOutUnprepareHeader"
.text
.globl _g1_forward_waveOutWrite
_g1_forward_waveOutWrite:
    pushl $_g1_forward_waveOutWrite_name
    call _g1_winmm_resolve
    addl $4, %esp
    testl %eax, %eax
    jz _g1_forward_waveOutWrite_missing
    jmp *%eax
_g1_forward_waveOutWrite_missing:
    xorl %eax, %eax
    ret
.section .rdata,"dr"
_g1_forward_waveOutWrite_name:
    .asciz "waveOutWrite"
.text
.globl _g1_forward_ordinal_2
_g1_forward_ordinal_2:
    pushl $2
    call _g1_winmm_resolve_ordinal
    addl $4, %esp
    testl %eax, %eax
    jz g1_forward_ordinal_2_missing
    jmp *%eax
g1_forward_ordinal_2_missing:
    xorl %eax, %eax
    ret
.globl _g1_forward_ordinal_3
_g1_forward_ordinal_3:
    pushl $3
    call _g1_winmm_resolve_ordinal
    addl $4, %esp
    testl %eax, %eax
    jz g1_forward_ordinal_3_missing
    jmp *%eax
g1_forward_ordinal_3_missing:
    xorl %eax, %eax
    ret
.globl _g1_forward_ordinal_4
_g1_forward_ordinal_4:
    pushl $4
    call _g1_winmm_resolve_ordinal
    addl $4, %esp
    testl %eax, %eax
    jz g1_forward_ordinal_4_missing
    jmp *%eax
g1_forward_ordinal_4_missing:
    xorl %eax, %eax
    ret

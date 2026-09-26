/* control_executor.h — control plane 실행기 (Win32 전용) */
#ifndef CONTROL_EXECUTOR_H
#define CONTROL_EXECUTOR_H

#include "control_protocol.h"

/* req 의 goal 을 실행하고 res 에 결과를 채운다. */
void control_executor_run(const control_request_t *req, control_result_t *res);

#endif /* CONTROL_EXECUTOR_H */

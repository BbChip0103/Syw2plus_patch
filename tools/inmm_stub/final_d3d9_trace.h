#ifndef FINAL_D3D9_TRACE_H
#define FINAL_D3D9_TRACE_H

/* Opt-in, observation-only D3D9 boundary trace. Disabled unless env=1. */
int final_d3d9_trace_install(void);
void final_d3d9_trace_detach(void);
void final_d3d9_trace_on_direct_draw_create_ex(void);

#endif

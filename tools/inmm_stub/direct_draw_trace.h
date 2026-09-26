#ifndef DIRECT_DRAW_TRACE_H
#define DIRECT_DRAW_TRACE_H

/* Environment-gated, observation-only DirectDraw presentation tracing. */
int g1_direct_draw_trace_install(void);
void g1_direct_draw_trace_detach(void);

#endif /* DIRECT_DRAW_TRACE_H */

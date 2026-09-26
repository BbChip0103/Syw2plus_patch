#ifndef TRACE_RECORD_SERIALIZER_H
#define TRACE_RECORD_SERIALIZER_H

#include <windows.h>

/* Build one JSONL record without a CRT or a formatter-sized output limit. */
BOOL trace_record_serialize(char *line, DWORD capacity, const char *prefix,
                            const char *details, DWORD *length_out);

#endif /* TRACE_RECORD_SERIALIZER_H */

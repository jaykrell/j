/* MPW C does not like this either, but MPW C++, MrC, MrCpp, SC, SCpp, mwccppc, mwc68k, gcc accept. */typedef struct s {int i;} s;s t = { 0 };s const * const u = &t;
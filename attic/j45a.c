typedef struct A { int x08; int x09;} A;#define C(y) case 0##y: return a->y;int B(A * a, int i){switch (i){C(x08)case 9: return a->x09;}}
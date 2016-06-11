#include "j.h"
#include <algorithm>

template <typename T> struct unsignedT;
template <typename T> struct signedT;
template <typename T> struct is_unsigned;
template <typename T> struct is_signed;

#define META_BOOL(x)    {enum{value=x};};
#define META_TRUE       META_BOOL(true)
#define META_FALSE      META_BOOL(false)

#define IS_CHAR_SIGNED ((char)((((char)0) - 1)) < (char)0)

// specialize
template <> struct is_unsigned<char>                META_BOOL(!IS_CHAR_SIGNED)
template <> struct is_unsigned<short>               META_FALSE
template <> struct is_unsigned<int>                 META_FALSE
template <> struct is_unsigned<long>                META_FALSE
template <> struct is_unsigned<__int64>             META_FALSE
template <> struct is_unsigned<signed char>         META_FALSE
template <> struct is_unsigned<unsigned char>       META_TRUE
template <> struct is_unsigned<unsigned short>      META_TRUE
template <> struct is_unsigned<unsigned int>        META_TRUE
template <> struct is_unsigned<unsigned long>       META_TRUE
template <> struct is_unsigned<unsigned __int64>    META_TRUE
template <> struct is_signed<char>                  META_BOOL(IS_CHAR_SIGNED)
template <> struct is_signed<short>                 META_TRUE
template <> struct is_signed<int>                   META_TRUE
template <> struct is_signed<long>                  META_TRUE
template <> struct is_signed<__int64>               META_TRUE
template <> struct is_signed<signed char>           META_TRUE
template <> struct is_signed<unsigned char>         META_FALSE
template <> struct is_signed<unsigned short>        META_FALSE
template <> struct is_signed<unsigned int>          META_FALSE
template <> struct is_signed<unsigned long>         META_FALSE
template <> struct is_signed<unsigned __int64>      META_FALSE

#define META_INT(t) { typedef t T;};
template <> struct unsignedT<char>              META_INT(unsigned char)
template <> struct unsignedT<short>             META_INT(unsigned short)
template <> struct unsignedT<int>               META_INT(unsigned int)
template <> struct unsignedT<long>              META_INT(unsigned long)
template <> struct unsignedT<__int64>           META_INT(unsigned __int64)
template <> struct unsignedT<signed char>       META_INT(unsigned char)
template <> struct unsignedT<unsigned char>     META_INT(unsigned char)
template <> struct unsignedT<unsigned short>    META_INT(unsigned short)
template <> struct unsignedT<unsigned int>      META_INT(unsigned int)
template <> struct unsignedT<unsigned long>     META_INT(unsigned long)
template <> struct unsignedT<unsigned __int64>  META_INT(unsigned __int64)
template <> struct signedT<char>                META_INT(signed char)
template <> struct signedT<short>               META_INT(short)
template <> struct signedT<int>                 META_INT(int)
template <> struct signedT<long>                META_INT(long)
template <> struct signedT<__int64>             META_INT(__int64)
template <> struct signedT<signed char>         META_INT(signed char)
template <> struct signedT<unsigned char>       META_INT(signed char)
template <> struct signedT<unsigned short>      META_INT(short)
template <> struct signedT<unsigned int>        META_INT(int)
template <> struct signedT<unsigned long>       META_INT(long)
template <> struct signedT<unsigned __int64>    META_INT(__int64)

template <typename T, bool> struct int_to_str_t;

template <typename T>
struct int_to_str_t<T, false> // unsigned
{
    static int getlen(T i)
    {
        int len = 1;
        while (i /= 10)
            len += 1;
        return len;
    }

    static int tostr(T i, char* a)
    {
        int len = 0;
        do {
            if (a)
                a[len] = "0123456789"[i % 10];
            len += 1;
        } while (i /= 10);
        // Alternatively to reverse, make two passes, one to get the length,
        // the other to fill in the digits from the end. We are making two passes
        // either way, but this way only does the div/mod once.
        if (a)
            std::reverse(a, a + len);
        return len;
    }
};

template <typename T>
T safe_negate(T i)
// T is a signed type and i is less than 0
// The most negative number cannot be safely negated.
// Add one, reducing the magnitude, then negate, then cast and add one again.
{
    typedef typename unsignedT<T>::T U;
    return 1 + static_cast<U>(-(i + 1));
}

template <typename T>
struct int_to_str_t<T, true> // signed
{
    typedef typename unsignedT<T>::T U1;
    typedef int_to_str_t<U1, false> U2;

    static int getlen(T i)
    {
        return (i < 0) ? (1 + U2::getlen(safe_negate(i)))
                       : U2::getlen(static_cast<U1>(i));
    }

    static int tostr(T i, char* a)
    {
        if (i < 0)
        {
            if (a) *a++ = '-';
            return 1 + U2::tostr(safe_negate(i), a);
        } 
        return U2::tostr(static_cast<U1>(i), a);
    }
};

template <typename T>
char* int_to_str(T i, char* a)
{
    int len = int_to_str_t<T, is_signed<T>::value>::tostr(i, a);
    if (a)
        a[len] = 0;
    return a;
}

template <typename T>
int int_to_str_len(T i)
{
    return int_to_str_t<T, is_signed<T>::value>::getlen(i);
}

unsigned char uc = (unsigned char)-2;
signed char sc = (signed char)-2;
char c = (char)-4;
int i = __LINE__;
short s = __LINE__;
unsigned short us = __LINE__;
__int64 i64 = -__LINE__;

char a[IS_CHAR_SIGNED + 1];

bool is_char_signed()
{
    return IS_CHAR_SIGNED;
}

//parse_guid(char* a, const void* guid, char

void main2()
{
  char buffer[65];

  printf("%s\n", int_to_str(sc, buffer));
  printf("%s\n", int_to_str(c, buffer));
  printf("%s\n", int_to_str(uc, buffer));
  printf("%s\n", int_to_str(i64, buffer));
  
  char a[] = {INIT_HEX16_SEP((UINT64)(size_t)&printf, '`'), 0};
  
  printf("printf is at %s\n", a);
}

int main() { main2(); }

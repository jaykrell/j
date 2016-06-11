#include <typeinfo>
#include <stdio.h>
#include <utility>

template<typename T>
std::enable_if_t<std::is_pod<T>::value>  f(T pod)
{
printf("1\n");
}

template<typename T>
std::enable_if_t<!std::is_pod<T>::value>  f(T non_pod)
{
printf("0\n");
}

struct A { virtual ~A() {}};

int main()
{
printf("%s\n", typeid(f(A())).name());
}

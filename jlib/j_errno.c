char every_file_must_have_at_least_one_symbol_j_errno;

#include "j.h"
#include <errno.h>

long
jk_get_errno(
    void)
{
    long err = errno;
    if (err == 0)
        err = -1;
    else if (err > 0)
        err = -err;
    return err;
}

long
jk_errno(
    void)
{
    return jk_get_errno();
}

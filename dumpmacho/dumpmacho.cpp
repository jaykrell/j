#include <stdio.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <mach-o/loader.h>

int main(int argc, char** argv)
{
    int f = open(argv[1], O_RDONLY);
    long size = lseek(f, 0, SEEK_END);
    void *p = mmap(0, size, PROT_READ,  MAP_PRIVATE, f, 0);
    printf("%d %ld %p\n", f, size, p);

    mach_header const *mh = (mach_header*)p;
    mach_header_64 const *mh64 = (mach_header_64*)p;

    printf("%X %X\n", (int)sizeof(*mh), (int)sizeof(*mh64));

    printf("mh magic:%X cpu:%X.%X type:%X ncmds:%X sizecmds:%X flags:%X\n",
        mh->magic,
        mh->cputype,
        mh->cpusubtype,
        mh->filetype,
        mh->ncmds,
        mh->sizeofcmds,
        mh->flags);

    printf("mh64 magic:%X cpu:%X.%X type:%X ncmds:%X sizecmds:%X flags:%X reserved:%X\n",
        mh64->magic,
        mh64->cputype,
        mh64->cpusubtype,
        mh64->filetype,
        mh64->ncmds,
        mh64->sizeofcmds,
        mh64->flags,
        mh64->reserved);
}

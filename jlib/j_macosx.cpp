char every_file_must_have_at_least_one_symbol_j_macosx;

#include "j.h"

#ifdef J_MACX

/*
include "ApplicationServices/ApplicationServices.h"
include <ApplicationServices/ApplicationServices.h>
*/
#include <ApplicationServices/ApplicationServices.h>
#include "/System/Library/Frameworks/ApplicationServices.framework/Frameworks/CoreGraphics.framework/Headers/CoreGraphics.h"

/* Removed from newer headers. */
J_EXTERN_C_BEGIN

void * CGDisplayBaseAddress ( CGDirectDisplayID display );
size_t CGDisplayBitsPerPixel ( CGDirectDisplayID display );
size_t CGDisplayBytesPerRow ( CGDirectDisplayID display );
size_t CGDisplayBitsPerSample ( CGDirectDisplayID display );
size_t CGDisplaySamplesPerPixel ( CGDirectDisplayID display );
size_t CGDisplayCanSetPalette ( CGDirectDisplayID display );

J_EXTERN_C_END

static
void
jk_macosx_cleanup_display(
    jk_display_t* d)
{
    jk_display_t e = { 0 };

// 10.8.
    //CGPaletteRelease(d->macosx.palette);
    *d = e;
}

#endif

long
jk_macosx_get_main_display(
    jk_display_t *d)
{
    CGDirectDisplayID id = CGMainDisplayID();
    jk_display_t e = { 0 };

    e.opaque_handle = (void*)(size_t)id;
    e.base_address = (unsigned char*)CGDisplayBaseAddress(id);
    e.height = CGDisplayPixelsHigh(id);
    e.width = CGDisplayPixelsWide(id);
    e.bits_per_pixel = CGDisplayBitsPerPixel(id);
    e.bytes_per_row = CGDisplayBytesPerRow(id);

    e.macosx.bits_per_sample = CGDisplayBitsPerSample(id);
    e.macosx.samples_per_pixel = CGDisplaySamplesPerPixel(id);
    e.macosx.can_set_palette = CGDisplayCanSetPalette(id);
    *d = e;
    return 0;
}

#ifndef J_MACX

static
void
jk_macosx_cleanup_display(
    jk_display_t* d)
{
    jk_display_t e = { 0 };
    *d = e;
}

long
jk_macosx_get_main_display(
    jk_display_t* d)
{
    jk_display_t e = { 0 };
    *d = e;
    return -1;
}

void
jk_get_mouse_state(
    jk_mouse_state_t* m)
{
    jk_unused(m);
}

void
jk_get_keyboard_state(
    jk_keyboard_state_t* k)
{
    jk_unused(k);
}

#endif

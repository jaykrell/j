#! /usr/bin/env python

#
# This is a wrapper for building gcc, ld, gas, etc.
# It's goals include:
#   minimizing rebuilds
#   minimizing rebuilds when building multiple toolsets
#   maximizing autoconf's cache
#   build multiple toolsets in one go, or in multiple
#     runs, mostly incrementally, while preserving
#     earlier goals of minimizing compiling anything
#     more than necessary.
#
# It duplicates parts of the topleve configure and makefile,
#   and some of that should be reduced. The plan here is
#   to run the toplevel configure, possibly per package.
#   Per-package can work by using -disable-pkg on all the other
#   packages. We might need per-package in order to vary
#   some options, like -enable-targets=all, at least until gas/ld fixed.
#
# It still builds per-target ld and as, but this appears
#   easy to eliminate.
#
# It still builds per-target gcc/cc1, and this is not necessarily
#   easy to eliminate.
#

import sys
import os
import re
import os.path
from os.path import dirname, isdir, isfile, splitext, getsize, getmtime, islink
import stat
from shutil import copy2

#
# more later
#
RecognizedPlatforms = [
    "i686-pc-cygwin",
    "sparc-sun-solaris2.10",
    "sparc64-sun-solaris2.10",
    "i686-pc-mingw32",
    "i586-pc-msdosdjgpp"
    ]

Prefix0 = "/usr/local"
# Prefix0 = "/usr"


# order is important
Platform_Build = 0
Platform_Host = 1
Platform_Target = 2
# order is important
Platforms = [ Platform_Build, Platform_Host, Platform_Target ]


def Run(Directory, Command):
    if Directory != ".":
        print("cd " + Directory + " && " + Command)
    else:
        print(Command)
    PreviousDirectory = os.getcwd()
    os.chdir(Directory)

    IgnoreError = False
    while (len(Command) != 0) and (Command[0] == "-"):
        IgnoreError = True
        Command = Command[1:]

    ExitCode = 0
    if os.name == "nt":
        Command = "sh -c \"" + Command + "\""
    ExitCode = os.system(Command)
    os.chdir(PreviousDirectory)

    if not IgnoreError:
        if ExitCode != 0:
            print("exiting")
            sys.exit(ExitCode)

    return True

def Configure_default(State, Package, Platform, Build, Host, Target, OutDir, Config):
    return Config


def PatchAfterConfigure_default(State, Package, Platform, Build, Host, Target, OutDir):
    pass


def Report(State, Package, Platform, Build, Host, Target, OutDir):
    PackageName = ""
    if Package:
        PackageName = Package.Name + ":"
    return (
        PackageName + "[" + Build + "/" + Host + "/" + Target + "]:" + ["build", "host", "target"][Platform] + ":"
        + [Build, Host, Target][Platform] + ":"
        + OutDir)

def IsAlreadyBuilt(State, Package, Platform, Build, Host, Target, OutDir):
    for Export in Package.Exports:
        if not FileExists(OutDir  + "/" + Export):
            #print(State, Package.Name + " is not already built because " + OutDir  + "/" + Export + " does not exist")
            return False
    return True


def CreateDirectories(a):
    if not isdir(a):
        if os.name == "nt":
            print("mkdir " + a)
        else:
            print("mkdir -pv -- " + a)
        os.makedirs(a)


def FileExists(a):
    b = a.replace(".lib/", "_lib/")
    for c in[a, a + ".exe", a + ".lnk", b, b + ".exe"]:
        if isfile(c):
            return c
    return False

def MyCopyFile_Incremental(From, To):
#
# Does not handle .lib vs. _lib.
# Don't care currently -- xcopy instead of selective import/export.
# Should be doing recursive linking though.
#
    if From == To:
        return
    AnyCopied = False
    CreatedDir = False
    for Ext in ["", ".exe", ".lnk"]:
        FromExt = From + Ext
        if isfile(FromExt):
            #print(FromExt + " exists")
            ToExt = To + Ext
            if ((not isfile(ToExt))
                    or (getsize(FromExt) != getsize(ToExt))
                    # The times are never actually equal.
                    or ((getmtime(FromExt) - getmtime(ToExt)) > 4.76837158204e-7)
                    or ((getmtime(FromExt) - getmtime(ToExt)) < -4.76837158204e-7)):
                if not CreatedDir:
                    CreateDirectories(dirname(ToExt))
                    CreatedDir = True
                print("copy " + FromExt + " " + ToExt)
                try:
                    copy2(FromExt, ToExt)
                    AnyCopied = True
                except:
                    pass

def Make_default(State, Package, Platform, Build, Host, Target, OutDir):

    if IsAlreadyBuilt(State, Package, Platform, Build, Host, Target, OutDir):
        return

    #print("making " + Package.Name + " in " + OutDir)
    CreateDirectories(OutDir)
    Run(OutDir, "make")

def GetReducedOutputDirectory(State, Package, Platform, Build, Host, Target):
    #
    # Generally, ObjRoot/Host/Target/Build/Package, but that is overkill,
    # and when building for multiple hosts/targets, code gets built redundantly.
    #
    # Roughly speaking:
    #
    # If package is target dependent, then
    #  ObjRoot/Host/Target/Package
    #
    # If package is not target dependent, then
    #  ObjRoot/Host/Package
    #
    # If package runs on target, then
    #  ObjRoot/Target/Package
    #
    # If package runs in build, and build != host and build != target, then
    #  ObjRoot/Build or ObjRoot/build-Build
    #
    # There are no packages that run in the build that are target-dependent.
    # So we never need ObjRoot/Build/Target or ObjRoot/Build/Host/Target.
    #
    Path = ObjRoot
    if Package.HostTarget:
        Path += "/" + Host + "/" + Target
        if Platform == Platform_Target:
            # This is inefficient. It caters to libgcc reaching into gcc, and
            # contributes to building libgcc more than necessary.
            Path += "/" + Target
    else:
        #
        # Voila: This is the point. Just list one platform, that which
        # the code will run on.
        # Path += "/" + [Build, Host, Target][Platform]
        #
        # Some packages configure differently not just per-platform,
        # but if they are build or host or target. libiberty
        # for example. Therefore, we should perhaps build
        # each package up to three times per-platform.
        # Perhaps. There is still savings here. In that
        # if we build multiple targets with the same build and host,
        # we'd only build the build and host variants once each,
        # instead of per-target.
        # e.g.
        #   build=cygwin host=cygwin target=cygwin
        #   build=cygwin host=cygwin target=sparc-solaris
        #   build=cygwin host=cygwin target=sparc64-solaris
        #
        # => maximum 5 libiberties instead of maximum 9 (not counting multilib)
        # => one gmp and mpfr instead of three (same as the previous algorithm)
        #
        Path += "/" + ["build", "host", "target"][Platform] + "/" + [Build, Host, Target][Platform]

    Path += "/" + Package.Name
    return Path

    
class Package():
    def __init__(self):
        self.Host = False
        self.Target = False
        self.Build = False
        self.PatchAfterConfigure = PatchAfterConfigure_default
        self.Install = False

        # really needs like:
        # self.BuildDependencies = [ ]
        # self.HostDependencies = [ ]
        # self.TargetDependencies = [ ]
        self.Dependencies = [ ]
        self.OptionalDependencies = [ ]

        self.Configure = Configure_default
        self.Make = Make_default
        self.Exports = [ ]
        self.OptionalExports = [ ]
        self.HostTarget = False

class BuildStep():
    def __init__(self):
        self.Name = None
        self.Code = None

class SourcePackage():
    def __init__(self):
        self.Extracted = False
        self.Directory = "."
        self.SourceDependencies = [ ]

    
SourceRoot = "/src/gcc"
DistFiles = "/net/distfiles"
ObjRoot = "/obj/1"
CreateDirectories(ObjRoot)


p = SourcePackage()
SourcePackage_gcc = p
p.Name = "gcc"
p.Version = "4.3.2"


p = SourcePackage()
SourcePackage_gmp = p
p.Name = "gmp"
p.Version = "4.2.3"
p.Directory = "gmp"
p.SourceDependencies = [ SourcePackage_gcc ]


p = SourcePackage()
SourcePackage_mpfr = p
p.Name = "mpfr"
p.Version = "2.3.1"
p.Directory = "mpfr"
p.SourceDependencies = [ SourcePackage_gcc ]


p = SourcePackage()
SourcePackage_binutils = p
p.Name = "binutils"
p.Version = "2.18"
p.SourceDependencies = [ SourcePackage_gcc ]


SourcePackages = [
    SourcePackage_binutils,
    SourcePackage_gmp,
    SourcePackage_mpfr,
    SourcePackage_gcc,
    ]


Package_gcc = Package()

Package_libdecnumber = Package()
Package_libcpp = Package()
Package_libstdcpp = Package()
Package_libgcc = Package()
Package_fixincludes = Package()

Package_bfd = Package()
Package_opcodes = Package()
Package_binutils = Package()
Package_gas = Package()
Package_ld = Package()

Package_libiberty = Package()
Package_gmp = Package()
Package_mpfr = Package()

#
# We really need to parse Makefile.def for the dependencies, and run toplevel configure
# for sniffing what languages to build.
#
# OptionalDependencies is really currently just how we get the merged binutils + gcc tree to build.
# We need to sort out build vs. host vs. target.
#
OptionalDependencies = [ Package_binutils, Package_gas, Package_ld ]

#
# Needs work:
#   Exports: if these all exist, the package has been built
#       Should just use our own marker file.
#   OptionalExports: copy all of these
#


def Configure_Force_EnableStatic_DisableShared(Config):
#
# for gmp/mpfr
#
    # first remove all forms of enable/disable shared/static
    for enable in ["enable", "disable"]:
        for shared in ["shared", "static"]:
            for dash in ["-", "--"]:
                Config = Config.replace(" " + dash + enable + shared + " ", " ")
    Config += " -enable-static -disable-shared "
    return Config

def Configure_gmp(State, Package, Platform, Build, Host, Target, OutDir, Config):
    return Configure_Force_EnableStatic_DisableShared(Config)

p = Package_gmp
p.Name = "gmp"
p.OptionalDependencies = OptionalDependencies
p.Exports = [ "libgmp.la", ".libs/libgmp.a", ".libs/libgmp.la" ]
p.SourcePackage = SourcePackage_gmp
p.Host = True
p.Configure = Configure_gmp


p = Package_fixincludes
p.Name = "fixincludes"
p.Dependencies = [ Package_libiberty ]
p.OptionalDependencies = OptionalDependencies
p.Exports = [ "fixinc.sh" ]
p.SourcePackage = SourcePackage_gcc # also binutils
p.Build = True


p = Package_libiberty
p.Name = "libiberty"
p.Dependencies = [ ]
p.OptionalDependencies = OptionalDependencies
p.Exports = [ "libiberty.a" ]
p.SourcePackage = SourcePackage_gcc # also binutils
p.Host = True
p.Target = True
p.Build = True


p = Package_fixincludes
p.Name = "fixincludes"
p.OptionalDependencies = OptionalDependencies
p.Dependencies = [ Package_libiberty ]
p.Exports = [ "fixincl", "fixinc.sh" ]
p.SourcePackage = SourcePackage_gcc
p.Build = True


def Configure_mpfr(State, Package, Platform, Build, Host, Target, OutDir, Config):
    #
    # duplicate the logic of toplevel configure for gmp/mpfr in the combined tree
    #
    gmpsrc = GetSourceDirectory(State, Package_gmp)
    gmpobj = GetReducedOutputDirectory(State, Package_gmp, Platform, Build, Host, Target)
    if isdir(gmpobj) and isdir(gmpsrc):
        Config += " -with-gmp-build=" + gmpobj

    Config = Configure_Force_EnableStatic_DisableShared(Config)

    return Config


p = Package_mpfr
p.Name = "mpfr"
p.OptionalDependencies = OptionalDependencies
p.Dependencies = [ Package_gmp ]
p.Exports = [ "libmpfr.la", ".libs/libmpfr.a", ".libs/libmpfr.la" ]
p.SourcePackage = SourcePackage_mpfr
p.Configure = Configure_mpfr
p.Host = True


def PatchAfterConfigure_bfd(State, Package, Platform, Build, Host, Target, OutDir):
    #
    # Given that we -enable-targets=all, remove the "tic" targets
    # that fail to build.
    #

    if IsAlreadyBuilt(State, Package, Platform, Build, Host, Target, OutDir):
        return

    for FileName in ["Makefile"]:
        FilePath = OutDir + "/" + FileName
        OldLines = file(FilePath).readlines()
        NewLines = [ ]
        Changed = False
        RemovedLines = [ ]
        for OldLine in OldLines:
            NewLine = OldLine
            if NewLine.find("tic") != -1:
                NewLine = OldLine
                for r in [
                        re.compile(x) for x in [
                            "^\\s+(cpu|aout|coff)-tic[0-9]+x?\\.(o|c|lo) \\\\\\n$" ]]:
                    if r.match(NewLine):
                        # print("matched " + NewLine)
                        RemovedLines += "# " + NewLine
                        NewLine = ""
                        Changed = True
                NewLine = NewLine.replace(" $(srcdir)/archures.c ", " archures.c ")
                NewLine = NewLine.replace(" $(srcdir)/targets.c ", " targets.c ")
                Changed = (Changed or (NewLine != OldLine))
            NewLines += NewLine
        if Changed:
            print("patching " + FilePath)
            FileHandle = file(FilePath, "w")
            FileHandle.writelines(NewLines)
            if RemovedLines:
                FileHandle.write("\n# removed lines:\n")
                FileHandle.writelines(RemovedLines)

    #
    # targmatch.h is a build output, and easier to patch it
    # during build than something before (we have no pre-build
    # patches so far, trying to keep it that way)
    #

    Run(OutDir, "make targmatch.h")

    SourceDir = GetSourceDirectory(State, Package)
    for a in ["archures.c", "targets.c"]:
        MyCopyFile_Incremental(SourceDir + "/" + a, OutDir + "/" + a)

    for FileName in ["archures.c", "targets.c", "targmatch.h"]:
        FilePath = OutDir + "/" + FileName
        OldLines = file(FilePath).readlines()
        NewLines = [ ]
        RemovedLines = [ ]
        Changed = False
        for OldLine in OldLines:
            NewLine = OldLine
            if NewLine.find("tic") != -1:
                for r in [
                        re.compile(x) for x in [
                            "^extern const bfd_((target tic.+_vec)|(arch_info_type bfd_tic.+_arch));\n$",
                            "^[ \t]+&(bfd_)?tic.+_(vec|arch),\n$" ]]:
                    if r.match(NewLine):
                        # print("matched " + NewLine)
                        RemovedLines += NewLine
                        NewLine = ""
                        Changed = True
                NewLine = re.sub("#if !defined \(SELECT_VECS\) \|\| defined \(HAVE_tic.+", "#if 0 /* tic patched out */\n", NewLine)
                Changed = (Changed or (NewLine != OldLine))
            NewLines += NewLine
        if Changed:
            print("patching " + FilePath)
            FileHandle = file(FilePath, "w")
            FileHandle.writelines(NewLines)
            if RemovedLines:
                FileHandle.write("\n#if 0 /* removed lines */\n")
                FileHandle.writelines(RemovedLines)
                FileHandle.write("#endif\n")


def PatchAfterConfigure_RemoveLibIconv(State, Package, Platform, Build, Host, Target, OutDir):

    #
    # More variations need testing here likely.
    #

    return

    #
    # also need to patch config.h
    #

    for FileName in ["Makefile"]:
        FilePath = OutDir + "/" + FileName
        OldLines = file(FilePath).readlines()
        NewLines = [ ]
        Changed = False
        for OldLine in OldLines:
            NewLine = OldLine
            if NewLine == "LIBICONV = -liconv\n":
                NewLine = "LIBICONV = \n"
                Changed = True
            NewLines += NewLine
        if Changed:
            print("patching libiconv out of " + FilePath)
            file(FilePath, "w").writelines(NewLines)

def PatchAfterConfigure_binutils(State, Package, Platform, Build, Host, Target, OutDir):
    #
    # -enable-targets=all bites again
    # /src/gcc/binutils/bin2c.c: In function `main":
    # /src/gcc/binutils/bin2c.c:89: warning: implicit declaration of function `_fileno"
    # /src/gcc/binutils/bin2c.c:89: warning: implicit declaration of function `_setmode"
    #

    if IsAlreadyBuilt(State, Package, Platform, Build, Host, Target, OutDir):
        return

    for FileName in ["Makefile"]:
        FilePath = OutDir + "/" + FileName
        OldLines = file(FilePath).readlines()
        NewLines = [ ]
        Changed = False
        for OldLine in OldLines:
            NewLine = OldLine
            if NewLine.startswith("BUILD_MISC = ") or NewLine.startswith("noinst_PROGRAMS = "):
                OldLine = OldLine.replace("\n", " \n")
                NewLine = OldLine
                NewLine = NewLine.replace(" bin2c$(EXEEXT_FOR_BUILD) ", " ")
                Changed = (Changed or (NewLine != OldLine))
            NewLines += NewLine
        if Changed:
            print("patching " + FilePath)
            file(FilePath, "w").writelines(NewLines)


p = Package_bfd
p.Name = "bfd"
p.Exports = [ "bfdver.h", "bfd.h", "bfd_stdint.h", "libbfd.a", "libbfd.la", ".libs/libbfd.a", ".libs/libbfd.la" ]
# p.PatchAfterConfigure = PatchAfterConfigure_bfd
p.SourcePackage = SourcePackage_binutils
p.Host = True


p = Package_opcodes
p.Name = "opcodes"
p.Dependencies = [ Package_bfd ]
p.Exports = [ "libopcodes.a", "libopcodes.la", ".libs/libopcodes.a", ".libs/libopcodes.la" ]
p.SourcePackage = SourcePackage_binutils
p.Host = True


p = Package_binutils
p.Name = "binutils"
p.Dependencies = [ Package_bfd, Package_opcodes ]
# NOTE binutils exports sh scripts AND executables, with
# the same names, except on NT where the names vary (foo vs. foo.exe)
p.Exports = ["addr2line", "ar", "nm-new", "objcopy", "objdump", "ranlib", "size", "strip-new"]
p.Exports += [".libs/" + a for a in p.Exports]
p.OptionalExports = ["coffdump", "cxxfilt", "dlltool", "dllwrap", "nlmconv", "readelf", "srconv", "strings", "sysdump", "sysinfo", "windmc", "windres"]
p.OptionalExports += [".libs/" + a for a in p.OptionalExports]
# p.PatchAfterConfigure = PatchAfterConfigure_binutils
p.SourcePackage = SourcePackage_binutils
p.Host = True
p.Install = True


def Configure_gas(State, Package, Platform, Build, Host, Target, OutDir, Config):
    # temporary?
    Config = Config.replace(" --enable-targets=all ", " ")
    Config = Config.replace(" -enable-targets=all ", " ")
    return Config

def Configure_ld(State, Package, Platform, Build, Host, Target, OutDir, Config):
    # temporary?
    Config = Config.replace(" --enable-targets=all ", " ")
    Config = Config.replace(" -enable-targets=all ", " ")
    return Config

p = Package_gas
p.Name = "gas"
p.SourcePackage = SourcePackage_binutils
p.Dependencies = [ Package_bfd, Package_opcodes ]
p.Exports = [ "as-new"  ]
p.Host = True
p.HostTarget = True # seems like a bug
p.Configure = Configure_gas
p.Install = True


p = Package_ld
p.Name = "ld"
p.SourcePackage = SourcePackage_binutils
p.Dependencies = [ Package_bfd, Package_opcodes ]
p.Exports = ["ld-new"]
p.Host = True
p.Install = True
p.HostTarget = True # just barely..seems like a bug
p.Configure = Configure_ld # temporary?


#
# BUG: This is probably only needed depending on how gcc is configured.
#
p = Package_libdecnumber
p.Name = "libdecnumber"
p.SourcePackage = SourcePackage_gcc
p.Host = True
p.Exports = [ "libdecnumber.a", "gstdint.h"  ]
p.Target = True


p = Package_libcpp
p.Name = "libcpp"
p.SourcePackage = SourcePackage_gcc
p.Exports = [ "libcpp.a"  ]
p.Host = True


p = Package_libgcc
p.Name = "libgcc"
p.SourcePackage = SourcePackage_gcc
p.Exports = [ "libgcc.a"  ]
p.OptionalExports = [ "libgcc_eh.a", "libgcc_s.so"  ]
p.Target = True
p.HostTarget = True # seems like a bug, because it uses gcc's libgcc.mvars.
p.Install = True


def Configure_gcc(State, Package, Platform, Build, Host, Target, OutDir, Config):
#
# We really need to somehow use the toplevel configure, since it knows what
# platforms support what libraries.
#
    #
    # duplicate the logic of toplevel configure for gmp/mpfr in the combined tree
    #
    gmpsrc = GetSourceDirectory(State, Package_gmp)
    gmpobj = GetReducedOutputDirectory(State, Package_gmp, Platform, Build, Host, Target)
    mpfrsrc = GetSourceDirectory(State, Package_mpfr)
    mpfrobj = GetReducedOutputDirectory(State, Package_mpfr, Platform, Build, Host, Target)
    if isdir(gmpobj) and isdir(gmpsrc) and isdir(mpfrobj) and isdir(mpfrsrc):
        gmplibs = " -L" + gmpobj + "/.libs -L" + gmpobj + "/_libs -L" + mpfrobj + "/.libs -L" + mpfrobj + "/_libs -lmpfr -lgmp"
        gmpinc = " -I" + gmpobj + " -I" + gmpsrc + " -I" + mpfrobj + " -I" + mpfrsrc
        Config += " GMPLIBS='" + gmplibs + "' GMPINC='" + gmpinc + "' "

    return Config


p = Package_gcc
p.Name = "gcc"
p.Dependencies = [ Package_gmp, Package_mpfr, Package_libiberty, Package_libdecnumber, Package_libcpp ]
p.OptionalDependencies = OptionalDependencies
p.SourcePackage = SourcePackage_gcc
p.Host = True
p.Exports = [ "xgcc", "cc1"  ]
#
# FUTURE: optionality should be enforced according to target and lenguages
#
p.OptionalExports = [ "gcc-cross", "g++-cross", "libgcov.a", "gnat1", "cc1obj", "cc1objplus", "tree1",
    "cc1obj", "cc1plus", "collect2", "cpp", "f951", "g++", "gcj", "gcov-dump",
    "gcov", "gfortran", "jc1", "jcf-dump", "jvgenmain" ]


p.HostTarget = True
p.Configure = Configure_gcc
p.Install = True


p = Package_libstdcpp
p.Name = "libstdc++-v3"
p.Dependencies = [ Package_libgcc, Package_libiberty ]
p.OptionalDependencies = OptionalDependencies
p.SourcePackage = SourcePackage_gcc
p.Exports = [ "src/libstdc++.la", "src/.libs/libstdc++.a", "src/.libs/libstdc++.la" ]
p.OptionalExports = [ "src/.libs/libstdc++.so", "src/.libs/libstdc++.so.6","src/.libs/libstdc++.so.6.0.10" ]
p.Target = True
p.Languages = [ "c++" ] # not yet handled
p.Install = True


Packages = [
    Package_libiberty,
    Package_fixincludes,
    Package_bfd,
    Package_opcodes,
    Package_binutils,
    Package_gas,
    Package_ld,
    Package_gmp,
    Package_mpfr,
    Package_libdecnumber,
    Package_libcpp,
    Package_gcc,
    Package_libstdcpp,
    Package_libgcc,
    #
    # TBD
    # zlib, libfortran, libgomp, libssp, libjava, libada, gnattools
    #
    ]


def Extract(Directory, File):
    #
    # Make these more portable by running bzcat, gzcat, etc. directly.
    #

    if os.path.isdir(Directory):
        return

    CreateDirectories(Directory)
    for ext in [".tar.gz", ".tgz"]:
        if isfile(File + ext):
            return Run(Directory, "tar --strip-components=1 -zxf " + File + ext)

    for ext in [".tar.bz2", ".tbz"]:
        if isfile(File + ext):
            return Run(Directory, "tar --strip-components=1 -jxf " + File + ext)

    for ext in [".tlz", ".tar.lzma"]:
        if isfile(File + ext):
            return Run(Directory, "tar --strip-components=1 --lzma -xf " + File + ext)

    return Run(Directory, "tar tar --strip-components=1 -xf " + File)

def ExtractSource(Package):
    if not Package.Extracted:
        for p in Package.SourceDependencies:
            ExtractSource(p)
        #
        # FUTURE: Probe for more file names.
        #
        Extract(SourceRoot + "/" + Package.Directory, DistFiles + "/" + Package.Name + "-" + Package.Version)
        Package.Extracted = True


def GetExpectedOutputDirectory(State, Package, Platform, Build, Host, Target):
    Path = ObjRoot + "/" + Host + "/" + Target
    Path += ["/build-" + Build, "", "/" + Target][Platform]
    Path += "/" + Package.Name
    return Path


ConfigCommon = " "
ConfigCommon += " -verbose "
ConfigCommon += " -disable-nls "
ConfigCommon += " -disable-intl "
ConfigCommon += " -disable-po "
ConfigCommon += " -disable-doc "
ConfigCommon += " -with-gnu-as "
ConfigCommon += " -with-gnu-ld "
ConfigCommon += " -disable-bootstrap "
ConfigCommon += " -enable-threads "
ConfigCommon += " -enable-cld "
ConfigCommon += " -enable-version-specific-runtime-libs "
ConfigCommon += " -disable-checking "
ConfigCommon += " -enable-targets=all "
ConfigCommon += " -disable-win32-registry "
ConfigCommon += " -enable-64-bit-bfd "
ConfigCommon += " -disable-multilib "
ConfigCommon += " -disable-libgomp "
ConfigCommon += " -disable-libssp "
ConfigCommon += " -enable-languages=c,c++ "
ConfigCommon += " -enable-static -disable-shared "
ConfigCommon = re.sub("  +", " ", ConfigCommon)


def GetSourceDirectory(State, Package):
    return SourceRoot + "/" + Package.Name


BuildStep_BuildDependencies = BuildStep()
BuildStep_Configure = BuildStep()
BuildStep_PatchAfterConfigure = BuildStep()
BuildStep_Make = BuildStep()
BuildStep_Mirror1 = BuildStep()
BuildStep_Mirror2 = BuildStep()
BuildStep_Install = BuildStep()


def Configure(State, Package, Platform, Build, Host, Target, OutDir):

    if FileExists(OutDir + "/" + "Makefile"):
        #print("already configured " + Package.Name)
        return

    #print("configuring " + Report(State, Package, Platform, Build, Host, Target, OutDir))
    CreateDirectories(OutDir)

    Config = ConfigCommon
    Config += " -host " + [Build, Host, Target][Platform]
    if Package.HostTarget:
        Config += " -target " + Target

    if Host != Target:
        Config += " -with-sysroot " # most directories don't care

    if Host != Build:
        #
        # This is for fixincludes. We don't need it otherwise.
        # Also, there is no default for -with-build-sysroot -- if we aren't
        # explicit, we get --sysroot=yes.
        #
        Config += " -with-build-sysroot=" + Prefix0 + "/" + Platform2 + "/sys-root "

    if Host == Target:
        Config += " -program-transform-name=s,y,y, "
    else: # if (Platform == Platform_Host) && Package.HostTarget:
        Config += " -program-transform-name='s,^," + Target + "-,' "

    Config += " -cache-file " + dirname(OutDir) + "/config.cache "
    Config = Package.Configure(State, Package, Platform, Build, Host, Target, OutDir, Config)

    Run(OutDir, GetSourceDirectory(State, Package) + "/" + "configure " + Config)


def PatchAfterConfigure_RemoveSubDir(State, Package, Platform, Build, Host, Target, OutDir, SubDir):

    for FileName in ["Makefile"]:
        FilePath = OutDir + "/" + FileName
        OldLines = file(FilePath).readlines()
        NewLines = [ ]
        Changed = False
        for OldLine in OldLines:
            NewLine = OldLine
            if NewLine.startswith("SUBDIRS = "):
                OldLine = OldLine.replace("\n", " \n")
                NewLine = OldLine
                NewLine = NewLine.replace(" " + SubDir + " ", " ")
                Changed = (Changed or (NewLine != OldLine))
            NewLines += NewLine
        if Changed:
            print("patching subdir " + SubDir + " out of " + FilePath)
            file(FilePath, "w").writelines(NewLines)


def PatchAfterConfigure(State, Package, Platform, Build, Host, Target, OutDir):

    if IsAlreadyBuilt(State, Package, Platform, Build, Host, Target, OutDir):
        return

    #print("patching " + Report(State, Package, Platform, Build, Host, Target, OutDir))
    SourceDir = GetSourceDirectory(State, Package)
    Package.PatchAfterConfigure(State, Package, Platform, Build, Host, Target, OutDir)

    for SubDir in ["doc", "po", "testsuite", "tests", "demos", "doc", "intl"]:
        PatchAfterConfigure_RemoveSubDir(State, Package, Platform, Build, Host, Target, OutDir, SubDir)

    PatchAfterConfigure_RemoveLibIconv(State, Package, Platform, Build, Host, Target, OutDir)

def Make(State, Package, Platform, Build, Host, Target, OutDir):

    if IsAlreadyBuilt(State, Package, Platform, Build, Host, Target, OutDir):
        return

    Package.Make(State, Package, Platform, Build, Host, Target, OutDir)

    if not IsAlreadyBuilt(State, Package, Platform, Build, Host, Target, OutDir):
        print("error building " + Package.Name)
        sys.exit(1)


def Import(State, Package, Platform, Build, Host, Target, OutDir):
    ReducedOutDir = BuildStep_Make.GetOutputDirectory(State, Package, Platform, Build, Host, Target)
    ExpectedOutDir = OutDir

    if ReducedOutDir == ExpectedOutDir:
        return
    #
    # FUTURE make this portable
    #

    Run(".", "xcopy /fiverdykh " + ExpectedOutDir.replace("/", "\\") + "\\ " + ReducedOutDir.replace("/", "\\") + "\\")


def Mirror(State, Package, Platform, Build, Host, Target):
    Dir1 = GetReducedOutputDirectory(State, Package, Platform, Build, Host, Target)
    Dir2 = GetExpectedOutputDirectory(State, Package, Platform, Build, Host, Target)

    if Dir1 == Dir2:
        return
    #
    # FUTURE make this portable
    #

    Dir1 = Dir1.replace("/", "\\") + "\\ "
    Dir2 = Dir2.replace("/", "\\") + "\\ "
    Run(".", "xcopy /fiverdykh " + Dir1 + Dir2)
    Run(".", "xcopy /fiverdykh " + Dir2 + Dir1)

def Install(State, Package, Platform, Build, Host, Target, OutDir):

    if Package.Install:
        print("installing " + Report(State, Package, Platform, Build, Host, Target, OutDir))
        #return

        # Run(OutDir, "-strip *.exe")
        # Run(OutDir, "-" + [Build, Host, Target][Platform] + "-strip *.exe")
        if Build == Host:
            Run(OutDir, "make install")
        else:
            Run(OutDir, "make install DESTDIR=" + Prefix0 + "/" + Host + "/install")

def ShouldBuild(State, Package, Platform):
    Result = (
        (Platform == Platform_Build and Package.Build)
        or (Platform == Platform_Host and Package.Host)
        or (Platform == Platform_Target and Package.Target))
    # print("ShouldBuild " + Package.Name + " " + str(Platform) + " => " + str(Result))
    return Result

p = BuildStep_BuildDependencies
p.Name = "BuildDependencies"

p = BuildStep_Configure
p.__call__ = Configure
p.Name = "Configure"

p = BuildStep_PatchAfterConfigure
p.__call__ = PatchAfterConfigure
p.Name = "PatchAfterConfigure"

p = BuildStep_Make
p.__call__ = Make
p.Name = "Make"

p = BuildStep_Mirror1
p.__call__ = Mirror
p.Name = "Mirror1"

p = BuildStep_Mirror2
p.__call__ = Mirror
p.Name = "Mirror2"

p = BuildStep_Install
p.__call__ = Install
p.Name = "Install"


BuildSteps = [
    BuildStep_BuildDependencies,
    BuildStep_Mirror1,
    BuildStep_Configure,
    BuildStep_PatchAfterConfigure,
    BuildStep_Make,
    BuildStep_Mirror2,
    BuildStep_Install,
    ]


PackagesToBuild = [ ]
NameToPackage = { }


for Package in Packages:
    NameToPackage[Package.Name] = Package
 
for p in sys.argv:
    if p in NameToPackage:
        PackagesToBuild += [ NameToPackage[p] ]

if not PackagesToBuild:
    PackagesToBuild = Packages

for Package in PackagesToBuild:
    ExtractSource(Package.SourcePackage)

Cygwin = "i686-pc-cygwin"
SparcSolaris = "sparc-sun-solaris2.10"
MsdosDjgpp = "i586-pc-msdosdjgpp"

#
# should sniff this
#
Build = Cygwin

def _BuildUpTo(State, Packages, Platform, Build, Host, Target):

    for Step in BuildSteps:
        StepState = State.get(Step.Name)
        if not StepState:
            State[Step.Name] = dict()

    for plat in Platforms:
        if plat <= Platform:
            for pkg in Packages:
                if ShouldBuild(State, pkg, plat):
                    if isdir(GetSourceDirectory(State, pkg)):
                        for Step in BuildSteps:
                            OutDir = GetExpectedOutputDirectory(State, pkg, plat, Build, Host, Target)
                            StepState = State.get(Step.Name)
                            if StepState.get(OutDir):
                                #print("skipping " + Step.Name + " " + Report(State, pkg, plat, Build, Host, Target, OutDir))
                                continue
                            #print(Step.Name + "'ing " + Report(State, pkg, plat, Build, Host, Target, OutDir))
                            StepState[OutDir] = True
                            # print("> " + Step.Name + " in " + Report(State, pkg, plat, Build, Host, Target, OutDir))
                            Step(State, pkg, plat, Build, Host, Target, OutDir)
                            # print("< " + Step.Name + " in " + Report(State, pkg, plat, Build, Host, Target, OutDir))


def BuildDependencies(State, Package, Platform, Build, Host, Target, OutDir):
    _BuildUpTo(State, Package.OptionalDependencies + Package.Dependencies, Platform, Build, Host, Target)

BuildStep_BuildDependencies.__call__ = BuildDependencies

def BuildTools(State, Host, Target, Packages):

    if Host == None and Target == None:
        Host = Build
        Target = Build

    #print("building " + Build + "/" + Host + "/" + Target)

    for Platform in Platforms:
        _BuildUpTo(State, PackagesToBuild, Platform, Build, Host, Target)

State = dict()

# native

BuildTools(State, Cygwin, Cygwin, PackagesToBuild)

# cross

BuildTools(State, Cygwin, SparcSolaris, PackagesToBuild)

# cross to native

BuildTools(State, SparcSolaris, SparcSolaris, PackagesToBuild)

# cross to cross (back)
# need not yet made sysroot for this
#
# BuildTools(State, SparcSolaris, Cygwin, PackagesToBuild)

# cross

BuildTools(State, Cygwin, MsdosDjgpp, PackagesToBuild)

# cross to native

BuildTools(State, MsdosDjgpp, MsdosDjgpp, PackagesToBuild)

#   File:       t.make#   Target:     t#   Created:    Wednesday, June 2, 2004 03:33:24 AMMAKEFILE        = t.make�MondoBuild�    = {MAKEFILE}  # Make blank to avoid rebuilds when makefile is modifiedObjDir          = :Includes        = Sym-PPC         = -sym offPPCCOptions     = {Includes} {Sym-PPC} ### Source Files ###SrcFiles        =  �				  t.c### Object Files ###ObjFiles-PPC    =  �				  "{ObjDir}t.c.x"### Libraries ###LibFiles-PPC    =  �				  "{SharedLibraries}InterfaceLib" �				  "{SharedLibraries}StdCLib" �				  "{SharedLibraries}MathLib" �				  "{PPCLibraries}StdCRuntime.o" �				  "{PPCLibraries}PPCCRuntime.o" �				  "{PPCLibraries}PPCToolLibs.o"### Default Rules ###.c.x  �  .c  {�MondoBuild�}	{PPCC} {depDir}{default}.c -o {targDir}{default}.c.x {PPCCOptions}### Build Rules ###t  ��  {ObjFiles-PPC} {LibFiles-PPC} {�MondoBuild�}	PPCLink �		-o {Targ} �		{ObjFiles-PPC} �		{LibFiles-PPC} �		{Sym-PPC} �		-mf -d �		-t 'MPST' �		-c 'MPS '### Required Dependencies ###"{ObjDir}t.c.x"  �  t.c### Optional Dependencies ###### Build this target to generate "include file" dependencies. ###Dependencies  �  $OutOfDate	MakeDepend �		-append {MAKEFILE} �		-ignore "{CIncludes}" �		-objdir "{ObjDir}" �		-objext .x �		{Includes} �		{SrcFiles}
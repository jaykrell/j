#   File:       1.make#   Target:     1#   Created:    Wednesday, January 28, 2004 03:58:05 AMMAKEFILE        = 1.make�MondoBuild�    = {MAKEFILE}  # Make blank to avoid rebuilds when makefile is modifiedObjDir          = :Includes        = Sym-68K         = -sym offCOptions        = {Includes} {Sym-68K} -model near ### Source Files ###SrcFiles        =  �				  1.c### Object Files ###ObjFiles-68K    =  �				  "{ObjDir}1.c.o"### Libraries ###LibFiles-68K    =  �				  "{Libraries}Stubs.o" �				  "{Libraries}MathLib.o" �				  "{CLibraries}StdCLib.o" �				  "{Libraries}MacRuntime.o" �				  "{Libraries}IntEnv.o" �				  "{Libraries}ToolLibs.o" �				  "{Libraries}Interface.o"### Default Rules ###.c.o  �  .c  {�MondoBuild�}	{C} {depDir}{default}.c -o {targDir}{default}.c.o {COptions}### Build Rules ###1  ��  {ObjFiles-68K} {LibFiles-68K} {�MondoBuild�}	ILink �		-o {Targ} �		{ObjFiles-68K} �		{LibFiles-68K} �		{Sym-68K} �		-mf -d �		-t 'MPST' �		-c 'MPS ' �		-model near �		-state rewrite �		-compact -pad 0	If "{Sym-68K}" =~ /-sym �[nNuU]�/		ILinkToSYM {Targ}.NJ -mf -sym 3.2 -c 'sade'	End### Required Dependencies ###"{ObjDir}1.c.o"  �  1.c### Optional Dependencies ###### Build this target to generate "include file" dependencies. ###Dependencies  �  $OutOfDate	MakeDepend �		-append {MAKEFILE} �		-ignore "{CIncludes}" �		-objdir "{ObjDir}" �		-objext .o �		{Includes} �		{SrcFiles}
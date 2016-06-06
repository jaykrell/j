bin_PROGRAMS += todo
todo_SOURCES = prog/main.cc

todo_CXXFLAGS=-I$(srcdir)/lib
todo_LDADD = libtodo.a

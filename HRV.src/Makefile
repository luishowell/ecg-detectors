# file: Makefile	Joe Mietus and George Moody	Feb 12 2008
#					Last revised:	Aug 4 2009 (by GBM)
# 'make' description file for the HRV Toolkit

# The WFDB library must be installed before the HRV Toolkit can be compiled.
# Get the WFDB software from http://physionet.org/physiotools/wfdb.shtml .

# The HRV Toolkit will be installed in BINDIR (by default, /usr/bin). If you
# change it, make sure that your PATH includes BINDIR.
BINDIR=/usr/local/bin

# These scripts need a POSIX shell (e.g., sh or bash) in order to run.
SCRIPTS = get_hrv plt_rrs
ALL = filt filtnn hours pwr seconds statnn

all: $(ALL)

# 'make install' copies the HRV toolkit's scripts and binaries to BINDIR.
install:
	cp -p $(SCRIPTS) $(ALL) $(BINDIR)

# 'make bin-tarball' creates a tarball of binaries.
bin-tarball:	all
	mkdir HRV
	cp -p $(SCRIPTS) $(ALL) Usages HRV
	tar cfvz HRV-`arch`-`uname`.tar.gz HRV
	rm -rf HRV

# 'make clean' removes old copies of the executables.
clean:
	rm -f $(ALL)

filt :		filt.c
	$(CC) -O -o $@ filt.c

filtnn :	filtnn.c
	$(CC) -O -o $@ filtnn.c

hours :		hours.c
	$(CC) -O -o $@ hours.c

pwr :		pwr.c
	$(CC) -O -o $@ pwr.c

seconds :	seconds.c
	$(CC) -O -o $@ seconds.c

statnn :	statnn.c
	$(CC) -O -o $@ statnn.c -lm


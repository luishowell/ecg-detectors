/* rrlist.c		Joe Mietus		Apr 1 2011 */

/* rrlist.c		Joe Mietus		Oct 7 2008 */

/*
rrlist :
Usage: rrlist annotator tape [options]
options are :
  [-f start] : begin at time 'start'
  [-t end] : end at time 'end'
  [-l length] : output for duration 'length'
  [-n count] : output 'count' intervals
  [-c] : output time in hh:mm:ss in first column
  [-h] : output time in hours in first column
  [-m] : output time in minutes in first column
  [-s] : output time in seconds in first column
  [-e] : output elapsed time from start
  [-a annotation] :   list only intervals between consecutive annotations
  [-r] : output ratio of specified annotation intervals to RR intervals
  [-H] : high precision intervals (8 significant digits vs 3)
  [-M] : output intervals in msec
*/

#include <stdio.h>
#include <wfdb/wfdb.h>
#include <wfdb/ecgmap.h>


main(argc, argv)	
int argc;
char *argv[];
{
    int i, nrr, nann, cnt, annotation;
    int cflag, hflag, mflag, sflag, eflag, aflag, rflag, hipre, msec;
    long start, end, length;
    double sps;
    struct WFDB_anninfo ai[1];
    struct WFDB_ann annot[2];

    if (argc < 3) {
        usage(argv[0]);
	exit(1);
    }

    nrr = nann = cnt = 0;
    cflag = hflag = mflag = sflag = eflag = aflag = rflag = hipre = msec = 0;
    start = end = length = 0L;

    sps = sampfreq(argv[2]);
    ai[0].name = argv[1];
    ai[0].stat = WFDB_READ;
    if (annopen(argv[2], ai, 1) < 0)
       exit(2);

    for (i=2; ++i < argc && *argv[i] == '-'; ) {
        switch(argv[i][1]) {
	    case 'f': start = strtim(argv[++i]);
	              break;
	    case 't': end = strtim(argv[++i]);
	              break;
	    case 'l': length = strtim(argv[++i]);
	              break;
	    case 'n': cnt = atoi(argv[++i]);
	              break;
	    case 'c': cflag = 1;
	              break;
	    case 'h': hflag = 1;
	              break;
	    case 'm': mflag = 1;
	              break;
	    case 's': sflag = 1;
	              break;
	    case 'e': eflag = 1;
	              break;
	    case 'a': annotation = strann(argv[++i]);
	              aflag = 1;
	              break;
	    case 'r': rflag = 1;
	              break;
	    case 'H': hipre = 1;
	              break;
            case 'M': msec = 1;
	              break;
	    default:  usage(argv[0]);
	              exit(1);
        }
    }
    if (end == 0L && length != 0L)
        end = start + length;

    if (iannsettime(start) < 0)
        exit(2);

    if (!eflag)
        start = 0L;

    while (getann(0, &annot[0]) >= 0) {
        if (isqrs(annot[0].anntyp))
	    nrr++;
        if ((!aflag && isqrs(annot[0].anntyp)) ||
            (aflag && annot[0].anntyp == annotation))
            break;
    }
    nrr--;

    if (cnt != 0) {
	while (getann(0, &annot[1]) >= 0 && (nann < cnt)) {
	    if ((!aflag && isqrs(annot[1].anntyp)) ||
                (aflag && annot[0].anntyp == annotation && 
                 annot[1].anntyp == annotation)) {

		if (cflag)
		    printf("%s ", mstimstr(annot[1].time-start));
		else if (hflag)
		    printf("%.8f ", (annot[1].time-start)/(sps*3600));
		else if (mflag)
		    printf("%.6f ", (annot[1].time-start)/(sps*60));
		else if (sflag)
		    printf("%.3f ", (annot[1].time-start)/sps);
		if (hipre) {
		    if(msec)
		        printf("%.5f %s\n", 1000*(annot[1].time - annot[0].time)/sps,
		                            annstr(annot[1].anntyp));
                    else
		        printf("%.8f %s\n", (annot[1].time - annot[0].time)/sps,
		                          annstr(annot[1].anntyp));
                }
		else {
		    if(msec)
		        printf("%.0f %s\n", 1000*(annot[1].time - annot[0].time)/sps,
		                            annstr(annot[1].anntyp));
                    else
		        printf("%.3f %s\n", (annot[1].time - annot[0].time)/sps,
		                            annstr(annot[1].anntyp));
                }
		nann++;
	    }
            if (isqrs(annot[1].anntyp)) {
		nrr++;
	        annot[0] = annot[1];
	    }
	}
	if (nann < cnt)
	    fprintf(stderr, "%s: insufficient data points (n = %d)\n",
		argv[0], nann);
    }

    else {
	while (getann(0, &annot[1]) >= 0 && 
               (annot[1].time <= end || end == 0L)) {
	    if ((!aflag && isqrs(annot[1].anntyp)) ||
                (aflag && annot[0].anntyp == annotation && 
                 annot[1].anntyp == annotation)) {

		if (cflag)
		    printf("%s ", mstimstr(annot[1].time-start));
		else if (hflag)
		    printf("%.8f ", (annot[1].time-start)/(sps*3600));
		else if (mflag)
		    printf("%.6f ", (annot[1].time-start)/(sps*60));
		else if (sflag)
		    printf("%.3f ", (annot[1].time-start)/sps);
		if (hipre) {
		    if(msec)
		        printf("%.5f %s\n", 1000*(annot[1].time - annot[0].time)/sps,
		                            annstr(annot[1].anntyp));
                    else
		        printf("%.8f %s\n", (annot[1].time - annot[0].time)/sps,
		                          annstr(annot[1].anntyp));
                }
		else {
		    if(msec)
		        printf("%.0f %s\n", 1000*(annot[1].time - annot[0].time)/sps,
		                            annstr(annot[1].anntyp));
                    else
		        printf("%.3f %s\n", (annot[1].time - annot[0].time)/sps,
		                            annstr(annot[1].anntyp));
                }
		nann++;
	    }
            if (isqrs(annot[1].anntyp)) {
		nrr++;
	        annot[0] = annot[1];
	    }
	}
    }
    if (rflag) {
        if (nrr == -1)
            nrr = 0;
        fprintf(stderr, "%s%s : RR = %d : %d = %.3f\n", annstr(annotation),
                annstr(annotation), nann, nrr, nrr==0 ? 0 : (float)nann/nrr);
    }

    exit(0);
}


usage(prog)
char *prog;
{
    fprintf(stderr, "Usage: %s annotator tape [options]\n", prog);
    fprintf(stderr, "options are :\n");
    fprintf(stderr, "  [-f start] : begin at time 'start'\n");
    fprintf(stderr, "  [-t end] : end at time 'end'\n");
    fprintf(stderr, "  [-l length] : output for duration 'length'\n");
    fprintf(stderr, "  [-n count] : output 'count' intervals\n");
    fprintf(stderr, "  [-c] : output time in hh:mm:ss in first column\n");
    fprintf(stderr, "  [-h] : output time in hours in first column\n");
    fprintf(stderr, "  [-m] : output time in minutes in first column\n");
    fprintf(stderr, "  [-s] : output time in seconds in first column\n");
    fprintf(stderr, "  [-e] : output elapsed time from start\n");
    fprintf(stderr, "  [-a annotation] : ");
    fprintf(stderr, "  list only intervals between consecutive annotations\n");
    fprintf(stderr, "  [-r] : ");
    fprintf(stderr, "output ratio of specified annotation intervals ");
    fprintf(stderr, "to RR intervals\n");
    fprintf(stderr, "  [-H] : high precision intervals ");
    fprintf(stderr, "(8 significant digits vs 3)\n");
    fprintf(stderr, "  [-M] : output intervals in msec\n");
}

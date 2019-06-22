/* statnn.c		Joe Mietus		Oct 7 2008 */

/* 
statnn :
Usage: statnn [options]
Reads stdin: time(sec), interval(sec), annotation
and calculates nn interval stats
Outputs nn/rr, avnn, sdnn, sdann,
sdnnindx, rmssd and pnn on stderr
  options :
  [-l len] : window length (default 5:00)
  [-m] : RR intervals in msec
  [-p nndif ...] : nn diffenence for pnn
  [-s] : short term stats
         nn/rr, avnn, sdnn, rmssd and pnn on stderr
  [-L] : print ratio avnn sdnn sdann sdnnindx rmssd pnns on one line
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAXBUF 2400
#define MAXP 10
#define NNDIF 0.05
#define ABS(A) ((A) < 0 ? -(A) : (A))
#define ROFFERR 1e-10

main(argc, argv)
int argc;
char *argv[];
{

    char ann, lastann[2];
    int i, j, len, lflag, mflag, sflag;
    int n, nb, nrr, totrr, nnn, totnn, totnnn, np;
    static int nnx[MAXP];
    double t, lastt, rr, lastrr, start, end, sum, sum2;
    double ratio, avnn, sdnn, sdann, sdnnindx, rmssd, pnnx;
    static double ratbuf[MAXBUF], avbuf[MAXBUF], sdbuf[MAXBUF];
    static double nndif[MAXP];

    /* default 5:00 non-overlapping segments */
    len = 300;

    lflag = mflag = sflag = 0;
    np = 1;
    nndif[0] = NNDIF;

    for (i=0; ++i < argc && *argv[i] == '-'; ) {
        switch(argv[i][1]) {
	    case 'l':  len = strtim(argv[++i]);
	               break;
	    case 'm':  mflag = 1;
	               break;
	    case 'p':  for (np=0; np<MAXP && i+1<argc && *argv[i+1]!='-'; np++)
	                   nndif[np] = atof(argv[++i]);
	               if (np==MAXP)
			   while (i+1<argc && *argv[i+1] != '-')
			       i++;
	               break;
            case 's':  sflag = 1;
	               break;
	    case 'L':  lflag = 1;
	               break;
            default :  usage(argv[0]);
                       exit(1);
        }
    }

    if (len < 60) {
        fprintf(stderr, "%s : len must be 1:00 or greater\n", argv[0]);
        exit(1);
    }

    for (j=0; j<np; j++) {
        if (nndif[j] > 1)
	    nndif[j] /= 1000;
	if (mflag)
	    nndif[j] *= 1000;
    }

    if (scanf("%lf %lf %c", &t, &rr, &ann) != 3) {
        fprintf(stderr, "%s : improperly formatted data\n", argv[0]);
        exit(2);
    }

    i = 0;
    totrr = nrr = 1;
    totnnn = totnn = nnn = 0;
    rmssd = sum = sum2 = 0.0;

    lastt = t;
    lastrr = rr;
    lastann[0] = 'X';
    lastann[1] = ann;
    end = t + len;

    while (scanf("%lf %lf %c", &t, &rr, &ann) == 3) {

	while (t > end+len) {
	    i++;
	    end += len;
	}

	if (t >= end) {
	    if (nnn > 1) {
		ratbuf[i] = (double)nnn/nrr;
	        sdbuf[i] = sqrt((sdbuf[i] - avbuf[i]*avbuf[i]/nnn) / (nnn-1));
	        avbuf[i] /= nnn;
	    }
	    i++;
	    nnn = nrr = 0;
	    end += len;
        }

        nrr++;
	totrr++;

        if (ann == 'N' && lastann[1] == 'N') {
            nnn++;
	    totnn++;
	    avbuf[i] += rr;
	    sum += rr;
	    sdbuf[i] += rr*rr;
	    sum2 += rr*rr;
	    if (lastann[0] == 'N') {
	      totnnn++;
	        rmssd += (rr-lastrr)*(rr-lastrr);

		/* modified 6-15-01 */
		/* equal may not be equal do to round of error !! */
	        /* if (ABS(rr-lastrr) > nndif) { */

		for (j=0; j<np; j++) {
		    if (ABS(rr-lastrr) - nndif[j] > ROFFERR) { 
		        nnx[j]++;
	            }
		}
	    }
	}

	lastrr = rr;
	lastann[0] = lastann[1];
	lastann[1] = ann;

    }

    if (nnn > 1) {
	ratbuf[i] = (double)nnn/nrr;
        sdbuf[i] = sqrt((sdbuf[i] - avbuf[i]*avbuf[i]/nnn) / (nnn-1));
        avbuf[i] /= nnn;
    }

    nb = ++i;

    if (lflag) {
        /* print NN/RR AVNN SDNN SDANN SDNNIDX rMSSD pNNs on one line */
        printf("%g", (double)totnn/totrr);
        printf(" %g", sum/totnn);
        printf(" %g", sqrt((sum2 - sum*sum/totnn) / (totnn-1)));
    }
    else {
        printf("NN/RR = %g\n", (double)totnn/totrr);
        printf("AVNN = %g\n", sum/totnn);
        printf("SDNN = %g\n", sqrt((sum2 - sum*sum/totnn) / (totnn-1)));
    }

    if (!sflag) {
        sum = sum2 = 0;
        for (i=0, n=0; i<nb; i++) {
            if (ratbuf[i] != 0) {
                 n++;
		 sum += avbuf[i];
	         sum2 += avbuf[i]*avbuf[i];
	    }
        }
        if (lflag) {
            if (n > 1)
                printf(" %g", sqrt((sum2 - sum*sum/n) / (n-1)));
            else
                printf(" -");
        }
        else {
            if (n > 1)
                printf("SDANN = %g\n", sqrt((sum2 - sum*sum/n) / (n-1)));
            else
                printf("SDANN = -\n");
        }

        sum = 0;
        for (i=0, n=0; i<nb; i++) {
            if (ratbuf[i] != 0) {
	        n++;
	        sum += sdbuf[i];
	    }
        }
        if (lflag) {
            if (n > 0)
                printf(" %g", sum/n);
            else
                printf(" -");
        }
        else {
            if (n > 0)
                 printf("SDNNIDX = %g\n", sum/n);
            else
                printf("SDNNIDX = -\n");
        }
    }

    if (lflag) {
        printf(" %g", sqrt(rmssd/totnnn));
        for (j=0; j<np; j++)
            printf(" %g", mflag ? 100*(double)nnx[j]/totnnn
                                : (double)nnx[j]/totnnn);
        printf("\n");
    }
    else {
        printf("rMSSD = %g\n", sqrt(rmssd/totnnn));
        for (j=0; j<np; j++) {
            printf("pNN%g = ", mflag ? nndif[j] : nndif[j]*1000);
            printf("%g\n", mflag ? 100*(double)nnx[j]/totnnn
		                 : (double)nnx[j]/totnnn);
        }
    }
}


/* convert string in [[HH:]MM:]SS format to seconds */

strtim(buf)
char *buf;
{
        int x, y, z;

        switch (sscanf(buf, "%d:%d:%d", &x, &y, &z)) {
                case 1: return (x);
                case 2: return (60*x + y);
                case 3: return (3600*x + 60*y + z);
                default: return (-1);
        }
}


usage(prog)
char *prog;
{
        fprintf(stderr, "Usage: %s [options]\n", prog);
        fprintf(stderr, "Reads stdin: time(sec), interval(sec), annotation\n");
        fprintf(stderr, "and calculates nn interval stats\n");
        fprintf(stderr, "Outputs nn/rr, avnn, sdnn, sdann,\n");
        fprintf(stderr, "sdnnindx, rmssd and pnn on stderr\n");
	fprintf(stderr, "  options :\n");
        fprintf(stderr, "  [-l len] : window length (default 5:00)\n");
        fprintf(stderr, "  [-m] : RR intervals in msec\n");
        fprintf(stderr, "  [-p nndif ...] : nn diffenence for pnn\n");
        fprintf(stderr, "  [-s] : short term stats\n");
        fprintf(stderr, "         nn/rr, avnn, sdnn, rmssd and pnn on stderr\n");
	fprintf(stderr, "  [-L] : print ratio avnn sdnn sdann sdnnindx");
	fprintf(stderr, " rmssd pnns on one line\n");
}

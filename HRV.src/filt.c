/* filt.c		Joe Mietus		Apr 1 2011 */

/* filt.c		Joe Mietus		Oct 7 2008 */
/* getline renamed to lineget May 18 2010 */

/*
filt :
Usage: filt filt hwin [options]
  Reads 1 (y) or 2 (x,y) columns from stdin and
  filters outliers by deleting those intervals outside
  of `filt' range of the average within a window
  `hwin' distance on either side of the
  current interval.
  options are :
  [-x min max] : exclude date outside min - max
  [-n] : print ratio of nout to nin
  [-p file] : print excluded points to file
              not including start/end hwin buffer
  excluded points may not be printed in time
  sequential order if -x opption is used
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAXSTR 256
#define MAXWIN 1024

char *prog, line[MAXSTR], tmp[MAXSTR];
int ncols;
static double x[MAXWIN+1], y[MAXWIN+1];
FILE *fp;


main(argc, argv)
int argc;
char * argv[];
{
    int hwin, win, i, j, k, nin, nout;
    int xflag, nflag, pflag;
    double filt, filtmin, filtmax, min, max, mtmp, sum, av;

    xflag = 0;
    nflag = pflag = nin = nout = 0;
    sum = 0.0;
    prog = argv[0];

    if (argc < 3) {
        usage();
	exit(1);
    }

    i = 1;
    if ((filt = atof(argv[i])) <= 0) {
            fprintf(stderr, "%s: filt must be greater than 0\n",
                    prog);
            exit(2);
    }
    if ((hwin = atoi(argv[++i])) <= 0) {
            fprintf(stderr, "%s: hwin must be integer greater than 0\n",
                    prog);
            exit(2);
    }
    if ((win = 2*hwin) > MAXWIN) {
            fprintf(stderr, "%s: max hwin = %d\n", prog, MAXWIN/2);
            exit(2);
    }

    for ( ; ++i < argc && *argv[i] == '-'; ) {
        switch(argv[i][1]) {
            case 'x': if (i+3 > argc) {
	                  usage();
			  exit(1);
		      }
	              min = atof(argv[++i]);
	              max = atof(argv[++i]);
                      if (min > max) {
		          mtmp = min;
			  min = max;
			  max = mtmp;
                      }
	              xflag = 1;
                      break;
            case 'n': nflag = 1;
                      break;
            case 'p': if ((fp = fopen(argv[++i], "w")) == NULL)
	                  fprintf(stderr, "%s : Can't open %s\n",
				  argv[0], argv[i]);
		      else
			  pflag = 1;
                      break;
            default:  usage();
                      exit(1);
        }
    }

    i = 0;
    if (fgets(line, MAXSTR, stdin) == NULL) {
	fprintf(stderr, "%s : no data read\n", prog);
	exit(2);
    }
    if (sscanf(line, "%lf %lf %s", &x[i], &y[i], tmp) == 3) {
	fprintf(stderr, "%s : incorrectly formatted data\n", prog);
	exit(2);
    }
    else if (sscanf(line, "%lf %lf", &x[i], &y[i]) == 2) {
        ncols = 2;
    }
    else if (sscanf(line, "%lf %s", &x[i], tmp) == 2) {
	fprintf(stderr, "%s : incorrectly formatted data\n", prog);
	exit(2);
    }
    else if (sscanf(line, "%lf", &y[i]) == 1) {
        ncols = 1;
	x[0] = 0;
    }
    else {
	fprintf(stderr, "%s : incorrectly formatted data\n", prog);
	exit(2);
    }

    nin++;
    if (pflag)
        fprintline(i);

    i++;
    while (i<=win) {
        if (lineget(i) == EOF) {
	    fprintf(stderr, "%s : insufficient data\n", prog);
            exit(2);
	}
        nin++;

        if (xflag && (y[i]<min || y[i]>max)) {
	    if (pflag)
	        fprintline(i);
        }
        else {
            if (pflag && i<hwin)
	        fprintline(i);
            i++;
        }
    }

    i = 0;
    j = hwin;

    for (i=0; i<=win; i++)
        sum += y[i];
    sum -= y[j];
    av = sum/win;
    sum += y[j] - y[0];

    filtmax = filtmin = filt * av;

    if (y[j] <= av+filtmax && y[j] >= av-filtmin) {
        printline(j);
        nout++;
    }
    else if (pflag)
        fprintline(j);

    i = 0;

    while (lineget(i) != EOF) {
        nin++;

	if (xflag && (y[i]<min || y[i]>max)) {
	    if (pflag)
                fprintline(i);
	}
        else {
            if (++j > win)
                j = 0;

            sum += y[i] - y[j];
	    av = sum/win;
            if (++i > win)
                i = 0;
	    sum += y[j] - y[i];

            filtmax = filtmin = filt * av;

            if (y[j] <= av+filtmax && y[j] >= av-filtmin) {
	        printline(j);
                nout++;
            }
	    else {
	        if (pflag)
                    fprintline(j);
            }
	}
    }

    if (pflag) {
        for (i=0; i<hwin; i++) {
            if (++j > win)
                j = 0;
            fprintline(j);
	}
    }

    if (nflag)
        fprintf(stderr, "nout : nin = %d : %d = %g\n", 
		nout, nin, (double)nout/nin);

    exit(0);
}



lineget(i)
int i;
{
    int j;
    static int n = 1;

    if (fgets(line, MAXSTR, stdin) == NULL)
        return(EOF);

    if (ncols == 1) {
        if ((j = sscanf(line, "%lf %s", &y[i], tmp)) != 1) {
            fprintf(stderr, "%s: incorrectly formatted data : ", prog);
	    fprintf(stderr, "line = %d\n", n+1);
	    exit(2);
        }
	x[i] = n;
    }
    else if (ncols == 2) {
        if ((j = sscanf(line, "%lf %lf %s", &x[i], &y[i], tmp)) != 2) {
            fprintf(stderr, "%s: incorrectly formatted data : ", prog);
	    fprintf(stderr, "line = %d\n", n+1);
	    exit(2);
        }
    }

    n++;

    return(j);
}


printline(i)
int i;
{
    if (ncols == 2)
        printf("%.9g ", x[i]);
    printf("%g\n", y[i]);
}


fprintline(i)
int i;
{
    if (ncols == 2)
        fprintf(fp, "%.9g ", x[i]);
    fprintf(fp, "%g\n", y[i]);
}


usage()
{
    fprintf(stderr, "Usage: %s filt hwin [options]\n", prog);
    fprintf(stderr, " Reads 1 (y) or 2 (x,y) columns from stdin and\n");
    fprintf(stderr, " filters outliers by deleting those intervals outside\n");
    fprintf(stderr, " of `filt' range of the average within a window\n");
    fprintf(stderr, " `hwin' distance on either side of the\n");
    fprintf(stderr, " current interval.\n\n");
    fprintf(stderr, " options are :\n");
    fprintf(stderr, " [-x min max] : exclude date outside min - max\n");
    fprintf(stderr, " [-n] : print ratio of nout to nin\n");
    fprintf(stderr, " [-p file] : print excluded points to file\n");
    fprintf(stderr, "             not including start/end hwin buffer\n");
    fprintf(stderr, " excluded points may not be printed in time\n");
    fprintf(stderr, " sequential order if -x opption is used\n");
}

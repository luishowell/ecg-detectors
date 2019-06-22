/* filtnn.c		Joe Mietus		Apr 1 2011 */

/* filtnn.c		Joe Mietus		Oct 7 2008 */
/* getline renamed to lineget May 18 2010 */

/*
filtnn :
Usage: filtnn [options] filt hwin
  Reads 2 (y,ann) or 3 (x,y,ann) columns from stdin and
  filters NN intervals by marking intervals not within `filt'
  range from the average of intervals
  within a window `hwin' distance on either side of
  current interval.
  NEED TO DO A `sort -n' ON FILTERED SERIES TO RESTORE TIME ORDER
  options are :
  [-n] : print ratio of nnout to nnin to rrin
  [-x min max] : exclude date outside min - max
  [-p] : print excluded data at start/end of hwin buffer
  [-C ann] : change annotation of excluded points to ann (default: X)
*/

#include <stdio.h>
#include <stdlib.h>

#define MAXSTR 256
#define MAXWIN 1024

char *prog, line[MAXSTR], tmp[MAXSTR], ann[MAXWIN+1];
int ncols;
static double t, x[MAXWIN+1], y[MAXWIN+1];
FILE *fp;


main(argc, argv)
int argc;
char * argv[];
{
    char c, lastann;
    int hwin, win, i, j, k, cflag, xflag, pflag, nflag, rrin, nnin, nnout;
    double filt, filtmin, filtmax, min, max, mtmp, sum, av;

    c = 'X';
    cflag = xflag = pflag = nflag = rrin = nnin = nnout = 0;
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
            case 'n': nflag = 1;
                      break;
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
            case 'p': pflag = 1;
                      break;
            case 'C': cflag = 1;
	              c = *argv[++i];
                      break;
            default:  usage();
                      exit(1);
        }
    }

    filtmax = 1.0 + filt;
    filtmin = 1.0 - filt;

    i = 0;
    if (fgets(line, MAXSTR, stdin) == NULL) {
	fprintf(stderr, "%s : no data read\n", prog);
	exit(2);
    }
    if (sscanf(line, "%lf %lf %c %s", &x[i], &y[i], &ann[i], tmp) == 4) {
	fprintf(stderr, "%s : incorrectly formatted data\n", prog);
	exit(2);
    }
    else if (sscanf(line, "%lf %lf %c", &x[i], &y[i], &ann[i]) == 3) {
        ncols = 3;
    }
    else if (sscanf(line, "%lf %c %s", &y[i], &ann[i], tmp) == 3) {
	fprintf(stderr, "%s : incorrectly formatted data\n", prog);
	exit(2);
    }
    else if (sscanf(line, "%lf %c", &y[i], &ann[i]) == 2) {
        x[i] = t = y[i];
        ncols = 2;
    }
    else {
	fprintf(stderr, "%s : incorrectly formatted data\n", prog);
	exit(2);
    }

    rrin++;
    lastann = ann[i];
    if (pflag)
	cprintline(i, c);

    while (i<=win) {
        if (lineget(i) == EOF) {
	    fprintf(stderr, "%s : insufficient data\n", prog);
            exit(2);
	}
        rrin++;

	if (ann[i] != 'N' || lastann != 'N') {
	    if (pflag)
	        printline(i);
            lastann = ann[i];
	}
        else if (xflag && (y[i]<min || y[i]>max)) {
	    if (pflag)
	        cprintline(i, c);
            lastann = ann[i];
        }
        else {
	    if (pflag && i<hwin)
	       cprintline(i, c);
	    nnin++;
            lastann = ann[i];
	    i++;
	}
    }

    j = hwin;

    for (i=0; i<=win; i++)
        sum += y[i];
    sum -= y[j];
    av = sum/win;
    sum += y[j] - y[0];

    if (y[j] <= filtmax*av && y[j] >= filtmin*av)
        nnout++;
    else
        ann[j] = c;
    printline(j);

    i = 0;

    while (lineget(i) != EOF) {
        rrin++;

	if (ann[i] != 'N' || lastann != 'N') {
	    printline(i);
            lastann = ann[i];
	}
        else if (xflag && (y[i]<min || y[i]>max)) {
	    cprintline(i, c);
            lastann = ann[i];
        }
        else {
	    nnin++;
	    if (++j > win)
	        j = 0;

	    sum += y[i];
	    sum -= y[j];
	    av = sum/win;
	    lastann = ann[i];
	    if (++i > win)
		i = 0;
	    sum += y[j] - y[i];

	    if (y[j] <= filtmax*av && y[j] >= filtmin*av) {
	        printline(j);
	        nnout++;
	    }
	    else
	        cprintline(j, c);
	}
    }

    if (pflag)
        for (i=0; i<hwin; i++) {
            if (++j > win)
                j = 0;
            cprintline(j, c);
        }

    if (nflag)
        fprintf(stderr, "nnout : nnin : rrin = %d : %d : %d = %g : %g = %g\n", 
		nnout, nnin, rrin, (double)nnout/nnin, (double)nnin/rrin,
		(double)nnout/rrin);

    exit(0);
}



lineget(i)
int i;
{
    int j;
    static int n = 2;

    if (fgets(line, MAXSTR, stdin) == NULL)
        return(EOF);

    if (ncols == 2) {
        if ((j = sscanf(line, "%lf %c %s", &y[i], &ann[i], tmp)) != 2) {
            fprintf(stderr, "%s: incorrectly formatted data : ", prog);
	    fprintf(stderr, "line = %d\n", n);
	    exit(2);
        }
	t += y[i];
	x[i] = t;
    }
    else if (ncols == 3) {
        if ((j = sscanf(line, "%lf %lf %c %s", &x[i], &y[i], &ann[i], tmp)) != 3) {
            fprintf(stderr, "%s: incorrectly formatted data : ", prog);
	    fprintf(stderr, "line = %d\n", n);
	    exit(2);
        }
    }

    n++;

    return(j);
}


printline(i)
int i;
{
    if (ncols == 3)
        printf("%.9g ", x[i]);
    printf("%.8g %c\n", y[i], ann[i]);
}


cprintline(i, c)
int i;
char c;
{
    if (ncols == 3)
        printf("%.9g ", x[i]);
    printf("%.8g %c\n", y[i], c);
}


usage()
{
    fprintf(stderr, "Usage: %s [options] filt hwin\n", prog);
    fprintf(stderr, " Reads 2 (y,ann) or 3 (x,y,ann) columns from stdin and\n");
    fprintf(stderr, " filters NN intervals by marking intervals not within `filt'\n");
    fprintf(stderr, " range from the average of intervals\n");
    fprintf(stderr, " within a window `hwin' distance on either side of\n");
    fprintf(stderr, " current interval.\n");
    fprintf(stderr, " NEED TO DO A `sort -n' ON FILTERED SERIES");
    fprintf(stderr, " TO RESTORE TIME ORDER\n\n");
    fprintf(stderr, " options are :\n");
    fprintf(stderr, " [-n] : print ratio of nnout to nnin to rrin\n");
    fprintf(stderr, " [-x min max] : exclude date outside min - max\n");
    fprintf(stderr, " [-p] : print excluded data at start/end of hwin buffer\n");
    fprintf(stderr, " [-C ann] : change annotation of excluded points to ann");
    fprintf(stderr, " (default: X)\n");
}

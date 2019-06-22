/* pwr.c		Joe Mietus		Oct 7 2008 */

/*
pwr :
Usage: pwr [-r] [-L] lo1 hi1 ... [lo10 hi10]
  Calculate total (and relative) power in fft between lo and hi.
  options :
  [-r] : print ratio of powers to total
  [-L] : print powers on one line
*/


#include <stdio.h>
#include <stdlib.h>

#define MAXBANDS 10

main(argc, argv)
int argc;
char *argv[];
{

    int i, n, nbands, rflag, lflag;
    double lo[MAXBANDS], hi[MAXBANDS], pr[MAXBANDS], tot;
    double freq[2], mag[2], hbin[2], pwr;


    if (argc < 3) {
        usage(argv[0]);
        exit(1);
    }

    rflag = lflag = 0;
    for (i=1, argc--; argv[i][0] == '-'; i++, argc--) {
        switch(argv[i][1]) {
        case 'r': rflag = 1;
                  break;
        case 'L': lflag = 1;
                  break;
        default: usage(argv[0]);
                 exit(1);
        }
    }
        
    if (argc % 2 != 0) {
        usage(argv[0]);
        exit(1);
    }

    if ((nbands = argc/2) > 10) {
        fprintf(stderr, "%s : max power bands = MAXBANDS\n");
        exit(1);
    }

    for (n=0; n<nbands; n++) {
        lo[n] = atof(argv[i++]);
        hi[n] = atof(argv[i++]);
        pr[n] = 0.0;
    }

    tot = 0.0;

    if (scanf("%lf%lf", &freq[0], &mag[0]) != 2)
        exit(2);
    if (scanf("%lf%lf", &freq[1], &mag[1]) != 2)
        exit(2);

    pwr = mag[0]*mag[0];
    tot += pwr;
    for (n=0; n<nbands; n++) {
        if (freq[0] >= lo[n] && freq[0] <= hi[n])
            pr[n] += pwr;
    }
    freq[0] = freq[1];
    mag[0] = mag[1];

    while (scanf("%lf%lf", &freq[1], &mag[1]) == 2) {
        pwr = mag[0]*mag[0];
        tot += pwr;
        for (n=0; n<nbands; n++) {
            if (freq[0] >= lo[n] && freq[0] <= hi[n])
                pr[n] += pwr;
        }
        freq[0] = freq[1];
	mag[0] = mag[1];
    }

    pwr = mag[0]*mag[0];
    tot += pwr;
    for (n=0; n<nbands; n++) {
        if (freq[0] >= lo[n] && freq[0] <= hi[n])
        pr[n] += pwr;
    }

    if (lflag) {
        printf("%g ", tot);
        for (n=0; n<nbands; n++) {
            printf("%g ", pr[n]);
            if (rflag)
                printf("(%.3f) ", pr[n]/tot);
        }
        printf("\n");
    }
    else {
        printf("Total = %g\n", tot);
        for (n=0; n<nbands; n++) {
            printf("%g - %g = %g", lo[n], hi[n], pr[n]);
            if (rflag)
                printf(" (%.3f)\n", pr[n]/tot);
            else
                printf("\n");
        }
    }
}


usage(prog)
char *prog;
{
    fprintf(stderr, "Usage: %s [-r] [-L] lo1 hi1 ... [lo10 hi10]\n", prog);
    fprintf(stderr, " Calculate total (and relative) power");
    fprintf(stderr, " in fft between lo and hi.\n");
    fprintf(stderr, " options :\n");
    fprintf(stderr, " [-r] : print ratio of powers to total\n");
    fprintf(stderr, " [-L] : print powers on one line\n");

}

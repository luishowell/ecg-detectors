/* hours.c		Joe Mietus		Oct 7 2008 */

/*
hours :
Usage: hours seconds | -
  Convert seconds to hh:mm:ss.
  `-' to read stdin
*/

#include <stdio.h>
#include <stdlib.h>

main(argc, argv)
int argc;
char *argv[];
{
    long sec, atol();
    char *timstr();

    if (argc < 2) {
	usage(argv[0]);  
	exit(1);
    }

    if (*argv[1] == '-')
        switch (argv[1][1]) {
	    case '\0' : while (scanf("%ld", &sec) == 1)
	                    printf("%s\n", timstr(sec));
		        exit(0);
	    default : usage(argv[0]);
		      exit(1);
	}
    else
	printf("%s\n", timstr(atol(argv[1])));
}


char *timstr(time)	/* convert seconds to [hh:]mm:ss */
long time;
{
    int hours, minutes, seconds;
    static char buf[9];

    hours = time / 3600L; time -= (long)hours * 3600;
    minutes = time / 60;
    seconds = time - minutes * 60;
    sprintf(buf, "%02d:%02d:%02d", hours, minutes, seconds);
    return (buf);
}


usage(prog)
char *prog;
{
    fprintf(stderr, "Usage: %s seconds | -\n", prog);
    fprintf(stderr, " Convert seconds to hh:mm:ss.\n");
    fprintf(stderr, " `-' to read stdin\n");
}

/* seconds.c		Joe Mietus		Oct 7 2008 */

/*
seconds :
Usage: seconds [[hh]:mm]:ss | -
  Convert string in [[hh:]mm:]ss to seconds
  `-' to read stdin
*/

#include <stdio.h>
#include <stdlib.h>

main(argc, argv)
int argc;
char *argv[];
{
    char *time[12];
    long strtim();

    if (argc < 2) {
        usage(argv[0]);
	exit(1);
    }

    if (*argv[1] == '-')
        switch (argv[1][1]) {
	    case '\0' : while (scanf("%s", time) == 1)
	                    printf("%ld\n", strtim(time));
		        exit(0);
	    default : usage(argv[0]);
		      exit(1);
	}
    else
        printf("%ld\n", strtim(argv[1]));
}


long strtim(buf)	/* convert string in [[hh:]mm:]ss to seconds */
char *buf;
{
	long x, y, z;

	switch (sscanf(buf, "%ld:%ld:%ld", &x, &y, &z)) {
		case 1: return (x);
		case 2: return (60*x + y);
		case 3: return (3600*x + 60*y + z);
		default: return (-1L);
	}
}


usage(prog)
char *prog;
{
    fprintf(stderr, "Usage: %s [[hh]:mm]:ss | -\n", prog);
    fprintf(stderr, " Convert string in [[hh:]mm:]ss to seconds\n");
    fprintf(stderr, " `-' to read stdin\n");
}

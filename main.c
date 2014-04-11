#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

/* The goal of this program is to pipe the output of "quodlibet 
 * --print-queue" to a usable queue file in case of awful 
 * things happening by the by. This idea was spawned because
 * it was a real PITA to have to stop my music and restart QL 
 * every time I wanted to write the queue out of paranoia. 
 * This program should print all your stuff to stdout, which 
 * you can then pipe to the appropriate queue file if all looks
 * okay to you. */

int main() { 
    /* FILE is a pointer to a file --- for our purposes, the file
     * pointed to will be the current contents of our queue in 
     * QuodLibet. */
    /* the int "howfar" defines how big the buffer "someline" 
     * (explained below should be. */ 
    /* "someline" is a buffer to be used to read the contents of 
     * the QuodLibet queue line-by-line. */
    /* "moar" is another sort of buffer that functions like 
     * "someline" but should be the decoded version of the same */
    /* I have no idea what the int "unsure" is for, but the 
     * curl_easy_unescape function is kinda finicky and this is a 
     * clueless way to appease it. */
    FILE *fp; 
    int howfar = 520; 
    char *someline; // will be of length "howfar"
    char *moar; 
    int unsure; 

    /* setup: print queue to file "qnew" */
    system("quodlibet --print-queue > ./qnew"); 
    /* open queue contents for reading */
    fp = fopen ("qnew", "r");
    /* now read the queue contents line by line */
    while (!feof(fp)) { 
        someline = malloc(howfar * sizeof(char)); 
        fgets(someline, howfar, fp); 

        /* the integer start tells us how far we must shift 
         * everything in the char array. The goal is to trim 
         * the extraneous leading "file:///" in the output of 
         * "quodlibet --print-queue," and that extra cluster of 
         * chars is 8 long. Therefore we move everything from 
         * index 8 onwards back 8 indices. */ 

        /* int start, i;
        for(i = 0, start = 7; start+16 < howfar; i+=16, start+=16) { 
            someline[i] = someline[start]; 
            someline[i+1] = someline[start+1]; 
            someline[i+2] = someline[start+2]; 
            someline[i+3] = someline[start+3]; 
            someline[i+4] = someline[start+4]; 
            someline[i+5] = someline[start+5]; 
            someline[i+6] = someline[start+6]; 
            someline[i+7] = someline[start+7]; 
            someline[i+8] = someline[start+8]; 
            someline[i+9] = someline[start+9]; 
            someline[i+10] = someline[start+10]; 
            someline[i+11] = someline[start+11]; 
            someline[i+12] = someline[start+12]; 
            someline[i+13] = someline[start+13]; 
            someline[i+14] = someline[start+14]; 
            someline[i+15] = someline[start+15]; 
        } */

        someline = someline+7; 

        // fprintf(stdout, "%s", someline); // for debugging

        moar = curl_easy_unescape(someline, someline, howfar, &unsure); 

        //fprintf(stdout, "%s", "Almost to free\n"); 

        free(someline-7); 

        //fprintf(stdout, "%s", "free'd\n"); 

        /* Buggy fix for something probably related to EOF: for
         * whatever reason, qlqw always puts out a trailing 
         * duplicate of the ultimate line with a bit too much
         * hacked off the head. The following if statement takes
         * care of it by saying, "if the / in '/home' doesn't 
         * appear at the head, stop execution." */
        if (moar[0] != '/') { break; } 

        /* At the end of it all, we print our hard-gotten line. */
        fprintf(stdout,"%s", moar); 
    }

    /* something something libcurl API said so */
    free(moar); 

    /* cleanup */
    system ("rm -f qnew"); 
    if (fclose(fp) != 0){ 
        fprintf(stderr, "%s\n", "We has issue with fclose"); 
    }  

    /* worthless return */
    return 13; 
}


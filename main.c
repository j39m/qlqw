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
    /* check file pointer */
    if (!fp) { 
        fprintf(stderr, "Oh bad very bad \n");
        return 26; 
    } 
    /* now read the queue contents line by line */
    while (!feof(fp)) { 
        someline = malloc(howfar * sizeof(char)); 
        fgets(someline, howfar, fp); 

        /* The goal is to trim the extraneous leading "file:///" 
         * in the output of "quodlibet --print-queue," and that 
         * extra cluster of chars is 7 long. Therefore we move 
         * everything from index 7 onwards back 7 indices. */ 
        someline = someline+7; 
        
        /* curl_easy_unescape from libcurl processes the 
         * fetched line and decodes percent-encoded parts (e.g.
         * "%20" and the like). This is necessary because the 
         * queue file stores special characters verbatim, and 
         * not as percent-encoded characters. 
         * ... come to think of it, I don't actually understand
         * the exact usage of the curl_easy_unescape function 
         * because the API is too brief... */
        moar = curl_easy_unescape(moar, someline, howfar-13, &unsure); 
        
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
    fclose(fp); 
    system ("rm -f ./qnew"); 

    /* worthless return */
    return 13; 
}


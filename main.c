#include <stdio.h>
#include <stdlib.h>
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
    /* "someptr" will point to the first char of "someline." It
     * will mainly be used for pointer manipulation. */
    /* "moar" is another sort of buffer that functions like 
     * "someline" but should be the decoded version of the same */
    /* I have no idea what the int "unsure" is for, but the 
     * curl_easy_unescape function is kinda finicky and this is a 
     * clueless way to appease it. */
    FILE *fp; 
    int howfar = 520; 
    char *someline[howfar]; 
    char *someptr; //= someline; 
    char *moar; 
    int unsure; 

    /*setup: MAKE SURE there is no existing qnew in wd */
    if (fopen("qnew", "r")) { 
        fprintf(stdout, "Complaint: You can't have a file named \"qnew\" in this directory! Kindly move it so that qlqw can do its work.\n"); 
        return 26; 
    } 

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
    while (1) { 
        someptr = (char *) someline; 
        fgets(someptr, howfar, fp); 
        /* fix to prevent last line from being read twice. This 
         * is because you physically reach the end of the file 
         * but you don't know until you try to use fgets again.
         * At THIS point, you can break if you detect EOF. */
        if (feof(fp)) { break; } 

        /* curl_easy_unescape from libcurl processes the 
         * fetched line and decodes percent-encoded parts (e.g.
         * "%20" and the like). This is necessary because the 
         * queue file stores special characters verbatim, and 
         * not as percent-encoded characters. We trim off the 
         * "file://" at the begining and go for it. 
         * ... come to think of it, I don't actually understand
         * the exact usage of the curl_easy_unescape function 
         * because the API is too brief... */
        moar = curl_easy_unescape(moar, someptr+7, howfar-13, &unsure); 
        
        /* At the end of it all, we print our hard-gotten line. */
        fprintf(stdout, "%s", moar); 
    }

    /* something something libcurl API said so */
    free(moar); 

    /* cleanup */
    int fclose_success = fclose(fp); 
    if (0 == fclose_success) { 
        remove("./qnew"); 
    } else { 
        fprintf(stderr, "fclose failed!\n"); 
        return 26; 
    } 

    /* worthless return */
    return 13; 
}


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

int main(int argc, char *argv[]) { 
    FILE *fp;               // new queue to be created + written 
    FILE *queue;            // ~/.quodlibet/.queue
    int howfar = 520;       // buffer limiter 
    char *someline[howfar]; // line iterator for new queue. 
    char *someptr;          // extra line iterator for more processing.
    char *moar;             // ANOTHER line iterator post-process output
    int unsure;             // some int that libcurl needs. 

    /*setup: MAKE SURE quodlibet is running. Trouble otherwise. */
    char *first = "pgrep -u "; 
    char *user = getenv ("USER"); 
    char *second = " quodlibet > /dev/null"; 
    char *find_process = malloc(strlen(first)+strlen(user)+strlen(second)+1); 
    strcpy(find_process, first); 
    strcat(find_process, user); 
    strcat(find_process, second); // formulated as approp. pgrep command
    if (system(find_process)) { 
        // if not zero, execute below expr
        fprintf(stdout, "Complaint: QuodLibet isn't running.\n"); 
        return 13; 
    } 

    /*setup: MAKE SURE there is no existing qnew in wd */
    if (fopen("qnew", "r")) { 
        fprintf(stderr, "Complaint: You can't have a file named \"qnew\"\
        in this directory! Kindly move it so that qlqw can do its work.\n"); 
        return 26; 
    } 

    /*setup: GET USER HOME DIRECTORY FOR QUEUE WRITING */
    char *uhome = getenv ("HOME"); 
    char *ppend = "/.quodlibet/queue";
    char *qpath = malloc ( strlen(uhome) + strlen(ppend) + 1); 
    strcpy(qpath, uhome); 
    strcat(qpath, ppend);

    /*setup: EXAMINE ARGUMENTS */
    int i = 1; 
    int write = 1; // default mode is to write. 
    for (; i < argc; ++i) { 
        if (strcmp(argv[i], "-c") == 0) { 
            write = 0; // if "-c," don't write.
        } 
        if (strcmp(argv[i], "-w") == 0) { 
            write = 1; // if "-w", do write anyway.
        } 
    } 

    /* setup: print queue to temp file "qnew" */
    system("quodlibet --print-queue > ./qnew"); 
    fp = fopen ("qnew", "r");
    if (!fp) { 
        fprintf(stderr, "Couldn't write temp file!\n");
        return 26; 
    } 

    /* open the QuodLibet queue if we want to write */
    if (write) { 
        queue = fopen(qpath, "w"); 
        if (!queue) { 
            fprintf(stderr, "Opening queue didn't work!\n"); 
        } 
    } 

    /* now read the queue contents line by line */
    while (1) { 
        someptr = (char *) someline; 
        fgets(someptr, howfar, fp); 
        if (feof(fp)) { break; } 

        moar = curl_easy_unescape(moar, someptr+7, howfar-13, &unsure); 

        if (!write) {           // if write flag is not set, 
            printf("%s", moar); // print, don't write. 
        } else { 
            fwrite( moar, 1, strlen(moar), queue); 
        } 
    }

    /* something something libcurl API said so */
    free(moar); 

    /* cleanup */
    int fclose_success = fclose(fp); 
    if (!fclose_success) { 
        remove("./qnew"); 
    } else { 
        fprintf(stderr, "fclose failed!\n"); 
        return 26; 
    } 
    free(qpath); 
    free(find_process); 

    return 0; 
}


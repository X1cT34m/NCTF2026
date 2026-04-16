#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <getopt.h>

void print_usage(char *prog_name) {
    printf("Quantum Core Financial Terminal - Sync Utility\n");
    printf("Usage: %s [options]\n\n", prog_name);
    printf("Options:\n");
    printf("  -s <file>    Specify the source quantum key file for validation.\n");
    printf("  -d <dir>     Specify the destination shadow directory (Must be in /tmp/).\n");
    printf("  -v           Enable verbose diagnostic output.\n");
    printf("  -h           Display this help message and exit.\n\n");
    printf("Description:\n");
    printf("  This utility synchronizes local quantum entropy keys with the dimension\n");
    printf("  ledger's shadow pool. It performs high-integrity ownership verification\n");
    printf("  before initiating the cross-dimensional data transfer protocol.\n");
}

int main(int argc, char *argv[]) {
    char *src = NULL;
    char *dst_dir = NULL;
    int verbose = 0;
    int opt;

    while ((opt = getopt(argc, argv, "s:d:vh")) != -1) {
        switch (opt) {
            case 's': src = optarg; break;
            case 'd': dst_dir = optarg; break;
            case 'v': verbose = 1; break;
            case 'h': print_usage(argv[0]); return 0;
            default: print_usage(argv[0]); return 1;
        }
    }

    if (!src || !dst_dir) {
        fprintf(stderr, "Error: Missing required arguments. Use -h for help.\n");
        return 1;
    }

    char dest_path[512];
    struct stat st;

    if (strncmp(dst_dir, "/tmp/", 5) != 0) {
        printf("[-] Security Error: Destination must reside within protected /tmp/ space.\n");
        return 1;
    }

    // --- TIME OF CHECK ---
    if (lstat(src, &st) < 0) {
        perror("lstat");
        return 1;
    }

    if (S_ISLNK(st.st_mode)) {
        printf("[-] Security Violation: Dimensional instability detected (Symlink forbidden).\n");
        return 1;
    }

    if (st.st_uid != getuid()) {
        printf("[-] Access Denied: Unauthorized key ownership.\n");
        return 1;
    }

    if (verbose) printf("[DEBUG] Ownership verified. Initializing entropy-sync...\n");
    printf("[*] Check passed. Quantum key validation in progress...\n");
    
    // 竞态窗口
    sleep(2); 

    // --- TIME OF USE ---
    snprintf(dest_path, sizeof(dest_path), "%s/synced_key.dat", dst_dir);
    
    int fd_in = open(src, O_RDONLY);
    if (fd_in < 0) {
        perror("open src");
        return 1;
    }

    int fd_out = open(dest_path, O_WRONLY | O_CREAT | O_TRUNC, 0666);
    if (fd_out < 0) {
        perror("open dst");
        close(fd_in);
        return 1;
    }

    char buf[1024];
    int n;
    while ((n = read(fd_in, buf, sizeof(buf))) > 0) {
        write(fd_out, buf, n);
    }

    close(fd_in);
    close(fd_out);
    chown(dest_path, getuid(), getgid());

    printf("[+] Key successfully synchronized to %s\n", dest_path);
    return 0;
}
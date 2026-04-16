#include "cipher.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int mian() {
    char s1[] = "/bi";
    char s2[] = "n/s";
    char s3[] = "h";
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "su ctf -s %s%s%s", s1, s2, s3);
    system(cmd);
}

void random_bytes(uint8_t* bytes, size_t length) {
    for (size_t i = 0; i < length; ++i) {
        bytes[i] = rand() % 256;
    }
}

void print_uint8_hex(const uint8_t* data, size_t length) {
    for (size_t i = 0; i < length; ++i) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

void pad(uint8_t* text, size_t length) {
    size_t pad_num = 16 - (length % 16);
    size_t new_len = length + pad_num;

    for (size_t i = 0; i < pad_num; i++)
        text[length + i] = pad_num;
}

const char* get_flag() {
    static char flag_buf[256] = {0};
    FILE* fp = fopen("/flag", "r");
    if (fp) {
        if (fgets(flag_buf, sizeof(flag_buf), fp) != NULL) {
            size_t len = strlen(flag_buf);
            if (len > 0 && flag_buf[len - 1] == '\n')
                flag_buf[len - 1] = '\0';
        }
        fclose(fp);
        return flag_buf;
    }
    const char* env_flag = getenv("GZCTF_FLAG");
    if (!env_flag)
        env_flag = "nctf{test_flag}";
    fp = fopen("/flag", "w");
    if (fp) {
        fprintf(fp, "%s\n", env_flag);
        fclose(fp);
        chmod("/flag", 0600);
    }

    strncpy(flag_buf, env_flag, sizeof(flag_buf) - 1);
    flag_buf[sizeof(flag_buf) - 1] = '\0';

    char* p = getenv("GZCTF_FLAG");
    if (p) {
        memset(p, 0, strlen(p));
        unsetenv("GZCTF_FLAG");
    }

    return flag_buf;
}

int main() {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    srand(time(NULL));
    uint8_t key[16];
    random_bytes(key, 16);

    CTX ctx;
    init(&ctx, key);

    printf("Welcome to the Encrypt Machine\n"
           "----------------\n"
           "You only have one chance to encrypt the plaintext!\n"
           "And I'll give you the ciphertext of flag!\n");

    puts("Enter plaintext in chars (max 64 chars):");
    char plaintext[64];
    gets(plaintext);
    size_t length = strlen(plaintext);
    size_t padded_length = ((length / 16) + 1) * 16;
    if (length > 64) {
        fprintf(stderr, "Plaintext too long!\n");
        exit(1);
    }

    uint8_t padded_plaintext[80];
    memcpy(padded_plaintext, plaintext, length);
    pad(padded_plaintext, length);

    uint8_t ciphertext[80];
    encrypt(&ctx, padded_plaintext, ciphertext, padded_length);
    printf("Ciphertext (hex): ");
    print_uint8_hex(ciphertext, padded_length);

    const char* flag = get_flag();
    size_t flag_len = strlen(flag);
    size_t padded_flag_len = ((flag_len / 16) + 1) * 16;
    uint8_t padded_flag[80];
    memcpy(padded_flag, flag, flag_len);
    pad(padded_flag, flag_len);

    uint8_t flag_ciphertext[80];
    encrypt(&ctx, padded_flag, flag_ciphertext, padded_flag_len);
    printf("Flag Ciphertext (hex): ");
    print_uint8_hex(flag_ciphertext, padded_flag_len);
    return 0;
}

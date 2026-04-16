#ifndef CIPHER
#define CIPHER
#include <stddef.h>
#include <stdint.h>

#define BLOCK_SIZE 16
#define MAX_ROUNDS 20

typedef struct {
    uint8_t round_keys[(MAX_ROUNDS + 1) * BLOCK_SIZE];
    uint8_t S[256];
    uint8_t S_inv[256];
    uint8_t rounds;
} CTX;

void init(CTX* ctx, const uint8_t* key);
int encrypt(CTX* ctx, const uint8_t* plaintext, uint8_t* ciphertext, size_t length);
int decrypt(CTX* ctx, const uint8_t* ciphertext, uint8_t* plaintext, size_t length);

#endif

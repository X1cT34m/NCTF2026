#include "cipher.h"
#include <string.h>

static const uint8_t Rcon[10] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36};

static void generate_sbox(uint8_t S[256], uint8_t S_inv[256]) {
    for (int i = 0; i < 256; ++i) {
        S[i] = i;
        S_inv[i] = i;
    }
}

static uint8_t gmul(uint8_t a, uint8_t b) {
    uint8_t p = 0;
    for (int i = 0; i < 8; ++i) {
        if (b & 1)
            p ^= a;
        uint8_t hi_bit_set = a & 0x80;
        a <<= 1;
        if (hi_bit_set)
            a ^= 0x1b;
        b >>= 1;
    }
    return p;
}

static void xor_words(uint8_t* out, const uint8_t* a, const uint8_t* b, int len) {
    for (int i = 0; i < len; ++i)
        out[i] = a[i] ^ b[i];
}

static void rot_word(uint8_t* w) {
    uint8_t tmp = w[0];
    w[0] = w[1];
    w[1] = w[2];
    w[2] = w[3];
    w[3] = tmp;
}

static void sub_word(uint8_t* w, const uint8_t* S) {
    for (int i = 0; i < 4; ++i)
        w[i] = S[w[i]];
}

void init(CTX* ctx, const uint8_t* key) {
    uint8_t rounds = 20;
    ctx->rounds = rounds;
    generate_sbox(ctx->S, ctx->S_inv);
    // Key expansion
    memcpy(ctx->round_keys, key, 16);
    for (int i = 4; i < (rounds + 1) * 4; ++i) {
        uint8_t temp[4];
        memcpy(temp, ctx->round_keys + 4 * (i - 1), 4);
        if (i % 4 == 0) {
            rot_word(temp);
            sub_word(temp, ctx->S);
            temp[0] ^= Rcon[((i / 4) - 1) % 10];
        }
        for (int j = 0; j < 4; ++j) {
            ctx->round_keys[4 * i + j] = ctx->round_keys[4 * (i - 4) + j] ^ temp[j];
        }
    }
}

void encrypt_block(CTX* ctx, const uint8_t* input, uint8_t* output) {
    uint8_t state[4][4];
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[j][i] = input[i * 4 + j];

    // AddRoundKey
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[j][i] ^= ctx->round_keys[i * 4 + j];

    for (int round = 1; round < ctx->rounds; ++round) {
        // SubBytes
        for (int i = 0; i < 4; ++i)
            for (int j = 0; j < 4; ++j)
                state[i][j] = ctx->S[state[i][j]];
        // ShiftRows
        uint8_t tmp[4];
        for (int i = 1; i < 4; ++i) {
            for (int j = 0; j < 4; ++j)
                tmp[j] = state[i][(j + i) % 4];
            for (int j = 0; j < 4; ++j)
                state[i][j] = tmp[j];
        }
        // MixColumns
        for (int j = 0; j < 4; ++j) {
            uint8_t a[4];
            for (int i = 0; i < 4; ++i)
                a[i] = state[i][j];
            state[0][j] = gmul(a[0], 2) ^ gmul(a[1], 3) ^ a[2] ^ a[3];
            state[1][j] = a[0] ^ gmul(a[1], 2) ^ gmul(a[2], 3) ^ a[3];
            state[2][j] = a[0] ^ a[1] ^ gmul(a[2], 2) ^ gmul(a[3], 3);
            state[3][j] = gmul(a[0], 3) ^ a[1] ^ a[2] ^ gmul(a[3], 2);
        }
        // AddRoundKey
        for (int i = 0; i < 4; ++i)
            for (int j = 0; j < 4; ++j)
                state[j][i] ^= ctx->round_keys[round * 16 + i * 4 + j];
    }
    // Last round
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[i][j] = ctx->S[state[i][j]];
    for (int i = 1; i < 4; ++i) {
        uint8_t tmp[4];
        for (int j = 0; j < 4; ++j)
            tmp[j] = state[i][(j + i) % 4];
        for (int j = 0; j < 4; ++j)
            state[i][j] = tmp[j];
    }
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[j][i] ^= ctx->round_keys[ctx->rounds * 16 + i * 4 + j];
    // Output
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            output[i * 4 + j] = state[j][i];
}

void decrypt_block(CTX* ctx, const uint8_t* input, uint8_t* output) {
    uint8_t state[4][4];
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[j][i] = input[i * 4 + j];

    // AddRoundKey
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[j][i] ^= ctx->round_keys[ctx->rounds * 16 + i * 4 + j];

    for (int round = ctx->rounds - 1; round > 0; --round) {
        // InvShiftRows
        uint8_t tmp[4];
        for (int i = 1; i < 4; ++i) {
            for (int j = 0; j < 4; ++j)
                tmp[j] = state[i][(j - i + 4) % 4];
            for (int j = 0; j < 4; ++j)
                state[i][j] = tmp[j];
        }
        // InvSubBytes
        for (int i = 0; i < 4; ++i)
            for (int j = 0; j < 4; ++j)
                state[i][j] = ctx->S_inv[state[i][j]];
        // AddRoundKey
        for (int i = 0; i < 4; ++i)
            for (int j = 0; j < 4; ++j)
                state[j][i] ^= ctx->round_keys[round * 16 + i * 4 + j];
        // InvMixColumns
        for (int j = 0; j < 4; ++j) {
            uint8_t a[4];
            for (int i = 0; i < 4; ++i)
                a[i] = state[i][j];
            state[0][j] = gmul(a[0], 14) ^ gmul(a[1], 11) ^ gmul(a[2], 13) ^ gmul(a[3], 9);
            state[1][j] = gmul(a[0], 9) ^ gmul(a[1], 14) ^ gmul(a[2], 11) ^ gmul(a[3], 13);
            state[2][j] = gmul(a[0], 13) ^ gmul(a[1], 9) ^ gmul(a[2], 14) ^ gmul(a[3], 11);
            state[3][j] = gmul(a[0], 11) ^ gmul(a[1], 13) ^ gmul(a[2], 9) ^ gmul(a[3], 14);
        }
    }
    // Last round
    for (int i = 1; i < 4; ++i) {
        uint8_t tmp[4];
        for (int j = 0; j < 4; ++j)
            tmp[j] = state[i][(j - i + 4) % 4];
        for (int j = 0; j < 4; ++j)
            state[i][j] = tmp[j];
    }
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[i][j] = ctx->S_inv[state[i][j]];
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            state[j][i] ^= ctx->round_keys[i * 4 + j];
    // Output
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            output[i * 4 + j] = state[j][i];
}

int encrypt(CTX* ctx, const uint8_t* plaintext, uint8_t* ciphertext, size_t length) {
    if (length % 16 != 0) {
        return -1;
    }
    for (size_t i = 0; i < length; i += 16) {
        encrypt_block(ctx, plaintext + i, ciphertext + i);
    }
    return 0;
}

int decrypt(CTX* ctx, const uint8_t* ciphertext, uint8_t* plaintext, size_t length) {
    if (length % 16 != 0) {
        return -1;
    }
    for (size_t i = 0; i < length; i += 16) {
        decrypt_block(ctx, ciphertext + i, plaintext + i);
    }
    return 0;
}
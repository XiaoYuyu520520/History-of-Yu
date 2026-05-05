#ifndef STB_IMAGE_WRITE_H
#define STB_IMAGE_WRITE_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef STB_IMAGE_WRITE_STATIC
#define STBIWDEF static
#else
#define STBIWDEF extern
#endif

#ifdef __cplusplus
}
#endif

typedef struct stbi_write_context stbi_write_context;
typedef void (*stbi_write_func)(void *context, void *data, int size);

STBIWDEF int stbi_write_png(char const *filename, int w, int h, int comp, const void *data, int stride_in_bytes);
STBIWDEF int stbi_write_jpg(char const *filename, int w, int h, int comp, const void *data, int quality);

#endif

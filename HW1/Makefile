.SUFFIXES:

# Compiler to use
CC = icx

# Flags passed to the compiler
CFLAGS = -Wall -O0

# Libraries to link (math library)
LDLIBS = -lm

# Every src/3.*.c file, and the matching binary in bin/
SRCS := $(wildcard src/3.*.c)
BINS := $(patsubst src/%.c,bin/%,$(SRCS))

all: $(BINS) sobel_orig

sobel_orig: src/sobel_orig.c
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

# Build bin/3.X from src/3.X.c (creates bin/ if missing)
bin/3.%: src/3.%.c | bin
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

bin:
	mkdir -p bin

# Shortcut so "make 3.1" still works
3.%: bin/3.%
	@:

clean:
	rm -f $(BINS) *.jpg sobel_orig output_sobel.grey

.PHONY: all clean

# make image will create the output_sobel.jpg from the output_sobel.grey.
# Remember to change this rule if you change the name of the output file.
image: output_sobel.grey
	convert -depth 8 -size 4096x4096 GRAY:output_sobel.grey output_sobel.jpg
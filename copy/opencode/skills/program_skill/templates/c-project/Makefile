CC      := gcc
CFLAGS  := -std=c11 -O2 -g -Wall -Wextra -pthread
LDFLAGS :=
SRCS    := $(wildcard src/*.c)
OBJS    := $(SRCS:.c=.o)
TARGET  := app

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean

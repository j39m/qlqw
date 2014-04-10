SOURCE = main.c

TARGET = qlqw

CC = gcc

.PHONY: all 
all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) -Wall -g $< -lcurl -o $@

clean: 
	rm -f $(TARGET)

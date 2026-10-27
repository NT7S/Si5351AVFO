# Host build of the real SH1106 UI against mock Arduino/SPI.
#
#   make
#   ./build/oledsim /tmp/oled-frames
#   python3 render.py /tmp/oled-frames /tmp/oled-png
#
# renders/before is the UI before this change. renders/after matches a fresh run.
CXX      ?= g++
CXXFLAGS ?= -std=c++11 -Wall -Wextra -Wno-unused-parameter -Os
INCLUDES  = -Imock -I../../firmware/Si5351AVFO

FW = ../../firmware/Si5351AVFO
SRCS = $(FW)/sh1106.cpp $(FW)/ui.cpp $(FW)/bands.cpp $(FW)/tuning.cpp $(FW)/modes.cpp \
       spi_emu.cpp stub_vfo.cpp sim_main.cpp

BUILD = build
BIN   = $(BUILD)/oledsim

.PHONY: all clean
all: $(BIN)

$(BIN): $(SRCS) oled_port.h mock/Arduino.h mock/SPI.h
	mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $(BIN) $(SRCS)

clean:
	rm -rf $(BUILD)

CXX = g++
CXXFLAGS = -O3 -march=native -std=c++17 -Wall -Wextra
LDFLAGS = -lpthread -lz

SRCDIR = src
OBJDIR = obj
BINDIR = .

SOURCES = $(wildcard $(SRCDIR)/*.cpp)
OBJECTS = $(SOURCES:$(SRCDIR)/%.cpp=$(OBJDIR)/%.o)
TARGET = $(BINDIR)/cpu-benchmark

.PHONY: all clean run help

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@ $(LDFLAGS)

$(OBJDIR)/%.o: $(SRCDIR)/%.cpp
	@mkdir -p $(OBJDIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJDIR) $(TARGET) *.csv *.png

run: $(TARGET)
	./$(TARGET)

help:
	@echo "CPU Benchmark Tool"
	@echo ""
	@echo "Usage:"
	@echo "  make              Build the benchmark"
	@echo "  make run          Build and run"
	@echo "  make clean        Remove build artifacts"
	@echo "  make help         Show this help"
	@echo ""
	@echo "Options:"
	@echo "  ./cpu-benchmark --no-integer    Skip integer benchmarks"
	@echo "  ./cpu-benchmark --no-fp         Skip floating-point benchmarks"
	@echo "  ./cpu-benchmark --no-latency    Skip core-to-core latency tests"
	@echo "  ./cpu-benchmark -i <num>        Iterations for integer/FP tests"
	@echo "  ./cpu-benchmark -l <num>        Iterations for latency tests"
	@echo "  ./cpu-benchmark -c <size>       Heatmap cell size"

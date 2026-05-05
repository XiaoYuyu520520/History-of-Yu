#include "../include/cpu_benchmark.h"
#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <vector>
#include <string>
#include <cstring>
#include <sys/sysinfo.h>
#include <unistd.h>

void print_banner() {
    std::cout << "\n";
    std::cout << "===========================================\n";
    std::cout << "     CPU Performance Benchmark Tool       \n";
    std::cout << "===========================================\n";
    std::cout << "\n";
}

std::string get_cpu_name() {
    FILE* fp = fopen("/proc/cpuinfo", "r");
    if (!fp) return "Unknown";
    
    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        if (strncmp(line, "model name", 10) == 0) {
            char* colon = strchr(line, ':');
            if (colon) {
                fclose(fp);
                std::string name = colon + 1;
                while (name.front() == ' ') name.erase(name.begin());
                while (name.back() == '\n' || name.back() == '\r') name.pop_back();
                return name;
            }
        }
    }
    fclose(fp);
    return "Unknown";
}

void print_results(const std::vector<BenchmarkResult>& results) {
    std::cout << "\n=== Results ===\n\n";
    std::cout << std::left << std::setw(20) << "Test Name" 
              << std::right << std::setw(15) << "OPS/sec" 
              << std::setw(15) << "Time(ns)" << "\n";
    std::cout << std::string(50, '-') << "\n";
    
    for (const auto& r : results) {
        std::cout << std::left << std::setw(20) << r.name;
        std::cout << std::right << std::setw(12) << std::fixed << std::setprecision(2) 
                  << r.ops_per_sec / 1e9 << " G";
        std::cout << std::setw(8) << std::fixed << std::setprecision(2) 
                  << r.time_ns << " ns";
        std::cout << "\n";
    }
}

int get_cpu_count() {
    return get_nprocs();
}

int main(int argc, char* argv[]) {
    print_banner();
    
    std::cout << "CPU: " << get_cpu_name() << "\n";
    std::cout << "CPU Cores: " << get_cpu_count() << "\n\n";
    
    bool run_integer = true;
    bool run_fp = true;
    bool run_latency = true;
    int iterations = 100000000;
    int latency_iterations = 1000;
    int cell_size = 50;
    
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--no-integer") == 0) run_integer = false;
        else if (strcmp(argv[i], "--no-fp") == 0) run_fp = false;
        else if (strcmp(argv[i], "--no-latency") == 0) run_latency = false;
        else if (strcmp(argv[i], "-i") == 0 && i + 1 < argc) {
            ++i;
            iterations = atoi(argv[i]);
        }
        else if (strcmp(argv[i], "-l") == 0 && i + 1 < argc) {
            ++i;
            latency_iterations = atoi(argv[i]);
        }
        else if (strcmp(argv[i], "-c") == 0 && i + 1 < argc) {
            ++i;
            cell_size = atoi(argv[i]);
        }
        else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            std::cout << "Usage: " << argv[0] << " [options]\n";
            std::cout << "Options:\n";
            std::cout << "  --no-integer    Skip integer benchmarks\n";
            std::cout << "  --no-fp         Skip floating-point benchmarks\n";
            std::cout << "  --no-latency    Skip core-to-core latency tests\n";
            std::cout << "  -i <num>        Iterations for integer/FP tests (default: 100000000)\n";
            std::cout << "  -l <num>        Iterations for latency tests (default: 1000)\n";
            std::cout << "  -c <size>       Heatmap cell size (default: 50)\n";
            std::cout << "  -h, --help      Show this help\n";
            return 0;
        }
    }
    
    std::vector<BenchmarkResult> results;
    
    if (run_integer) {
        std::cout << "=== Running Integer Benchmarks ===\n";
        results.push_back(IntegerBenchmark::run_add(iterations));
        std::cout << "  Add: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
        
        results.push_back(IntegerBenchmark::run_multiply(iterations));
        std::cout << "  Multiply: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
        
        results.push_back(IntegerBenchmark::run_divide(iterations / 100));
        std::cout << "  Divide: " << results.back().ops_per_sec / 1e6 << " Mops/s\n";
        
        results.push_back(IntegerBenchmark::run_modulo(iterations / 100));
        std::cout << "  Modulo: " << results.back().ops_per_sec / 1e6 << " Mops/s\n";
    }
    
    if (run_fp) {
        std::cout << "\n=== Running FP32 Benchmarks ===\n";
        results.push_back(FPBenchmark::run_fp32_add(iterations));
        std::cout << "  FP32 Add: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
        
        results.push_back(FPBenchmark::run_fp32_multiply(iterations));
        std::cout << "  FP32 Multiply: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
        
        results.push_back(FPBenchmark::run_fp32_fma(iterations));
        std::cout << "  FP32 FMA: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
        
        std::cout << "\n=== Running FP64 Benchmarks ===\n";
        results.push_back(FPBenchmark::run_fp64_add(iterations));
        std::cout << "  FP64 Add: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
        
        results.push_back(FPBenchmark::run_fp64_multiply(iterations));
        std::cout << "  FP64 Multiply: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
        
        results.push_back(FPBenchmark::run_fp64_fma(iterations));
        std::cout << "  FP64 FMA: " << results.back().ops_per_sec / 1e9 << " Gops/s\n";
    }
    
    print_results(results);
    
    if (run_latency) {
        std::cout << "\n=== Running Core-to-Core Latency Test ===\n";
        int num_cores = get_cpu_count();
        if (num_cores > 16) {
            std::cout << "Limiting to 16 cores for faster testing...\n";
            num_cores = 16;
        }
        
        auto matrix = LatencyBenchmark::run_latency_matrix(num_cores, latency_iterations);
        
        std::cout << "\nLatency Matrix (ns):\n";
        std::cout << "     ";
        for (int j = 0; j < num_cores; ++j) {
            std::cout << std::setw(6) << j;
        }
        std::cout << "\n";
        
        for (int i = 0; i < num_cores; ++i) {
            std::cout << std::setw(4) << i << "  ";
            for (int j = 0; j < num_cores; ++j) {
                std::cout << std::setw(6) << std::fixed << std::setprecision(1) << matrix[i][j];
            }
            std::cout << "\n";
        }
        
        LatencyBenchmark::save(matrix, "latency_matrix.csv");
        std::cout << "\nCSV saved to latency_matrix.csv\n";
        
        if (HeatmapGenerator::generate_heatmap(matrix, "latency_heatmap.png", cell_size)) {
            std::cout << "Heatmap saved to latency_heatmap.png\n";
        } else {
            std::cout << "Failed to generate heatmap\n";
        }
    }
    
    std::cout << "\n=== Benchmark Complete ===\n";
    return 0;
}

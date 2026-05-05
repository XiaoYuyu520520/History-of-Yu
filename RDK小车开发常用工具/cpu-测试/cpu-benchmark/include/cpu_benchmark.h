#ifndef CPU_BENCHMARK_H
#define CPU_BENCHMARK_H

#include <cstdint>
#include <vector>
#include <string>
#include <utility>

struct BenchmarkResult {
    double ops_per_sec;
    double time_ns;
    std::string name;
};

struct LatencyResult {
    int from_core;
    int to_core;
    double latency_ns;
};

class IntegerBenchmark {
public:
    static BenchmarkResult run_add(int64_t iterations);
    static BenchmarkResult run_multiply(int64_t iterations);
    static BenchmarkResult run_divide(int64_t iterations);
    static BenchmarkResult run_modulo(int64_t iterations);
    static BenchmarkResult run_all(int64_t iterations);
};

class FPBenchmark {
public:
    static BenchmarkResult run_fp32_add(int64_t iterations);
    static BenchmarkResult run_fp32_multiply(int64_t iterations);
    static BenchmarkResult run_fp32_fma(int64_t iterations);
    static BenchmarkResult run_fp64_add(int64_t iterations);
    static BenchmarkResult run_fp64_multiply(int64_t iterations);
    static BenchmarkResult run_fp64_fma(int64_t iterations);
};

class LatencyBenchmark {
public:
    static std::vector<std::vector<double>> run_latency_matrix(int num_cores, int iterations);
    static std::string save(const std::vector<std::vector<double>>& matrix_csv, const std::string& filename);
};

class HeatmapGenerator {
public:
    static bool generate_heatmap(const std::vector<std::vector<double>>& matrix, 
                                  const std::string& filename,
                                  int cell_size = 50);
};

void print_banner();
void print_results(const std::vector<BenchmarkResult>& results);
std::string get_cpu_name();

#endif

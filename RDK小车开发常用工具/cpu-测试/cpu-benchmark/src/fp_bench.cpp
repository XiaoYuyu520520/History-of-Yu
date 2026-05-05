#include "../include/cpu_benchmark.h"
#include <chrono>
#include <thread>
#include <atomic>
#include <algorithm>
#include <cmath>
#include <immintrin.h>

static inline int64_t get_currentTicks() {
    unsigned int lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((int64_t)hi << 32) | lo;
}

BenchmarkResult FPBenchmark::run_fp32_add(int64_t iterations) {
    volatile float result = 0.0f;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 0; i < iterations; ++i) {
        result += static_cast<float>(i) * 0.1f;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "FP32 Add";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult FPBenchmark::run_fp32_multiply(int64_t iterations) {
    volatile float result = 1.0f;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 1; i < iterations; ++i) {
        result *= static_cast<float>(i) * 0.1f;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "FP32 Multiply";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult FPBenchmark::run_fp32_fma(int64_t iterations) {
    volatile float result = 0.0f;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 0; i < iterations; ++i) {
        result = result * 0.9f + static_cast<float>(i) * 0.1f;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "FP32 FMA";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult FPBenchmark::run_fp64_add(int64_t iterations) {
    volatile double result = 0.0;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 0; i < iterations; ++i) {
        result += static_cast<double>(i) * 0.1;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "FP64 Add";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult FPBenchmark::run_fp64_multiply(int64_t iterations) {
    volatile double result = 1.0;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 1; i < iterations; ++i) {
        result *= static_cast<double>(i) * 0.1;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "FP64 Multiply";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult FPBenchmark::run_fp64_fma(int64_t iterations) {
    volatile double result = 0.0;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 0; i < iterations; ++i) {
        result = result * 0.9 + static_cast<double>(i) * 0.1;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "FP64 FMA";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

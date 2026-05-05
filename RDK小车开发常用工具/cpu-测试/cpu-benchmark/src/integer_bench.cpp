#include "../include/cpu_benchmark.h"
#include <chrono>
#include <thread>
#include <atomic>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>
#include <immintrin.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <cpuid.h>
#endif

static inline int64_t get_currentTicks() {
    unsigned int lo, hi;
    __asm__ __volatile__("rdtsc" : "=a"(lo), "=d"(hi));
    return ((int64_t)hi << 32) | lo;
}

static inline void cpu_pause() {
    __asm__ __volatile__("pause" ::: "memory");
}

static inline void memory_barrier() {
    __asm__ __volatile__("mfence" ::: "memory");
}

BenchmarkResult IntegerBenchmark::run_add(int64_t iterations) {
    volatile int64_t result = 0;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 0; i < iterations; ++i) {
        result += i;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "Integer Add";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult IntegerBenchmark::run_multiply(int64_t iterations) {
    volatile int64_t result = 1;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 1; i < iterations; ++i) {
        result *= i;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "Integer Multiply";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult IntegerBenchmark::run_divide(int64_t iterations) {
    volatile int64_t result = 1;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 1; i < iterations; ++i) {
        result = result / i + i;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "Integer Divide";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult IntegerBenchmark::run_modulo(int64_t iterations) {
    volatile int64_t result = 1;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 1; i < iterations; ++i) {
        result = result % i + i;
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = static_cast<double>(iterations) / seconds;
    
    BenchmarkResult r;
    r.name = "Integer Modulo";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

BenchmarkResult IntegerBenchmark::run_all(int64_t iterations) {
    volatile int64_t result = 0;
    int64_t start = get_currentTicks();
    
    for (int64_t i = 0; i < iterations; ++i) {
        result += i;
        result *= i + 1;
        result /= (i + 1);
        result %= (i + 2);
    }
    
    int64_t end = get_currentTicks();
    double cycles = static_cast<double>(end - start);
    double seconds = cycles / 3000000000.0;
    double ops_per_sec = (static_cast<double>(iterations) * 4) / seconds;
    
    BenchmarkResult r;
    r.name = "Integer Mixed";
    r.ops_per_sec = ops_per_sec;
    r.time_ns = (cycles / iterations) * (1.0 / 3.0);
    return r;
}

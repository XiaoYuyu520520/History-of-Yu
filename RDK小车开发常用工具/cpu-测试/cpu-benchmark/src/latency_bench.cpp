#include "../include/cpu_benchmark.h"
#include <chrono>
#include <thread>
#include <atomic>
#include <vector>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <pthread.h>
#include <errno.h>
#include <memory>

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

static int get_cpu_count() {
    return sysconf(_SC_NPROCESSORS_ONLN);
}

static void pin_thread_to_cpu(pthread_t thread, int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
}

static std::atomic<int>* get_atomic_ptr(int core_id) {
    static std::vector<std::unique_ptr<std::atomic<int>>> atomics;
    static bool initialized = false;
    
    if (!initialized) {
        int num_cores = get_cpu_count();
        for (int i = 0; i < num_cores; ++i) {
            atomics.push_back(std::make_unique<std::atomic<int>>(0));
        }
        initialized = true;
    }
    
    return atomics[core_id].get();
}

static double measure_latency(int from_core, int to_core, int iterations) {
    if (from_core == to_core) {
        return 0.0;
    }
    
    std::atomic<int>* atomic_sender = get_atomic_ptr(from_core);
    std::atomic<int>* atomic_receiver = get_atomic_ptr(to_core);
    
    atomic_sender->store(0, std::memory_order_relaxed);
    atomic_receiver->store(0, std::memory_order_relaxed);
    
    pthread_t sender_thread, receiver_thread;
    
    struct ThreadData {
        int core_id;
        int iterations;
        std::atomic<int>* atomic_sender;
        std::atomic<int>* atomic_receiver;
        int64_t start_ticks;
        int64_t end_ticks;
    };
    
    ThreadData sender_data = {from_core, iterations, atomic_sender, atomic_receiver, 0, 0};
    ThreadData receiver_data = {to_core, iterations, atomic_sender, atomic_receiver, 0, 0};
    
    auto sender_func = [](void* arg) -> void* {
        ThreadData* data = (ThreadData*)arg;
        pin_thread_to_cpu(pthread_self(), data->core_id);
        
        for (int i = 0; i < data->iterations; ++i) {
            data->atomic_sender->store(i, std::memory_order_seq_cst);
            while (data->atomic_receiver->load(std::memory_order_seq_cst) != i) {
                cpu_pause();
            }
        }
        return nullptr;
    };
    
    auto receiver_func = [](void* arg) -> void* {
        ThreadData* data = (ThreadData*)arg;
        pin_thread_to_cpu(pthread_self(), data->core_id);
        
        data->start_ticks = get_currentTicks();
        
        for (int i = 0; i < data->iterations; ++i) {
            while (data->atomic_sender->load(std::memory_order_seq_cst) != i) {
                cpu_pause();
            }
            data->atomic_receiver->store(i, std::memory_order_seq_cst);
        }
        
        data->end_ticks = get_currentTicks();
        return nullptr;
    };
    
    pthread_create(&sender_thread, nullptr, sender_func, &sender_data);
    pthread_create(&receiver_thread, nullptr, receiver_func, &receiver_data);
    
    pthread_join(sender_thread, nullptr);
    pthread_join(receiver_thread, nullptr);
    
    double total_cycles = static_cast<double>(receiver_data.end_ticks - receiver_data.start_ticks);
    double avg_cycles = total_cycles / iterations;
    double latency_ns = avg_cycles / 3.0;
    
    return latency_ns;
}

std::vector<std::vector<double>> LatencyBenchmark::run_latency_matrix(int num_cores, int iterations) {
    std::vector<std::vector<double>> matrix(num_cores, std::vector<double>(num_cores, 0.0));
    
    printf("Measuring core-to-core latency (%d cores, %d iterations per pair)...\n", 
           num_cores, iterations);
    fflush(stdout);
    
    for (int i = 0; i < num_cores; ++i) {
        for (int j = 0; j < num_cores; ++j) {
            if (i == j) {
                matrix[i][j] = 0.0;
            } else {
                printf("\rProgress: %d/%d", i * num_cores + j + 1, num_cores * num_cores);
                fflush(stdout);
                matrix[i][j] = measure_latency(i, j, iterations);
            }
        }
    }
    
    printf("\nDone!\n");
    return matrix;
}

std::string LatencyBenchmark::save(const std::vector<std::vector<double>>& matrix, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return "Error: Cannot open file for writing";
    }
    
    int num_cores = static_cast<int>(matrix.size());
    
    file << " ,";
    for (int j = 0; j < num_cores; ++j) {
        file << "Core" << j;
        if (j < num_cores - 1) file << ",";
    }
    file << "\n";
    
    for (int i = 0; i < num_cores; ++i) {
        file << "Core" << i << ",";
        for (int j = 0; j < num_cores; ++j) {
            file << std::fixed << std::setprecision(2) << matrix[i][j];
            if (j < num_cores - 1) file << ",";
        }
        file << "\n";
    }
    
    file.close();
    return "Saved to " + filename;
}

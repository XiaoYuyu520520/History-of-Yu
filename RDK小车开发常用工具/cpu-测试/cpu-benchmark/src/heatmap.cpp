#include "../include/cpu_benchmark.h"
#include <vector>
#include <algorithm>
#include <cmath>
#include <string>
#include <fstream>
#include <cstring>
#include <zlib.h>

namespace {
    
    void write_be32(std::ofstream& f, uint32_t val) {
        f.put(static_cast<char>((val >> 24) & 0xff));
        f.put(static_cast<char>((val >> 16) & 0xff));
        f.put(static_cast<char>((val >> 8) & 0xff));
        f.put(static_cast<char>(val & 0xff));
    }
    
    uint32_t crc32_table[256];
    bool crc32_init = false;
    
    void init_crc32() {
        if (crc32_init) return;
        for (uint32_t i = 0; i < 256; i++) {
            uint32_t c = i;
            for (int j = 0; j < 8; j++) {
                c = (c >> 1) ^ (c & 1 ? 0xedb88320 : 0);
            }
            crc32_table[i] = c;
        }
        crc32_init = true;
    }
    
    uint32_t crc32(const unsigned char* data, int len) {
        init_crc32();
        uint32_t crc = 0xffffffff;
        for (int i = 0; i < len; i++) {
            crc = crc32_table[(crc ^ data[i]) & 0xff] ^ (crc >> 8);
        }
        return crc ^ 0xffffffff;
    }
    
    void apply_color(unsigned char* pixel, double value, double min_val, double max_val) {
        double normalized = (value - min_val) / (max_val - min_val);
        normalized = std::max(0.0, std::min(1.0, normalized));
        
        double r, g, b;
        
        if (normalized < 0.25) {
            r = 0;
            g = normalized * 4 * 255;
            b = 255;
        } else if (normalized < 0.5) {
            r = 0;
            g = 255;
            b = (1.0 - (normalized - 0.25) * 4) * 255;
        } else if (normalized < 0.75) {
            r = (normalized - 0.5) * 4 * 255;
            g = 255;
            b = 0;
        } else {
            r = 255;
            g = (1.0 - (normalized - 0.75) * 4) * 255;
            b = 0;
        }
        
        pixel[0] = static_cast<unsigned char>(r);
        pixel[1] = static_cast<unsigned char>(g);
        pixel[2] = static_cast<unsigned char>(b);
    }
}

bool HeatmapGenerator::generate_heatmap(const std::vector<std::vector<double>>& matrix, 
                                        const std::string& filename,
                                        int cell_size) {
    int num_cores = static_cast<int>(matrix.size());
    int width = num_cores * cell_size + 40;
    int height = num_cores * cell_size + 20;
    int img_width = width;
    int img_height = height;
    
    std::vector<unsigned char> image(img_width * img_height * 3, 255);
    
    double min_val = 0.0;
    double max_val = 0.0;
    
    for (int i = 0; i < num_cores; ++i) {
        for (int j = 0; j < num_cores; ++j) {
            if (i != j && matrix[i][j] > 0) {
                max_val = std::max(max_val, matrix[i][j]);
            }
        }
    }
    if (max_val == 0.0) max_val = 100.0;
    
    for (int i = 0; i < num_cores; ++i) {
        for (int j = 0; j < num_cores; ++j) {
            int x = j * cell_size + 20;
            int y = i * cell_size + 10;
            
            unsigned char pixel[3];
            apply_color(pixel, matrix[i][j], min_val, max_val);
            
            for (int py = 0; py < cell_size; ++py) {
                for (int px = 0; px < cell_size; ++px) {
                    int idx = ((y + py) * img_width + (x + px)) * 3;
                    image[idx] = pixel[0];
                    image[idx + 1] = pixel[1];
                    image[idx + 2] = pixel[2];
                }
            }
        }
    }
    
    std::ofstream f(filename, std::ios::binary);
    if (!f.is_open()) return false;
    
    f.put(0x89);
    f.put(0x50);
    f.put(0x4E);
    f.put(0x47);
    f.put(0x0D);
    f.put(0x0A);
    f.put(0x1A);
    f.put(0x0A);
    
    write_be32(f, 13);
    f.put('I');
    f.put('H');
    f.put('D');
    f.put('R');
    write_be32(f, img_width);
    write_be32(f, img_height);
    f.put(8);
    f.put(2);
    f.put(0);
    f.put(0);
    f.put(0);
    
    unsigned char ihdr_crc[15] = {0x00, 0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    write_be32(f, crc32(ihdr_crc, 15));
    
    int raw_len = img_width * img_height * 3 + img_height;
    std::vector<unsigned char> raw_data(raw_len);
    int raw_idx = 0;
    for (int y = 0; y < img_height; y++) {
        raw_data[raw_idx++] = 0;
        for (int x = 0; x < img_width; x++) {
            int idx = (y * img_width + x) * 3;
            raw_data[raw_idx++] = image[idx];
            raw_data[raw_idx++] = image[idx + 1];
            raw_data[raw_idx++] = image[idx + 2];
        }
    }
    
    uLongf comp_len = raw_len;
    std::vector<unsigned char> comp_data(raw_len);
    compress2(comp_data.data(), &comp_len, raw_data.data(), raw_len, 9);
    
    write_be32(f, static_cast<uint32_t>(comp_len));
    f.put('I');
    f.put('D');
    f.put('A');
    f.put('T');
    f.write(reinterpret_cast<const char*>(comp_data.data()), comp_len);
    
    std::vector<unsigned char> crc_data(comp_len + 4);
    crc_data[0] = 'I';
    crc_data[1] = 'D';
    crc_data[2] = 'A';
    crc_data[3] = 'T';
    memcpy(crc_data.data() + 4, comp_data.data(), comp_len);
    write_be32(f, crc32(crc_data.data(), static_cast<int>(comp_len + 4)));
    
    write_be32(f, 0);
    f.put('I');
    f.put('E');
    f.put('N');
    f.put('D');
    unsigned char iend_crc[8] = {0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60};
    write_be32(f, crc32(iend_crc, 8));
    
    f.close();
    return true;
}

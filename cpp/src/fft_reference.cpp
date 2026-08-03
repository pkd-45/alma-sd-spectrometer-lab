#include <algorithm>
#include <cmath>
#include <complex>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr double pi = 3.141592653589793238462643383279502884;

bool is_power_of_two(std::size_t n) { return n > 0 && (n & (n - 1)) == 0; }

void fft(std::vector<std::complex<double>>& values) {
    const std::size_t n = values.size();
    if (!is_power_of_two(n)) {
        throw std::invalid_argument("FFT size must be a power of two");
    }
    for (std::size_t i = 1, j = 0; i < n; ++i) {
        std::size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) {
            std::swap(values[i], values[j]);
        }
    }
    for (std::size_t length = 2; length <= n; length <<= 1) {
        const double angle = -2.0 * pi / static_cast<double>(length);
        const std::complex<double> wlen(std::cos(angle), std::sin(angle));
        for (std::size_t i = 0; i < n; i += length) {
            std::complex<double> w(1.0, 0.0);
            for (std::size_t j = 0; j < length / 2; ++j) {
                const auto u = values[i + j];
                const auto v = values[i + j + length / 2] * w;
                values[i + j] = u + v;
                values[i + j + length / 2] = u - v;
                w *= wlen;
            }
        }
    }
}

int self_test() {
    constexpr std::size_t n = 1024;
    constexpr std::size_t expected_bin = 37;
    std::vector<std::complex<double>> samples(n);
    for (std::size_t index = 0; index < n; ++index) {
        const double phase = 2.0 * pi * static_cast<double>(expected_bin * index) /
                             static_cast<double>(n);
        samples[index] = std::sin(phase);
    }
    fft(samples);
    std::size_t peak_bin = 1;
    double peak_power = 0.0;
    for (std::size_t bin = 1; bin <= n / 2; ++bin) {
        const double power = std::norm(samples[bin]);
        if (power > peak_power) {
            peak_power = power;
            peak_bin = bin;
        }
    }
    std::cout << std::setprecision(12)
              << "{\"fft_size\":" << n << ",\"peak_bin\":" << peak_bin
              << ",\"peak_power\":" << peak_power << "}\n";
    return peak_bin == expected_bin ? EXIT_SUCCESS : EXIT_FAILURE;
}
}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            return self_test();
        }
        std::cerr << "Usage: alma_fft_reference --self-test\n";
        return EXIT_FAILURE;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}

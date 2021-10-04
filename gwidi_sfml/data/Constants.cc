#include "Constants.h"

std::vector<int>& Constants::octaves() {
    static std::vector<int> v = { 0, 1, 2, 3, 4, 5, 6, 7, 8 };
    return v;
}
// TODO: 200 is throwing bad alloc, run with memcheck / asan
// TODO: Once data is done, use that to determine what to build instead of the counts of rows / cols / etc
int Constants::measure_count = 100;
int Constants::slots_per_measure = 16;
std::unordered_map<const char*, int> Constants::notes = {
        {"C2", 8},
        {"B", 7},
        {"A", 6},
        {"G", 5},
        {"F", 4},
        {"E", 3},
        {"D", 2},
        {"C1", 1},
};

int UiConstants::slot_width = 35;
int UiConstants::slot_height = 20;
int UiConstants::octave_spacing = 10;
int UiConstants::measure_spacing = 10;
int UiConstants::measure_label_height = 20;

int UiConstants::measure_width = Constants::slots_per_measure * UiConstants::slot_width;
int UiConstants::measure_height = Constants::notes.size() * UiConstants::slot_height;

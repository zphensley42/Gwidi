#ifndef GWIDI_SFML_CONSTANTS_H
#define GWIDI_SFML_CONSTANTS_H

#include <vector>
#include <unordered_map>
#include <cstdint>

struct Constants {
    static int slots_per_measure;
    static int measure_count;
    static std::vector<int> octaves;
    static std::unordered_map<const char*, int> notes;
};

struct UiConstants {
    static int slot_width;
    static int slot_height;
    static int octave_spacing;
    static int measure_spacing;

    static int measure_width;
    static int measure_height;

    enum Note_RowType {
        NOTE = 0,
        OCTAVE_SPACING = 1
    };

    enum Slot_ColType {
        SLOT = 0,
        MEASURE_SPACING = 1
    };
};

#endif //GWIDI_SFML_CONSTANTS_H

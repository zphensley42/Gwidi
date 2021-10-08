#include <cstdint>
#include "Note.h"
#include "Slot.h"
#include <sstream>

Note::Note() : Note(EMPTY_IDENTIFIER, UiConstants::Note_RowType::NOTE) {}

Note::Note(Identifier id) : UiView(id) {
    int cols = Constants::slots_per_measure;
    int width = cols * UiConstants::slot_width;
    int height = UiConstants::slot_height;
    int y = UiConstants::slot_height * id.note_index;
    for(int c = 0; c < cols; c++) {
        m_bounds.top_left = {0, y};
        m_bounds.bottom_left = {0, y + height};
        m_bounds.top_right = {width, y};
        m_bounds.bottom_right = {width, y + height};

        m_slots.emplace_back(Slot{{0, 0, id.note_index, c}});
    }
}

Note::Note(gwidi::data::Note& note, Identifier id) : UiView(id) {
    int cols = note.slots().size();
    int width = cols * UiConstants::slot_width;
    int height = UiConstants::slot_height;
    int y = UiConstants::slot_height * id.note_index;
    for(int c = 0; c < cols; c++) {
        m_bounds.top_left = {0, y};
        m_bounds.bottom_left = {0, y + height};
        m_bounds.top_right = {width, y};
        m_bounds.bottom_right = {width, y + height};

        m_slots.emplace_back(Slot{note.slots()[c], {m_id.octave_index, m_id.measure_index, id.note_index, c}});
    }
}

Note::Note(Identifier& id, UiConstants::Note_RowType type) : m_type{type} {
    int octaves_height_offset = id.octave_index * (Constants::notes.size() * UiConstants::slot_height);
    int note_height_offset = id.note_index * UiConstants::slot_height;
    int octaves_spacing_offset = id.octave_index * UiConstants::octave_spacing;

    int measure_width = (Constants::slots_per_measure * UiConstants::slot_width);
    int measure_width_offset = id.measure_index * (Constants::slots_per_measure * UiConstants::slot_width);
    int measure_spacing_offset = id.measure_index * UiConstants::measure_spacing;

    switch (m_type) {
        case UiConstants::Note_RowType::NOTE: {
            int64_t cols = Constants::slots_per_measure * Constants::measure_count;
            for(size_t i = 0; i < cols; i++) {
                Identifier slot_id{};
                slot_id.octave_index = id.octave_index;
                slot_id.note_index = id.note_index;
                slot_id.measure_index = int(i / Constants::slots_per_measure);
                slot_id.slot_index = int(i % Constants::slots_per_measure);
                auto is_spacer = slot_id.slot_index == 0;
                if(is_spacer && i > 0) {
                    m_slots.emplace_back(Slot(slot_id, UiConstants::Slot_ColType::MEASURE_SPACING));
                }
                m_slots.emplace_back(Slot(slot_id, UiConstants::Slot_ColType::SLOT));
            }

            m_bounds.top_left.x = 0;
            m_bounds.top_left.y = octaves_height_offset + octaves_spacing_offset + note_height_offset;

            m_bounds.bottom_left.x = 0;
            m_bounds.bottom_left.y = m_bounds.top_left.y + UiConstants::slot_height;

            // Width is determined by our slots
            m_bounds.top_right.x = m_slots.back().bounds().top_right.x;
            m_bounds.top_right.y = m_bounds.top_left.y;

            m_bounds.bottom_right.x = m_slots.back().bounds().top_right.x;
            m_bounds.bottom_right.y = m_bounds.bottom_left.y;
            break;
        }
        case UiConstants::Note_RowType::OCTAVE_SPACING: {
            // No slots in a spacing row
            // Use different spacings to determine our positions (min/max)

            m_bounds.top_left.x = measure_width_offset + measure_spacing_offset;
            m_bounds.top_left.y = octaves_height_offset + octaves_spacing_offset + note_height_offset;

            m_bounds.bottom_left.x = measure_width_offset + measure_spacing_offset;
            m_bounds.bottom_left.y = m_bounds.top_left.y + UiConstants::octave_spacing;

            // TODO: Need to calc the width properly as octave spacing still draws something
            m_bounds.top_right.x = m_bounds.top_left.x + measure_width;
            m_bounds.top_right.y = m_bounds.top_left.y;

            m_bounds.bottom_right.x = m_bounds.bottom_left.x + measure_width;
            m_bounds.bottom_right.y = m_bounds.bottom_left.y;
            break;
        }
    }
}

Note::operator std::string() const {
    std::stringstream ss;
    ss << "Note{ ";
    ss << "bounds: " << (std::string)m_bounds << std::endl;
    for(auto &slot : m_slots) {
        ss << (std::string)slot;
    }
    ss << "}" << std::endl;
    return ss.str();
}

#include "Slot.h"
#include <sstream>
#include "../gui/LayoutManager.h"

Slot::Slot() : Slot(Identifier{}, UiConstants::Slot_ColType::SLOT) {}

Slot::Slot(Identifier id) : UiView(id) {
    int width = UiConstants::slot_width;
    int height = UiConstants::slot_height;
    int y = id.note_index * UiConstants::slot_height;
    int x = id.slot_index * UiConstants::slot_width;

    m_bounds.top_left = {x, y};
    m_bounds.bottom_left = {x, y + height};
    m_bounds.top_right = {x + width, y};
    m_bounds.bottom_right = {x + width, y + height};

    auto noteIt = std::find_if(Constants::notes.begin(), Constants::notes.end(),[&id](std::unordered_map<const char*, int>::value_type &entry) {
        return entry.second == (Constants::notes.size() - id.note_index);
    });
    std::string noteLabel = "Note Not Found";
    if(noteIt != Constants::notes.end()) {
        noteLabel = noteIt->first;
    }
    m_noteLabel.setFont(LayoutManager::instance().mainFont());
    m_noteLabel.setString(noteLabel);
    m_noteLabel.setCharacterSize(10);
    m_noteLabel.setFillColor(sf::Color::Black);
    m_noteLabel.setPosition(m_bounds.top_left.x, m_bounds.top_left.y);
}

Slot::Slot(gwidi::data::Slot& slot, Identifier id) : UiView(id) {
    switch(slot.state()) {
        case gwidi::data::Slot::State::SLOT_ACTIVATED: {
            m_drawState = DrawState::DS_ACTIVATED;
            break;
        }
        case gwidi::data::Slot::State::SLOT_HELD: {
            m_drawState = DrawState::DS_HELD;
            break;
        }
    }

    int width = UiConstants::slot_width;
    int height = UiConstants::slot_height;
    int y = id.note_index * UiConstants::slot_height;
    int x = id.slot_index * UiConstants::slot_width;

    m_bounds.top_left = {x, y};
    m_bounds.bottom_left = {x, y + height};
    m_bounds.top_right = {x + width, y};
    m_bounds.bottom_right = {x + width, y + height};

    auto noteIt = std::find_if(Constants::notes.begin(), Constants::notes.end(),[&id](std::unordered_map<const char*, int>::value_type &entry) {
        return entry.second == (Constants::notes.size() - id.note_index);
    });
    std::string noteLabel = "Note Not Found";
    if(noteIt != Constants::notes.end()) {
        noteLabel = noteIt->first;
    }
    m_noteLabel.setFont(LayoutManager::instance().mainFont());
    m_noteLabel.setString(noteLabel);
    m_noteLabel.setCharacterSize(10);
    m_noteLabel.setFillColor(sf::Color::Black);
    m_noteLabel.setPosition(m_bounds.top_left.x, m_bounds.top_left.y);
}

Slot::Slot(Identifier id, UiConstants::Slot_ColType type) : m_type{type} {
    int octaves_height_offset = id.octave_index * (Constants::notes.size() * UiConstants::slot_height);
    int note_height_offset = id.note_index * UiConstants::slot_height;
    int octaves_spacing_offset = id.octave_index * UiConstants::octave_spacing;

    int measure_width_offset = id.measure_index * (Constants::slots_per_measure * UiConstants::slot_width);
    int measure_spacing_offset = id.measure_index * UiConstants::measure_spacing;
    int slot_width_offset = id.slot_index * UiConstants::slot_width;

    switch (m_type) {
        case UiConstants::Slot_ColType::SLOT: {
            // Use different spacings to determine our positions (min/max)
            m_bounds.top_left.x = measure_width_offset + measure_spacing_offset + slot_width_offset;
            m_bounds.top_left.y = octaves_height_offset + octaves_spacing_offset + note_height_offset;

            m_bounds.bottom_left.x = m_bounds.top_left.x;
            m_bounds.bottom_left.y = m_bounds.top_left.y + UiConstants::slot_height;

            // Spacing has no width
            m_bounds.top_right.x = m_bounds.top_left.x + UiConstants::slot_width;
            m_bounds.top_right.y = m_bounds.top_left.y;

            m_bounds.bottom_right.x = m_bounds.top_right.x;
            m_bounds.bottom_right.y = m_bounds.bottom_left.y;
            break;
            break;
        }
        case UiConstants::Slot_ColType::MEASURE_SPACING: {
            // Use different spacings to determine our positions (min/max)
            m_bounds.top_left.x = measure_width_offset + measure_spacing_offset + slot_width_offset;
            m_bounds.top_left.y = octaves_height_offset + octaves_spacing_offset + note_height_offset;

            m_bounds.bottom_left.x = m_bounds.top_left.x;
            m_bounds.bottom_left.y = m_bounds.top_left.y + UiConstants::slot_height;

            // Spacing has no height
            m_bounds.top_right.x = m_bounds.top_left.x + UiConstants::measure_spacing;
            m_bounds.top_right.y = m_bounds.top_left.y;

            m_bounds.bottom_right.x = m_bounds.top_right.x;
            m_bounds.bottom_right.y = m_bounds.bottom_left.y;
            break;
        }
    }
}

Slot::operator std::string() const {
    std::stringstream ss;
    ss << "Slot{ ";
    ss << "bounds: " << (std::string)m_bounds;
    ss << " }" << std::endl;
    return ss.str();
}

// TODO: Foreground/background transparency
void Slot::draw_foreground(sf::Uint8 *pixels, Coord2D &size) {
    m_lastSize = size;

    sf::Color color{sf::Color::White};
    switch(m_drawState) {
        case DS_ACTIVATED: {
            color = sf::Color::Green;
            break;
        }
        case DS_HELD: {
            color = sf::Color::Cyan;
            break;
        }
        default: {
            color = sf::Color::White;
            break;
        }
    }

    switch(m_playState) {
        case PS_PLAYING: {
            color = sf::Color::Blue;
            break;
        }
        default: {
            break;
        }
    }
    color.a = 150;
    m_bounds.assignToPixels(pixels, size, color, {1, 1});
}

void Slot::draw_background(sf::Uint8 *pixels, Coord2D &size) {
    m_lastSize = size;

    sf::Color color{sf::Color::White};
    switch(m_drawState) {
        case DS_ACTIVATED: {
            color = sf::Color::Green;
            break;
        }
        case DS_HELD: {
            color = sf::Color::Cyan;
            break;
        }
        default: {
            color = sf::Color::White;
            break;
        }
    }

    switch(m_playState) {
        case PS_PLAYING: {
            color = sf::Color::Blue;
            break;
        }
        default: {
            break;
        }
    }
    m_bounds.assignToPixels(pixels, size, color, {2, 2});
}


// TODO: Draw this to render texture (measure should pull that out and use it to fill the sprite)
void Slot::drawText(sf::RenderTexture &targetTexture, sf::Vector2f offset) {
    m_noteLabel.setPosition(m_bounds.top_left.x + offset.x, m_bounds.top_left.y + offset.y);
    targetTexture.draw(m_noteLabel);
}
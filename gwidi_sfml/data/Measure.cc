#include <iostream>
#include "Measure.h"

Measure::Measure() : Measure(Identifier{}) {}

Measure::Measure(Identifier id) : UiView(id) {

    // Build our notes/slots from the id information / constants
    int rows = Constants::notes.size();
    for(int r = 0; r < rows; r++) {
        m_notes.emplace_back(Note{{id.octave_index, id.measure_index, r, 0}});
    }

    m_bounds.top_left = {m_notes.front().bounds().top_left.x, m_notes.front().bounds().top_left.y};
    m_bounds.top_right = {m_notes.front().bounds().top_right.x, m_notes.front().bounds().top_right.y};
    m_bounds.bottom_left = {m_notes.back().bounds().bottom_left.x, m_notes.back().bounds().bottom_left.y};
    m_bounds.bottom_right = {m_notes.back().bounds().bottom_right.x, m_notes.back().bounds().bottom_right.y};
}

void Measure::build(sf::Vector2f offset) {
    m_initialPos = offset;
    auto size = m_bounds.size();
    m_image_pixels = new sf::Uint8[size.x * size.y * 4];  // entries are utf32, but the type is utf8 so we need to mult by 4
    for(auto &n : m_notes) {
        for(auto &s : n.slots()) {
            s.draw(m_image_pixels, size);
        }
    }
    m_image.create(size.x, size.y, m_image_pixels);
    m_texture.create(size.x, size.y);
    m_texture.update(m_image);
    m_sprite.setTexture(m_texture);
    m_sprite.setPosition(m_initialPos);
}

void Measure::scroll(sf::Vector2f offset) {
    m_sprite.setPosition(m_initialPos + offset);
}

Slot* Measure::slotIndexForMouse(int x, int y) {
    auto g_bounds = m_sprite.getGlobalBounds();
    if(g_bounds.contains(x, y)) {
        // Get index via the slot width / height vs bounds
        float offset_x = x - g_bounds.left;
        float offset_y = y - g_bounds.top;
        int slot_index = static_cast<int>((offset_x / float(UiConstants::measure_width)) * float(Constants::slots_per_measure));
        int note_index = static_cast<int>((offset_y / float(UiConstants::measure_height)) * float(Constants::notes.size()));

        std::cout << "slot index found for mouse: " << slot_index << ", " << note_index << std::endl;
        auto &slot = m_notes[note_index].slots()[slot_index];

        // Use these indices / this measure to trigger the slot
        slot.updateStates(Slot::DrawState::DS_ACTIVATED, slot.playState());
//        if(m_last_window) {
            m_texture.update(m_image_pixels);
            m_sprite.setTexture(m_texture);
//            m_last_window->draw(m.sprite());
//        }
        return &slot;
    }
    return nullptr;
}
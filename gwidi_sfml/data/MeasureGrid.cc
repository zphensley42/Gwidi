#include "MeasureGrid.h"
#include "Slot.h"
#include "Note.h"
#include "Constants.h"
#include <sstream>
#include <SFML/Graphics.hpp>
#include <iostream>
#include "../events/ThreadPool.h"

MeasureGrid::MeasureGrid(bool splitMeasures) {
    if(splitMeasures) {
        int measures = Constants::measure_count;
        for(int m = 0; m < measures; m++) {
            for(int o : Constants::octaves) {
                m_measures.emplace_back(Measure{{o, m, 0, 0}});
            }
        }

        for(auto &m : m_measures) {
            auto size = m.bounds().size();
            int x = (m.id().measure_index * size.x) + (m.id().measure_index * UiConstants::measure_spacing);
            int y = (m.id().octave_index * size.y) + (m.id().octave_index * UiConstants::octave_spacing);
            m.build(sf::Vector2f(x, y));
        }

        // Each measure needs to be positioned according to their bounds + their indices
        return;
    }

    int64_t rows = Constants::notes.size() * Constants::octaves.size();
    for(size_t i = 0; i < rows; i++) {
        Identifier id{};
        id.note_index = int(i % Constants::notes.size());
        id.octave_index = int(i / Constants::notes.size());
        auto is_spacer = id.note_index == 0;
        if(is_spacer && i > 0) {
            m_notes.emplace_back(Note(id, UiConstants::Note_RowType::OCTAVE_SPACING));
        }
        m_notes.emplace_back(Note(id, UiConstants::Note_RowType::NOTE));
    }

    // TODO: Separate into multiple textures as the size is way too high for # of measures (maybe 1 texture per measure?)

    int content_height = m_notes.back().bounds().bottom_left.y;
    int content_width = m_notes.front().bounds().top_right.x;
    m_bounds.top_left = {0, 0};
    m_bounds.bottom_left = {0, content_height};
    m_bounds.top_right = {content_width, 0};
    m_bounds.bottom_right = {content_width, content_height};
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
}

MeasureGrid::operator std::string() const {
    std::stringstream ss;
    ss << "Grid{" << std::endl;
    for(auto &note : m_notes) {
        ss << (std::string)note;
    }
    ss << "}" << std::endl;
    return ss.str();
}

void MeasureGrid::draw(sf::RenderWindow &window) {
    m_last_window = &window;
    // scroll should move the image instead of the squares
//    m_sprite.setPosition(sf::Vector2f(m_scroll_x, m_scroll_y));
//    window.draw(m_sprite);

    // TODO: Don't construct the vector here, just use it
    for(auto &m : m_measures) {
        m.scroll(sf::Vector2f(m_scroll_x, m_scroll_y));
        window.draw(m.sprite());
    }
}

void MeasureGrid::onScrolled(int x, int y) {
    m_scroll_x = x;
    m_scroll_y = y;
}

bool MeasureGrid::onLeftDown(int x, int y) {
    ThreadPool::instance().schedule([this, x, y]() {
        for(auto &m : m_measures) {
            auto slot = m.slotIndexForMouse(x, y);
            if(slot) {
                // Use these indices / this measure to trigger the slot
                std::cout << "onLeftDown measure found {o: " << m.id().octave_index << ", m: " << m.id().measure_index << "}" << std::endl;
                return true;
            }
        }
    });
    return false;
}

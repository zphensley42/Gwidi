#include "MeasureGrid.h"
#include "Slot.h"
#include "Note.h"
#include "Constants.h"
#include <sstream>
#include <SFML/Graphics.hpp>
#include <iostream>
#include "../events/ThreadPool.h"
#include "../gui/LayoutManager.h"

MeasureGrid::MeasureGrid(bool splitMeasures) {
    if(splitMeasures) {
        int measures = Constants::measure_count;
        for(int m = 0; m < measures; m++) {
            for(int o : Constants::octaves()) {
                m_measures.emplace_back(Measure{{o, m, 0, 0}});
            }
        }

        for(auto &m : m_measures) {
            auto size = m.bounds().size();
            int x = (m.id().measure_index * size.x) + (m.id().measure_index * UiConstants::measure_spacing);
            int y = (m.id().octave_index * size.y) + (m.id().octave_index * UiConstants::octave_spacing);
            m.build(sf::Vector2f(x, y));
        }

        auto front_bounds = m_measures.front().globalBounds();
        auto back_bounds = m_measures.back().globalBounds();

        // Each measure needs to be positioned according to their bounds + their indices
        m_bounds.top_left = {static_cast<int>(front_bounds.left), static_cast<int>(front_bounds.top)};
        m_bounds.bottom_right = {static_cast<int>(back_bounds.left + back_bounds.width), static_cast<int>(back_bounds.top + back_bounds.height)};

        int w = m_bounds.bottom_right.x - m_bounds.top_left.x;
        int h = m_bounds.bottom_right.y - m_bounds.top_left.y;
        m_bounds.bottom_left = {m_bounds.top_left.x, m_bounds.top_left.y + h};
        m_bounds.top_right = {m_bounds.top_left.x + w, m_bounds.top_left.y};

        return;
    }
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

void MeasureGrid::draw(sf::RenderWindow &window, sf::View &target, sf::Vector2f position) {
    // scroll should move the image instead of the squares
    // TODO: Don't construct the vector here, just use it
    for(auto &m : m_measures) {
        sf::Vector2f offset{position.x + m_scroll_x, position.y + m_scroll_y};
        m.scroll(sf::Vector2f(offset.x, offset.y));
        window.setView(target);
        m.draw();
    }

    // TODO: Draw measure / octave labels
}

void MeasureGrid::onScrolled(int x, int y) {
    m_scroll_x = x;
    m_scroll_y = y;
}

bool MeasureGrid::onLeftDown(int x, int y) {
    // Need to determine the proper x/y position by coordinate conversion since the measures are in a view now
    auto mappedCoords = LayoutManager::instance().window()->mapPixelToCoords({x, y}, LayoutManager::instance().contentTarget());
    ThreadPool::instance().schedule([this, mappedCoords]() {
        for(auto &m : m_measures) {
            auto slot = m.slotIndexForMouse(mappedCoords.x, mappedCoords.y);
            if(slot) {
                // Use these indices / this measure to trigger the slot
                std::cout << "onLeftDown measure found {o: " << m.id().octave_index << ", m: " << m.id().measure_index << "}" << std::endl;
                return true;
            }
        }
    });
    return false;
}

void MeasureGrid::onLeftUp(int x, int y) {
    ThreadPool::instance().schedule([this]() {
        for(auto &m : m_measures) {
            m.clearTriggeredSlotsStatus();
        }
    });
}

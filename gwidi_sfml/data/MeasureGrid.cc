#include "MeasureGrid.h"
#include "Slot.h"
#include "Note.h"
#include "Constants.h"
#include <sstream>
#include <SFML/Graphics.hpp>
#include <iostream>
#include "../events/ThreadPool.h"
#include "../gui/LayoutManager.h"

MeasureGrid::MeasureGrid() {
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
}

MeasureGrid::MeasureGrid(gwidi::data::Track &track) {
    auto& measures = track.measures();
    for(int m = 0; m < measures.size(); m++) {
        auto& octaves = measures[m].octaves();
        for(int o = 0; o < octaves.size(); o++) {
            m_measures.emplace_back(Measure{octaves[o], {o, m, 0, 0}});
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

bool MeasureGrid::onMouseMove(int x, int y) {
    if(m_dragDown) {
        auto diffX = m_last_frame_x - x;
        auto diffY = m_last_frame_y - y;

        m_scroll_x -= diffX;
        m_scroll_y -= diffY;

        m_last_frame_x = x;
        m_last_frame_y = y;

        clampScrollValues();
    }
    else if(m_selectDown) {
        performIndexChecks(x, y, m_last_down_but == 2); // todo: use stack for last buttons?
    }

    return false;
}

bool MeasureGrid::onMouseDown(int x, int y, int but) {
    if(but == 1) {
        if(!m_dragDown) {
            m_last_frame_x = x;
            m_last_frame_y = y;
        }
        m_dragDown = true;
        return true;
    }
    else if(!m_dragDown && (but == 0 || but == 2)) {
        m_selectDown = true;
        m_last_down_but = but;
        return performIndexChecks(x, y, but == 2);
    }
    return false;
}

bool MeasureGrid::onMouseUp(int but) {
    if(but == 1) {
        m_dragDown = false;
        return true;
    }
    else {
        m_selectDown = false;
        clearTriggeredIndices();
    }

    return false;
}



void MeasureGrid::clearTriggeredIndices() {
    ThreadPool::instance().schedule([this]() {
        for(auto &m : m_measures) {
            m.clearTriggeredSlotsStatus();
        }
    });
}

bool MeasureGrid::performIndexChecks(int x, int y, bool remove) {
    // Need to determine the proper x/y position by coordinate conversion since the measures are in a view now
    auto mappedCoords = LayoutManager::instance().window()->mapPixelToCoords({x, y}, LayoutManager::instance().contentTarget());
    ThreadPool::instance().schedule([this, mappedCoords, remove]() {
        for(auto &m : m_measures) {
            auto slot = m.slotIndexForMouse(mappedCoords.x, mappedCoords.y, remove);
            if(slot) {
                // Use these indices / this measure to trigger the slot
                std::cout << "onMouseDown measure found {o: " << m.id().octave_index << ", m: " << m.id().measure_index << "}" << std::endl;
                return true;
            }
        }
    });
    return false;
}



void MeasureGrid::setScrollAmountLimits(int min_x, int max_x, int min_y, int max_y) {
    m_scroll_x_min = min_x;
    m_scroll_x_max = max_x;
    m_scroll_y_min = min_y;
    m_scroll_y_max = max_y;

    clampScrollValues();
}


void MeasureGrid::clampScrollValues() {
    if(m_scroll_x < m_scroll_x_min) {
        m_scroll_x = m_scroll_x_min;
    }
    if(m_scroll_x > m_scroll_x_max) {
        m_scroll_x = m_scroll_x_max;
    }
    if(m_scroll_y < m_scroll_y_min) {
        m_scroll_y = m_scroll_y_min;
    }
    if(m_scroll_y > m_scroll_y_max) {
        m_scroll_y = m_scroll_y_max;
    }
}


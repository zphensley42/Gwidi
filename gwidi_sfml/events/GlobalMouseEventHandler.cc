#include <iostream>
#include "GlobalMouseEventHandler.h"

void GlobalMouseEventHandler::handleMouseDown(int but, int x, int y) {
    // If already dragging with right click, do nothing until we stop
    if(m_isDragging) {
        return;
    }
    m_isDown = true;
    m_down_mouse_but = but;
    m_last_frame_x = x;
    m_last_frame_y = y;
}

void GlobalMouseEventHandler::handleMouseUp() {
    m_isDown = false;
    m_isDragging = false;
    m_last_frame_x = 0;
    m_last_frame_y = 0;
}

// TODO: Offload mouse-over detection? (i.e. don't loop over all slots while drawing)
void GlobalMouseEventHandler::handleMouseMove(int x, int y) {
    if(m_isDown) {
        m_isDragging = true;
    }
    else {
        return;
    }

    if(m_down_mouse_but == 1) {
        // When dragging, track how much we drag so we can 'scroll' the view
        m_scroll_x += x - m_last_frame_x;
        m_scroll_y += y - m_last_frame_y;
        clampScrollValues();

        m_last_frame_x = x;
        m_last_frame_y = y;

//        std::cout << "scroll_x: " << m_scroll_x << ", scroll_y: " << m_scroll_y << std::endl;

        for(auto& cb : m_cbs) {
            cb->onScrolled(m_scroll_x, m_scroll_y);
        }
    }
    else if(m_down_mouse_but == 0) {
        for(auto& cb : m_cbs) {
            if(cb->onLeftDown(x, y)) {
                break;
            }
        }
    }
}

void GlobalMouseEventHandler::subscribe(const std::shared_ptr<Callback>& cb) {
    m_cbs.push_back(cb);
}

void GlobalMouseEventHandler::unsubscribe(const std::shared_ptr<Callback> &cb) {
    m_cbs.remove_if([cb](std::shared_ptr<Callback> &c){ return c == cb; });
}

void GlobalMouseEventHandler::setScrollAmountLimits(int min_x, int max_x, int min_y, int max_y) {
    m_scroll_x_min = min_x;
    m_scroll_x_max = max_x;
    m_scroll_y_min = min_y;
    m_scroll_y_max = max_y;

    clampScrollValues();
}

void GlobalMouseEventHandler::clampScrollValues() {
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

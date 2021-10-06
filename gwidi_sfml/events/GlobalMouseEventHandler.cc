#include <iostream>
#include "GlobalMouseEventHandler.h"

void GlobalMouseEventHandler::handleMouseDown(int but, int x, int y) {
    for(auto& cb : m_cbs) {
        if(cb->onMouseDown(x, y, but)) {
            m_cbOverride = cb;
            break;
        }
    }
}

void GlobalMouseEventHandler::handleMouseUp(int but) {
    for(auto& cb : m_cbs) {
        if(m_cbOverride && cb == m_cbOverride && cb->onMouseUp(but)) {
            m_cbOverride = nullptr;
            cb->onMouseUp(but);
        }
        else if(!m_cbOverride) {
            cb->onMouseUp(but);
        }
    }
}

// TODO: Offload mouse-over detection? (i.e. don't loop over all slots while drawing)
void GlobalMouseEventHandler::handleMouseMove(int x, int y) {
    for(auto& cb : m_cbs) {
        if(m_cbOverride && cb == m_cbOverride) {
            if(cb->onMouseMove(x, y)) {
                break;
            }
        }
        else if(!m_cbOverride) {
            if(cb->onMouseMove(x, y)) {
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

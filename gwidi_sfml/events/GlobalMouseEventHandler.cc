#include <iostream>
#include "GlobalMouseEventHandler.h"

void GlobalMouseEventHandler::handleMouseDown(int but, int x, int y) {
    for(auto& cb : m_cbs) {
        cb->onMouseDown(x, y, but);
    }
}

void GlobalMouseEventHandler::handleMouseUp(int but) {
    for(auto& cb : m_cbs) {
        cb->onMouseUp(but);
    }
}

// TODO: Offload mouse-over detection? (i.e. don't loop over all slots while drawing)
void GlobalMouseEventHandler::handleMouseMove(int x, int y) {
    for(auto& cb : m_cbs) {
        cb->onMouseMove(x, y);
    }
}

void GlobalMouseEventHandler::subscribe(const std::shared_ptr<Callback>& cb) {
    m_cbs.push_back(cb);
}

void GlobalMouseEventHandler::unsubscribe(const std::shared_ptr<Callback> &cb) {
    m_cbs.remove_if([cb](std::shared_ptr<Callback> &c){ return c == cb; });
}

#include "ControlBar.h"
#include "LayoutManager.h"

ControlBar::ControlBar() : UiView() {

}

void ControlBar::draw(sf::Vector2<int> position) {

    auto* window = LayoutManager::instance().window();
    window->setView(LayoutManager::instance().controlsTarget());

    m_bounds.top_left = {0, 0};
    m_bounds.top_right = {100, 0};
    m_bounds.bottom_left = {0, 50};
    m_bounds.bottom_right = {100, 50};
    auto size = m_bounds.size();

    // TODO: Assign size instead of wrap?
    m_playBut.init("Play", sf::Color::Black, sf::Color::Cyan, sf::Color::Green, sf::Color::Red);
    m_playBut.setPosition({static_cast<float>(position.x), static_cast<float>(position.y)});

    m_playBut.draw(*window);

//    auto size = m_bounds.size();
//    m_playBut.setSize({static_cast<float>(size.x), static_cast<float>(size.y)});
//    m_playBut.setFillColor(sf::Color(29, 29, 29, 255));
//    m_playBut.setPosition({static_cast<float>(m_bounds.top_left.x + position.x), static_cast<float>(m_bounds.top_left.y + position.y)});
//
//    m_playText.setString("Play");
//    m_playText.setFillColor(sf::Color::White);
//    m_playText.setCharacterSize(16);
//    m_playText.setFont(LayoutManager::instance().mainFont());
//    auto text_lb = m_playText.getLocalBounds();
//    m_playText.setOrigin(text_lb.width / 2.f, text_lb.height / 2.f);
//    m_playText.setPosition(m_playBut.getPosition() + (m_playBut.getSize() / 2.f));

//    window->draw(m_playBut);
//    window->draw(m_playText);
}

void ControlBar::refreshPlayButtonState(int x, int y) {
    bool shouldHover = m_playBut.contains(x, y);
    bool shouldPress = m_mouseDown;

    if(shouldHover) {
        if(shouldPress) {
            m_playBut.setState(UiButton::ButtonState::BS_PRESSED);
        }
        else {
            m_playBut.setState(UiButton::ButtonState::BS_HOVERED);
        }
    }
    else {
        if(shouldPress) {
            m_playBut.setState(UiButton::ButtonState::BS_PRESSED);
        }
        else {
            m_playBut.setState(UiButton::ButtonState::BS_NONE);
        }
    }
}


void ControlBar::onMouseMove(int x, int y) {
    refreshPlayButtonState(x, y);
}

bool ControlBar::onMouseDown(int x, int y, int but) {
    if(but == 0 && m_playBut.contains(x, y)) {
        m_mouseDown = true;
    }
    refreshPlayButtonState(x, y);
}

void ControlBar::onMouseUp( int but) {
    if(but == 0) {
        m_mouseDown = false;
    }
    refreshPlayButtonState(-1, -1);
}

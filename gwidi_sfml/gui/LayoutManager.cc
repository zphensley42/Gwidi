#include <iostream>
#include "LayoutManager.h"

LayoutManager &LayoutManager::instance() {
    static LayoutManager s_instance{};
    return s_instance;
}

// TODO: View for the note labels on the left? (may just rely on the text in the slots instead)
void LayoutManager::setup(sf::RenderWindow &window, GlobalMouseEventHandler& handler) {
    if (!m_mainFont.loadFromFile("E:/tools/repos/gwidi_sfml/assets/arial.ttf")) {
        std::cerr << "Failed to load main font\n";
    }

    auto totalSize = window.getSize();
    m_controlsView.reset({0, 0, static_cast<float>(totalSize.x), 100.f});
    m_controlsView.setViewport({0, 0, 1.f, 0.125f});

    m_contentView.reset({0, 0, static_cast<float>(totalSize.x), totalSize.y - 200.f});
    m_contentView.setViewport({0, 0.125f, 1.f, 0.75f});

    m_scrubView.reset({0, 0, static_cast<float>(totalSize.x), 100.f});
    m_scrubView.setViewport({0, 0.875f, 1.f, 0.125f});

    // backgrounds
    m_controlsBack.setFillColor(sf::Color::Red);
    m_controlsBack.setSize(m_controlsView.getSize());

    m_contentBack.setFillColor(sf::Color::Black);
    m_contentBack.setSize(m_contentView.getSize());

    m_scrubBack.setFillColor(sf::Color::Blue);
    m_scrubBack.setSize(m_scrubView.getSize());

    if(!m_controlBar) {
        m_controlBar = std::make_shared<ControlBar>();
        handler.subscribe(m_controlBar);
    }
}

void LayoutManager::draw(sf::RenderWindow &window) {
    window.setView(m_controlsView);
    window.draw(m_controlsBack);
    m_controlBar->draw({0, 0});

    window.setView(m_contentView);
    window.draw(m_contentBack);

    window.setView(m_scrubView);
    window.draw(m_scrubBack);
}

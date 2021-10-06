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


    // Calculated view positions / sizes
    float desired_height_top = 100.f;
    float desired_height_percent_top = desired_height_top / static_cast<float>(totalSize.y);
    float desired_height_bottom = 100.f;
    float desired_height_percent_bottom = desired_height_bottom / static_cast<float>(totalSize.y);
    float desired_height_center = static_cast<float>(totalSize.y) - (desired_height_top + desired_height_bottom);
    float desired_height_percent_center = 1.f - (desired_height_percent_top + desired_height_percent_bottom);
    float desired_top_bottom_percent = desired_height_percent_top + desired_height_percent_center;

    // Top view
    m_controlsView.reset({0, 0, static_cast<float>(totalSize.x), desired_height_top});
    m_controlsView.setViewport({0, 0, 1.f, desired_height_percent_top});    // TODO: Percentage of the screen can be calculated to determine X pixels height for staticly-size views even on resize


    // Bottom view
    m_scrubView.reset({0, 0, static_cast<float>(totalSize.x), desired_height_bottom});
    m_scrubView.setViewport({0, desired_top_bottom_percent, 1.f, desired_height_percent_bottom});


    // Center view
    m_contentView.reset({0, 0, static_cast<float>(totalSize.x), desired_height_center});
    m_contentView.setViewport({0, desired_height_percent_top, 1.f, desired_height_percent_center});

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

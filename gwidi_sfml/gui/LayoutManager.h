#ifndef GWIDI_SFML_LAYOUTMANAGER_H
#define GWIDI_SFML_LAYOUTMANAGER_H

#include <SFML/Graphics.hpp>

class LayoutManager {
public:
    static LayoutManager& instance();
    LayoutManager() = default;

    void setup(sf::RenderWindow &window);
    void draw(sf::RenderWindow &window);

    inline void assignWindow(sf::RenderWindow& window) {
        m_window = &window;
    }
    inline sf::RenderWindow* window() {
        return m_window;
    }

    inline sf::Font& mainFont() {
        return m_mainFont;
    }

    inline sf::View& contentTarget() {
        return m_contentView;
    }
private:
    sf::RenderWindow* m_window{nullptr};

    sf::View m_controlsView;
    sf::View m_contentView;
    sf::View m_scrubView;
    sf::RectangleShape m_controlsBack;
    sf::RectangleShape m_contentBack;
    sf::RectangleShape m_scrubBack;

    sf::Font m_mainFont;
};


#endif //GWIDI_SFML_LAYOUTMANAGER_H

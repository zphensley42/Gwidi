#ifndef GWIDI_SFML_CONTROLBAR_H
#define GWIDI_SFML_CONTROLBAR_H

#include <SFML/Graphics.hpp>


class ControlBar {
public:
    ControlBar();
    void draw(sf::RenderWindow &window, sf::Vector2<int> position);
private:
};


#endif //GWIDI_SFML_CONTROLBAR_H

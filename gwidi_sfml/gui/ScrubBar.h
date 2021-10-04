#ifndef GWIDI_SFML_SCRUBBAR_H
#define GWIDI_SFML_SCRUBBAR_H

#include <SFML/Graphics.hpp>

class ScrubBar {
public:
    ScrubBar();

    void build();
    void draw();

private:
    sf::Image m_image;
    sf::Texture m_texture;
    sf::Uint8 * m_pixels;
    sf::Sprite m_sprite;
};


#endif //GWIDI_SFML_SCRUBBAR_H

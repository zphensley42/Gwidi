#ifndef GWIDI_SFML_MEASURE_H
#define GWIDI_SFML_MEASURE_H

#include "Base.h"
#include "Note.h"
#include <vector>
#include <SFML/Graphics.hpp>

class Measure : public UiView {
private:
    sf::Uint8* m_image_pixels;
    sf::Image m_image;
    sf::Texture m_texture;
    sf::Sprite m_sprite;

    std::vector<Note> m_notes;
    sf::Vector2f m_initialPos;

public:
    Measure();
    Measure(Identifier id);
    ~Measure() = default;

    void build(sf::Vector2f offset);
    void scroll(sf::Vector2f offset);
    inline sf::Sprite& sprite() {
        return m_sprite;
    }

    Slot* slotIndexForMouse(int x, int y);
};


#endif //GWIDI_SFML_MEASURE_H

#ifndef GWIDI_SFML_MEASURE_H
#define GWIDI_SFML_MEASURE_H

#include "Base.h"
#include "Note.h"
#include <vector>
#include <SFML/Graphics.hpp>
#include <mutex>
#include "GwidiData.h"

class Measure : public UiView {
private:
    sf::Uint8* m_background_image_pixels;
    sf::Uint8* m_foreground_image_pixels;
    sf::Image m_background_image;
    sf::Image m_foreground_image;
    sf::RenderTexture* m_background_renderTexture{nullptr};
    sf::Texture m_foreground_texture;
    sf::Texture m_background_texture;
    sf::Sprite m_background_sprite;
    sf::Sprite m_foreground_sprite;

    std::vector<Note> m_notes;
    sf::Vector2f m_initialPos;

    std::vector<Coord2D> m_triggeredSlots;
    std::mutex* m_triggeredSlotsMutex{nullptr};

    std::string measureLabelText();

public:
    Measure();
    Measure(Identifier id);
    Measure(gwidi::data::Octave &o, Identifier id);
    ~Measure();

    void build(sf::Vector2f offset);
    void scroll(sf::Vector2f offset);
    inline sf::Sprite& sprite() {
        return m_background_sprite;
    }
    void draw();
    void clearTriggeredSlotsStatus();

    sf::FloatRect globalBounds() const;
    sf::Vector2f initialPos() const;

    Slot* slotIndexForMouse(int x, int y, bool remove = false);
};


#endif //GWIDI_SFML_MEASURE_H

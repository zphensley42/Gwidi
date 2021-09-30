#ifndef GWIDI_SFML_MEASUREGRID_H
#define GWIDI_SFML_MEASUREGRID_H

#include <vector>
#include <cstdint>
#include "Base.h"
#include "Note.h"
#include "Measure.h"
#include <SFML/Graphics.hpp>
#include "../events/GlobalMouseEventHandler.h"

class Slot;

class MeasureGrid : public UiView, public GlobalMouseEventHandler::Callback {
private:
    std::vector<Measure> m_measures;
    std::vector<Note> m_notes;
    int m_scroll_x{0};
    int m_scroll_y{0};


    sf::RenderWindow *m_last_window{nullptr};
    sf::Uint8* m_image_pixels;
    sf::Image m_image;
    sf::Texture m_texture;
    sf::Sprite m_sprite;

    // TODO: Max scroll amounts

public:
    MeasureGrid(bool splitMeasures = true);
    ~MeasureGrid() = default;

    void onScrolled(int x, int y) override;
    bool onLeftDown(int x, int y) override;

    void scroll(int x, int y);
    void draw(sf::RenderWindow& window);

    explicit operator std::string() const;
};


#endif //GWIDI_SFML_MEASUREGRID_H

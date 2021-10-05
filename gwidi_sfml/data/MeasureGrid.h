#ifndef GWIDI_SFML_MEASUREGRID_H
#define GWIDI_SFML_MEASUREGRID_H

#include <vector>
#include <cstdint>
#include "Base.h"
#include "Note.h"
#include "Measure.h"
#include <SFML/Graphics.hpp>
#include "../events/GlobalMouseEventHandler.h"
#include "GwidiData.h"

class Slot;

class MeasureGrid : public UiView, public GlobalMouseEventHandler::Callback {
private:
    std::vector<Measure> m_measures;
    std::vector<Note> m_notes;
    int m_scroll_x{0};
    int m_scroll_y{0};

public:
    MeasureGrid();
    MeasureGrid(gwidi::data::Track &track);
    ~MeasureGrid() = default;

    void onScrolled(int x, int y) override;
    bool onLeftDown(int x, int y) override;
    void onLeftUp(int x, int y) override;

    void draw(sf::RenderWindow &window, sf::View& target, sf::Vector2f position);

    explicit operator std::string() const;
};


#endif //GWIDI_SFML_MEASUREGRID_H

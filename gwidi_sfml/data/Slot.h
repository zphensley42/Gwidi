#ifndef GWIDI_SFML_SLOT_H
#define GWIDI_SFML_SLOT_H

#include "Constants.h"
#include "Base.h"
#include <SFML/Graphics.hpp>

class Slot : public UiView {
public:
    enum DrawState {
        DS_NONE = 0,
        DS_ACTIVATED = 1,
        DS_HELD = 2
    };

    enum PlayState {
        PS_NONE = 0,
        PS_PLAYING = 1
    };

    Slot();
    Slot(Identifier id);
    Slot(Identifier id, UiConstants::Slot_ColType type);
    ~Slot() = default;

    inline void updateStates(DrawState drawState, PlayState playState) {
        m_drawState = drawState;
        m_playState = playState;
        if(m_last_pixels) {
            draw(m_last_pixels, m_lastSize);
        }
    }
    void draw(sf::Uint8 *pixels, Coord2D &size);
    explicit operator std::string() const;

    inline DrawState drawState() const { return m_drawState; }
    inline PlayState playState() const { return m_playState; }

private:
    UiConstants::Slot_ColType m_type;

    bool m_isDrawn{false};
    DrawState m_drawState{DS_NONE};
    PlayState m_playState{PS_NONE};

    sf::Uint8 *m_last_pixels{nullptr};
    Coord2D m_lastSize;
};


#endif //GWIDI_SFML_SLOT_H

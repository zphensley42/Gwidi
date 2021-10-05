#ifndef GWIDI_SFML_SLOT_H
#define GWIDI_SFML_SLOT_H

#include "Constants.h"
#include "Base.h"
#include "GwidiData.h"
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
    Slot(gwidi::data::Slot& s, Identifier id);
    Slot(Identifier id, UiConstants::Slot_ColType type);
    ~Slot() = default;

    inline void updateStates(DrawState drawState, PlayState playState, sf::Uint8* pixels) {
        m_drawState = drawState;
        m_playState = playState;
        if(pixels) {
            // TODO: Determine alpha from our states
            draw_foreground(pixels, m_lastSize);
        }
    }
    void draw_background(sf::Uint8 *pixels, Coord2D &size);
    void draw_foreground(sf::Uint8 *pixels, Coord2D &size);
    void drawText(sf::RenderTexture &targetTexture, sf::Vector2f offset);
    explicit operator std::string() const;

    inline DrawState drawState() const { return m_drawState; }
    inline PlayState playState() const { return m_playState; }

private:
    UiConstants::Slot_ColType m_type;
    sf::Text m_noteLabel;

    bool m_isDrawn{false};
    DrawState m_drawState{DS_NONE};
    PlayState m_playState{PS_NONE};

    Coord2D m_lastSize;
};


#endif //GWIDI_SFML_SLOT_H

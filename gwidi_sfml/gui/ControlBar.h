#ifndef GWIDI_SFML_CONTROLBAR_H
#define GWIDI_SFML_CONTROLBAR_H

#include <SFML/Graphics.hpp>
#include "../data/Base.h"
#include "../events/GlobalMouseEventHandler.h"
#include "UiButton.h"


class ControlBar : public UiView, public GlobalMouseEventHandler::Callback {
public:
    ControlBar();
    void draw(sf::Vector2<int> position);

    void onMouseMove(int x, int y) override;
    bool onMouseDown(int x, int y, int but) override;
    void onMouseUp(int but) override;
private:
    UiButton m_playBut;
    bool m_mouseDown{false};

    void refreshPlayButtonState(int x, int y);
};


#endif //GWIDI_SFML_CONTROLBAR_H

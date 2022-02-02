#ifndef GWIDI_SFML_CONTROLBAR_H
#define GWIDI_SFML_CONTROLBAR_H

#include <SFML/Graphics.hpp>
#include "../data/Base.h"
#include "../events/GlobalMouseEventHandler.h"
#include "UiButton.h"


class ControlBar : public UiView, public GlobalMouseEventHandler::Callback {
public:
    ControlBar();
    ~ControlBar();
    void draw(sf::Vector2<int> position);

    bool onMouseMove(int x, int y) override;
    bool onMouseDown(int x, int y, int but) override;
    bool onMouseUp(int but) override;
private:
    friend class PlayCb;
    friend class LoadCb;
    friend class SaveCb;
    friend class ClearCb;
    friend class ImportCb;

    UiButton::Callback* m_playCb;
    UiButton::Callback* m_loadCb;
    UiButton::Callback* m_saveCb;
    UiButton::Callback* m_clearCb;
    UiButton::Callback* m_importCb;

    // TODO: Need a pop-up class for the settings dialog

    UiButton m_playBut;
    UiButton m_loadBut;
    UiButton m_saveBut;
    UiButton m_clearBut;
    UiButton m_settingsBut;
    UiButton m_importBut;

    // Cached values used in drawing (to prevent draw loop allocations)
    sf::Vector2f m_draw_pos{};
};


#endif //GWIDI_SFML_CONTROLBAR_H

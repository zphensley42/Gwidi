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
#include "../playback/PlaybackManager.h"

namespace gwidi { namespace view {

class Slot;

class MeasureGrid : public UiView, public GlobalMouseEventHandler::Callback, public gwidi::playback::PlaybackManager::Callback {
private:
    std::vector<Measure> m_measures;
    std::vector<Note> m_notes;

    int m_scroll_x{0};
    int m_scroll_y{0};
    int m_last_frame_x{0};
    int m_last_frame_y{0};

    int m_scroll_x_min{0};
    int m_scroll_x_max{0};
    int m_scroll_y_min{0};
    int m_scroll_y_max{0};
    int m_last_down_but{-1};

    bool m_dragDown{false};
    bool m_selectDown{false};

    unsigned int* m_playingSlot{nullptr};
    sf::Sprite m_playOverlaySprite;
    sf::Vector2f m_playOverlayPos;
    sf::RectangleShape m_playOverRect;
    sf::RenderTexture m_playOverRt;


    void clampScrollValues();
    bool performIndexChecks(int x, int y, bool remove = false);
    void clearTriggeredIndices();

    void init();
    void repositionPlayOverlay();

public:
    MeasureGrid();
    MeasureGrid(gwidi::data::Track &track);
    ~MeasureGrid();

    void assignTrack(gwidi::data::Track &track);

    bool onMouseMove(int x, int y) override;
    bool onMouseDown(int x, int y, int but) override;
    bool onMouseUp(int but) override;

    void playSlot(unsigned int index) override;

    void draw(sf::RenderWindow &window, sf::View& target, sf::Vector2f position);

    void setScrollAmountLimits(int min_x, int max_x, int min_y, int max_y);

    explicit operator std::string() const;
};

}}

#endif //GWIDI_SFML_MEASUREGRID_H

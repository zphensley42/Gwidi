#include "DataManager.h"
#include "../events/ThreadPool.h"

DataManager &DataManager::instance() {
    static DataManager s_instance;
    return s_instance;
}

void DataManager::load(GlobalMouseEventHandler &handler) {
    if(m_isLoaded.load()) {
        return;
    }

    ThreadPool::instance().schedule([this, &handler]() {
        // Start with an empty song
//        m_song = std::make_shared<gwidi::data::Song>();
//        m_song->emptyInit(1, 3);

        // Convert our data to the 'grid' (song -> grid -- use our m_selectedTrack inside of Song)
//        m_grid = std::make_shared<MeasureGrid>(m_song->tracks()[0]);

        // For testing, always import something
//        m_song = std::make_shared<gwidi::data::Song>();
        auto song = gwidi::data::Importer::instance().import("E:\\Tools\\repos\\Gwidi\\gwidi_sfml\\external\\Gwidi_Importer\\assets\\test_data\\simple.mid");
        m_song = std::shared_ptr<gwidi::data::Song>(song);
//        m_song->emptyInit(1, 3);
        m_grid = std::make_shared<MeasureGrid>(m_song->tracks()[0]);

        auto octave4_noteb_slots = m_song->slotsForParams(0, 4, "B");


        handler.subscribe(m_grid);
        auto mgBounds = m_grid->bounds();
        int min_scroll_x = (mgBounds.top_right.x * -1) + UiConstants::measure_width;
        int max_scroll_x = UiConstants::measure_width;
        int min_scroll_y = (mgBounds.bottom_left.y * -1) + UiConstants::measure_height;
        int max_scroll_y = UiConstants::measure_height;
        handler.setScrollAmountLimits(min_scroll_x, max_scroll_x, min_scroll_y, max_scroll_y);

        m_isLoaded.store(true);
    });
}

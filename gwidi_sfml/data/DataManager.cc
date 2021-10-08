#include "DataManager.h"
#include "../events/ThreadPool.h"

DataManager &DataManager::instance() {
    static DataManager s_instance;
    return s_instance;
}

void DataManager::load(GlobalMouseEventHandler &handler, Callback* callback) {
    if(m_isLoaded.load()) {
        return;
    }

    m_cb = callback;

    ThreadPool::instance().schedule([this, &handler]() {
        // Start with an empty song
//        m_song = std::make_shared<gwidi::data::Song>();
//        m_song->emptyInit(1, 3);

        // Convert our data to the 'grid' (song -> grid -- use our m_selectedTrack inside of Song)
//        m_grid = std::make_shared<MeasureGrid>(m_song->tracks()[0]);

        // For testing, always import something
//        m_song = std::make_shared<gwidi::data::Song>();
//        auto song = gwidi::data::Importer::instance().import("E:\\Tools\\repos\\Gwidi\\gwidi_sfml\\external\\Gwidi_Importer\\assets\\test_data\\simple.mid");
//        auto song = gwidi::data::Importer::instance().import("E:\\Tools\\repos\\Gwidi\\gwidi_sfml\\external\\Gwidi_Importer\\assets\\test_data\\upwards_scale_test.mid");
//        auto song = gwidi::data::Importer::instance().import("E:\\Tools\\repos\\Gwidi\\gwidi_sfml\\external\\Gwidi_Importer\\assets\\Star Wars - Imperial March_1632388875429.mid");
        auto song = gwidi::data::Importer::instance().import("E:\\Tools\\repos\\Gwidi\\gwidi_sfml\\external\\Gwidi_Importer\\assets\\hm.mid");
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
        m_grid->setScrollAmountLimits(min_scroll_x, max_scroll_x, min_scroll_y, max_scroll_y);

        m_isLoaded.store(true);
        if(m_cb) {
            m_cb->onLoadComplete();
        }
    });
}

// TODO: addSlot needs a paired removeSlot (or a bool)
void DataManager::updateSlot(Slot& slot) {
    gwidi::data::SlotInfo info;
//    int octave{0};
//    int measure_index{0};
//    std::string note_key{0};
//    int length_in_slots{0};
//    int start_in_slots{0};  // slot index, 0 based
//    int channel{0};
//    std::string instrument{""};
//    int track{0};
//    bool is_held{false};
    info.octave = Constants::octaves()[slot.id().octave_index];
    info.measure_index = slot.id().measure_index;
    info.note_key = slot.noteKey();
    info.length_in_slots = 1;
    info.start_in_slots = (info.measure_index * Constants::slots_per_measure) + slot.id().slot_index;
    info.channel = 0;
    info.instrument = "";
    info.track = m_selectedTrack;
    info.is_held = slot.drawState() == Slot::DrawState::DS_HELD;
    info.is_activated = slot.drawState() != Slot::DrawState::DS_NONE;
    m_song->addSlot(info);
}

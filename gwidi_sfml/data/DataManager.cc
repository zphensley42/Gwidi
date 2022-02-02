#include "DataManager.h"
#include "../events/ThreadPool.h"
#include <fstream>

#define DEBUG_SAVE_LOAD true

namespace gwidi { namespace data {

DataManager &DataManager::instance() {
    static DataManager s_instance;
    return s_instance;
}

void DataManager::load(GlobalMouseEventHandler &handler, Callback* callback) {
    if(m_isLoaded.load()) {
        return;
    }

    m_globalEventHandler = &handler;
    m_cb = callback;
    clear();
}

void DataManager::importFromFile(const std::string &file) {
//    auto song = gwidi::data::Importer::instance().import("E:\\Tools\\repos\\Gwidi\\gwidi_sfml\\external\\Gwidi_Importer\\assets\\hm.mid");
    auto song = gwidi::data::Importer::instance().import(file);
    assignSong(song);
}

void DataManager::assignSong(gwidi::data::Song* song) {
    m_isLoaded.store(false);
    ThreadPool::instance().schedule([song, this]() {
        if(m_globalEventHandler) {
            m_globalEventHandler->unsubscribe(m_grid);
        }
        m_grid = nullptr;

        m_song = std::shared_ptr<gwidi::data::Song>(song);
        m_grid = std::make_shared<gwidi::view::MeasureGrid>(m_song->tracks()[0]);
        if(m_globalEventHandler) {
            m_globalEventHandler->subscribe(m_grid);
        }

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

void DataManager::clear() {
    auto song = new gwidi::data::Song();
    song->emptyInit(1, 3);
    assignSong(song);
}

gwidi::data::Song* DataManager::loadSongFromStream(std::istream& in) {
#ifdef DEBUG_SAVE_LOAD
    debugInFile(true);
#endif

    Song* song = new Song();

    // Read our tempo
    int tempo;
    readFromStream("tempo", in, &tempo, sizeof(int));

    int selectedTrack;
    readFromStream("selectedTrack", in, &selectedTrack, sizeof(int));

    int numSlotsHorizontal;
    int numOctavesVertical;
    int numNotesInOctave;

    readFromStream("numSlotsHorizontal", in, &numSlotsHorizontal, sizeof(int));
    readFromStream("numOctavesVertical", in, &numOctavesVertical, sizeof(int));
    readFromStream("numNotesInOctave", in, &numNotesInOctave, sizeof(int));

    // Read vertical slices of slots and add to song
    for(int i = 0; i < numSlotsHorizontal; i++) {
        // Each slot is stored as:   <slot#><slot octave><slot note size><slot note><slot state>
        size_t vertSlots = numOctavesVertical * numNotesInOctave;
        for(int j = 0; j < vertSlots; j++) {
            int slotNum;
            int slotOctave;
            int slotNoteSize;
            int slotState;

            readFromStream("slotNum", in, &slotNum, sizeof(int));
            readFromStream("slotOctave", in, &slotOctave, sizeof(int));
            readFromStream("slotNoteSize", in, &slotNoteSize, sizeof(int));


            char* slotNoteStr = new char[slotNoteSize];

            readFromStream("slotNoteStr", in, slotNoteStr, slotNoteSize);
            readFromStream("slotState", in, &slotState, sizeof(int));


            // TODO: Loading / Saving seems identical now -- the outlier is that the code below this seems to be messing something up

            Identifier id;
            id.measure_index = j / Constants::slots_per_measure;

            int octaveIndex = 0;
            for(octaveIndex = 0; octaveIndex < Constants::octaves().size(); octaveIndex++) {
                if(Constants::octaves()[octaveIndex] == slotOctave) {
                    break;
                }
            }
            if(octaveIndex >= Constants::octaves().size()) {
                octaveIndex = 0;
            }

            id.octave_index = octaveIndex;
            id.slot_index = slotNum;
            id.note_index = Constants::notes[slotNoteStr];
            auto slot = gwidi::view::Slot(id);

            auto state = static_cast<Slot::State>(slotState);
            auto drawState = static_cast<gwidi::view::Slot::DrawState>(state);
            slot.updateDrawState(drawState, nullptr);
            auto info = slotToInfo(slot);
            song->addSlot(info);

            delete[] slotNoteStr;
        }
    }

    song->setTempo(tempo);

#ifdef DEBUG_SAVE_LOAD
    debugInFile().close();
#endif

    return song;
}

void DataManager::readFromStream(const std::string& label, std::istream &in, int *data, std::streamsize n) {
    in.read(reinterpret_cast<char*>(data), n);
#ifdef DEBUG_SAVE_LOAD
    static std::string newlineStr = "\n";
    debugInFile().write(label.c_str(), label.size());
    debugInFile().write("  ", 2);
    std::stringstream ss;
    ss << *data;
    auto str = ss.str();
    debugInFile().write(str.c_str(), str.size());
    debugInFile().write(newlineStr.c_str(), newlineStr.size());
#endif
}

void DataManager::readFromStream(const std::string& label, std::istream &in, char *data, std::streamsize n) {
    in.read(data, n);
#ifdef DEBUG_SAVE_LOAD
    static std::string newlineStr = "\n";
    debugInFile().write(label.c_str(), label.size());
    debugInFile().write("  ", 2);
    debugInFile().write(data, n);
    debugInFile().write(newlineStr.c_str(), newlineStr.size());
#endif
}

#ifdef DEBUG_SAVE_LOAD
std::ofstream& DataManager::debugInFile(bool open) {
    static std::ofstream debugInInstance;
    if(open) {
        debugInInstance.open("debug_load_output.txt", std::ios::out);
    }
    return debugInInstance;
}
#endif

void DataManager::loadFromFile(const std::string &file) {
    clear();

    ThreadPool::instance().schedule([file, this]() {
        // Need to determine .gwm file format for this new version
        // Build our output data from m_song
        std::ifstream in(file.c_str(), std::ios::in | std::ios::binary);
        auto song = loadSongFromStream(in);
        in.close();

        assignSong(song);
    });
}

void DataManager::saveToFile(const std::string &file) {
    std::ofstream out(file.c_str(), std::ios::out | std::ios::binary);
    m_song->saveAsBinary(out, m_selectedTrack);
    out.close();
}

// TODO: addSlot needs a paired removeSlot (or a bool)
void DataManager::updateSlot(gwidi::view::Slot& slot) {
    auto info = slotToInfo(slot);
    m_song->addSlot(info);
}

gwidi::data::SlotInfo DataManager::slotToInfo(gwidi::view::Slot& slot) {
    gwidi::data::SlotInfo info;

    info.octave = Constants::octaves()[slot.id().octave_index];
    info.measure_index = slot.id().measure_index;
    info.note_key = slot.noteKey();
    info.length_in_slots = 1;
    info.start_in_slots = (info.measure_index * Constants::slots_per_measure) + slot.id().slot_index;
    info.channel = 0;
    info.instrument = "";
    info.track = m_selectedTrack;
    info.is_held = slot.drawState() == gwidi::view::Slot::DrawState::DS_HELD;
    info.is_activated = slot.drawState() != gwidi::view::Slot::DrawState::DS_NONE;

    return info;
}

}}

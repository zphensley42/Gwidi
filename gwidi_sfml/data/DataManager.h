#ifndef GWIDI_SFML_DATAMANAGER_H
#define GWIDI_SFML_DATAMANAGER_H

#include "MeasureGrid.h"
#include <memory>
#include <atomic>
#include "GwidiData.h"

#define DEBUG_SAVE_LOAD true

// TODO: Create data classes for slots / notes / etc that can be 'applied' to the UI grid for updates
// TODO: 2d array of slots as the primary class?

namespace gwidi { namespace data {

class DataManager {
public:
    class Callback {
    public:
        virtual void onLoadComplete() = 0;
    };

    static DataManager& instance();
    void load(GlobalMouseEventHandler &handler, Callback* callback);

    void clear();
    void assignSong(gwidi::data::Song* song);
    void loadFromFile(const std::string& file);
    void saveToFile(const std::string& file);
    void importFromFile(const std::string& file);

    gwidi::data::Song* loadSongFromStream(std::istream& in);

    inline std::shared_ptr<gwidi::view::MeasureGrid> grid() {
        return m_grid;
    }

    inline std::shared_ptr<Song> song() {
        return m_song;
    }

    bool isLoaded() const { return m_isLoaded.load(); }

    void updateSlot(gwidi::view::Slot& slot);
    gwidi::data::SlotInfo slotToInfo(gwidi::view::Slot& slot);
private:
    Callback* m_cb{nullptr};

    void readFromStream(const std::string& label, std::istream &in, int* data, std::streamsize n);
    void readFromStream(const std::string& label, std::istream &in, char *data, std::streamsize n);

#ifdef DEBUG_SAVE_LOAD
    static std::ofstream& debugInFile(bool open = false);
#endif

    std::atomic_bool m_isLoaded{false};
    std::shared_ptr<gwidi::view::MeasureGrid> m_grid{nullptr};

    std::shared_ptr<Song> m_song{nullptr};
    int m_selectedTrack{1};

    GlobalMouseEventHandler* m_globalEventHandler{nullptr};
};

}}

#endif //GWIDI_SFML_DATAMANAGER_H

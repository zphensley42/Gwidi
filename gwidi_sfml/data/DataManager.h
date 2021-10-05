#ifndef GWIDI_SFML_DATAMANAGER_H
#define GWIDI_SFML_DATAMANAGER_H

#include "MeasureGrid.h"
#include <memory>
#include <atomic>
#include "GwidiData.h"

// TODO: Create data classes for slots / notes / etc that can be 'applied' to the UI grid for updates
// TODO: 2d array of slots as the primary class?

class DataManager {
public:
    static DataManager& instance();
    void load(GlobalMouseEventHandler &handler);

    inline std::shared_ptr<MeasureGrid> grid() {
        return m_grid;
    }

    bool isLoaded() const { return m_isLoaded.load(); }
private:
    std::atomic_bool m_isLoaded{false};
    std::shared_ptr<MeasureGrid> m_grid{nullptr};

    std::shared_ptr<gwidi::data::Song> m_song{nullptr};
    int m_selectedTrack{0};
};


#endif //GWIDI_SFML_DATAMANAGER_H

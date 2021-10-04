#ifndef GWIDI_SFML_DATAMANAGER_H
#define GWIDI_SFML_DATAMANAGER_H

#include "MeasureGrid.h"
#include <memory>
#include <atomic>

// TODO: Create data classes for slots / notes / etc that can be 'applied' to the UI grid for updates
// TODO: 2d array of slots as the primary class?
class DataSlot {
public:
private:

};

class DataNote {
public:
private:
    std::vector<DataSlot> m_slots;
};

class DataOctave {
public:
private:
    std::vector<DataNote> m_notes;
};

class DataMeasure {
public:
private:
    std::vector<DataOctave> m_octaves;
};

class DataSong {
public:
private:
    std::vector<DataMeasure> m_measures;
};

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
};


#endif //GWIDI_SFML_DATAMANAGER_H

#ifndef GWIDI_SFML_DATAMANAGER_H
#define GWIDI_SFML_DATAMANAGER_H

#include "MeasureGrid.h"
#include <memory>
#include <atomic>

class DataManager {
public:
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

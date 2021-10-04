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
        m_grid = std::make_shared<MeasureGrid>();

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

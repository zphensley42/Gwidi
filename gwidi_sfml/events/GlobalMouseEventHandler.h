#ifndef GWIDI_SFML_GLOBALMOUSEEVENTHANDLER_H
#define GWIDI_SFML_GLOBALMOUSEEVENTHANDLER_H
#include <SFML/Graphics.hpp>
#include <list>
#include <memory>

class GlobalMouseEventHandler {
private:
    bool m_isDown{false};
    bool m_isDragging{false};
    int m_down_mouse_but{0};

    int m_scroll_x{0};
    int m_scroll_y{0};
    int m_last_frame_x{0};
    int m_last_frame_y{0};

    int m_scroll_x_min{0};
    int m_scroll_x_max{0};
    int m_scroll_y_min{0};
    int m_scroll_y_max{0};
public:

    class Callback {
    public:
        virtual void onScrolled(int x, int y) = 0;
        virtual bool onLeftDown(int x, int y) = 0;
        virtual void onLeftUp(int x, int y) = 0;

        virtual bool onRightDown(int x, int y) = 0;
        virtual void onRightUp(int x, int y) = 0;
    };

    void handleMouseDown(int but, int x, int y);
    void handleMouseUp();
    void handleMouseMove(int x, int y);

    void subscribe(const std::shared_ptr<Callback>& cb);
    void unsubscribe(const std::shared_ptr<Callback>& cb);

    void setScrollAmountLimits(int min_x, int max_x, int min_y, int max_y);

private:
    void clampScrollValues();

    std::list<std::shared_ptr<Callback>> m_cbs{};
};


#endif //GWIDI_SFML_GLOBALMOUSEEVENTHANDLER_H

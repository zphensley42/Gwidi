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
public:

    class Callback {
    public:
        virtual void onScrolled(int x, int y) = 0;
        virtual bool onLeftDown(int x, int y) = 0;
    };

    void handleMouseDown(int but, int x, int y);
    void handleMouseUp();
    void handleMouseMove(int x, int y);

    void subscribe(const std::shared_ptr<Callback>& cb);
    void unsubscribe(const std::shared_ptr<Callback>& cb);

private:
    std::list<std::shared_ptr<Callback>> m_cbs{};
};


#endif //GWIDI_SFML_GLOBALMOUSEEVENTHANDLER_H

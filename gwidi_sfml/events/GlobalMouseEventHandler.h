#ifndef GWIDI_SFML_GLOBALMOUSEEVENTHANDLER_H
#define GWIDI_SFML_GLOBALMOUSEEVENTHANDLER_H
#include <SFML/Graphics.hpp>
#include <list>
#include <memory>

class GlobalMouseEventHandler {
public:
    class Callback {
    public:
        virtual bool onMouseMove(int x, int y) = 0;
        virtual bool onMouseDown(int x, int y, int but) = 0;
        virtual bool onMouseUp(int but) = 0;
    };

    // TODO: Instead of the 'bool' responses on the callbacks above, implement 'focus' and only allow callbacks to be used if they have gained focus for move/up

    void handleMouseDown(int but, int x, int y);
    void handleMouseUp(int but);
    void handleMouseMove(int x, int y);

    void subscribe(const std::shared_ptr<Callback>& cb);
    void unsubscribe(const std::shared_ptr<Callback>& cb);

private:
    std::list<std::shared_ptr<Callback>> m_cbs{};
    std::shared_ptr<Callback> m_cbOverride{nullptr};
};


#endif //GWIDI_SFML_GLOBALMOUSEEVENTHANDLER_H

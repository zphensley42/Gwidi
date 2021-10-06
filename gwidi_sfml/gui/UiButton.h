#ifndef GWIDI_SFML_UIBUTTON_H
#define GWIDI_SFML_UIBUTTON_H

#include "../data/Base.h"
#include <SFML/Graphics.hpp>
#include <unordered_map>
#include <atomic>

class UiButton : public UiView {
public:
    class Callback {
    public:
        virtual ~Callback() = default;
        virtual void clicked() = 0;
    };

    UiButton(const std::string &text, sf::Vector2f size, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ);
    UiButton();

    void init(const std::string &text, sf::Vector2f size, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ);

    void setPosition(sf::Vector2f pos);
    void draw(sf::RenderWindow &window);
    void setText(const std::string &text);
    sf::Color& fillColor();

    void mouseDown() override;

    bool contains(float x, float y);

    inline void assign(Callback* cb) {
        m_cb = cb;
    }

    inline void setActivated(bool act) {
        m_isActivated.store(act);
    }
    inline bool isActivated() {
        return m_isActivated.load();
    }

private:
    std::atomic_bool m_isActivated{false};

    sf::Vector2f m_sizeParam;
    void autoSizeRect();

    std::unordered_map<UiView::MouseState, sf::Color> m_colorMap;
    sf::RectangleShape m_rect;
    sf::Text m_label;

    Callback* m_cb{nullptr};
};


#endif //GWIDI_SFML_UIBUTTON_H

#ifndef GWIDI_SFML_UIBUTTON_H
#define GWIDI_SFML_UIBUTTON_H

#include "../data/Base.h"
#include <SFML/Graphics.hpp>
#include <unordered_map>

class UiButton : public UiView {
public:
    class Callback {
    public:
        virtual void clicked() = 0;
    };
    enum ButtonState {
        BS_NONE = 0,
        BS_HOVERED,
        BS_PRESSED,
        BS_ACTIVATED
    };

    UiButton(const std::string &text, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ);
    UiButton();

    void init(const std::string &text, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ);

    void setPosition(sf::Vector2f pos);
    void draw(sf::RenderWindow &window);
    void setText(const std::string &text);
    sf::Color& fillColor();

    inline void setState(ButtonState state) {
        m_state = state;
    }

    inline ButtonState state() {
        return m_state;
    }

    bool contains(float x, float y);

    inline void assign(Callback* cb) {
        m_cb = cb;
    }

private:
    ButtonState m_state{ButtonState::BS_NONE};

    std::unordered_map<ButtonState, sf::Color> m_colorMap;
    sf::RectangleShape m_rect;
    sf::Text m_label;

    // TODO: Move event handling here? (i.e. mouse move / down / up)
    Callback* m_cb{nullptr};
};


#endif //GWIDI_SFML_UIBUTTON_H

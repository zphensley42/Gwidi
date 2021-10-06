#include "UiButton.h"
#include "LayoutManager.h"

// TODO: Currently size wraps the text, but this should maybe be assignable?
UiButton::UiButton(const std::string &text, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ) : UiView() {
    init(text, def, hov, press, activ);
}

UiButton::UiButton() : UiButton("Button", sf::Color::White, sf::Color::White, sf::Color::White, sf::Color::White) {}

sf::Color& UiButton::fillColor() {
    return m_colorMap[m_state];
}

void UiButton::setPosition(sf::Vector2f pos) {
    m_rect.setPosition(pos);
    m_label.setPosition(m_rect.getPosition() + (m_rect.getSize() / 2.f));
}

void UiButton::draw(sf::RenderWindow &window) {
    m_rect.setFillColor(fillColor());

    window.draw(m_rect);
    window.draw(m_label);
}

void UiButton::setText(const std::string &text) {
    // Update text
    m_label.setString(text);

    // Update size / position
    auto label_lb = m_label.getLocalBounds();
    m_label.setOrigin(label_lb.width / 2, label_lb.height / 2);
    m_rect.setSize({label_lb.width + 30, label_lb.height + 30});
    m_label.setPosition(m_rect.getPosition() + (m_rect.getSize() / 2.f));
}

bool UiButton::contains(float x, float y) {
    return m_rect.getGlobalBounds().contains(x, y);
}

void UiButton::init(const std::string &text, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ) {
    m_colorMap[ButtonState::BS_NONE] = def;
    m_colorMap[ButtonState::BS_HOVERED] = hov;
    m_colorMap[ButtonState::BS_PRESSED] = press;
    m_colorMap[ButtonState::BS_ACTIVATED] = activ;

    m_label.setFont(LayoutManager::instance().mainFont());
    m_label.setCharacterSize(16);
    m_label.setString(text);
    auto label_lb = m_label.getLocalBounds();
    m_label.setOrigin(label_lb.width / 2, label_lb.height / 2);

    // 10 padding
    m_rect.setSize({label_lb.width + 30, label_lb.height + 30});
}

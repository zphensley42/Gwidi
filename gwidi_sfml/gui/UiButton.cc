#include "UiButton.h"
#include "LayoutManager.h"

// TODO: Currently size wraps the text, but this should maybe be assignable?
UiButton::UiButton(const std::string &text, sf::Vector2f size, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ) : UiView() {
    init(text, size, def, hov, press, activ);
}

UiButton::UiButton() : UiButton("Button", {-1, -1}, sf::Color::White, sf::Color::White, sf::Color::White, sf::Color::White) {}

sf::Color& UiButton::fillColor() {
    return m_colorMap[m_mouseState];
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
    if(m_sizeParam.x < 0 || m_sizeParam.y < 0) {
        autoSizeRect();
    }
    else {
        auto label_lb = m_label.getLocalBounds();
        m_label.setOrigin(label_lb.width / 2, label_lb.height / 2);
        m_label.setPosition(m_rect.getPosition() + (m_rect.getSize() / 2.f));
    }
}

bool UiButton::contains(float x, float y) {
    return m_rect.getGlobalBounds().contains(x, y);
}

void UiButton::autoSizeRect() {
    auto label_lb = m_label.getLocalBounds();
    m_label.setOrigin(label_lb.width / 2, label_lb.height / 2);
    m_rect.setSize({label_lb.width + 30, label_lb.height + 30});
    m_label.setPosition(m_rect.getPosition() + (m_rect.getSize() / 2.f));
}

void UiButton::init(const std::string &text, sf::Vector2f size, sf::Color def, sf::Color hov, sf::Color press, sf::Color activ) {
    m_colorMap[UiView::MouseState::MS_NONE] = def;
    m_colorMap[UiView::MouseState::MS_HOVER] = hov;
    m_colorMap[UiView::MouseState::MS_HOVER_DOWN] = press;
    m_colorMap[UiView::MouseState::MS_DOWN] = press;

    m_sizeParam = size;

    m_label.setFont(LayoutManager::instance().mainFont());
    m_label.setCharacterSize(16);
    m_label.setString(text);

    auto label_lb = m_label.getLocalBounds();
    m_label.setOrigin(label_lb.width / 2, label_lb.height / 2);

    // 10 padding
    if(m_sizeParam.x < 0 || m_sizeParam.y < 0) {
        autoSizeRect();
    }
    else {
        m_rect.setSize(m_sizeParam);
        m_label.setOrigin(label_lb.width / 2, label_lb.height / 2);
        m_label.setPosition(m_rect.getPosition() + (m_rect.getSize() / 2.f));
    }
}

void UiButton::mouseDown() {
    bool oldIsDown = isMouseDown();

    UiView::mouseDown();

    if(!oldIsDown && isMouseDown()) {
        // Clicked
        if(m_cb) {
            m_cb->clicked();
        }
    }
}

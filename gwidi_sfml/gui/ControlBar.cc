#include <iostream>
#include "ControlBar.h"
#include "LayoutManager.h"
#include "../playback/PlaybackManager.h"
#include "nfd.h"

class NfdOpenDialogWrapper {
public:
    NfdOpenDialogWrapper() = delete;
    NfdOpenDialogWrapper(const std::string& defPath, const std::string& filter) {

        nfdchar_t *outPath = nullptr;
        auto result = NFD_OpenDialog(filter.c_str(), defPath.c_str(), &outPath);
        switch(result) {
            case NFD_OKAY: {
                m_selectedPath = std::string(outPath);
                free(outPath);
                break;
            }
            case NFD_ERROR:
            case NFD_CANCEL: {
                // Nothing selected, log a message?
                break;
            }
        }
    }
    std::string selected() const {
        return m_selectedPath;
    }
private:
    std::string m_selectedPath;
};


class PlayCb : public UiButton::Callback {
public:
    PlayCb(ControlBar* owner) : m_owner{owner} {}
    void clicked() override {
        m_owner->m_playBut.setActivated(!m_owner->m_playBut.isActivated());
        std::string t = m_owner->m_playBut.isActivated() ? "Pause" : "Play";
        m_owner->m_playBut.setText(t);

        if(m_owner->m_playBut.isActivated()) {
            gwidi::playback::PlaybackManager::instance().play();
        }
        else {
            gwidi::playback::PlaybackManager::instance().pause();
        }
    }
private:
    ControlBar* m_owner;
};

class LoadCb : public UiButton::Callback {
public:
    LoadCb(ControlBar* owner) : m_owner{owner} {}
    void clicked() override {

        // Use nfd to select a file to load
        auto selectedFile = NfdOpenDialogWrapper("gwm", "").selected();
        if(!selectedFile.empty()) {
            std::cout << "Selected file to load: " << selectedFile << std::endl;
        }
        else {
            std::cout << "Did not select a file to load" << std::endl;
        }

        m_owner->m_loadBut.mouseUp();
    }
private:
    ControlBar* m_owner;
};



ControlBar::ControlBar() : UiView() {
    m_playCb = new PlayCb(this);
    m_playBut.assign(m_playCb);

    auto size = LayoutManager::instance().controlsTarget().getSize();
    m_bounds.top_left = {0, 0};
    m_bounds.top_right = {static_cast<int>(size.x), 0};
    m_bounds.bottom_left = {0, static_cast<int>(size.y)};
    m_bounds.bottom_right = {static_cast<int>(size.x), static_cast<int>(size.y)};

    m_playBut.init("Play", {100, 50}, sf::Color::Black, sf::Color::Cyan, sf::Color::Green, sf::Color::Red);
    m_loadBut.init("Load", {100, 50}, sf::Color::Black, sf::Color::Cyan, sf::Color::Green, sf::Color::Red);
    m_loadCb = new LoadCb(this);
    m_loadBut.assign(m_loadCb);
    m_saveBut.init("Save", {100, 50}, sf::Color::Black, sf::Color::Cyan, sf::Color::Green, sf::Color::Red);
    m_clearBut.init("Clear", {100, 50}, sf::Color::Black, sf::Color::Cyan, sf::Color::Green, sf::Color::Red);
    m_settingsBut.init("Settings", {100, 50}, sf::Color::Black, sf::Color::Cyan, sf::Color::Green, sf::Color::Red);
    m_importBut.init("Import", {100, 50}, sf::Color::Black, sf::Color::Cyan, sf::Color::Green, sf::Color::Red);
}

ControlBar::~ControlBar() {
    m_playBut.assign(nullptr);
    delete m_playCb;
}

void ControlBar::draw(sf::Vector2<int> position) {

    auto* window = LayoutManager::instance().window();
    window->setView(LayoutManager::instance().controlsTarget());

    m_draw_pos.x = static_cast<float>(position.x) + 10;
    m_draw_pos.y = static_cast<float>(position.y) + 10;
    m_playBut.setPosition(m_draw_pos);
    m_playBut.draw(*window);

    m_draw_pos.x += 100 + 10;
    m_loadBut.setPosition(m_draw_pos);
    m_loadBut.draw(*window);

    m_draw_pos.x += 100 + 10;
    m_saveBut.setPosition(m_draw_pos);
    m_saveBut.draw(*window);

    m_draw_pos.x += 100 + 10;
    m_clearBut.setPosition(m_draw_pos);
    m_clearBut.draw(*window);

    m_draw_pos.x += 100 + 10;
    m_settingsBut.setPosition(m_draw_pos);
    m_settingsBut.draw(*window);

    m_draw_pos.x += 100 + 10;
    m_importBut.setPosition(m_draw_pos);
    m_importBut.draw(*window);
}


bool ControlBar::onMouseMove(int x, int y) {
    static std::vector<UiButton*> buttons {
        &m_playBut,
        &m_loadBut,
        &m_saveBut,
        &m_clearBut,
        &m_settingsBut,
        &m_importBut,
    };

    for(auto& b : buttons) {
        if(b->contains(x, y) && !b->isMouseHovered()) {
            b->mouseEntered();
        }
        else if(!b->contains(x, y) && b->isMouseHovered()) {
            b->mouseExited();
        }
    }

    return false;
}

bool ControlBar::onMouseDown(int x, int y, int but) {
    static std::vector<UiButton*> buttons {
            &m_playBut,
            &m_loadBut,
            &m_saveBut,
            &m_clearBut,
            &m_settingsBut,
            &m_importBut,
    };

    if(but == 0) {
        for(auto& b : buttons) {
            if(b->contains(x, y)) {
                b->mouseDown();
                return true;
            }
        }
    }

    return false;
}

bool ControlBar::onMouseUp( int but) {
    static std::vector<UiButton*> buttons {
            &m_playBut,
            &m_loadBut,
            &m_saveBut,
            &m_clearBut,
            &m_settingsBut,
            &m_importBut,
    };

    if(but == 0) {
        for(auto& b : buttons) {
            if(b->isMouseDown()) {
                b->mouseUp();
                return true;
            }
        }
    }

    return false;
}

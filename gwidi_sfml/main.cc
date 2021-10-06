#include <iostream>
#include <SFML/Audio.hpp>
#include <SFML/Graphics.hpp>
#include "events/GlobalMouseEventHandler.h"

#include "data/DataManager.h"
#include "gui/LayoutManager.h"
#include "playback/PlaybackManager.h"
#include "gui/ControlBar.h"
#include "events/ThreadPool.h"
#include "data/MeasureGrid.h"

// TODO: For the text on the slots, draw them to a render texture, save that out, use it as the texture of the sprite that we modify with clicks
// TODO: See: https://progsv.epfl.ch/www/doc-sfml/html/classsf_1_1RenderTexture.htm   https://en.sfml-dev.org/forums/index.php?topic=16086.0

// TODO: Logic to 'select' the octaves we want to play (3 main octaves)

// TODO: Make a logger class

int main() {
    // Create the main window
    sf::RenderWindow window(sf::VideoMode(800, 600), "SFML window");
    // Load music to play
//    sf::Music music;
//    if (!music.openFromFile("E:/tools/repos/gwidi_sfml/assets/gw_prophecies.ogg"))
//        return EXIT_FAILURE;
//    // Play the music
//    music.play();

    class DataManagerCb : public DataManager::Callback {
    public:
        void onLoadComplete() override {
            gwidi::playback::PlaybackManager::instance().init(DataManager::instance().song(), 0);
        }
    };

    DataManagerCb cb;
    GlobalMouseEventHandler handler;
    LayoutManager::instance().assignWindow(window);
    LayoutManager::instance().setup(window, handler);
    DataManager::instance().load(handler, &cb);

    // Start the game loop
    while (window.isOpen())
    {
        // Process events
        sf::Event event;
        while (window.pollEvent(event))
        {
            // Close window: exit
            if (event.type == sf::Event::Closed)
                window.close();
            else if(event.type == sf::Event::MouseButtonPressed) {
                std::cout << "event pressed, button: " << event.mouseButton.button << std::endl;
                if (event.mouseButton.button == 1 || event.mouseButton.button == 0 || event.mouseButton.button == 2) {
                    handler.handleMouseDown(event.mouseButton.button, event.mouseButton.x, event.mouseButton.y);
                }
            }
            else if(event.type == sf::Event::MouseButtonReleased) {
                if(event.mouseButton.button == 1 || event.mouseButton.button == 0 || event.mouseButton.button == 2) {
                    handler.handleMouseUp(event.mouseButton.button);
                }
            }
            else if(event.type == sf::Event::MouseMoved) {
                handler.handleMouseMove(event.mouseMove.x, event.mouseMove.y);
            }
            else if (event.type == sf::Event::Resized) {
                // update the view to the new size of the window (show more instead of stretch views to the new 'size')
//                sf::FloatRect visibleArea(0, 0, event.size.width, event.size.height);
                LayoutManager::instance().setup(window, handler);
//                window.setView(sf::View(visibleArea));
            }
        }

        // Clear screen
        window.clear(sf::Color::Black);

        // Draw some layout stuff (Z-order == order of draw)
        // 3 panels (control bar, grid content, scrub bar)
        // Set views / viewports so that content in the middle is restrained
        LayoutManager::instance().draw(window);

        if(DataManager::instance().isLoaded()) {
            DataManager::instance().grid()->draw(window, LayoutManager::instance().contentTarget(), {0, 0});
        }

        // Update the window
        window.display();
    }

    ThreadPool::instance().shutdown();

    return EXIT_SUCCESS;
}
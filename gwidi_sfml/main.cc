#include <iostream>
#include <SFML/Audio.hpp>
#include <SFML/Graphics.hpp>
#include "events/GlobalMouseEventHandler.h"

#include "data/MeasureGrid.h"

// Don't need this yet, but might for other events that need to call window.clear
//class GlobalHandler : public GlobalMouseEventHandler::Callback{
//    virtual void onScrolled(int x, int y) {
//
//    }
//};

// TODO: Don't draw shapes, draw sf::Image with pixels so we only call 'draw' once for it vs so many others

int main()
{
    // Create the main window
    sf::RenderWindow window(sf::VideoMode(800, 600), "SFML window");
    // Load a sprite to display
    sf::Texture texture;
    if (!texture.loadFromFile("E:/tools/repos/gwidi_sfml/assets/cute_image.jpg"))
        return EXIT_FAILURE;
    sf::Sprite sprite(texture);
    // Create a graphical text to display
    sf::Font font;
    if (!font.loadFromFile("E:/tools/repos/gwidi_sfml/assets/arial.ttf"))
        return EXIT_FAILURE;
    sf::Text text("Hello SFML", font, 50);
    // Load a music to play
    sf::Music music;
    if (!music.openFromFile("E:/tools/repos/gwidi_sfml/assets/gw_prophecies.ogg"))
        return EXIT_FAILURE;
    // Play the music
    music.play();

    // Build our data
    std::shared_ptr<MeasureGrid> measureGrid = std::make_shared<MeasureGrid>();
//    std::cout << (std::string)*measureGrid << std::endl;

    // TODO: Offload loading the grid, it takes too long for large amounts

    GlobalMouseEventHandler handler;
    handler.subscribe(measureGrid);

    auto draw_grid = [&measureGrid](sf::RenderWindow &window){
        measureGrid->draw(window);
    };

    // Start the game loop
    bool first_draw{true};
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
                if (event.mouseButton.button == 1 || event.mouseButton.button == 0) {
                    handler.handleMouseDown(event.mouseButton.button, event.mouseButton.x, event.mouseButton.y);
                }
            }
            else if(event.type == sf::Event::MouseButtonReleased) {
                if(event.mouseButton.button == 1 || event.mouseButton.button == 0) {
                    handler.handleMouseUp();
                }
            }
            else if(event.type == sf::Event::MouseMoved) {
                handler.handleMouseMove(event.mouseMove.x, event.mouseMove.y);
            }
            else if (event.type == sf::Event::Resized) {
                // update the view to the new size of the window (show more instead of stretch views to the new 'size')
                sf::FloatRect visibleArea(0, 0, event.size.width, event.size.height);
                window.setView(sf::View(visibleArea));
            }
        }
        // Clear screen
//        if(first_draw) {
//            first_draw = false;
            window.clear(sf::Color::Black);
//        }

        draw_grid(window);

        // Update the window
        window.display();
    }
    return EXIT_SUCCESS;
}
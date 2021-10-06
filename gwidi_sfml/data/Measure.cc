#include <iostream>
#include "Measure.h"
#include "../gui/LayoutManager.h"

// TODO: Draw 2 textures: the background render texture (that has the text for the note labels) and the foreground
// TODO: Foreground is transparent except for squares that are activated (and these are semi-transparent as 'overlays' of the slots behind)
// TODO: This is an efficiency thing b/c the data lives in GPU buffers and we can't constantly update the same data for render texture as result (but we can a texture)

// TODO: Draw quarter note measure lines (every 4th slot) -- draw as part of background texture

Measure::~Measure() {
    if(m_background_renderTexture) {
        delete m_background_renderTexture;
        m_background_renderTexture = nullptr;
    }
    if(m_triggeredSlotsMutex) {
        delete m_triggeredSlotsMutex;
        m_triggeredSlotsMutex = nullptr;
    }
}

Measure::Measure() : Measure(Identifier{}) {}

Measure::Measure(Identifier id) : UiView(id) {

    // Build our notes/slots from the id information / constants
    int rows = Constants::notes.size();
    for(int r = 0; r < rows; r++) {
        m_notes.emplace_back(Note{{id.octave_index, id.measure_index, r, 0}});
    }

    m_bounds.top_left = {m_notes.front().bounds().top_left.x, m_notes.front().bounds().top_left.y};
    m_bounds.top_right = {m_notes.front().bounds().top_right.x, m_notes.front().bounds().top_right.y};
    m_bounds.bottom_left = {m_notes.back().bounds().bottom_left.x, m_notes.back().bounds().bottom_left.y};
    m_bounds.bottom_right = {m_notes.back().bounds().bottom_right.x, m_notes.back().bounds().bottom_right.y};

    m_bounds.bottom_left.y += UiConstants::measure_label_height;
    m_bounds.bottom_right.y += UiConstants::measure_label_height;
}

Measure::Measure(gwidi::data::Octave& o, Identifier id) : UiView(id) {

    // Build our notes/slots from the id information / constants
    int index = 0;
    for(auto &note : o.notes()) {
//        std::cout << "note key: " << note.key() << ", octave_index: " << id.octave_index << ", note_index: " << index << std::endl;
        m_notes.emplace_back(Note{note, {id.octave_index, id.measure_index, index, 0}});
        index++;
    }

    m_bounds.top_left = {m_notes.front().bounds().top_left.x, m_notes.front().bounds().top_left.y};
    m_bounds.top_right = {m_notes.front().bounds().top_right.x, m_notes.front().bounds().top_right.y};
    m_bounds.bottom_left = {m_notes.back().bounds().bottom_left.x, m_notes.back().bounds().bottom_left.y};
    m_bounds.bottom_right = {m_notes.back().bounds().bottom_right.x, m_notes.back().bounds().bottom_right.y};

    m_bounds.bottom_left.y += UiConstants::measure_label_height;
    m_bounds.bottom_right.y += UiConstants::measure_label_height;
}

std::string Measure::measureLabelText() {
    std::stringstream ss;
    ss << "Octave " << Constants::octaves()[id().octave_index] << "  Measure " << (id().measure_index + 1);
    return ss.str();
}

void Measure::build(sf::Vector2f offset) {
    m_triggeredSlotsMutex = new std::mutex();
    m_initialPos = offset;
    auto size = m_bounds.size();
    m_background_image_pixels = new sf::Uint8[size.x * size.y * 4];  // entries are utf32, but the type is utf8 so we need to mult by 4
    m_foreground_image_pixels = new sf::Uint8[size.x * size.y * 4];  // entries are utf32, but the type is utf8 so we need to mult by 4
    for(auto &n : m_notes) {
        for(auto &s : n.slots()) {
            s.draw_background(m_background_image_pixels, size);
            s.draw_foreground(m_foreground_image_pixels, size);
        }
    }
    // This creates our base grid texture
    m_background_image.create(size.x, size.y, m_background_image_pixels);
    m_background_texture.create(size.x, size.y);
    m_background_texture.update(m_background_image);
    m_background_sprite.setTexture(m_background_texture);

    // This stores this sprite onto the render texture
    m_background_renderTexture = new sf::RenderTexture();
    m_background_renderTexture->create(size.x, size.y);
    m_background_renderTexture->draw(m_background_sprite);

    // Draw quarter note boundaries
    for(auto &n : m_notes) {
        int index = 0;
        for(auto &s : n.slots()) {
            index++;
            if(index % 4 == 0) {
                sf::RectangleShape quarterNoteRect({2.f, static_cast<float>(s.bounds().size().y)});
                quarterNoteRect.setFillColor(sf::Color::Red);
                quarterNoteRect.setPosition(s.bounds().top_right.x, s.bounds().top_right.y);
                m_background_renderTexture->draw(quarterNoteRect);
            }
        }
    }

    sf::RectangleShape labelRect({static_cast<float>(size.x), static_cast<float>(UiConstants::measure_label_height)});
    labelRect.setPosition({0.f, static_cast<float>( size.y - UiConstants::measure_label_height)});
    labelRect.setFillColor(sf::Color(170, 4, 4, 255));

    sf::Text labelText(measureLabelText(), LayoutManager::instance().mainFont(), 13);
    auto textBounds = labelText.getLocalBounds();
    labelText.setFillColor(sf::Color::White);
    labelText.setOrigin(textBounds.left + (textBounds.width / 2.f), textBounds.top + (textBounds.height / 2.f));
    int text_posx = labelRect.getPosition().x + labelRect.getSize().x / 2;
    int text_posy = labelRect.getPosition().y + labelRect.getSize().y / 2;
    // Use ints here so that we draw on pixel-perfect positions (otherwise font can be blurry)
    labelText.setPosition({static_cast<float>(text_posx), static_cast<float>(text_posy)});

    m_background_renderTexture->draw(labelRect);
    m_background_renderTexture->draw(labelText);

    // This adds text
    for(auto &n : m_notes) {
        for(auto &s : n.slots()) {
            s.drawText(*m_background_renderTexture, m_background_sprite.getPosition());
        }
    }
    // Required to display before retrieving the texture (leaves drawn objects in undefined state otherwise)
    m_background_renderTexture->display();

    // Finally, this applies the rendered texture (both grid + text) as the sprite itself
    m_background_sprite.setTexture(m_background_renderTexture->getTexture());


    // Apply our foreground imaging
    m_foreground_image.create(size.x, size.y, m_foreground_image_pixels);
    m_foreground_texture.create(size.x, size.y);
    m_foreground_texture.update(m_foreground_image);
    m_foreground_sprite.setTexture(m_foreground_texture);


    m_background_sprite.setPosition(m_initialPos);
}

void Measure::draw() {
    LayoutManager::instance().window()->draw( m_background_sprite);
    LayoutManager::instance().window()->draw(m_foreground_sprite);
}


void Measure::scroll(sf::Vector2f offset) {
    m_background_sprite.setPosition(m_initialPos + offset);
    m_foreground_sprite.setPosition(m_initialPos + offset);
}

Slot* Measure::slotIndexForMouse(int x, int y, bool remove) {
    auto g_bounds = m_background_sprite.getGlobalBounds();
    if(g_bounds.contains(x, y)) {
        // Get index via the slot width / height vs bounds
        float offset_x = x - g_bounds.left;
        float offset_y = y - g_bounds.top;
        int slot_index = static_cast<int>((offset_x / float(UiConstants::measure_width)) * float(Constants::slots_per_measure));
        int note_index = static_cast<int>((offset_y / float(UiConstants::measure_height)) * float(Constants::notes.size()));

        std::cout << "slot index found for mouse: " << slot_index << ", " << note_index << std::endl;
        if(note_index >= m_notes.size() || slot_index >= m_notes[note_index].slots().size()) {
            return nullptr;
        }

        std::cout << "slot index found for mouse: " << slot_index << ", " << note_index << std::endl;
        {
            std::lock_guard<std::mutex> lock(*m_triggeredSlotsMutex);
            auto found = std::find_if(m_triggeredSlots.begin(), m_triggeredSlots.end(), [&note_index, &slot_index](Coord2D &entry){
                return entry.x == note_index && entry.y == slot_index;
            }) != m_triggeredSlots.end();
            // Don't re-trigger
            if(found) {
                return nullptr;
            }
            else {
                m_triggeredSlots.emplace_back(Coord2D{note_index, slot_index});
            }
        }
        auto &slot = m_notes[note_index].slots()[slot_index];

        // Use these indices / this measure to trigger the slot
        if(remove) {
            slot.updateDrawState(Slot::DrawState::DS_NONE, m_foreground_image_pixels);
        }
        else {
            if(slot.drawState() == Slot::DrawState::DS_ACTIVATED) {
                slot.updateDrawState(Slot::DrawState::DS_HELD, m_foreground_image_pixels);
            }
            else {
                slot.updateDrawState(Slot::DrawState::DS_ACTIVATED, m_foreground_image_pixels);
            }
        }

        m_foreground_texture.update(m_foreground_image_pixels);
        m_foreground_sprite.setTexture(m_foreground_texture);
        return &slot;
    }
    return nullptr;
}

sf::FloatRect Measure::globalBounds() const {
    return m_background_sprite.getGlobalBounds();
}

void Measure::clearTriggeredSlotsStatus() {
    std::lock_guard<std::mutex> lock(*m_triggeredSlotsMutex);
    m_triggeredSlots.clear();
}
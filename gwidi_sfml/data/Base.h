#ifndef GWIDI_SFML_BASE_H
#define GWIDI_SFML_BASE_H
#include <sstream>
#include <SFML/Graphics.hpp>

// Union instead? Need to reduce from 4 ints to X needed instead
struct Identifier {
    int octave_index{0};
    int measure_index{0};
    int note_index{0};
    int slot_index{0};
    Identifier() : Identifier(0, 0, 0, 0) {}
    Identifier(int octave, int measure, int note, int slot) : octave_index{octave}, measure_index{measure}, note_index{note}, slot_index{slot} {}
};
static Identifier EMPTY_IDENTIFIER;

struct Coord2D {
    Coord2D() : Coord2D(0, 0) {}
    Coord2D(int inx, int iny) : x{inx}, y{iny} {}
    int x = 0;
    int y = 0;
};

struct RectBounds {
    Coord2D top_left;
    Coord2D top_right;
    Coord2D bottom_left;
    Coord2D bottom_right;

    Coord2D padding_top_left;
    Coord2D padding_top_right;
    Coord2D padding_bottom_left;
    Coord2D padding_bottom_right;

    explicit operator std::string() const {
        std::stringstream ss;
        ss << "[ top_left: [" << top_left.x << ", " << top_left.y << "], ";
        ss << "top_right: [" << top_right.x << ", " << top_right.y << "], ";
        ss << "bottom_left: [" << bottom_left.x << ", " << bottom_left.y << "], ";
        ss << "bottom_right: [" << bottom_right.x << ", " << bottom_right.y << "] ]";
        return ss.str();
    }

    void assignToPixels(sf::Uint8 *pixels, Coord2D &size, sf::Color color, sf::Vector2<int> padding = {0, 0}) {
        // pixels is 1d, need to get the indices
        Coord2D* tl = &top_left;
        Coord2D* tr = &top_right;
        Coord2D* bl = &bottom_left;
        Coord2D* br = &bottom_right;
        if(padding.x != 0 && padding.y != 0) {
            padding_top_left        = {top_left.x + padding.x, top_left.y + padding.y};
            padding_top_right       = {top_right.x - padding.x, top_right.y + padding.y};
            padding_bottom_left     = {bottom_left.x + padding.x, bottom_left.y - padding.y};
            padding_bottom_right    = {bottom_right.x - padding.x, bottom_right.y - padding.y};

            tl = &padding_top_left;
            tr = &padding_top_right;
            bl = &padding_bottom_left;
            br = &padding_bottom_right;
        }

        // Assign pixels from top-left -> bottom-right
        // Each entry is 32 bits, need to increment as necessary
        for(size_t x = tl->x; x < tr->x; x++) {
            for(size_t y = tl->y; y < bl->y; y++) {
                size_t index = ((size.x * y) + x) * 4;
                pixels[index + 0] = color.r; // R
                pixels[index + 1] = color.g; // G
                pixels[index + 2] = color.b; // B
                pixels[index + 3] = color.a; // A
            }
        }
    }

    Coord2D size() {
        auto w = std::abs(top_right.x - top_left.x);
        auto h = std::abs(bottom_left.y - top_left.y);
        return {w, h};
    }
};

class UiView {
protected:
    Identifier m_id;
    RectBounds m_bounds;
public:
    UiView() = default;
    UiView(Identifier id) : m_id{id} {}
    Identifier id() { return m_id; }
    virtual RectBounds& bounds() { return m_bounds; }
};

#endif //GWIDI_SFML_BASE_H

#ifndef GWIDI_SFML_NOTE_H
#define GWIDI_SFML_NOTE_H

#include "Constants.h"
#include <vector>
#include "Base.h"
#include "Slot.h"
#include "GwidiData.h"

namespace gwidi { namespace view {

class Note : public UiView {
private:
    std::vector<Slot> m_slots;
    UiConstants::Note_RowType m_type;

public:
    Note();

    Note(Identifier id);

    Note(gwidi::data::Note &n, Identifier id);

    Note(Identifier &id, UiConstants::Note_RowType type);

    ~Note() = default;

    std::vector<Slot> &slots() {
        return m_slots;
    }

    explicit operator std::string() const;
};

}}

#endif //GWIDI_SFML_NOTE_H

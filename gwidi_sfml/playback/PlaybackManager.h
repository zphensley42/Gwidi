#ifndef GWIDI_SFML_PLAYBACKMANAGER_H
#define GWIDI_SFML_PLAYBACKMANAGER_H

#include "GwidiData.h"
#include <thread>
#include <mutex>
#include <condition_variable>
#include <SFML/Audio.hpp>

namespace gwidi {
namespace playback {

// TODO: Callback for when a slot is 'played'

class PlaybackManager {
public:
    class Callback {
    public:
        virtual void playSlot(unsigned int index) = 0;
    };

    enum PlaybackState {
        PBS_NONE = 0,
        PBS_INITIALIZED,
        PBS_PLAYING,
        PBS_PAUSED,
        PBS_STOPPED,
        PBS_SKIPPING
    };
    PlaybackManager();
    ~PlaybackManager();
    static PlaybackManager& instance();

    void init(std::shared_ptr<gwidi::data::Song> song, int trackNum);
    void play();
    void pause();
    void stop(bool doJoin = true);
    void skip(int position);

    inline void assign(Callback* cb) {
        m_cb = cb;
    }

    PlaybackState state();

private:
    int sleepTick();
    void playSlot(gwidi::data::VerticalSlotRepr &slot);
    void initSample(const std::string &note, int octave);

    std::mutex m_stateMutex;
    void updateState(PlaybackState state);

    PlaybackState m_playbackState;

    std::thread* m_playbackThread{nullptr};
    int m_currentTrack{-1};
    std::shared_ptr<gwidi::data::Song> m_currentSong{nullptr};
    int m_currentSongBpmTick{1};

    std::condition_variable m_pauseCv;
    std::mutex m_pauseMutex;

    std::condition_variable m_initCv;
    std::mutex m_initMutex;

    std::condition_variable m_skipCv;
    std::mutex m_skipMutex;

    unsigned int m_startPlayPosition{0};
    unsigned int m_playPosition{0};
    unsigned int m_slotLimit{0};

    Callback* m_cb{nullptr};

    std::unordered_map<std::string, sf::Music> m_pianoSamples;
};

}
}


#endif //GWIDI_SFML_PLAYBACKMANAGER_H

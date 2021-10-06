#include "PlaybackManager.h"

#include <utility>
#include <iostream>
#include <sstream>

namespace gwidi{
namespace playback {

PlaybackManager &PlaybackManager::instance() {
    static PlaybackManager s;
    return s;
}

void PlaybackManager::initSample(const std::string &note, int octave) {
    sf::Music m;
    std::stringstream ss;
    ss << "Build/gwidi/assets/samples/piano/";
    ss << note << octave << ".wav";

    std::stringstream ss2;
    ss2 << note << octave;
    m_pianoSamples[ss2.str()].openFromFile(ss.str());
}

PlaybackManager::PlaybackManager() {
    // Initialize our music files
    for(int i = 4; i <= 7; i++) {
        initSample("C", i);
        initSample("D", i);
        initSample("E", i);
        initSample("F", i);
        initSample("G", i);
        initSample("A", i);
        initSample("B", i);
    }
}

PlaybackManager::~PlaybackManager() {
    stop();
}

int PlaybackManager::sleepTick() {
    if(m_currentSong) {
        float sleep_mult = 4.f / 16.f;    // 4 / slots per measure (ticks are defined in 16th notes currently)
        float sleep_amount = (60 * sleep_mult) / static_cast<float>(m_currentSong->tempo());
        int sleep_millis = static_cast<int>(sleep_amount * 1000.f);
        return sleep_millis;
    }
    return 1;
}

void PlaybackManager::playSlot(gwidi::data::VerticalSlotRepr &slot) {
    std::stringstream ss;
    auto note_converted = slot.note;
    if(note_converted == "C1" || note_converted == "C2") {
        note_converted = "C";
    }
    ss << note_converted << slot.octave_num;
    m_pianoSamples[ss.str()].setLoop(false);
    m_pianoSamples[ss.str()].stop();
    m_pianoSamples[ss.str()].play();
}

void PlaybackManager::init(std::shared_ptr<gwidi::data::Song> song, int trackNum) {
    if(state() == PBS_NONE || state() == PBS_STOPPED) {
        m_currentTrack = trackNum;
        m_currentSong = std::move(song);
        m_currentSongBpmTick = sleepTick();
        m_slotLimit = m_currentSong->slotsForParams(0, 0, "A").size();

        if(!m_currentSong) {
            updateState(PBS_STOPPED);
            // Error, no song to play
            return;
        }
        updateState(PBS_INITIALIZED);


        m_playbackThread = new std::thread([this]() {
            // Wait for playback to actually begin
            // While paused, wait until we notify
            while(state() == PBS_INITIALIZED) {
                std::unique_lock<std::mutex> lock(m_initMutex);
                m_initCv.wait(lock);
            }

            // Reset our playback position
            m_playPosition = m_startPlayPosition;

            while(state() == PBS_PLAYING || state() == PBS_PAUSED || state() == PBS_SKIPPING) {
                {
                    // While paused, wait until we notify
                    if(state() == PBS_PAUSED) {
                        std::unique_lock<std::mutex> lock(m_pauseMutex);
                        m_pauseCv.wait(lock);
                        continue;
                    }

                    // While skipping, wait until we notify
                    if(state() == PBS_SKIPPING) {
                        std::unique_lock<std::mutex> lock(m_skipMutex);
                        m_skipCv.wait(lock);
                        continue;
                    }
                }

                if(m_cb) {
                    m_cb->playSlot(m_playPosition);
                }
                auto slots = m_currentSong->slotsForParams(m_currentTrack, m_playPosition);  // TODO: Fix these unsigned vs signed issues
                for(auto& slot : slots) {
                    if(slot.slot.state() == data::Slot::SLOT_ACTIVATED) {
                        playSlot(slot);
                        std::cout << "Playing note: " << slot.note << ", octave: " << slot.octave_num << std::endl;
                    }
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(m_currentSongBpmTick));

                // Move to the next position
                m_playPosition++;

                if(m_playPosition >= m_slotLimit) {
                    stop(false);
                    init(m_currentSong, m_currentTrack);    // Reset ourselves
                }
            }
        });
    }
}

void PlaybackManager::play() {
    switch(state()) {
        case PlaybackState::PBS_INITIALIZED: {
            // start play
            updateState(PBS_PLAYING);
            m_initCv.notify_one();
            break;
        }
        case PlaybackState::PBS_PAUSED: {
            // resume play
            updateState(PBS_PLAYING);
            m_pauseCv.notify_one();
            break;
        }
    }
}

void PlaybackManager::pause() {
    if(state() == PBS_PLAYING) {
        updateState(PBS_PAUSED);
    }
}

void PlaybackManager::stop(bool doJoin) {
    if(state() != PBS_STOPPED) {
        updateState(PBS_STOPPED);
        if(m_playbackThread) {
            if(doJoin) {
                m_playbackThread->join();
            }
            m_playbackThread = nullptr;
        }
    }
}

void PlaybackManager::skip(int position) {
    if(state() == PBS_PLAYING || state() == PBS_PAUSED) {
        updateState(PBS_SKIPPING);
        m_playPosition = position;

        updateState(PBS_PLAYING);
        m_skipCv.notify_one();
    }
}

void PlaybackManager::updateState(PlaybackState state) {
    std::lock_guard<std::mutex> lock(m_stateMutex);
    m_playbackState = state;
}

PlaybackManager::PlaybackState PlaybackManager::state() {
    std::lock_guard<std::mutex> lock(m_stateMutex);
    return m_playbackState;
}


}
}
#ifndef GWIDI_SFML_THREADPOOL_H
#define GWIDI_SFML_THREADPOOL_H

#include <thread>
#include <functional>
#include <condition_variable>
#include <mutex>
#include <queue>
#include <vector>

class ThreadTask {
public:
    ThreadTask();
    ThreadTask(std::function<void()> fn);
    void exec();
private:
    std::function<void()> m_fn{nullptr};
};

class ThreadInstance {
public:
    ThreadInstance();
    ~ThreadInstance();

    void run();
    void kill();
    void pushTask(ThreadTask* task);
    inline int taskCount() {
        return m_tasks.size();
    }
private:
    std::thread *m_thread{nullptr};
    std::queue<ThreadTask*> m_tasks;
    std::condition_variable m_taskCv;
    std::mutex m_taskMutex;

    bool m_alive{false};
};

class ThreadPool {
public:
    static ThreadPool &instance();
    ThreadPool();
    ~ThreadPool();

    void schedule(std::function<void()> task);
    void shutdown();

private:
    std::vector<ThreadInstance*> m_threads;
};


#endif //GWIDI_SFML_THREADPOOL_H

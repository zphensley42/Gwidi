#include <iostream>
#include "ThreadPool.h"

// TODO: Something is occasionally hanging when scheduling a lot of tasks quickly

ThreadPool::ThreadPool() {
//    int num_threads = std::thread::hardware_concurrency();
    int num_threads = 4;

    for(unsigned int i = 0; i < num_threads; i++) {
        m_threads.emplace_back(new ThreadInstance{});
        m_threads.back()->run();
    }
    // TODO: Don't always run, spin-up as necessary
}

ThreadPool::~ThreadPool() {
    for(auto& t : m_threads) {
        delete t;
    }
    m_threads.clear();
}

void ThreadPool::schedule(std::function<void()> task) {
    int leastCount = -1;
    ThreadInstance* leastThreadInstance = nullptr;
    for(auto &t : m_threads) {
        if(leastCount == -1 || leastCount > t->taskCount()) {
            leastCount = t->taskCount();
            leastThreadInstance = t;
        }
    }
    if(leastThreadInstance) {
        auto newTask = new ThreadTask(std::move(task));
        leastThreadInstance->pushTask(newTask);
    }
}

ThreadPool& ThreadPool::instance() {
    static ThreadPool tp;
    return tp;
}

ThreadInstance::ThreadInstance() {
}

ThreadInstance::~ThreadInstance() {
    while(!m_tasks.empty()) {
        auto &t = m_tasks.front();
        delete t;
        m_tasks.pop();
    }
    m_taskCv.notify_all();
}

void ThreadInstance::run() {
    if(!m_thread) {
        m_alive = true;
        m_thread = new std::thread([this](){
            while(m_alive) {
                std::cout << "ThreadInstance waiting for task, count: " << m_tasks.size() << std::endl;
                if(m_tasks.empty()) {
                    std::unique_lock<std::mutex> lock(m_taskMutex);
                    m_taskCv.wait(lock);
                }
                auto &task = m_tasks.front();
                if(task) {
                    std::cout << "ThreadInstance task retrieved\n";
                    task->exec();
                    std::cout << "ThreadInstance task executed\n";
                    delete task;
                    m_tasks.pop();
                    std::cout << "ThreadInstance task poppped, new count: " << m_tasks.size() << std::endl;
                }
            }
        });
    }
}

void ThreadInstance::pushTask(ThreadTask *task) {
    m_tasks.push(task);
    m_taskCv.notify_one();
}

void ThreadInstance::kill() {
    m_alive = false;
    m_taskCv.notify_all();
}

ThreadTask::ThreadTask() : ThreadTask(nullptr){}
ThreadTask::ThreadTask(std::function<void()> fn) : m_fn{fn} {
}

void ThreadTask::exec() {
    if(m_fn) {
        m_fn();
    }
}

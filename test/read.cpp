#include <chronolog_client.h>
#include <iostream>
#include <cassert>
#include <vector>
#include <map>
#include <limits>
#include "chrono_monitor.h"  // For logger initialization

int main() {
    // Configuration file path (update this as needed)
    std::string conf_file_path = "/home/ssonar/chronolog/Debug/conf/./default_conf.json";

    // Initialize the ChronoLog client configuration
    ChronoLog::ConfigurationManager confManager(conf_file_path);

    // Logger initialization using configuration parameters
    int logger_init = chronolog::chrono_monitor::initialize(
        confManager.CLIENT_CONF.CLIENT_LOG_CONF.LOGTYPE,
        confManager.CLIENT_CONF.CLIENT_LOG_CONF.LOGFILE,
        confManager.CLIENT_CONF.CLIENT_LOG_CONF.LOGLEVEL,
        confManager.CLIENT_CONF.CLIENT_LOG_CONF.LOGNAME,
        confManager.CLIENT_CONF.CLIENT_LOG_CONF.LOGFILESIZE,
        confManager.CLIENT_CONF.CLIENT_LOG_CONF.LOGFILENUM,
        confManager.CLIENT_CONF.CLIENT_LOG_CONF.FLUSHLEVEL
    );
    if (logger_init == 1) {
        std::cerr << "Logger initialization failed." << std::endl;
        return -1;
    }
    std::cout << "[Reader] Logger successfully initialized." << std::endl;

    // Initialize the ChronoLog client
    chronolog::Client client(confManager);

    // Connect to ChronoVisor
    int ret = client.Connect();
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "[Reader] Failed to connect to ChronoVisor. Error code: " << ret << std::endl;
        return -1;
    }
    std::cout << "[Reader] Connected to ChronoVisor successfully." << std::endl;

    // Define the chronicle and story names (should match those used when writing)
    std::string chronicle_name = "chronicle_9990";
    std::string story_name = "story_9990";

    // Use flags = 1.
    int flags = 1;
    std::map<std::string, std::string> story_attrs;

    // Acquire the story for reading
    auto acquire_ret = client.AcquireStory(chronicle_name, story_name, story_attrs, flags);
    std::cout << "[Reader] Acquired story: " << chronicle_name << " " << story_name 
              << " Ret: " << acquire_ret.first << std::endl;
    
    // Assert that acquisition returned a permissible code
    assert(acquire_ret.first == chronolog::CL_SUCCESS ||
           acquire_ret.first == chronolog::CL_ERR_NOT_EXIST ||
           acquire_ret.first == chronolog::CL_ERR_NO_KEEPERS);

    if (acquire_ret.first == chronolog::CL_SUCCESS) {
        auto story_handle = acquire_ret.second;

        uint64_t segment_start = 0;
        uint64_t segment_end = std::numeric_limits<uint64_t>::max();

        std::vector<chronolog::Event> playback_events;

        std::cout << "[Reader] Sending playback request for story: " << chronicle_name << " " << story_name 
                  << " segment " << segment_start << "-" << segment_end << std::endl;
        ret = story_handle->playback_story(segment_start, segment_end, playback_events);
        if(ret == chronolog::CL_ERR_NO_PLAYERS) {
            std::cout << "[Reader] No Player found for story: " << chronicle_name << " " << story_name 
                      << ", ret: " << ret << std::endl;
        } else {
            std::cout << "[Reader] Playback request successful for story: " << chronicle_name << " " << story_name 
                      << ", ret: " << ret << std::endl;
        }


        // Release the story
        ret = client.ReleaseStory(chronicle_name, story_name);
        std::cout << "[Reader] Released story: " << chronicle_name << " " << story_name 
                  << " Ret: " << ret << std::endl;
        assert(ret == chronolog::CL_SUCCESS || ret == chronolog::CL_ERR_NO_CONNECTION || ret == chronolog::CL_ERR_NOT_ACQUIRED);
    }

    // Disconnect from ChronoVisor
    ret = client.Disconnect();
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "[Reader] Failed to disconnect from ChronoVisor. Error code: " << ret << std::endl;
    } else {
        std::cout << "[Reader] Disconnected from ChronoVisor successfully." << std::endl;
    }

    return 0;
}


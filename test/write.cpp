#include <chronolog_client.h>
#include <iostream>
#include <cassert>
#include "chrono_monitor.h"
#include <string>
#include <map>

int main() {
    // Configuration file path (update this to your configuration file location)
    std::string conf_file_path = "/home/ssonar/chronolog/Debug/conf/./default_conf.json";

    // Initialize ChronoLog client configuration
    ChronoLog::ConfigurationManager confManager(conf_file_path);

    // Initialize logger using configuration parameters
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
    std::cout << "Logger successfully initialized." << std::endl;

    // Initialize the ChronoLog client
    chronolog::Client client(confManager);

    // Connect to ChronoVisor
    int ret = client.Connect();
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "Failed to connect to ChronoVisor. Error code: " << ret << std::endl;
        return -1;
    }
    std::cout << "Successfully connected to ChronoVisor." << std::endl;

    // Set number of chronicles (M) and messages per chronicle (N)
    const int M = 5;  // number of chronicles/logs
    const int N = 10; // messages per chronicle

    for (int i = 0; i < M; ++i) {
        // Define a unique chronicle name for each log
        std::string chronicle_name = "chronicle_427" + std::to_string(i);
        
        // Create the chronicle
        std::map<std::string, std::string> chronicle_attrs;
        chronicle_attrs.emplace("Priority", "High");
        int flag = 0;
        ret = client.CreateChronicle(chronicle_name, chronicle_attrs, flag);
        if (ret != chronolog::CL_SUCCESS && ret != chronolog::CL_ERR_CHRONICLE_EXISTS) {
            std::cerr << "Failed to create chronicle '" << chronicle_name 
                      << "'. Error code: " << ret << std::endl;
            continue;  // Skip to the next chronicle if creation fails
        }
        if (ret == chronolog::CL_SUCCESS)
            std::cout << "Chronicle '" << chronicle_name << "' created successfully." << std::endl;
        else
            std::cout << "Chronicle '" << chronicle_name << "' already exists." << std::endl;

        // Acquire a story in the chronicle for logging events
        std::string story_name = "story_427" + std::to_string(i);
        std::map<std::string, std::string> story_attrs;
        int acquire_flag = 0;
        auto acquire_ret = client.AcquireStory(chronicle_name, story_name, story_attrs, acquire_flag);
        if (acquire_ret.first != chronolog::CL_SUCCESS) {
            std::cerr << "Failed to acquire story '" << story_name 
                      << "' in chronicle '" << chronicle_name 
                      << "'. Error code: " << acquire_ret.first << std::endl;
            continue;
        }
        std::cout << "Story '" << story_name 
                  << "' acquired in chronicle '" << chronicle_name << "'." << std::endl;

        // Get the story handle and log N messages to it
        auto story_handle = acquire_ret.second;
        for (int j = 0; j < N; ++j) {
            std::string message = "Message " + std::to_string(j) + " for " + chronicle_name;
            story_handle->log_event(message);
        }
        std::cout << "Logged " << N << " messages to " << chronicle_name << "." << std::endl;

        // Release the story after logging events
        ret = client.ReleaseStory(chronicle_name, story_name);
        if (ret != chronolog::CL_SUCCESS) {
            std::cerr << "Failed to release story '" << story_name 
                      << "' in chronicle '" << chronicle_name 
                      << "'. Error code: " << ret << std::endl;
        } else {
            std::cout << "Story '" << story_name << "' released successfully." << std::endl;
        }
    }

    // Disconnect the client
    ret = client.Disconnect();
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "Failed to disconnect from ChronoVisor. Error code: " << ret << std::endl;
        return -1;
    }
    std::cout << "Disconnected from ChronoVisor successfully." << std::endl;

    return 0;
}

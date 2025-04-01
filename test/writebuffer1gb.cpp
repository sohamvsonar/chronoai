#include <chronolog_client.h>
#include <iostream>
#include <cassert>
#include "chrono_monitor.h"  // For logger initialization

int main() {
    // Configuration file path (update this to your configuration file location)
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

    // Define the chronicle and story names
    std::string chronicle_name = "hello";
    std::string story_name = "world";

    // Create a chronicle
    std::map<std::string, std::string> chronicle_attrs;
    chronicle_attrs.emplace("Priority", "High");
    int flag = 0;
    ret = client.CreateChronicle(chronicle_name, chronicle_attrs, flag);
    if (ret != chronolog::CL_SUCCESS && ret != chronolog::CL_ERR_CHRONICLE_EXISTS) {
        std::cerr << "Failed to create chronicle. Error code: " << ret << std::endl;
        return -1;
    }
    if (ret == chronolog::CL_SUCCESS)
        std::cout << "Chronicle '" << chronicle_name << "' created successfully." << std::endl;
    else
        std::cout << "Chronicle '" << chronicle_name << "' already exists." << std::endl;

    // Acquire a story in the chronicle
    std::map<std::string, std::string> story_attrs;
    int acquire_flag = 0;
    auto acquire_ret = client.AcquireStory(chronicle_name, story_name, story_attrs, acquire_flag);
    if (acquire_ret.first != chronolog::CL_SUCCESS) {
        std::cerr << "Failed to acquire story. Error code: " << acquire_ret.first << std::endl;
        return -1;
    }
    std::cout << "Story '" << story_name << "' acquired successfully in chronicle '" << chronicle_name << "'." << std::endl;

    // Write a 1GB buffer to the story
    auto story_handle = acquire_ret.second;
    // Create a 1GB buffer filled with 'A'
    std::string buffer(1024ULL * 1024 * 1024, 'A'); 
    story_handle->log_event(buffer);
    std::cout << "Logged a 1GB event to story '" << story_name << "'." << std::endl;

    // Release the story
    ret = client.ReleaseStory(chronicle_name, story_name);
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "Failed to release story. Error code: " << ret << std::endl;
    } else {
        std::cout << "Story '" << story_name << "' released successfully." << std::endl;
    }

    // Disconnect the client
    ret = client.Disconnect();
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "Failed to disconnect. Error code: " << ret << std::endl;
    } else {
        std::cout << "Disconnected from ChronoVisor successfully." << std::endl;
    }

    return 0;
}


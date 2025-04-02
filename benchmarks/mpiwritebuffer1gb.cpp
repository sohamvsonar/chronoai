#include <mpi.h>
#include <chronolog_client.h>
#include <iostream>
#include <cassert>
#include <sstream>
#include <map>
#include "chrono_monitor.h"  // For logger initialization

int main(int argc, char **argv) {
    // Initialize MPI
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

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
        std::cerr << "[Rank " << rank << "] Logger initialization failed." << std::endl;
        MPI_Finalize();
        return -1;
    }
    std::cout << "[Rank " << rank << "] Logger successfully initialized." << std::endl;

    // Initialize the ChronoLog client
    chronolog::Client client(confManager);

    // Connect to ChronoVisor
    int ret = client.Connect();
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "[Rank " << rank << "] Failed to connect to ChronoVisor. Error code: " << ret << std::endl;
        MPI_Finalize();
        return -1;
    }
    std::cout << "[Rank " << rank << "] Connected to ChronoVisor successfully." << std::endl;

    // All processes use the same chronicle name but a unique story name per rank
    std::string chronicle_name = "hello";
    std::ostringstream oss;
    oss << "world_" << rank;
    std::string story_name = oss.str();

    // Create the chronicle (if already exists, it's acceptable)
    std::map<std::string, std::string> chronicle_attrs;
    chronicle_attrs.emplace("Priority", "High");
    int flag = 0;
    ret = client.CreateChronicle(chronicle_name, chronicle_attrs, flag);
    if (ret != chronolog::CL_SUCCESS && ret != chronolog::CL_ERR_CHRONICLE_EXISTS) {
        std::cerr << "[Rank " << rank << "] Failed to create chronicle. Error code: " << ret << std::endl;
        MPI_Finalize();
        return -1;
    }
    if (ret == chronolog::CL_SUCCESS)
        std::cout << "[Rank " << rank << "] Chronicle '" << chronicle_name << "' created successfully." << std::endl;
    else
        std::cout << "[Rank " << rank << "] Chronicle '" << chronicle_name << "' already exists." << std::endl;

    // Acquire a story in the chronicle (unique per process)
    std::map<std::string, std::string> story_attrs;
    int acquire_flag = 0;
    auto acquire_ret = client.AcquireStory(chronicle_name, story_name, story_attrs, acquire_flag);
    if (acquire_ret.first != chronolog::CL_SUCCESS) {
        std::cerr << "[Rank " << rank << "] Failed to acquire story '" << story_name 
                  << "'. Error code: " << acquire_ret.first << std::endl;
        MPI_Finalize();
        return -1;
    }
    std::cout << "[Rank " << rank << "] Story '" << story_name << "' acquired successfully in chronicle '" 
              << chronicle_name << "'." << std::endl;

    // Write a 1GB buffer event
    auto story_handle = acquire_ret.second;
    std::string buffer(1024ULL * 1024 * 1024, 'A');  // 1GB buffer filled with 'A'
    story_handle->log_event(buffer);
    std::cout << "[Rank " << rank << "] Logged a 1GB event to story '" << story_name << "'." << std::endl;

    // Release the story (without destroying it)
    ret = client.ReleaseStory(chronicle_name, story_name);
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "[Rank " << rank << "] Failed to release story '" << story_name 
                  << "'. Error code: " << ret << std::endl;
    } else {
        std::cout << "[Rank " << rank << "] Story '" << story_name << "' released successfully." << std::endl;
    }

    // Disconnect from ChronoVisor
    ret = client.Disconnect();
    if (ret != chronolog::CL_SUCCESS) {
        std::cerr << "[Rank " << rank << "] Failed to disconnect. Error code: " << ret << std::endl;
    } else {
        std::cout << "[Rank " << rank << "] Disconnected from ChronoVisor successfully." << std::endl;
    }

    // Finalize MPI
    MPI_Finalize();
    return 0;
}


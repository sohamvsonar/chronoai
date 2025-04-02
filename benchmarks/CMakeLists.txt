cmake_minimum_required(VERSION 3.10)
project(ChronoLogClientDemo)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

list(APPEND CMAKE_PREFIX_PATH "/home/ssonar/spack/opt/spack/linux-ubuntu24.04-zen/gcc-13.3.0/spdlog-1.12.0")
list(APPEND CMAKE_PREFIX_PATH "/home/ssonar/ChronoLog/.spack-env/view/include")
list(APPEND CMAKE_PREFIX_PATH "/home/ssonar/ChronoLog/.spack-env/view/include/spdlog")

# Find spdlog (it must be installed with its CMake config file)
find_package(spdlog REQUIRED)

#find_package(MPI REQUIRED)

# Locate the ChronoLog client library
find_library(CHRONOLOG_LIB chronolog_client PATHS /home/ssonar/chronolog/Debug/include /home/ssonar/chronolog/Debug/lib)
if(NOT CHRONOLOG_LIB)
    message(FATAL_ERROR "ChronoLog client library not found. Ensure ChronoLog is installed and the library is in your linker's search path.")
endif()

# Locate json-c
find_library(JSONC_LIB json-c PATHS /home/ssonar/chronolog/Debug/lib /usr/lib)

if(NOT JSONC_LIB)
    message(FATAL_ERROR "json-c library not found")
endif()

# Create the executable
add_executable(ChronoLogClientDemo sample.cpp)

target_link_libraries(ChronoLogClientDemo PRIVATE ${CHRONOLOG_LIB} json-c)
#target_link_libraries(ChronoLogClientDemo PRIVATE MPI::MPI_CXX)

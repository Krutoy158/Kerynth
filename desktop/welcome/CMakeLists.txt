cmake_minimum_required(VERSION 3.21)
project(kerynth-welcome LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 6.2 REQUIRED COMPONENTS Widgets)

add_executable(kerynth-welcome main.cpp)
target_link_libraries(kerynth-welcome PRIVATE Qt6::Widgets)

install(TARGETS kerynth-welcome RUNTIME DESTINATION bin)

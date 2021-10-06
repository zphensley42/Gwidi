cmake_minimum_required(VERSION 3.15.3)
project(gwidi_sfml)

set(SFML_USE_STATIC_STD_LIBS ON)
set(SFML_STATIC_LIBRARIES ON)
set(SFML_BUILD_EXAMPLES ON cache BOOL "Build sfml examples")
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -g -O0")

set(Gwidi_Importer_DIR ${CMAKE_CURRENT_LIST_DIR}/external/Gwidi_Importer/)
find_package(Gwidi_Importer REQUIRED)

# Find SFML. Note: this handles all dependencies, libraries and include directories.
#set(SFML_DIR "external/SFML/cmake")
#add_subdirectory("external/SFML")
if (WIN32)
    set(SFML_DIR "external/compiled/SFML-2.5.1/lib/cmake/SFML")
    find_package(SFML 2.5 COMPONENTS audio graphics window system REQUIRED)
else()
    add_subdirectory(external/SFML)
endif (WIN32)

if(NOT SFML_FOUND)
    set(SFML_DIR "" CACHE PATH "SFML top-level directory")
    message("\n-> SFML directory not found. Set SFML_DIR (not SFML_ROOT) to SFML's top-level path (containing \"include\" and \"lib\" directories).")
    message("-> Make sure the SFML libraries >= 2.5 with the same configuration (Release/Debug, Static/Dynamic) exist.\n")
endif()

add_executable(gwidi_sfml main.cc data/Slot.cc data/Slot.h data/MeasureGrid.cc data/MeasureGrid.h data/Constants.h data/Note.cc data/Note.h data/Constants.cc data/Base.h events/GlobalMouseEventHandler.cc events/GlobalMouseEventHandler.h data/Measure.cc data/Measure.h events/ThreadPool.cc events/ThreadPool.h data/DataManager.cc data/DataManager.h gui/ControlBar.cc gui/ControlBar.h gui/LayoutManager.cc gui/LayoutManager.h gui/ScrubBar.cc gui/ScrubBar.h gui/UiButton.cc gui/UiButton.h playback/PlaybackManager.cc playback/PlaybackManager.h)
target_link_libraries(gwidi_sfml Gwidi_Importer sfml-audio sfml-graphics sfml-window sfml-system)
get_target_property(Gwidi_Importer_Includes Gwidi_Importer INCLUDE_DIRECTORIES)
message("Gwidi_Importer_Includes: ${Gwidi_Importer_Includes}")
target_include_directories(gwidi_sfml PUBLIC ${Gwidi_Importer_Includes})


# Copy assets to build directory
set(copy_source_dir "${CMAKE_SOURCE_DIR}/assets")
set(copy_dest_dir "${CMAKE_BINARY_DIR}/Build/gwidi/assets")
add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory ${copy_dest_dir}
)
add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${copy_source_dir}" "${copy_dest_dir}"
        COMMENT "Copying assets to build directory"
)
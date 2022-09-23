cmake_minimum_required(VERSION 3.13)

# initialize pico-sdk from submodule
# note: this must happen before project()
include(pico-sdk/pico_sdk_init.cmake)

project(tracked_rc_bot)

# initialize the Raspberry Pi Pico SDK
pico_sdk_init()

# rest of project
add_executable(main
    main.cpp
    dabble.cpp
    track.cpp
)

target_link_libraries(main
    pico_stdlib
    hardware_pwm
    hardware_uart
)

# create map/bin/hex/uf2 file in addition to ELF.
pico_add_extra_outputs(main)

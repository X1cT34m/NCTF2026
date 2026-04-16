cmake_minimum_required(VERSION 3.10)
project(main)

set(CMAKE_C_STANDARD 99)

add_library(cipher SHARED cipher.c)

add_executable(main task.c)

target_compile_options(main PRIVATE
    -fno-stack-protector
)

target_link_options(main PRIVATE
    -no-pie
)

target_include_directories(main PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(main PRIVATE cipher)

set_target_properties(main PROPERTIES
    BUILD_RPATH "$ORIGIN"
    INSTALL_RPATH "$ORIGIN"
)

# Keep build system files in the build dir, but put final binaries in a
# predictable location.
set(_out_dir "${CMAKE_BINARY_DIR}/out")
foreach(_tgt cipher main)
  set_target_properties(${_tgt} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${_out_dir}"
    LIBRARY_OUTPUT_DIRECTORY "${_out_dir}"
    ARCHIVE_OUTPUT_DIRECTORY "${_out_dir}"
  )

  add_custom_command(TARGET ${_tgt} POST_BUILD
    COMMAND ${CMAKE_STRIP} $<TARGET_FILE:${_tgt}>
    COMMENT "Stripping symbols from ${_tgt}"
  )
endforeach()

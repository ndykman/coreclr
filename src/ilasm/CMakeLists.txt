project(ilasm)

add_definitions(-DUNICODE)
add_definitions(-D_UNICODE)
add_definitions(-D_FEATURE_NO_HOST)
add_definitions(-D__ILASM__)

add_definitions(-DFEATURE_CORECLR)

include_directories(.)
include_directories(../ildasm/unixcoreclrloader)

if(CLR_CMAKE_PLATFORM_UNIX)
  add_compile_options(-fPIE)
endif(CLR_CMAKE_PLATFORM_UNIX)

set(ILASM_SOURCES
  assem.cpp
  writer.cpp
  writer_enc.cpp
  method.cpp
  asmman.cpp
  main.cpp
  assembler.cpp
  prebuilt/asmparse.c
)
if(WIN32)
  set(ILASM_RESOURCES Native.rc)
  add_definitions(-DFX_VER_INTERNALNAME_STR=ilasm.exe)
endif(WIN32)

set_source_files_properties( prebuilt/asmparse.c PROPERTIES LANGUAGE CXX )

if(CLR_CMAKE_PLATFORM_UNIX)
  add_compile_options(-x c++)
  # Need generate a right form of asmparse.c to avoid the following options.
  # Clang also produces a bad-codegen on this prebuilt file with optimization.
  # https://github.com/dotnet/coreclr/issues/2305
  add_compile_options(-Wno-delete-non-virtual-dtor)
  add_compile_options(-Wno-deprecated-register)
  add_compile_options(-Wno-array-bounds)
  add_compile_options(-Wno-unused-label)
  set_source_files_properties( prebuilt/asmparse.c PROPERTIES COMPILE_FLAGS -O0 )
endif(CLR_CMAKE_PLATFORM_UNIX)

_add_executable(ilasm
  ${ILASM_SOURCES}
  ${ILASM_RESOURCES}
)

set(ILASM_LINK_LIBRARIES
  utilcodestaticnohost
  mscorpe
  mdhotdata_full
  corguids
)

if(CLR_CMAKE_PLATFORM_UNIX)
  target_link_libraries(ilasm
    ${ILASM_LINK_LIBRARIES}
    ceefgen
    unixcoreclrloader
    utilcodestaticnohost
    mscorrc_debug
    coreclrpal
    palrt
  )

  # FreeBSD and NetBSD implement dlopen(3) in libc
  if(NOT CMAKE_SYSTEM_NAME STREQUAL FreeBSD AND NOT CMAKE_SYSTEM_NAME STREQUAL NetBSD)
    target_link_libraries(ilasm
      dl
    )
  endif(NOT CMAKE_SYSTEM_NAME STREQUAL FreeBSD AND NOT CMAKE_SYSTEM_NAME STREQUAL NetBSD)
else()
  target_link_libraries(ilasm
    ${ILASM_LINK_LIBRARIES}
    coreclr
    ole32
    oleaut32
    shell32
  )
endif(CLR_CMAKE_PLATFORM_UNIX)

install_clr(ilasm)
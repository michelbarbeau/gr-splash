INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SPLASH splash)

FIND_PATH(
    SPLASH_INCLUDE_DIRS
    NAMES splash/api.h
    HINTS $ENV{SPLASH_DIR}/include
        ${PC_SPLASH_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SPLASH_LIBRARIES
    NAMES gnuradio-splash
    HINTS $ENV{SPLASH_DIR}/lib
        ${PC_SPLASH_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SPLASH DEFAULT_MSG SPLASH_LIBRARIES SPLASH_INCLUDE_DIRS)
MARK_AS_ADVANCED(SPLASH_LIBRARIES SPLASH_INCLUDE_DIRS)


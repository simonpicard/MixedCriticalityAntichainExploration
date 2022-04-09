cmake_minimum_required(VERSION 3.0.0)
project(mcs VERSION 0.1.0)

include(CTest)
enable_testing()

add_executable(mcs main.cpp GraphPeriodic.cpp StatePeriodic.cpp JobPeriodic.cpp GraphSporadic.cpp StateSporadic.cpp JobSporadic.cpp Scheduler.cpp Job.cpp State.cpp Graph.cpp)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)

add_library(todoStatic STATIC todo.cpp)
add_library(todoShared SHARED ../empty.cpp)
target_link_libraries(todoShared todoStatic)

SET_TARGET_PROPERTIES(todoStatic todoShared PROPERTIES OUTPUT_NAME todo)
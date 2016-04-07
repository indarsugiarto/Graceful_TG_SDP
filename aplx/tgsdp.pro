TEMPLATE = app
CONFIG += console c++11
CONFIG -= app_bundle
CONFIG -= qt

SOURCES += tgsdp.c \
    srcsink.c \
    helper.c


INCLUDEPATH += /opt/spinnaker_tools_134/include
DEPENDPATH += /opt/spinnaker_tools_134/include

HEADERS += \
    tgsdp.h

DISTFILES += \
    Makefile \
    how.does.it.work \
    dag0020.xml \
    README \
    ../dag0020.odg

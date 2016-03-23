##---------------------------------------------------------------------------------
##
## Makefile        Makefile for a Traffic Generator with SDP Mechanism in SpiNNaker
##
## Copyright (C)   The University of Manchester - 2016
##
## Author          Indar Sugiarto, APT Group, School of Computer Science
##
## Email           indar.sugiarto@manchester.ac.uk
##
##------------------------------------------------------------------------------

# This Makefile is a simplified version of the generic Makefil for SpiNNaker
# application written by Steve Temple.
# In this version, we use only GNU toolchain. To use it, simply call:
# make
# make tidy

# Put the correct SPINN and GNU toolchain here:
SPINN_DIRS := /opt/spinnaker_tools_134
GNU_DIRS := /opt/arm-2013.05/bin

APP := tgsdp

# Configuration options

# Set to 1 for GNU tools, 0 for ARM

GNU := 1

# Set to 1 if using SARK/API (0 for SARK)

API := 1

# Set to 1 to make Thumb code (0 for ARM)

THUMB := 1

# Prefix for GNU tool binaries

GP  := $(GNU_DIRS)/arm-none-eabi

# Set to 1 if making a library (advanced!)

LIB := 0

# If SPINN_DIRS is defined, use that to find include and lib directories
# otherwise look two levels up

ifdef SPINN_DIRS
  LIB_DIR := $(SPINN_DIRS)/lib
  INC_DIR := $(SPINN_DIRS)/include
else
  LIB_DIR := ../../lib
  INC_DIR := ../../include
endif

#-------------------------------------------------------------------------------

# Set up the various compile/link options for GNU and ARM tools

# GNU tool setup

ifeq ($(GNU),1)
  AS := $(GP)-as --defsym GNU=1 -mthumb-interwork -march=armv5te

  CA := $(GP)-gcc -c -Os -mthumb-interwork -march=armv5te -std=gnu99 \
	-I $(INC_DIR)

  CT := $(CA) -mthumb -DTHUMB

ifeq ($(LIB),1)
  CFLAGS += -fdata-sections -ffunction-sections
endif

ifeq ($(API),1)
#  LIBRARY := -L$(LIB_DIR) -lspin1_api
  LIBRARY := $(LIB_DIR)/libspin1_api.a
else
#  LIBRARY := -L$(LIB_DIR) -lsark
  LIBRARY := $(LIB_DIR)/libsark.a
endif

  SCRIPT := $(LIB_DIR)/sark.lnk

  LD := $(GP)-gcc -T$(SCRIPT) -Wl,-e,cpu_reset -Wl,--gc-sections -Wl,--use-blx 

  AR := $(GP)-ar -rcs
  OC := $(GP)-objcopy
  OD := $(GP)-objdump -dxt > $(APP).txt

# ARM tool setup

else
  AS := armasm --keep --cpu=5te --apcs /interwork

  CA := armcc -c --c99 --cpu=5te --apcs /interwork --min_array_alignment=4 \
	-I $(INC_DIR)

  CT := $(CA) --thumb -DTHUMB

ifeq ($(LIB),1)
  CFLAGS += --split_sections
endif

ifeq ($(API),1)
  LIBRARY := $(LIB_DIR)/spin1_api.a
else
  LIBRARY := $(LIB_DIR)/sark.a
endif

  SCRIPT := $(LIB_DIR)/sark.sct

  LD := armlink --scatter=$(SCRIPT) --remove --entry cpu_reset

  AR := armar -rcs
  OC := fromelf
  OD := fromelf -cds --output $(APP).txt

endif

ifeq ($(THUMB),1)
  CC := $(CT)
else
  CC := $(CA)
endif

CAT := \cat
RM  := \rm -f
LS  := \ls -l

#-------------------------------------------------------------------------------

# Build the application

# List of objects making up the application. If there are other files
# in the application, add their object file names to this variable.

OBJECTS := $(APP).o


# Primary target is an APLX file - built from the ELF

#  1) Create a binary file which is the concatenation of RO and RW sections
#  2) Make an APLX header from the ELF file with "mkaplx" and concatenate
#     that with the binary to make the APLX file
#  3) Remove temporary files and "ls" the APLX file

$(APP).aplx: $(APP).elf
ifeq ($(GNU),1)
	$(OC) -O binary -j RO_DATA -j .ARM.exidx $(APP).elf RO_DATA.bin
	$(OC) -O binary -j RW_DATA $(APP).elf RW_DATA.bin
	mkbin RO_DATA.bin RW_DATA.bin > $(APP).bin
else
	$(OC) --bin --output $(APP).bin $(APP).elf
endif
	mkaplx $(APP).elf | $(CAT) - $(APP).bin > $(APP).aplx
	$(RM) $(APP).bin RO_DATA.bin RW_DATA.bin
	$(LS) $(APP).aplx


# Build the ELF file

#  1) Make a "sark_build.c" file containing app. name and build time
#     with "mkbuild" and compile it
#  2) Link application object(s), build file and library to make the ELF
#  3) Tidy up temporaries and create a list file

$(APP).elf: $(OBJECTS) $(SCRIPT) $(LIBRARY) 
	mkbuild $(APP) > sark_build.c
	$(CC) sark_build.c
	$(LD) $(LFLAGS) $(OBJECTS) sark_build.o $(LIBRARY) -o $(APP).elf
	$(RM) sark_build.c sark_build.o
	$(OD) $(APP).elf


# Build the main object file. If there are other files in the
# application, place their build dependencies below this one.

$(APP).o: $(APP).c $(INC_DIR)/spinnaker.h $(INC_DIR)/sark.h \
	  $(INC_DIR)/spin1_api.h
	$(CC) $(CFLAGS) $(APP).c


# Tidy and cleaning dependencies

tidy:
	$(RM) $(OBJECTS) $(APP).elf $(APP).txt
clean:
	$(RM) $(OBJECTS) $(APP).elf $(APP).txt $(APP).aplx

#-------------------------------------------------------------------------------

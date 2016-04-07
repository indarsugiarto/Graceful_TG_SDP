# This Makefile is a simplified version of the generic Makefil for SpiNNaker
# application written by Steve Temple. In this version, we use only GNU toolchain.

# APP := tgsdp

# Put the correct SPINN and GNU toolchain here:
SPINN_DIRS := /opt/spinnaker_tools_134
GNU_DIRS   := /opt/arm-2013.05/bin
LIB_DIR    := $(SPINN_DIRS)/lib
INC_DIR    := $(SPINN_DIRS)/include

#-------------------------------------------------------------------------------

# Set up the various compile/link options for GNU tools
GP      := $(GNU_DIRS)/arm-none-eabi
AS      := $(GP)-as --defsym GNU=1 -mthumb-interwork -march=armv5te
CA      := $(GP)-gcc -c -Os -mthumb-interwork -march=armv5te -std=gnu99 -I $(INC_DIR)
CT      := $(CA) -mthumb -DTHUMB
LIBRARY := $(LIB_DIR)/libspin1_api.a
SCRIPT  := $(LIB_DIR)/sark.lnk
LD      := $(GP)-gcc -T$(SCRIPT) -Wl,-e,cpu_reset -Wl,--gc-sections -Wl,--use-blx
AR      := $(GP)-ar -rcs
OC      := $(GP)-objcopy
OD      := $(GP)-objdump -dxt > $(APP).txt
CC      := $(CT)
CAT     := \cat
RM      := \rm -f
LS      := \ls -l

#-------------------------------------------------------------------------------

# List of objects making up the application.
OBJECTS := $(APP).o helper.o


# Primary target is an APLX file - built from the ELF
$(APP).aplx: $(APP).elf
	$(OC) -O binary -j RO_DATA -j .ARM.exidx $(APP).elf RO_DATA.bin
	$(OC) -O binary -j RW_DATA $(APP).elf RW_DATA.bin
	$(SPINN_DIRS)/tools/mkbin RO_DATA.bin RW_DATA.bin > $(APP).bin
	$(SPINN_DIRS)/tools/mkaplx $(APP).elf | $(CAT) - $(APP).bin > $(APP).aplx
	$(RM) $(APP).bin RO_DATA.bin RW_DATA.bin
	$(LS) $(APP).aplx


# Build the ELF file
$(APP).elf: $(OBJECTS) $(SCRIPT) $(LIBRARY) 
	$(SPINN_DIRS)/tools/mkbuild $(APP) > sark_build.c
	$(CC) sark_build.c
	$(LD) $(LFLAGS) $(OBJECTS) sark_build.o $(LIBRARY) -o $(APP).elf
	$(RM) sark_build.c sark_build.o helper.o
	$(OD) $(APP).elf


# Build the main object file.
$(APP).o: $(APP).c $(INC_DIR)/spinnaker.h $(INC_DIR)/sark.h $(INC_DIR)/spin1_api.h
	$(CC) $(CFLAGS) $(APP).c

helper.o: helper.c $(INC_DIR)/spinnaker.h $(INC_DIR)/sark.h $(INC_DIR)/spin1_api.h
	$(CC) $(CFLAGS) helper.c

# Tidy and cleaning dependencies
tidy:
	$(RM) $(OBJECTS) $(APP).elf $(APP).txt
clean:
	$(RM) $(OBJECTS) $(APP).elf $(APP).txt $(APP).aplx

#-------------------------------------------------------------------------------

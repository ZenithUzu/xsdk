#include <assert.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>

#include "xsdk/display.h"
#include "xsdk/thread.h"

static volatile uint32_t *registers;
static bool acknowledge;
static uint32_t restore_errors;

void xsdk_log_write(const char *format, ...)
{
	(void)format;
	restore_errors++;
}

void VdQueryVideoMode(VIDEO_MODE *mode)
{
	*mode = (VIDEO_MODE){ .display_width = 1280, .display_height = 720, .is_widescreen = 1 };
}

NTSTATUS xsdk_thread_sleep(uint32_t milliseconds)
{
	(void)milliseconds;
	registers[0x1928] = 2;
	if (acknowledge)
		registers[0x183B] = 0;
	return STATUS_SUCCESS;
}

int main(void)
{
	// Linux host only: a page-backed stand-in for the register window, not a GPU simulation.
	void *const mapping = mmap((void *)0x7FC80000, 0x10000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	assert(mapping != MAP_FAILED && mapping == (void *)0x7FC80000);
	registers = mapping;
	registers[0x1961] = 640u << 16 | 480;
	registers[0x1844] = 0x100000;
	registers[0x1848] = 640;
	registers[0x184D] = 640;
	registers[0x184E] = 480;
	uint32_t width;
	uint32_t height;
	acknowledge = true;
	assert(NT_SUCCESS(xsdk_display_open(XSDK_DISPLAY_KERNEL, &width, &height)));
	assert(width == 640 && height == 480);
	assert(NT_SUCCESS(xsdk_display_show(0x200000, 640)));
	acknowledge = false;
	assert(xsdk_display_close() == STATUS_IO_TIMEOUT);
	assert(restore_errors == 1);
	// A failed close must leave the display open for a retry.
	acknowledge = true;
	assert(NT_SUCCESS(xsdk_display_show(0x200000, 640)));
	assert(NT_SUCCESS(xsdk_display_close()));
	assert(registers[0x1844] == 0x100000);
	assert(registers[0x1848] == 640 && registers[0x184E] == 480);
	assert(NT_SUCCESS(xsdk_display_close()));
	assert(munmap(mapping, 0x10000) == 0);
	puts("PASS: display restore timeout, retry, original surface and repeated close");
	return 0;
}

# Main Program of STM32F103VET6

> [!TIP]
> This is the main program of STM32F103VET6 written in C language and compiled using STM32CubeIDE.

## File Structure

A complete STM32 project is too large to be stored in this repository. Therefore, only the main program is stored here ([`Core`](Core/)). For the sake of quick reference, some relevant includes are also stored here ([`Drivers`](Drivers/)).

```shell
.
├── Core (source code of the main program)
│   ├── Inc
│   └── Src
├── Drivers (firmware libraries)
│   ├── CMSIS (bottom layer of the firmware)
│   └── STM32F1xx_HAL_Driver (abstraction layer of the firmware)
├── main_prog.ioc (project settings files)
└── README.md
```

# README

## Abstract

Master-Slave synchronous control robotic arm system.

Adopted a new controlling structure,Master-Slave synchronous control,refer to film *Pacific Rim* and *Avatar*.

This robotic arm system have six joint made by BUS servo and Mechanical structure components.

## Overall Architecture

<img src="./Documents/pics/charts_EN/文档内图纸-overall%20system%20architechture.drawio.png" title="" alt="图片描述" data-align="center">

## Key Techonology

master-slave control architecture

High Real-Time Chained Task Scheduling Based on FreeRTOS

High-priority task scheduling triggered by external hardware interrupts

Chained task triggering scheduling

![](./Documents/pics/charts_EN/文档内图纸-controll%20layer%20architecture.drawio.png)

Multi-Bus Coordination  Based on High-Speed Memory Block Copy

<img title="" src="./Documents/pics/charts_EN/文档内图纸-high%20speed%20RAM%20copy%201.drawio.png" alt="" width="555" data-align="center">

<img title="" src="./Documents/pics/charts_EN/文档内图纸-high%20speed%20RAM%20copy%202.drawio.png" alt="" width="552" data-align="center">

Initial State Alignment and Dead-Zone Nonlinear Filtering Based on Finite State Machines

Time-Division Multiplexed Joint Position Data Transmission Protocol

<img title="" src="./Documents/pics/charts_EN/文档内图纸-transmition%20protocol%20architecture.drawio.png" alt="" data-align="center" width="704">

<img title="" src="./Documents/pics/charts_EN/文档内图纸-data%20frame%20format.drawio.png" alt="" data-align="center" width="131">

Real-Time Task Performance Analysis Based on GPIO

<img src="./Documents/pics/屏幕截图_20260715_195421.png" title="" alt="" data-align="center">

Hardware microsecond-level precise delay

<img title="" src="./Documents/pics/charts_EN/文档内图纸-microsecond%20precise%20delay.drawio.png" alt="" data-align="center" width="166">

## System Inplementation

### Sensor Layer

The sensing layer uses six bus servos to form a protocol-based UART bus sensor network. The main MCU polls by sending commands to read the current position, and then receives the values returned by the bus servos.

<img title="" src="./Documents/pics/charts_EN/文档内图纸-sensor%20layer%20architecture.drawio.png" alt="" width="358" data-align="center">

### Transmit Layer

When the host MCU receives position data returned from the bus servos, it extracts the joint address and position, creates a data packet made up of five bytes, and sends it to the slave MCU via the SPI protocol. The host's SPI chip select is controlled by software, meaning it manually toggles the specified chip select pin on the host MCU to trigger the slave MCU to receive the data packet on the SPI bus, ensuring that the host’s sending and the slave’s receiving happen in sync. Once the slave receives the data packet from the host, it extracts the joint address and the corresponding position from it.

<img title="" src="./Documents/pics/charts_EN/文档内图纸-transmit%20layer%20architecture.drawio.png" alt="" data-align="center" width="653">

### Controll Layer

After the slave MCU extracts the joint address and corresponding position from the data packet, it generates an actuation command based on this information and sends it over the UART bus network to the specified joint for execution. Immediately afterward, the slave MCU sends a command to read the position from the arm joints to achieve position feedback.  

We split the operations of receiving, parsing, and sending actuation commands as well as providing feedback on the actual joint positions into two FreeRTOS tasks. Task scheduling is managed using hardware external interrupts and chain-trigger techniques between tasks. The actuation task is a high-priority task and is assigned a hardware external interrupt pin, which is connected to the host’s SPI chip-select enable pin. When the host sends a chip-select signal via the SPI pin, the external interrupt pin is pulled low, triggering the actuation task. The slave then starts SPI reception, generates the actuation command, and sends it. When the actuation task finishes, it sets a process flag osThreadFlags to trigger the execution of the position feedback task. After the position feedback task completes, the system moves on to the next task scheduling cycle.

<img src="./Documents/pics/charts_EN/文档内图纸-controll%20layer%20architecture.drawio.png" title="" alt="" data-align="center">

### Development and Debug

#### Environment

Operating System: Fedora Linux 44  
Programming Environment: Microsoft VS Code + STM32CubeIDE for Visual Studio Code plugin  
Compiler: arm-none-eabi-gcc (GNU Arm Embedded Toolchain 10.3-2021.10)  
Flashing & Debugger: DAPLink + OpenOCD 0.12.0  
Pin Definitions & Initialization Code Generation: STM32CubeMX 6.18.0

#### Debug

Real-time Task Performance Analysis Based on GPIO: 
To observe and debug the timing of system operations and task scheduling, we used GPIO-based real-time task performance analysis. We set up task scheduling indicator pins for each task: pulling the corresponding pin low when a task starts and restoring it when the task ends. By connecting these indicator pins to a logic analyzer, we can visually see the task scheduling and operation timing on the Pulseview software on a PC, monitor the time consumption of each operation, and also use Pulseview's built-in decoder to analyze signal integrity across different signal paths.



## Component Introduce

**Bus Servo ** 
    Zonling Technology ZP25S and ZP25D bus servos  

<img title="" src="./Documents/pics/servo1.png" alt="" width="277" data-align="center">

<img title="" src="./Documents/pics/servo2.png" alt="" width="279" data-align="center">

**Master-Slave MCU  **
    STM32F407ZGT6 development board  

<img title="" src="./Documents/pics/IMG_0004.JPG" alt="" data-align="center" width="340">

<img title="" src="./Documents/pics/IMG_0005.JPG" alt="" data-align="center" width="348">

**Servo Driver ** 
    ZLink bus servo driver module

<img title="" src="./Documents/pics/IMG_0007.JPG" alt="" data-align="center" width="508">

**Programmer/debugger  **
    DAPLink  

<img title="" src="./Documents/pics/IMG_0009.JPG" alt="" data-align="center" width="512">

**Logic Analyzer**  
    nanoDLA 8-channel  

<img title="" src="./Documents/pics/tb_image_share_1784696362655.png" alt="" data-align="center" width="421">

<img title="" src="./Documents/pics/tb_image_share_1784696374015.png" alt="" data-align="center" width="420">

**DC Regulated Power Supply ** 
    Maisheng MN-3010F  

<img title="" src="./Documents/pics/tb_image_share_1784696559917.png" alt="" data-align="center" width="217">

**Structural Components  **
    Aluminum alloy sandblasted sheet metal components,         aluminum alloy CNC servo horns

<img title="" src="./Documents/pics/tb_image_share_1784696590545.png" alt="" data-align="center" width="297">

<img title="" src="./Documents/pics/tb_image_share_1784696593620.png" alt="" data-align="center" width="298">

<img title="" src="./Documents/pics/tb_image_share_1784696635951.png" alt="" data-align="center" width="303">

<img title="" src="./Documents/pics/tb_image_share_1784696638976.png" alt="" data-align="center" width="306">

<img title="" src="./Documents/pics/tb_image_share_1784696655284.png" alt="" data-align="center" width="309">

<img src="./Documents/pics/tb_image_share_1784696662639.png" title="" alt="" data-align="center">

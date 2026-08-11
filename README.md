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



### Transmit Layer



### Controll Layer



### Development and Debug

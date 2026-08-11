# README

## Abstract

Master-Slave synchronous control robotic arm system.

Adopted a new controlling structure,Master-Slave synchronous control,refer to film *Pacific Rim* and *Avatar*.

This robotic arm system have six joint made by BUS servo and Mechanical structure components.

## overall architecture

<img src="file:///home/fedora/Jaeger_robotic_arm/Documents/pics/charts_EN/文档内图纸-overall%20system%20architechture.drawio.png" title="" alt="" data-align="center">

## Key Techonology

master-slave control architecture

High Real-Time Chained Task Scheduling Based on FreeRTOS

High-priority task scheduling triggered by external hardware interrupts

Chained task triggering scheduling

Multi-Bus Coordination  Based on High-Speed Memory Block Copy

Initial State Alignment and Dead-Zone Nonlinear Filtering Based on Finite State Machines

Time-Division Multiplexed Joint Position Data Transmission Protocol

Real-Time Task Performance Analysis Based on GPIO

Hardware microsecond-level precise delay

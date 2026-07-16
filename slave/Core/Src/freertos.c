/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stdio.h"
#include "string.h"
#include "queue.h"
#include "spi.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
struct serial_print_pack
{
  char receive_position[5];
};
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */
extern SPI_HandleTypeDef hspi3;
extern UART_HandleTypeDef huart1,huart4;

char position_pack[5]="";
char command_actuate[15]="#000P0500T0000!";
char command_get_position[9]="#000PRAD!";
char receive_position[11]="";
char num_joint;
uint8_t counter=0;
int anti_locked=0;
/* USER CODE END Variables */
/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for Actuation */
osThreadId_t ActuationHandle;
const osThreadAttr_t Actuation_attributes = {
  .name = "Actuation",
  .stack_size = 256 * 4,
  .priority = (osPriority_t) osPriorityHigh,
};
/* Definitions for FeedBack */
osThreadId_t FeedBackHandle;
const osThreadAttr_t FeedBack_attributes = {
  .name = "FeedBack",
  .stack_size = 512 * 4,
  .priority = (osPriority_t) osPriorityAboveNormal,
};
/* Definitions for slave_tasks */
osMessageQueueId_t slave_tasksHandle;
const osMessageQueueAttr_t slave_tasks_attributes = {
  .name = "slave_tasks"
};

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */

/* USER CODE END FunctionPrototypes */

void StartDefaultTask(void *argument);
void Start_Actuation(void *argument);
void Start_FeedBack(void *argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* Create the queue(s) */
  /* creation of slave_tasks */
  slave_tasksHandle = osMessageQueueNew (16, 16, &slave_tasks_attributes);

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of defaultTask */
  defaultTaskHandle = osThreadNew(StartDefaultTask, NULL, &defaultTask_attributes);

  /* creation of Actuation */
  ActuationHandle = osThreadNew(Start_Actuation, NULL, &Actuation_attributes);

  /* creation of FeedBack */
  FeedBackHandle = osThreadNew(Start_FeedBack, NULL, &FeedBack_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

}

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN StartDefaultTask */
  /* Infinite loop */
  for(;;)
  {
    //osDelay(1);
  }
  /* USER CODE END StartDefaultTask */
}

/* USER CODE BEGIN Header_Start_Actuation */
/**
* @brief Function implementing the Actuation thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Start_Actuation */
void Start_Actuation(void *argument)
{
  /* USER CODE BEGIN Start_Actuation */
  /* Infinite loop */
  for(;;)
  {
    //运动控制
    osThreadFlagsWait(0x01, osFlagsWaitAny, osWaitForever);
    HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8,GPIO_PIN_RESET);

    HAL_SPI_Receive(&hspi3,(uint8_t*)position_pack,sizeof(position_pack),2);
    //Anti Lock Rotor
    if(position_pack[0]=='5')
    {
      anti_locked= 1000*(position_pack[1]-'0') + 100*(position_pack[2]-'0') + 10*(position_pack[3]-'0') + 1*(position_pack[4]-'0');
      if(!(anti_locked>600 && anti_locked<1500))
      {
        HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8,GPIO_PIN_SET);
        osThreadFlagsClear(0x01);
        continue;
      }
    }
    
    memcpy(&command_actuate[3],&position_pack[0],1);
    memcpy(&command_actuate[5], &position_pack[1], 4);
    //*(uint32_t*)&command_actuate[5] = *(uint32_t*)&position_pack[1];
    
    HAL_UART_Transmit(&huart4,(uint8_t*)command_actuate,sizeof(command_actuate),5);
    num_joint=position_pack[0]; counter++;
    
    osThreadFlagsSet(FeedBackHandle, 0x02);
    osThreadFlagsClear(0x01);

    HAL_GPIO_WritePin(GPIOB,GPIO_PIN_8,GPIO_PIN_SET);
    //osDelay(1);
  }
  
  /* USER CODE END Start_Actuation */
}

/* USER CODE BEGIN Header_Start_FeedBack */
/**
* @brief Function implementing the FeedBack thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_Start_FeedBack */
void Start_FeedBack(void *argument)
{
  /* USER CODE BEGIN Start_FeedBack */
  
  /* Infinite loop */
  for(;;)
  {
    osThreadFlagsWait(0x02, osFlagsWaitAny, osWaitForever);
    HAL_GPIO_WritePin(GPIOB,GPIO_PIN_7,GPIO_PIN_RESET);

    command_get_position[3]=num_joint;
    HAL_UART_Transmit(&huart4,(uint8_t*)command_get_position,sizeof(command_get_position),1);
    HAL_UART_Receive(&huart4,(uint8_t*)receive_position,sizeof(receive_position),3);

    printf("%c%c%c%c%c\r\n",receive_position[3],receive_position[5],receive_position[6],receive_position[7],receive_position[8]);
    if(counter>5)
    {
      printf("\033[6A"); counter=0;
    }
    
    osThreadFlagsClear(0x02);
    HAL_GPIO_WritePin(GPIOB,GPIO_PIN_7,GPIO_PIN_SET);
    //osDelay(1);
  }
  /* USER CODE END Start_FeedBack */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */
int _write(int file,char *ptr,int len)
{
  if(HAL_UART_Transmit_DMA(&huart1,(uint8_t*)ptr,len)!=HAL_OK)
  {return -1;}
  return len;
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == GPIO_PIN_0) // PB0 触发
    {
      // 确保这里的句柄叫 ActuationHandle，对应你图片里的 Task Name
      osThreadFlagsSet(ActuationHandle, 0x01);
      portYIELD_FROM_ISR(pdTRUE);
    }
}
/* USER CODE END Application */


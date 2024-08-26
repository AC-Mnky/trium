/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2024 STMicroelectronics.
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
#include "main.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "motor.h"
#include "PID.h"
#include "message.h"
#include "tick.h"
#include "stm32f1xx_hal.h"
#include "ultra.h"
#include <string.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void) {

	/* USER CODE BEGIN 1 */

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_TIM1_Init();
	MX_TIM3_Init();
	MX_TIM4_Init();
	MX_TIM5_Init();
	MX_TIM8_Init();
	MX_TIM6_Init();
	MX_USART3_UART_Init();
	MX_USART1_UART_Init();
	MX_TIM7_Init();
	/* USER CODE BEGIN 2 */
	const uint32_t dangerous_distance = 10;
	const uint32_t safe_distance = 20;

	uint8_t buffer[23] = { 0, 0, 0, 0, 0, 0, 0, 5, 1, 1, 100, 1, 10, 20, 0, 5,
			1, 1, 100, 1, 10, 20, 0 }; //buffer used to receive messages
	uint8_t buffer_0x80 = 0; //buffer used to receive 0x80
	struct PID_struct PID_obj_1;
	struct PID_struct PID_obj_2;

	uint32_t distance[2];
	uint8_t urgent_flag = 0;

	PID_init(&PID_obj_1, buffer[7], buffer[8], buffer[9], buffer[10],
			buffer[11], buffer[12], buffer[13]);
	PID_init(&PID_obj_2, buffer[15], buffer[16], buffer[17], buffer[18],
			buffer[19], buffer[20], buffer[21]);

	motor_init();
	HAL_TIM_Base_Start(&htim6);
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, SET);

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1) {
		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */

		//receive controlling message
		const uint8_t max_attempt = 5;
		for (uint8_t attempt_count = 0; attempt_count < max_attempt;
				++attempt_count) {
			HAL_UART_Receive(&huart3, &buffer_0x80, 1, 500);
			if (buffer_0x80 == 0x80) {
				HAL_UART_Receive(&huart3, buffer, 23, 500);
				break;
			}
		}

		//urgency dealing
		if (urgent_flag == 1) {
			buffer[1] = -80;
			buffer[2] = 80;
		} else if (urgent_flag == 2) {
			buffer[1] = 80;
			buffer[2] = -80;
		}
		//soft restart
		if (buffer[0] == 1) {
			PID_obj_1.integral = 0;
			PID_obj_1.integral = 0;
		}

		PID_change_para(&PID_obj_1, buffer[7], buffer[8], buffer[9], buffer[10],
				buffer[11], buffer[12], buffer[13]);
		PID_change_para(&PID_obj_2, buffer[15], buffer[16], buffer[17],
				buffer[18], buffer[19], buffer[20], buffer[21]);

		const uint8_t head_length = 4;
		uint8_t head[head_length];
		memset(head, 128, head_length);
		HAL_UART_Transmit(&huart3, head, head_length, 50);

		const uint8_t empty_length = 8;
		uint8_t empty[empty_length];
		memset(empty, 0, empty_length);

		HAL_UART_Transmit(&huart3, buffer, 28, 200);

		uint32_t real_tick_2;
		uint16_t encoder_CNT_2 = get_encoder_CNT(2, &real_tick_2);
		set_motor_speed(2,
				PID_vel(&PID_obj_2, buffer[2], encoder_CNT_2, real_tick_2));

		//send feedback messages
		HAL_UART_Transmit(&huart3, (uint8_t*) (&real_tick_2), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&encoder_CNT_2), 2, 50);
		HAL_UART_Transmit(&huart3, empty, 2, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.actual_val), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.target_val), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.output_val), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.integral), 4, 50);
		HAL_UART_Transmit(&huart3, empty, 8, 50);

		uint32_t real_tick_1;
		uint16_t encoder_CNT_1 = get_encoder_CNT(1, &real_tick_1);
		set_motor_speed(1,
				PID_vel(&PID_obj_1, buffer[1], encoder_CNT_1, real_tick_1));

		//send feedback messages
		HAL_UART_Transmit(&huart3, (uint8_t*) (&real_tick_1), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&encoder_CNT_1), 2, 50);
		HAL_UART_Transmit(&huart3, empty, 2, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.actual_val), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.target_val), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.output_val), 4, 50);
		HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.integral), 4, 50);
		HAL_UART_Transmit(&huart3, empty, 8, 50);

//		//integral num decrease
//		PID_obj_1.integral -= PID_obj_1.integral >> 12;
//		PID_obj_2.integral -= PID_obj_2.integral >> 12;

		if (PID_obj_1.target_val == 0) {
			PID_obj_1.integral = 0;
		}
		if (PID_obj_2.target_val == 0) {
			PID_obj_2.integral = 0;
		}

		//control the brush and servo motor
		if (buffer[3]) {
			set_motor_speed(3, 80);
		} else {
			set_motor_speed(3, 0);
		}
		if (buffer[4]) {
			set_servo_angle(250);
		} else {
			set_servo_angle(150);
		}

		//urgency dealing
		get_distance(distance, 0);
		if ((distance[0] <= dangerous_distance
				|| distance[1] <= dangerous_distance) && urgent_flag == 0) {
			if (distance[0] > distance[1]) {
				urgent_flag = 1;
			} else {
				urgent_flag = 2;
			}
		} else if ((distance[0] >= safe_distance & distance[1] >= safe_distance)
				&& urgent_flag != 0) {
			urgent_flag = 0;
		} else {
		}
		//time controller
		while (__HAL_TIM_GET_COUNTER(&htim6) < 100) {
		}
		__HAL_TIM_SET_COUNTER(&htim6, 0);
	}
	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void) {
	RCC_OscInitTypeDef RCC_OscInitStruct = { 0 };
	RCC_ClkInitTypeDef RCC_ClkInitStruct = { 0 };

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
	RCC_OscInitStruct.HSEState = RCC_HSE_ON;
	RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
	RCC_OscInitStruct.HSIState = RCC_HSI_ON;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
			| RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK) {
		Error_Handler();
	}
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void) {
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1) {
	}
	/* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

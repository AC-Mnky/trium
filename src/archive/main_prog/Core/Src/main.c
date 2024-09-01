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
#include "ultra.h"
#include <string.h>
#include "math.h"
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

/* @brief choose whether to enable debug message prints.
 * @description debug prints -> program variables | reflect -> retransmit messages to PC
 * @type unit8_t
 * @value 0: disable | 1: enable
 * @note  uart1 -> PC |  uart3 -> pi4B
 * */
const uint8_t debug_print = 0;
const uint8_t reflect = 1;

/* @brief buffers used for message transmission
 * @description temp_buffer -> temporary buffer used to check messages
 * @description receive_buffer -> buffer used to receive messages
 * @note 127-protocol: 6 bytes | 128-protocol: 24 bytes
 * */
// 127-protocol
uint8_t temp_buffer[6] = { 0 };
uint8_t receive_buffer[6] = { 0 };

// 128-protocol
uint8_t temp_buffer_128[24] = { 0 };
uint8_t temp_buffer_2[23] = { 0 };
uint8_t receive_buffer_128[24] = { 0 };

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* @brief call urgency by analyzing the speed and distance
 * @param distance: distance to the obstacle detected by the ultrasonic sensor
 * @param encoder_CNT1->encoder count of motor 1 | encoder_CNT2->encoder count of motor 2
 * @retval call_flag: 1 (urgency) | 0 (no urgency)
 * @note ratio = max(v1 / distance, v2 / distance)
 * @note call_flag = 1 if ratio > 1 | call_flag = 0 otherwise
 * */
uint8_t urgency_call(uint8_t distance, uint16_t encoder_CNT1, uint16_t encoder_CNT2) {
	uint8_t call_flag = (get_encoder_direction(1) == get_encoder_direction(2)) ? 1 : 0;
	if (call_flag) {
		uint8_t v1 = (uint8_t) 3 * M_PI * encoder_CNT1 / 8; // cm/s
		uint8_t v2 = (uint8_t) 3 * M_PI * encoder_CNT2 / 8; //
		uint8_t ratio = (uint8_t) (v1 > v2) ? (v1 / distance) : (v2 / distance);
		if (ratio > 1) {
			return 1;
		}
	}
	return 0;
}
/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void) {

	/* USER CODE BEGIN 1 */
	const uint8_t transmit_protocol = 127;
	const uint8_t urgent_count_init = 1;
	const uint8_t max_attempt = 30;
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

// messages settings
	uint8_t transmit_buffer[13] = { 127, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

//	uint32_t start_tick = uwTick;
	uint32_t *motor2time = (uint32_t*) &transmit_buffer[1];
	uint16_t *motor2count = (uint16_t*) &transmit_buffer[5];
	uint32_t *motor1time = (uint32_t*) &transmit_buffer[7];
	uint16_t *motor1count = (uint16_t*) &transmit_buffer[11];
//	uint32_t *transmit_tick = (uint32_t*) &transmit_buffer[13];

// used only for 128-protocol
	const uint8_t empty_length = 8;
	uint8_t empty[empty_length];
	memset(empty, 0, empty_length);

// start to receive messages
	if (transmit_protocol == 127) {
		HAL_UART_Receive_IT(&huart3, temp_buffer, 6); // 127-protocol
	}

	// urgency settings
	uint8_t urgent_flag = 0;
	uint8_t urgent_count = urgent_count_init;

	// initialization
	motor_init();
	struct PID_struct PID_obj_1;
	struct PID_struct PID_obj_2;
	uint8_t PID_para_1[8] = { 15, 10, 40, 1, 0, 10, 5, 0 };
	uint8_t PID_para_2[8] = { 15, 10, 40, 1, 0, 10, 5, 0 };
	PID_init(&PID_obj_1, PID_para_1[0], PID_para_1[1], PID_para_1[2], PID_para_1[3], PID_para_1[4],
			PID_para_1[5], PID_para_1[6]);
	PID_init(&PID_obj_2, PID_para_2[0], PID_para_2[1], PID_para_2[2], PID_para_2[3], PID_para_2[4],
			PID_para_2[5], PID_para_2[6]);
	uint8_t speed_1 = 0;
	uint8_t speed_2 = 0;

	HAL_TIM_Base_Start(&htim6);
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, SET);

	/* @brief ultra sonic sensor order init
	 * @note 0 -> left | 1 -> right
	 * */
	uint8_t ultra_order = 0;
	uint8_t distance = 0;

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1) {
		/* USER CODE END WHILE */

		/* USER CODE BEGIN 3 */

		/* @brief receive controlling message under 128-protocol
		 * @note 0x80 -> head of the message
		 * @note inquiry mode
		 * */
		if (transmit_protocol == 128) {

			for (uint8_t j = 0; j < max_attempt; ++j) {
				temp_buffer_128[0] = 0;
				HAL_UART_Receive(&huart3, &temp_buffer_128[0], 1, 10);

				if (temp_buffer_128[0] == 0x80) {
					HAL_UART_Receive(&huart3, temp_buffer_2, 23, 10);
					for (uint8_t i = 0; i < 23; ++i) {
						HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_13);
						temp_buffer_128[i + 1] = temp_buffer_2[i];
						receive_buffer_128[i + 1] = temp_buffer_2[i];
					}
					break;
				}
			}
		}

		// debug message of receiving
		if (debug_print)
			HAL_UART_Transmit(&huart1, (uint8_t*) "received\n", 9, 400);

		// soft restart
		if (receive_buffer[1] == 1) {
			PID_obj_1.integral = 0;
			PID_obj_2.integral = 0;
//			start_tick = uwTick;
			memset(receive_buffer, 0, 6);
			HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_SET);
		}

		if (transmit_protocol == 128) {
			speed_1 = receive_buffer_128[2], speed_2 = receive_buffer_128[3];
		} else if (transmit_protocol == 127) {
			speed_1 = receive_buffer[2], speed_2 = receive_buffer[3];
		}

		// urgent case dealing
		if (urgent_count > 0) {
			--urgent_count;
			if (urgent_flag == 1) {
				speed_1 = -20;
				speed_2 = -50;
			} else if (urgent_flag == 2) {
				speed_1 = -50;
				speed_2 = -20;
			}
		}

		// debug message of urgency handling
		if (debug_print)
			HAL_UART_Transmit(&huart1, (uint8_t*) "urgency handled\n", 16, 400);

		if (transmit_protocol == 128) {
			PID_change_para(&PID_obj_1, receive_buffer_128[8], receive_buffer_128[9],
					receive_buffer_128[10], receive_buffer_128[11], receive_buffer_128[12],
					receive_buffer_128[13], receive_buffer_128[14]);
			PID_change_para(&PID_obj_2, receive_buffer_128[16], receive_buffer_128[17],
					receive_buffer_128[18], receive_buffer_128[19], receive_buffer_128[20],
					receive_buffer_128[21], receive_buffer_128[22]);
		}

		// debug message of pid parameters change
		if (debug_print) {
			HAL_UART_Transmit(&huart1, (uint8_t*) "pid para changed\n", 17, 400);
		}

		if (transmit_protocol == 128) {
			const uint8_t head_length = 4;
			uint8_t head[head_length];
			memset(head, 128, head_length);
			HAL_UART_Transmit(&huart3, head, head_length, 20);
			HAL_UART_Transmit(&huart3, temp_buffer_128, 32 - head_length, 50);
		} else {
		}

		// debug message of head transmission
		if (debug_print)
			HAL_UART_Transmit(&huart1, (uint8_t*) "head transmitted\n", 17, 400);

		/* @brief velocity control under 128-protocol.
		 * */
		if (transmit_protocol == 128) {
			uint32_t real_tick_2;
			uint16_t encoder_CNT_2 = get_encoder_CNT(2, &real_tick_2);
			set_motor_speed(2, PID_vel(&PID_obj_2, speed_2, encoder_CNT_2, real_tick_2));

			// send feedback message
			HAL_UART_Transmit(&huart3, (uint8_t*) (&real_tick_2), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&encoder_CNT_2), 2, 20);
			HAL_UART_Transmit(&huart3, empty, 2, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.actual_val), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.target_val), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.output_val), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_2.integral), 4, 20);
			HAL_UART_Transmit(&huart3, empty, 8, 20);

			uint32_t real_tick_1;
			uint16_t encoder_CNT_1 = get_encoder_CNT(1, &real_tick_1);
			set_motor_speed(1, PID_vel(&PID_obj_1, speed_1, encoder_CNT_1, real_tick_1));

			// send feedback messages
			HAL_UART_Transmit(&huart3, (uint8_t*) (&real_tick_1), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&encoder_CNT_1), 2, 20);
			HAL_UART_Transmit(&huart3, empty, 2, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.actual_val), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.target_val), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.output_val), 4, 20);
			HAL_UART_Transmit(&huart3, (uint8_t*) (&PID_obj_1.integral), 4, 20);
			HAL_UART_Transmit(&huart3, empty, 8, 20);

		}
		/* @brief velocity control under 127-protocol.
		 * */
		else if (transmit_protocol == 127) {
			*motor2count = get_encoder_CNT(2, motor2time);
			*motor1count = get_encoder_CNT(1, motor1time);
			set_motor_speed(2, PID_vel(&PID_obj_2, speed_2, *motor2count, *motor2time));
			set_motor_speed(1, PID_vel(&PID_obj_1, speed_1, *motor1count, *motor1time));

			// debug message of motor speed
			if (debug_print) {
				HAL_UART_Transmit(&huart1, (uint8_t*) "motor speed set\n", 16, 400);
			}
//			*transmit_tick = get_real_tick() - start_tick;
//			*transmit_tick = uwTick - start_tick;
			HAL_UART_Transmit_IT(&huart3, transmit_buffer, 13);

			// debug message of transmission
			if (debug_print)
				HAL_UART_Transmit(&huart1, (uint8_t*) "transmitted\n", 12, 400);
		}

		/* @brief clear integral when velocity is set to zero.
		 * */
		if (PID_obj_1.target_val == 0) {
			PID_obj_1.integral = 0;
		}
		if (PID_obj_2.target_val == 0) {
			PID_obj_2.integral = 0;
		}

		// debug message of pid integral zeroing
		if (debug_print) {
			HAL_UART_Transmit(&huart1, (uint8_t*) "pid integral set\n", 17, 400);
		}

		/* @brief control the brush and servo motor
		 * @note brush -> motor 3 | servo -> motor 4
		 * @note receive_buffer[4] -> brush | reveive_buffer[5] -> servo
		 * */
		if (receive_buffer[4]) {
			set_motor_speed(3, 80);
		} else {
			set_motor_speed(3, 0);
		}
		/* 250 -> door open | 150 -> door close */
		if (receive_buffer[5]) {
			set_servo_angle(250);
		} else {
			set_servo_angle(150);
		}

		// debug message of brush & servo
		if (debug_print) {
			HAL_UART_Transmit(&huart1, (uint8_t*) "brush and servo set\n", 20, 400);
		}

		distance = get_distance_single(ultra_order);
		ultra_order = ultra_order ? 0 : 1;

		if (urgency_call(distance, *motor1count, *motor2count)) {
			urgent_flag = ultra_order ? 1 : 2;
			urgent_count = 3;
		} else {
			urgent_flag = 0;
			urgent_count = 0;
		}

		/* @brief control the time of one loop
		 * @note set  the time of one loop to 200 ticks of timer 6 (0.1ms per tick)
		 * */
		while (__HAL_TIM_GET_COUNTER(&htim6) < 200) {
		}
		__HAL_TIM_SET_COUNTER(&htim6, 0);

		if (debug_print) {
			HAL_UART_Transmit(&huart1, (uint8_t*) "timer ended\n", 12, 400);
		}

		/* @brief use blink to test whether the loop is conducted properly
		 * HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_13);
		 * */
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
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1
			| RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK) {
		Error_Handler();
	}
}

/* USER CODE BEGIN 4 */

/**
 * @brief  This interrupt callback function is executed in case of receiving message finished.
 * @retval None
 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
	if (temp_buffer[0] == 0x80) {
		memcpy(receive_buffer, temp_buffer, 6);
		HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_13);
	}

	// reflect messages to PC
	if (reflect) {
		HAL_UART_Transmit(&huart1, temp_buffer, 6, 400);
	}

	HAL_UART_Receive_IT(&huart3, temp_buffer, 6);

}

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

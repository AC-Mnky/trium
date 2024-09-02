#include "ultra.h"
#include "tim.h"
#include "gpio.h"
#include "usart.h"

const uint8_t ultra_debug_print = 1;

/* @brief Delay certain time (in us) counted by TIM7
 * @param n_us: time to delay (in us)
 * @retval None
 * */
void TIM7_Delay_us(uint16_t n_us) {
	__HAL_TIM_SetCounter(&htim7, 0);
	__HAL_TIM_ENABLE(&htim7);
	while (__HAL_TIM_GetCounter(&htim7) < (1 * n_us - 1)) {

	};
	__HAL_TIM_DISABLE(&htim7);
}

/* @brief Get the distance detected by certain ultrasonic sensor
 * @param num: 1 -> left sensor | 2 -> right sensor
 * @retval distance (in cm)
 * */
uint8_t get_distance_single(int num) {
	int CSB_value = 0;
	GPIO_TypeDef *trig_port = GPIOD;
	GPIO_TypeDef *echo_port = GPIOD;
	uint16_t trig_pin = (num == 1) ? Trig_L_Pin : Trig_R_Pin;
	uint16_t echo_pin = (num == 1) ? Echo_L_Pin : Echo_R_Pin;

	if (ultra_debug_print)
		HAL_UART_Transmit(&huart1, (uint8_t*) "before trigger", 14, 100);

	HAL_GPIO_WritePin(trig_port, trig_pin, GPIO_PIN_SET);
	TIM7_Delay_us(15);
	HAL_GPIO_WritePin(trig_port, trig_pin, GPIO_PIN_RESET);

	if (ultra_debug_print)
		HAL_UART_Transmit(&huart1, (uint8_t*) "after trigger", 13, 100);

	__HAL_TIM_ENABLE(&htim7);

	//等待接收引脚变成高电平
	__HAL_TIM_SetCounter(&htim7, 0);
	while (HAL_GPIO_ReadPin(echo_port, echo_pin) == 0) {
		if ( __HAL_TIM_GetCounter(&htim7) > 5000) {
			__HAL_TIM_DISABLE(&htim7);
			return 127;
		};
		if (ultra_debug_print)
			HAL_UART_Transmit(&huart1, (uint8_t*) "wait1", 5, 100);
	};

	if (ultra_debug_print)
		HAL_UART_Transmit(&huart1, (uint8_t*) "between", 7, 100);

	//接收完全后不再为高电平，即当接收引脚变成低电平后，停止计时，获取计数时间
	__HAL_TIM_SetCounter(&htim7, 0);
	while (HAL_GPIO_ReadPin(echo_port, echo_pin) == 1) {
		if (__HAL_TIM_GetCounter(&htim7) > 5000) {
			__HAL_TIM_DISABLE(&htim7);
			return 127;
		}
		if (ultra_debug_print)
			HAL_UART_Transmit(&huart1, (uint8_t*) "wait2", 5, 100);
	}

	CSB_value = __HAL_TIM_GetCounter(&htim7);
	__HAL_TIM_DISABLE(&htim7);

	return (uint8_t) (CSB_value * 346 / 20000);  // cm
}

/* @brief Get the distance detected by both ultrasonic sensor
 * @param distance: array to store the distance detected by left and right sensor
 * @retval distance array (in cm)
 * */
void get_distance(uint8_t *distance) {
	int CSB_value_L = 0;
	int CSB_value_R = 0;

	int start_time_L = 0;
	int start_time_R = 0;
	int end_time_L = 0;
	int end_time_R = 0;

	uint8_t distance_L = 0;
	uint8_t distance_R = 0;

	HAL_GPIO_WritePin(Trig_L_GPIO_Port, Trig_L_Pin, GPIO_PIN_SET);
	HAL_GPIO_WritePin(Trig_R_GPIO_Port, Trig_R_Pin, GPIO_PIN_SET);
	TIM7_Delay_us(15);
	HAL_GPIO_WritePin(Trig_L_GPIO_Port, Trig_L_Pin, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(Trig_R_GPIO_Port, Trig_R_Pin, GPIO_PIN_RESET);

	__HAL_TIM_SetCounter(&htim7, 0);
	__HAL_TIM_ENABLE(&htim7);

	int check_1 = 0;
	int check_2 = 0;
	int Past_turn_L = 0;
	int Past_turn_R = 0;

	//等待两侧接收引脚变成高电平，某边变高就开始记时
	while (check_1 == 0 || check_2 == 0) {

		if (HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 1 && Past_turn_L == 0) {
			start_time_L = __HAL_TIM_GetCounter(&htim7);
			check_1 = 1;
		}

		if (HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin) == 1 && Past_turn_R == 0) {
			start_time_R = __HAL_TIM_GetCounter(&htim7);
			check_2 = 1;
		}

		if ( __HAL_TIM_GetCounter(&htim7) > 2000) {
			start_time_L = 0;
			start_time_R = 0;
			end_time_L = 2000;
			end_time_R = 2000;
			break;
		}

		Past_turn_L = HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin);
		Past_turn_R = HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin);

	}

	int check_3 = 0;
	int check_4 = 0;
	int Past_turn_L_2 = 0;
	int Past_turn_R_2 = 0;

	//接收完全后不再为高电平，即当接收引脚变成低电平后，停止计时，获取计数时间
	while (check_3 == 0 && check_4 == 0) {

		if (HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 0 && Past_turn_L_2 == 1) {
			end_time_L = __HAL_TIM_GetCounter(&htim7);
			check_3 = 1;
		}

		if (HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin) == 0 && Past_turn_R_2 == 1) {
			end_time_R = __HAL_TIM_GetCounter(&htim7);
			check_4 = 1;
		}

		if ( __HAL_TIM_GetCounter(&htim7) > 2000) {
			start_time_L = 0;
			start_time_R = 0;
			end_time_L = 2000;
			end_time_R = 2000;
			break;
		}

		Past_turn_L_2 = HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin);
		Past_turn_R_2 = HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin);

	}

	__HAL_TIM_DISABLE(&htim7);

	CSB_value_L = end_time_L - start_time_L;
	CSB_value_R = end_time_R - start_time_R;

	distance_L = (uint8_t) (CSB_value_L * 346 / 20000);  // cm
	distance_R = (uint8_t) (CSB_value_R * 346 / 20000);  // cm
// (uint8_t) (CSB_value * 346 / 2000);  // mm

	distance[0] = distance_L;
	distance[1] = distance_R;
}

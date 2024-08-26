#include "ultra.h"
#include "tim.h"
#include "gpio.h"

void TIM7_Delay_us(uint16_t n_us) {
	__HAL_TIM_SetCounter(&htim7, 0);
	__HAL_TIM_ENABLE(&htim7);
	while (__HAL_TIM_GetCounter(&htim7) < (1 * n_us - 1)) {

	};
	__HAL_TIM_DISABLE(&htim7);
}

void get_distance(uint8_t* distance, uint8_t type) {
	int CSB_value_L = 0;
	int CSB_value_R = 0;

	int start_time_L = 0;
	int start_time_R = 0;
	int end_time_L = 0;
	int end_time_R = 0;

	uint8_t distance_L = 0;
	uint8_t distance_R = 0;

	if (type==0){
		HAL_GPIO_WritePin(Trig_L_GPIO_Port, Trig_L_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(Trig_R_GPIO_Port, Trig_R_Pin, GPIO_PIN_SET);
		TIM7_Delay_us(15);
		HAL_GPIO_WritePin(Trig_L_GPIO_Port, Trig_L_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(Trig_R_GPIO_Port, Trig_R_Pin, GPIO_PIN_RESET);

		__HAL_TIM_SetCounter(&htim7, 0);
		__HAL_TIM_ENABLE(&htim7);

		//等待两侧接收引脚变成高电平，某边变高就开始记时
		while (HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 0 || HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin) == 0) {
			if(HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 1) start_time_L = __HAL_TIM_GetCounter(&htim7);
			if(HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin) == 1) start_time_R = __HAL_TIM_GetCounter(&htim7);
			if( __HAL_TIM_GetCounter(&htim7) > 2000){
				break;
			}
		}

		//接收完全后不再为高电平，即当接收引脚变成低电平后，停止计时，获取计数时间
		while (HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 1 || HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin) == 1) {
			if(HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 0) end_time_L = __HAL_TIM_GetCounter(&htim7);
			if(HAL_GPIO_ReadPin(Echo_R_GPIO_Port, Echo_R_Pin) == 0) end_time_R = __HAL_TIM_GetCounter(&htim7);
			if( __HAL_TIM_GetCounter(&htim7) > 2000){
				break;
			}
		}
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

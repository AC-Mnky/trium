#include "ultra.h"
#include "tim.h"
#include "gpio.h"

void TIM1_Delay_us(uint16_t n_us) {
	__HAL_TIM_SetCounter(&htim1, 0);
	__HAL_TIM_ENABLE(&htim1);
	while (__HAL_TIM_GetCounter(&htim1) < (1 * n_us - 1)) {

	};
	__HAL_TIM_DISABLE(&htim1);
}

uint8_t get_distance(uint8_t type) {
	int CSB_value = 0;

	if (type==0){
		HAL_GPIO_WritePin(Trig_L_GPIO_Port, Trig_L_Pin, GPIO_PIN_SET);
		TIM1_Delay_us(15);
		HAL_GPIO_WritePin(Trig_L_GPIO_Port, Trig_L_Pin, GPIO_PIN_RESET);
		//等待接收引脚变成高电平
		while (HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 0) {
		}
		;
		__HAL_TIM_SetCounter(&htim1, 0);
		__HAL_TIM_ENABLE(&htim1);
		//接收完全后不再为高电平，即当接收引脚变成低电平后，停止计时，获取计数时间
		while (HAL_GPIO_ReadPin(Echo_L_GPIO_Port, Echo_L_Pin) == 1) {
		};
	}

	CSB_value = __HAL_TIM_GetCounter(&htim1);
	__HAL_TIM_DISABLE(&htim1);

//	return (uint8_t) (CSB_value * 346 / 2000);  // mm
	return (uint8_t) (CSB_value * 346 / 20000);  // cm
}

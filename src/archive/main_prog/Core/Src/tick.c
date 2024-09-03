/**
 * tick.c
 *
 *  Created on: Aug 24, 2024
 *      Author: 86186
 */

#include "stm32f1xx_hal.h"

/**
 * @brief  get realtime ticks
 * @retval ticks elapsed
 */
int32_t get_real_tick() {
	return (uwTick + 1) * 72000 - SysTick->VAL;
}

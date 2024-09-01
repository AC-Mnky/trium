#include "tim.h"
#include "gpio.h"
#include "motor.h"
#include "tick.h"

void motor_init() {
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_ALL);
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);

	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_13, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_14, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_15, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_8, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_9, GPIO_PIN_RESET);

	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);

	HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start(&htim4, TIM_CHANNEL_ALL);
}

void set_motor_speed(uint8_t num, int pulse) {
	if (num == 1) {
		if (pulse > 0) {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_12, GPIO_PIN_SET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_13, GPIO_PIN_RESET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, pulse); // Set CCR, also called 'pulse'
		} else if (pulse < 0) {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_12, GPIO_PIN_RESET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_13, GPIO_PIN_SET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, -pulse);
		} else {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_12, GPIO_PIN_RESET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_13, GPIO_PIN_RESET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
		}
	} else if (num == 2) {
		if (pulse > 0) {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_14, GPIO_PIN_RESET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_15, GPIO_PIN_SET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, pulse); // Set CCR, also called 'pulse'
		} else if (pulse < 0) {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_14, GPIO_PIN_SET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_15, GPIO_PIN_RESET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, -pulse);
		} else {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_14, GPIO_PIN_RESET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_15, GPIO_PIN_RESET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 0);
		}
	} else if (num == 3) {
		if (pulse > 0) {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_8, GPIO_PIN_SET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_9, GPIO_PIN_RESET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, pulse); // Set CCR, also called 'pulse'
		} else if (pulse < 0) {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_8, GPIO_PIN_RESET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_9, GPIO_PIN_SET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, -pulse);
		} else {
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_8, GPIO_PIN_RESET); // IN1
			HAL_GPIO_WritePin(GPIOE, GPIO_PIN_9, GPIO_PIN_RESET); // IN2
			__HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, 0);
		}
	} else {
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET); // Show errors
	}
}

uint16_t get_encoder_CNT(int num, uint32_t *out_real_tick_elapsed) {
	uint16_t iTimEncoder = 0;
	static int32_t last_call[3];
	int32_t t = get_real_tick();
	if (num == 1) {
		*out_real_tick_elapsed = t - last_call[0];
		last_call[0] = t;
		iTimEncoder = __HAL_TIM_GET_COUNTER(&htim5);
		__HAL_TIM_SET_COUNTER(&htim5, 0);
	} else if (num == 2) {
		*out_real_tick_elapsed = t - last_call[1];
		last_call[1] = t;
		iTimEncoder = __HAL_TIM_GET_COUNTER(&htim3);
		__HAL_TIM_SET_COUNTER(&htim3, 0);
	} else if (num == 3) {
		*out_real_tick_elapsed = t - last_call[2];
		last_call[2] = t;
		iTimEncoder = __HAL_TIM_GET_COUNTER(&htim4);
		__HAL_TIM_SET_COUNTER(&htim4, 0);
	} else {
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET); // Show errors
	}
	return iTimEncoder;
}

/* @brief Get the direction of the encoder
 * @param num: 1, 2, 3 (number of motor)
 * @retval direction_flag (uint8_t): 1 (down), 0 (up)
 * @note This function is never used (?)
 * */
uint8_t get_encoder_direction(uint8_t num) {
	uint8_t direction_flag = 0;
	if (num == 1) {
		direction_flag = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim5) ? 1 : 0;
	} else if (num == 2) {
		direction_flag = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim3) ? 1 : 0;
	} else if (num == 3) {
		direction_flag = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim4) ? 1 : 0;
	} else {
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET); // Show errors
	}
	return direction_flag;
}

/* @brief Set the angle of the servo motor
 * @param pulse: 50 ~ 250 (250 -> door open | 150 -> door close)
 * @retval None
 * @note The rotation action is set to complete in 100ms in order to be smoother
 * */
void set_servo_angle(uint16_t pulse) {
	uint16_t current_pulse = __HAL_TIM_GET_COMPARE(&htim8, TIM_CHANNEL_1);
	uint8_t step_num = 10;
	uint8_t step = (pulse - current_pulse) / step_num;
	for (uint8_t i = 0; i < step_num; i++) {
		current_pulse += step;
		__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_1, current_pulse);
		HAL_Delay(10);
	}
//	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_1, pulse);
}

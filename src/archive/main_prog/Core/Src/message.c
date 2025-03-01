#include "usart.h"
#include "message.h"

/**
 * @brief Send a message to the computer.
 * @note  This function is aborted.
 */
void send_message(uint8_t data_1, uint8_t data_2, uint8_t data_3, uint8_t data_4, uint8_t data_5,
		uint8_t data_6, uint8_t data_7, uint8_t data_8) {
	uint8_t data[9] = { 80, data_1, data_2, data_3, data_4, data_5, data_6, data_7, data_8 };
	HAL_UART_Transmit(&huart3, data, 9, 20);
}

/**
 * @brief  Convert 16-bit data to 8-bit data.
 * @param  data: 16-bit data to be converted
 * @param  num: 1 or 2 (1 -> high 8 bits, 2 -> low 8 bits)
 * @retval 8-bit data (converted part)
 * @note   This function is aborted.
 */
uint8_t convert(uint16_t data, int num) {
	uint8_t data_1 = data >> 8;
	uint8_t data_2 = data;
	if (num == 1) {
		return data_1;
	} else {
		return data_2;
	}
}

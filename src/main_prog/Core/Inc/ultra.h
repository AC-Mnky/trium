#ifndef __ULTRA_H
#define __ULTRA_H
#include <stdint.h>

void TIM1_Delay_us(uint16_t n_us);
void get_distance(uint8_t* distance, uint8_t type);

#endif

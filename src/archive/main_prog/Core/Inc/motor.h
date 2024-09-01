#ifndef __MOTOR_H
#define __MOTOR_H

void motor_init(void);
void set_motor_speed(uint8_t num, int8_t pulse);
void set_servo_angle(uint16_t pulse);
void set_servo_angle_delay(uint16_t pulse);

uint16_t get_encoder_CNT(int num, uint32_t *out_real_tick_elapsed);
uint8_t get_encoder_direction(uint8_t num);

#endif

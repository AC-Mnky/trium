#ifndef __MOTOR_H
#define __MOTOR_H

void motor_init(void);
void set_motor_speed(uint8_t, int);
void set_servo_angle(uint16_t);
void set_servo_angle_delay(uint16_t pulse);

uint16_t get_encoder_CNT(int, uint32_t*);
uint8_t get_encoder_direction(uint8_t);

#endif

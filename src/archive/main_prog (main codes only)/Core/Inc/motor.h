#ifndef __MOTOR_H
#define __MOTOR_H

void motor_init(void);
void set_motor_speed(int, int);
void set_servo_angle(int);

uint16_t get_encoder_CNT(int, uint32_t*);
uint8_t get_encoder_direction(int);

#endif

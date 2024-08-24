#ifndef __PID_H
#define __PID_H

struct PID_struct{
	int32_t target_val;
	int32_t actual_val;
	int32_t Error;
	int32_t LastError;
	int32_t Kp_mul,Ki_mul,Kd_mul;
	int32_t Kp_frac,Ki_frac,Kd_frac;
	int32_t integral, differential;
	int32_t output_val;
};

void PID_init(struct PID_struct*);
int32_t PID_vel(struct PID_struct* pid, uint8_t PWM_Pulse, uint16_t Encoder_pulse, int32_t real_tick_elapsed);

#endif

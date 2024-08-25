#include "tim.h"
#include "gpio.h"
#include <stdlib.h>
#include "PID.h"

const int32_t Encoder_Pulse_Every_round = 44; // ppr = 11, four times frequency
//const int32_t Motor_Reduction_Ration = 20; // 20.4 actually
const int32_t Motor_Max_Velocity = 90; //RPS, before velocity decrease
const int32_t PWM_Period = 100;
// const int32_t Encoder_Read_freq = 500; //s^-1
const int32_t upper_integral = 20;
const int32_t real_tick_freq = 72000000;
const int32_t real_tick_freq_div256 = real_tick_freq >> 8;

void PID_init(struct PID_struct *pid, int32_t Kp_mul_n, int32_t Kp_frac_n , int32_t Ki_mul_n, int32_t Ki_frac_n, int32_t Kd_mul_n, int32_t Kd_frac_n) {
	pid->target_val = 0; // << 8
	pid->actual_val = 0; // << 8
	pid->output_val = 0; // << 8
	pid->Error = 0; // << 8
	pid->LastError = 0; // << 8

	pid->Kp_mul = Kp_mul_n;
	pid->Kp_frac = Kp_frac_n;

	pid->Ki_mul = Ki_mul_n;
	pid->Ki_frac = Ki_frac_n;

	pid->Kd_mul = Kd_mul_n;
	pid->Kd_frac = Kp_frac_n;
}

void PID_change_para(struct PID_struct *pid, int32_t Kp_mul_n, int32_t Kp_frac_n , int32_t Ki_mul_n, int32_t Ki_frac_n, int32_t Kd_mul_n, int32_t Kd_frac_n){
	pid->Kp_mul = Kp_mul_n;
	pid->Kp_frac = Kp_frac_n;

	pid->Ki_mul = Ki_mul_n;
	pid->Ki_frac = Ki_frac_n;

	pid->Kd_mul = Kd_mul_n;
	pid->Kd_frac = Kp_frac_n;
}

int32_t PID_vel(struct PID_struct *pid, uint8_t PWM_Pulse,
		uint16_t Encoder_pulse, int32_t real_tick_elapsed) {
	int32_t real_tick_elapsed_div256 = real_tick_elapsed >> 8;

	pid->target_val = ((int8_t) (PWM_Pulse)) << 8;

	int32_t Encoder_pulse_short = (short)Encoder_pulse;

	pid->actual_val = (real_tick_freq_div256 * PWM_Period >> 8) * Encoder_pulse_short /
			((Encoder_Pulse_Every_round * real_tick_elapsed_div256) * Motor_Max_Velocity >> 16);
	//give the actual PWM pulse

	//			(PWM_Period * Encoder_pulse_short * Encoder_Read_freq
//			/ (Encoder_Pulse_Every_round * Motor_Max_Velocity)) << 8; //give the actual PWM pulse

	pid->LastError = pid->Error;
	pid->Error = pid->actual_val - pid->target_val;

	pid->integral += pid->Error * real_tick_elapsed_div256 / real_tick_freq_div256;
	if (pid->integral > (upper_integral << 8)) {
		pid->integral = (upper_integral << 8);
	} else if (pid->integral < -(upper_integral << 8)) {
		pid->integral = -(upper_integral << 8);
	}
	pid->differential = (((pid->Error - pid->LastError) >> 4) * (real_tick_freq_div256 >> 4) / real_tick_elapsed_div256); // >> 8

	pid->output_val = pid->target_val
					- pid->Error * pid->Kp_mul / pid->Kp_frac
					- pid->integral * pid->Ki_mul / pid->Ki_frac
					- pid->differential * pid->Kd_mul / pid->Kd_frac
					;
	return (pid->output_val >> 8);
}

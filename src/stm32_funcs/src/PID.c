#include "tim.h"
#include "gpio.h"
#include <stdlib.h>
#include "PID.h"

const int Encoder_Pulse_Every_round = 22; // ppr = 11, double frequency
const int Motor_Reduction_Ration = 35;
const int Motor_Max_Velocity = 163;//RPS, before velocity decrease
const int PWM_Period = 100;
const int Encoder_Read_freq = 500; //s^-1
const int upper_integral = 100;

void PID_init(struct PID_struct* pid){
	pid->target_val = 0;
	pid->actual_val = 0;
	pid->output_val = 0;
	pid->Error = 0;
	pid->LastError = 0;
	pid->Kp_frac = 2;
	pid->Ki_frac = 100;
	pid->Kd_frac = 10;
}

int PID_vel(struct PID_struct* pid, int PWM_Pulse, uint16_t Encoder_pulse){
	pid->target_val = PWM_Pulse;
	int Encoder_pulse_short = abs((short)Encoder_pulse);

	pid->actual_val = PWM_Period * Encoder_pulse_short*Encoder_Read_freq/(Encoder_Pulse_Every_round*Motor_Max_Velocity);//give the actual PWM pulse

	pid->LastError = pid->Error;
	pid->Error = (short)(pid->target_val - pid->actual_val);

	if (pid->integral < upper_integral){
		pid->integral += pid->Error;
	}
	else{
		pid->integral = upper_integral;
	}
	pid->output_val += pid -> Error / pid -> Kp_frac +
					  pid -> integral / pid -> Ki_frac +
					  (pid -> Error - pid -> LastError) / pid -> Kd_frac;

	return pid->output_val;
}

#ifndef __PID_H
#define __PID_H

struct PID_struct{
	int target_val;
	int actual_val;
	int Error;
	int LastError;
	int Kp_frac,Ki_frac,Kd_frac;
	int integral;
	int output_val;
};

void PID_init(struct PID_struct*);
int PID_vel(struct PID_struct*, int, uint16_t);

#endif

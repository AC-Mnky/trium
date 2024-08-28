import csv
import os.path

from encoder import get_omega
from nnn import decide_u
from pwm import set_u

write_version = "test"


if __name__ == "__main__":

    i = 0
    omega: list[int] = [0]  # len(omega) == i + 1
    u: list[int] = [0]  # len(u) == i + 1
    delta_omega: list[int] = []  # len(delta_omega) == i

    while i < 1000:

        omega.append(get_omega(i))
        delta_omega.append(omega[-1] - omega[-2])
        i += 1

        u.append(decide_u(i, omega, u, delta_omega))
        set_u(u[-1])

    omega.pop()
    u.pop()

    repository_path = os.path.dirname(os.path.realpath(__file__)) + "/../.."
    filename = repository_path + "/assets/motor_data/" + write_version + ".csv"
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        for i in range(len(omega)):
            writer.writerow([omega[i], u[i], delta_omega[i]])

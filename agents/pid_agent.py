import housebuilder

constants = housebuilder.get_constants()

KP = 0.1
KI = 0
KD = 0

class PIDController:
	def __init__(self, KP: float, KI: float, KD: float, FF: float):
		self.KP, self.KI, self.KD, self.FF = KP, KI, KD, FF
		self.integral = 0
		self.old_error = None
	def calc(self, error: float):
		self.integral += error
		P = error * self.KP
		I = self.integral * self.KI
		D = (error - self.old_error) * self.KD
		self.old_error = error
		return P + I + D + self.FF
	
pid = PIDController(KP, KI, KD)

def prelim_agent(house: housebuilder.House, room0_temp: float, room0_setp: float, room1_temp: float, room1_setp: float):
	if room0_temp > room0_setp + constants.epsilon and room1_temp > room1_setp + constants.epsilon:
		return (constants.settings.index(-1), [[False, False]])
	if room0_temp < room0_setp - constants.epsilon and room1_temp < room1_setp - constants.epsilon:
		return (constants.settings.index(1), [[False, False]])

	if room0_temp > room0_setp + constants.epsilon and abs(room1_temp - room1_setp) < constants.epsilon:
		return (constants.settings.index(-1), [[False, True]])
	if room1_temp > room1_setp + constants.epsilon and abs(room0_temp - room0_setp) < constants.epsilon:
		return (constants.settings.index(-1), [[True, False]])
	
	if room0_setp < room0_setp - constants.epsilon and abs(room1_temp - room1_setp) < constants.epsilon:
		return (constants.settings.index(1), [[False, True]])
	if room1_temp < room1_setp - constants.epsilon and abs(room0_temp - room0_setp) < constants.epsilon:
		return (constants.settings.index(1), [[True, False]])
	
	if room0_temp > room0_setp + constants.epsilon and room1_temp < room1_setp - constants.epsilon:
		error0, error1 = abs(room0_temp - room0_setp), abs(room1_temp - room1_setp)
		if error0 > error1:
			return (constants.settings.index(-1), [[False, True]])
		else:
			return (constants.settings.index(1), [[True, False]])
	if room0_temp < room0_setp - constants.epsilon and room1_temp > room1_setp + constants.epsilon:
		error0, error1 = abs(room0_temp - room0_setp), abs(room1_temp - room1_setp)
		if error0 > error1:
			return (constants.settings.index(1), [[False, True]])
		else:
			return (constants.settings.index(-1), [[True, False]])
	
	if abs(room0_temp - room0_setp) < constants.epsilon and abs(room1_temp - room1_setp) < constants.epsilon:
		return (constants.settings.index(0), house.dampers)

	return (house.ac_status, house.dampers)

def agent(house: housebuilder. House, outside_temp: float):
	room0_temp = house.rooms[0][0].get_temp()
	room0_setp = house.rooms[0][0].get_setpoint()
	room1_temp = house.rooms[0][1].get_temp()
	room1_setp = house.rooms[0][1].get_setpoint()

	ac_status, dampers = prelim_agent(house, room0_temp, room0_setp, room1_temp, room1_setp)
	if room0_temp > outside_temp and room1_temp > outside_temp and constants.settings[ac_status] < 0:
		ac_status = constants.settings.index(0)
		dampers = house.dampers
	if room0_temp < outside_temp and room1_temp < outside_temp and constants.settings[ac_status] > 0:
		ac_status = constants.settings.index(0)
		dampers = house.dampers
	
	return (ac_status, dampers)
import sys

def get_problem(def_fpath):
	states = {}
	controls = {}
	algebraic_vars = {}
	parameters = {}
	constants = {}
	boundary_conds = {}
	constraints = {}
	with open(def_fpath) as def_fin:
		for l in def_fin:
			l = l.strip()
			if not l or l.startswith('#') or 'dimension' in l:
				continue
			num, _ , name = l.split()
			if l.startswith('state'):
				states[int(num[len('state.'):])] = name
			if l.startswith('control'):
				controls[int(num[len('control.'):])] = name
			if l.startswith('algebraic.'):
				algebraic_vars[int(num[len('algebraic.'):])] = name
			if l.startswith('parameter.'):
				parameters[int(num[len('parameter.'):])] = name
			if l.startswith('constant.'):
				constants[int(num[len('constant.'):])] = name
			if l.startswith('boundarycond.'):
				boundary_conds[int(num[len('boundarycond.'):])] = name
			if l.startswith('constraint.'):
				constraints[int(num[len('constraint.'):])] = name
	return states, controls, algebraic_vars, parameters, constants, boundary_conds, constraints



def print_elements(elements, datatype, element_name, append=''):
	print ('\t%s %s;' % (datatype, ', '.join(['%s%s' % (el, append) for el in elements.values()])))
	for i, el in elements.items():
		print ('\t%s%s = %s[%d];' % (el, append, element_name, i))

def print_constants():
	print_elements(constants, 'double', 'constants')

def print_states():
	print_elements(states, 'Tdouble', 'state')

def print_initial_states():
	print_elements(states, 'Tdouble', 'initial_state', append='_t0')

def print_final_states():
	print_elements(states, 'Tdouble', 'final_state', append='_tf')

def print_algebraic():
	print_elements(algebraic_vars, 'Tdouble', 'algebraicvars')

def print_controls():
	print_elements(controls, 'Tdouble', 'control')

def print_input(elements, name):
	for i, s in elements.items():
		print ('\t// %s' % s)
		print ('\t%s[%d] = ;' % (name, i))

def print_state_dynamics():
	for i, s in states.items():
		print ('\t// %s' % s)
		print ('\tstate_dynamics[%d] = ;' % i)



if __name__ == '__main__':
	def_fpath = sys.argv[1]

	states, controls, algebraic_vars, parameters, constants, boundary_conds, constraints = get_problem(def_fpath)
	
	# interest = 'dynamics'
	interest = 'boundarycond'
	# interest = 'pathcond'

	if interest == 'dynamics':
		print_algebraic()
		print("")
		print_constants()
		print("")
		print_states()
		print("")
		print_controls()
		print("")
		print_input(states, 'state_dynamics')

	elif interest == 'boundarycond':
		print_constants()
		print("") 
		print_initial_states()
		print("")
		print_final_states()
		print("")
		print_input(boundary_conds, 'boundary_conditions')

	elif interest == 'pathcond':
		print_algebraic()
		print("")
		print_constants()
		print("")
		print_states()
		print("")
		print_controls()
		print("")
		print_input(constraints, 'path_constraints')

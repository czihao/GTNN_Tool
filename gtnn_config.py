NUM_NEURON = 0
USER_DATA = 6
VMAX = 1
DT = 2
TMAX = 3
TAU = 4
ETA = 5
LAMBDA = 7
VTH = 8
C = 9
INPUT_FILE = 10

# arg_list = []

# arg_list.insert(NUM_NEURON, 800)
# arg_list.insert(VMAX, 1)
# arg_list.insert(DT, 0.001)
# arg_list.insert(TMAX, 10)
# arg_list.insert(TAU, 0.1)
# arg_list.insert(ETA, 0.1)
# arg_list.insert(USER_DATA, "G14_1.txt")
# arg_list.insert(LAMBDA, 5)
# arg_list.insert(VTH, 0)
# arg_list.insert(C, 1)

arg_list = {
    'NUM_NEURON' : 800,
    'QFILE' : 'G14_1.txt',
    'VMAX' : 1,
    'DT' : 0.001,
    'TMAX' : 10,
    'TAU' : 0.1,
    'ETA' : 0.1,
    'LAMBDA' : 5,
    'VTH' : 0,
    'C' : 1,
    'INPUT_FILE' : 'eg_input.txt',
    'LAYER_FILE' : 'eg_layer.txt',
    'RECIP_FILE' : 'eg_recip.txt',
    'LAYER_DENSITY' : 0.3,
    'NUM_RECIP' : 6,
    'OVERLAP' : 0
}

# def modify_args(user_args):
#     global arg_list
#     arg_list[NUM_NEURON] = user_args[NUM_NEURON]
#     arg_list[VMAX] = user_args[VMAX]
#     arg_list[DT] = user_args[DT]
#     arg_list[TMAX] = user_args[TMAX]
#     arg_list[TAU] = user_args[TAU]
#     arg_list[ETA] = user_args[ETA]
#     arg_list[USER_DATA] = user_args[USER_DATA]
#     arg_list[LAMBDA] = user_args[LAMBDA]
#     arg_list[VTH] = user_args[VTH]
#     arg_list[C] = user_args[C]
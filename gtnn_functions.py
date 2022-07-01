import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import numpy.matlib as matlab

# from gtnn import MATRIX_SIZE
#import GTNNLearning
# from pycuda import driver, compiler, gpuarray, tools
from scipy.sparse import csr_matrix, vstack, block_diag, coo_matrix
from gtnn_config import arg_list


def genQ_txt(num_neuron=None, user_data_file=None):
    global arg_list
    
    user_data = np.loadtxt(user_data_file, skiprows=0, dtype=int)
    col = user_data[:,1].T - 1
    row = user_data[:,0].T - 1
    data = user_data[:,2].T
    coo_Q = coo_matrix((data,(row,col)), shape=(num_neuron, num_neuron), dtype=int)
    array_Q = coo_Q.toarray()
    
    full_Q = (np.triu(array_Q, k=1))
    full_Q = full_Q + full_Q.T
    

    return coo_matrix(full_Q)

def genQ_random(overall_density, num_recip, ff_flag, overlap=0):
    global arg_list
    num_neuron = arg_list['NUM_NEURON']
    num_layers = int(np.floor(1/overall_density))

    # Random layer sizes 
    layer_sizes = np.random.dirichlet(np.ones((num_layers), \
        dtype=np.single)*100, size=1).reshape(num_layers)
    layer_sizes *= num_neuron
    layer_sizes = layer_sizes.astype(np.uint)
    if np.sum(layer_sizes) != num_neuron:
        layer_sizes[-1] += num_neuron - np.sum(layer_sizes)
    assert(np.sum(layer_sizes) == num_neuron)
    # Init coo matrix attrs
    col = np.zeros((1,)).astype(int)
    row = np.zeros((1,)).astype(int)
    data = np.zeros((1,)).astype(int)

    # Random reciprocal connections
    recip_map = np.ones((num_layers, num_layers), dtype=int)
    upper = np.triu(recip_map, 1)
    if ff_flag:
        lower = np.triu(recip_map.T, 2).T
    else:
        lower = np.triu(recip_map.T, 1).T
    mask = np.logical_not(upper + lower)
    num_nonzero_blocks = num_layers**2 - np.count_nonzero(mask)
    offset = np.cumsum(layer_sizes)
    offset = np.insert(offset, 0, 0)
    offset = np.delete(offset, -1)
    # TODO May add overlap
    recip_per_block = int(num_recip/(num_nonzero_blocks))
    for i in range(num_layers):
        for j in range(num_layers):
            if ~mask[i, j]:
                for k in range(recip_per_block):
                    row_size = layer_sizes[i]
                    col_size = layer_sizes[j]
                    rand_row = int(np.random.randint(0, row_size, (1,)) + offset[i])
                    rand_col = int(np.random.randint(0, col_size, (1,)) + offset[j])
                    rand_data = np.random.rand(1)
                    col = np.append(col, rand_col)
                    row = np.append(row, rand_row)
                    data = np.append(data, rand_data)
    
    # Generate Q based on layer_sizes and recip_layers
    for i in range(num_layers):
        # Fully connected Q for each layer
        temp = np.empty((0))
        overlap_size = 0
        if i == 0:
            temp = np.random.rand(layer_sizes[i], layer_sizes[i]).astype(np.float16)
        else:
            overlap_size = int(overlap * layer_sizes[i-1])
            layer_size = int(layer_sizes[i] + overlap_size)
            if ff_flag:
                temp = np.random.rand(layer_size, layer_sizes[i-1]+layer_sizes[i]).astype(np.float16)
            else:
                temp = np.random.rand(layer_size, layer_size).astype(np.float16)
        temp_coo = coo_matrix(temp, dtype=(np.float16))
        row_temp = temp_coo.row + np.sum(layer_sizes[0:i]) - overlap_size
        if i == 0:
            col_temp = temp_coo.col 
        else:
            if ff_flag:
                col_temp = temp_coo.col + np.sum(layer_sizes[0:i-1])
            else:
                col_temp = temp_coo.col + np.sum(layer_sizes[0:i]) - overlap_size

        col = np.concatenate((col, col_temp))
        row = np.concatenate((row, row_temp))
        data = np.concatenate((data, temp_coo.data))

    res = coo_matrix((data, (row, col)), shape=(arg_list['NUM_NEURON'], arg_list['NUM_NEURON']), dtype=(np.float16))
    res = res * np.logical_not(np.eye(arg_list['NUM_NEURON']))
    res = coo_matrix((data, (row, col)), shape=(arg_list['NUM_NEURON'], arg_list['NUM_NEURON']), dtype=(np.float16))
    # res = res.tocsr()
    # return res.toarray()
    return res

# MODE: "random identity", "identity", "random feedforward", "feedforward", "user data"
def generateQ(mode):
    global arg_list
    if np.char.equal(mode, "user data"):
        num_neuron = arg_list['NUM_NEURON']
        Qfile = arg_list['QFILE']
        return genQ_txt(num_neuron=num_neuron, user_data_file=Qfile)
    elif np.char.equal(mode, "random identity") or\
         np.char.equal(mode, "random feedforward"):
        ff_flag = True if np.char.equal(mode, "random feedforward") else False
        overall_density = float(arg_list['LAYER_DENSITY'])
        num_recip = int(arg_list['NUM_RECIP'])
        overlap = float(arg_list['OVERLAP'])
        print(overall_density, num_recip, overlap, ff_flag)
        return genQ_random(overall_density, num_recip, ff_flag, overlap)
     

def generateV(mode):
    global arg_list
    if np.char.equal(mode, "rand"):
        # vp = np.sign(np.random.rand(num_neuron,1).astype(np.float16)) * -0.5
        # vn = np.sign(np.random.rand(num_neuron,1).astype(np.float16)) * -0.5
        vp = np.ones((arg_list['NUM_NEURON'], 1), dtype=np.float16) * -0.5 * arg_list['VMAX']
        vn = np.ones((arg_list['NUM_NEURON'], 1), dtype=np.float16) * -0.5 * arg_list['VMAX']

        #return -0.5 * np.ones((num_neuron, 1), dtype=np.float16)
        return vp, vn

# Mode "random", "user file", "zero"
def generateI(mode, file=None):
    global arg_list
    if np.char.equal(mode, "user file"):
        b = np.loadtxt(file, dtype=int)
    elif np.char.equal(mode, "random"):
        b = np.random.rand(arg_list['NUM_NEURON'], 1).astype(np.float16)
    elif np.char.equal(mode, "zero"):
        b = np.zeros((arg_list['NUM_NEURON'], 1))
        
    if b.shape[0] != arg_list['NUM_NEURON']:
        # TODO
        print("WRONG")
    return b

def max_cut(adj, v):
    v = v.reshape(arg_list['NUM_NEURON'],)
    e = 1e-3
    v[v > arg_list['VMAX'] - e] = 1
    v[v < -arg_list['VMAX'] + e] = 0
    num_converged = np.sum(v == 1) + np.sum(v == 0)
    # 0 activation
    v = v > 0
    out = 2*np.outer(v, v)
    i = matlab.repmat(v, arg_list['NUM_NEURON'], 1).T
    j = matlab.repmat(v, arg_list['NUM_NEURON'], 1)
    # print(j.shape)
    # print(out.shape)
    # print(out)
    # print(j)
    # print(i)
    num_maxcut = np.sum(np.triu(adj * -(out-i-j)))

    return num_maxcut, num_converged

def adapt_Q(iter, Q, Psip, Psin, vp, vn, M=np.array(np.mat('1 0 0 1 1; 1 1 1 0 1; 1 1 1 0, 0; 1 1 1 1 0; 1 1 1 1 1'))):
    global arg_list

    Qmax = 20
    Q = Q + 0.5*arg_list['ETA'] * M * np.outer((Psip - Psin), (vp-vn))
    # Q[Q >= Qmax] = Qmax
    # Q = np.eye(arg_list['NUM_NEURON']) - 0.5 * Q

    # Q = np.eye(arg_list['NUM_NEURON']) - 0.1 * Q
    # if iter % 200000 == 0:
    #     norm = matplotlib.colors.Normalize()
    #     fig = plt.figure()
    #     ax = fig.add_subplot(1, 1, 1)
    #     ax.imshow(Q, norm=norm, cmap=plt.cm.gray)
    #     # ax.set_title(titles[i], fontsize=10)
    #     ax.set_xticks([])
    #     ax.set_yticks([])
    #     plt.show()
    # if iter > 10000:
    #     Q -= 0.001 * M * Q
    # rand_M = np.random.rand(arg_list[NUM_NEURON], arg_list[NUM_NEURON])
    # rand_M[rand_M < 0.8] = 1
    # rand_M[rand_M < 1] = 0
    # rand_M[:32, :] = 1
    # Q = Q * rand_M

    return Q

def gtnn_evolve(mode, M, vp, vn, Q, b):
    global arg_list

    if np.char.equal(mode, "routing"):
        vp_ev = np.zeros((arg_list['NUM_NEURON'], int(arg_list['TMAX']/arg_list['DT'])))
        vn_ev = np.zeros((arg_list['NUM_NEURON'], int(arg_list['TMAX']/arg_list['DT'])))
        Qv_ev = np.zeros(int(arg_list['TMAX']/arg_list['DT']))
        Qb_ev = np.zeros(int(arg_list['TMAX']/arg_list['DT']))

    Psip = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
    Psin = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
    power_ev = np.zeros(int(arg_list['TMAX']/arg_list['DT']))
   
   
    iter = 0
    # plt.ion()
    # figure, ax = plt.subplots(figsize=(10, 8))
    # ax.set_ylim(-20, 20)
    # v_plot = Q @ (vp-vn)
    # line1, = ax.plot(v_plot, 'b')
    # line2, = ax.plot(b, 'r')
    # plt.title( 'Iteration %d' % iter )

    while True:   


        if iter * arg_list['DT'] >= arg_list['TMAX']:
            print('end')
            break


        if np.char.equal(mode, "routing"):
            ################################## Compressive sensing & routing
            vp_ev[:, iter] = vp.reshape(arg_list['NUM_NEURON'],)
            vn_ev[:, iter] = vn.reshape(arg_list['NUM_NEURON'],)
            Gp = -b + Q @ (vp-vn) + Psip + np.diag(Q).reshape(vn.shape) * vn
            Gn = b - Q @ (vp-vn) + Psin + np.diag(Q).reshape(vp.shape) * vp
            Gp[Gp > arg_list['LAMBDA']] = arg_list['LAMBDA']
            Gp[Gp < -arg_list['LAMBDA']] = -arg_list['LAMBDA']
            Gn[Gn > arg_list['LAMBDA']] = arg_list['LAMBDA']
            Gn[Gn < -arg_list['LAMBDA']] = -arg_list['LAMBDA']
            

            Psip = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
            Psin = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
            
            vp = vp + (arg_list['DT']/arg_list['TAU']) * ((vp*vp - arg_list['VMAX']**2) * Gp)\
                    / (-vp * Gp + arg_list['LAMBDA'] * arg_list['VMAX'])
            vn = vn + (arg_list['DT']/arg_list['TAU']) * ((vn*vn - arg_list['VMAX']**2) * Gn)\
                    / (-vn * Gn + arg_list['LAMBDA'] * arg_list['VMAX'])
            # vp = vp - (arg_list['DT']/arg_list['TAU']) * (vp + np.sign(Gp) * arg_list['VMAX'])
            # vn = vn - (arg_list['DT']/arg_list['TAU']) * (vn + np.sign(Gn) * arg_list['VMAX'])

            vp_flag = np.logical_or(np.abs(vp) > arg_list['VMAX'], np.abs(Gp) > arg_list['LAMBDA'])
            vn_flag = np.logical_or(np.abs(vn) > arg_list['VMAX'], np.abs(Gn) > arg_list['LAMBDA'])
            
            if np.any(vp_flag) or np.any(vn_flag):
                print("WTF!!!!!!!!!! %d" %(iter))
                print("Gp: %d", np.sum(np.abs(Gp) > arg_list['LAMBDA']))
                print("Gn: %d", np.sum(np.abs(Gn) > arg_list['LAMBDA']))
                print(Gn)
                print(Gp)
                break
            else:
                pass
                # _,num_converged = max_cut(Q, vp-vn)
                # if num_converged == arg_list['NUM_NEURON']:
                #     print("Converged!!! NOW CHECK Qv==b")
                #     print(np.sum(Q @ (vp-vn) - b))
                #     print(np.sum(np.linalg.inv(Q) @ b - (vp-vn)))


            Psip[vp > arg_list['VTH']] = arg_list['C']
            Psin[vn > arg_list['VTH']] = arg_list['C']
            vp[vp > arg_list['VTH']] = arg_list['VTH']
            vn[vn > arg_list['VTH']] = arg_list['VTH']

            power_ev[iter] = np.sum(Psip + Psin)
            

            e = 1e-3
            Qv = np.sum((Q @ (vp-vn) - b) > e)
            Qb = np.sum((np.linalg.inv(Q) @ b - (vp-vn)) > e)
            Qv_ev[iter] = Qv
            Qb_ev[iter] = Qb

            if iter == 100000:
                print(vp-vn)

            if iter > 100000:
                pass
                if iter % 1000 == 0:
                    Q = adapt_Q(iter, Q, Psip, Psin, vp, vn, M)

            
            # if iter > 400000:
            if Qv == 0 and Qb == 0:
                print(Q @ (vp-vn))
                print(b)
                print(np.linalg.inv(Q) @ b)
                print((vp-vn))
                print('end %d' %iter)
                break
            

        elif np.char.equal(mode, 'combinatorial'):
            ################################### Combinatory
            # if iter <= 1000:
            #     Gp = - b + Q @ (vp-vn) + Psip + np.diag(Q).reshape(vn.shape) * vn
            #     Gn = b - Q @ (vp-vn) + Psin + np.diag(Q).reshape(vp.shape) * vp
            #     Psip = np.zeros((arg_list[NUM_NEURON], 1)).astype(np.float16)
            #     Psin = np.zeros((arg_list[NUM_NEURON], 1)).astype(np.float16)
                
            #     vp = vp + (arg_list[DT]/arg_list[TAU]) * ((vp*vp - arg_list[VMAX]**2) * Gp)\
            #         /(-vp * Gp + arg_list[LAMBDA] * arg_list[VMAX])
            #     vn = vn + (arg_list[DT]/arg_list[TAU]) * ((vn*vn - arg_list[VMAX]**2) * Gn)\
            #         /(-vn * Gn + arg_list[LAMBDA] * arg_list[VMAX])
            # else:
            
            ##### NO RESET ######
            # Gp = Q @ (vp-vn) + Psip - np.cos(np.pi/2 * (vp-vn)) + Q @ np.cos(np.pi/2 * (vp-vn))
            # Gn = -Q @ (vp-vn) + Psin + np.cos(np.pi/2 * (vp-vn)) - Q @ np.cos(np.pi/2 * (vp-vn))
            cos_temp = np.cos(np.pi/2 * (vp-vn))
            # G_temp = Q @ ((vp-vn) + cos_temp)
            G_temp = Q @ (vp-vn)
            
            # Gp = G_temp + Psip - cos_temp 
            # Gn = -G_temp + Psin + cos_temp

            Gp = G_temp + Psip 
            Gn = -G_temp + Psin 

            ##### RESET #####
            # if iter >= 100000:
            #     if iter == 100000:
            #         v = vp-vn
            #         e = 1e-2
            #         vp[v <= -arg_list[VMAX] + e] = -1
            #         vn[v <= -arg_list[VMAX] + e] = 0
            #         vp[v >= arg_list[VMAX] - e] = 0
            #         vn[v >= arg_list[VMAX] - e] = -1
            #         vp[np.logical_and(arg_list[VMAX] - e > v, v > -arg_list[VMAX] + e)] = 0
            #         vn[np.logical_and(arg_list[VMAX] - e > v, v > -arg_list[VMAX] + e)] = 0
            #         # print(vp)
            #         # print(vn)
            #         print("reset!!!")
            #     cos_temp = np.cos(np.pi/2 * (vp-vn))
            #     G_temp = Q @ ((vp-vn) + cos_temp)
                
            #     Gp = G_temp + Psip - cos_temp 
            #     Gn = -G_temp + Psin + cos_temp

            # else :
            #     Gp = vp + Q @ (vp-vn) + Psip
            #     Gn = vn -Q @ (vp-vn) + Psin
            
            Psip = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
            Psin = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)

            vp = vp - arg_list['TAU'] * (vp + np.sign(Gp) * arg_list['VMAX'])
            vn = vn - arg_list['TAU'] * (vn + np.sign(Gn) * arg_list['VMAX'])

            Psip[vp > arg_list['VTH']] = arg_list['C']
            Psin[vn > arg_list['VTH']] = arg_list['C']
            vp[vp > arg_list['VTH']] = arg_list['VTH']
            vn[vn > arg_list['VTH']] = arg_list['VTH']

            if iter %10000 == 0:
                num_maxcut, num_converged = max_cut(Q.toarray(), vp-vn)
                print("max cut: %d, number converged: %d" %(num_maxcut, num_converged))
            # time.sleep(0.1)
        
        

        iter += 1

        # print(len(prev_g_lst))
        # print(prev_g_lst[0].shape)


        # toc = time()
        # update_t = toc-tic
    # plt.hist(vp-vn)
    # plt.show()

        # # print(np.linalg.norm(g))
        # e = 1e-10
        # v_final = v_evolution[:,iter-1].copy()
        # res = []
        # res.insert(0, np.where(v_final > vmax - e))
        # res.insert(1, np.where(v_final < -vmax + e))
        # # print(v_final)
       
        # #v_final[v_final > vmax - e] = 1
        # #v_final[v_final < -vmax + e] = 0
        # #d = np.sum(v_final == 1) + np.sum(v_final == 0)

        # plt.figure(1)
        # plt.grid(True)
        # plt.plot(v_evolution[:,:].T)
        # plt.ylim(-vmax, vmax)
        # plt.show()
    # print(updateQ)
    # norm = matplotlib.colors.Normalize()
    # fig = plt.figure()
    # ax = fig.add_subplot(1, 1, 1)
    # ax.imshow(Q, norm=norm, cmap=plt.cm.gray)
    # # ax.set_title(titles[i], fontsize=10)
    # ax.set_xticks([])
    # ax.set_yticks([])
    # plt.show()
    p_ev = np.zeros((1000))
    for i in range(1000):
        p_ev[i] = np.sum(power_ev[i * 500:(i + 1) * 500])/500

    if np.char.equal(mode, "routing"):
        norm = matplotlib.colors.Normalize()
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 3, 1)
        ax1.imshow(Q, norm=norm, cmap=plt.cm.gray)
        ax1.set_title('Q')
        ax2 = fig.add_subplot(2,3,2)
        ax2.plot(vp_ev.T)
        ax2.plot(vn_ev.T)
        ax2.set_title('vp, vn')
        ax3 = fig.add_subplot(2, 3, 3)
        temp = vp_ev[0:2, :] - vn_ev[0:2, :]
        ax3.plot(temp.T)
        ax3.set_title('vp - vn')
        ax4 = fig.add_subplot(2, 3, 4)
        ax4.plot(Qv_ev, 'b')
        ax4.plot(Qb_ev, 'r')
        ax4.set_title('Qv, Qb')
        ax5 = fig.add_subplot(2, 3, 5)
        ax5.plot(p_ev)
        ax5.set_title('power')
        ax6 = fig.add_subplot(2,3,6)
        ax6.plot(power_ev)
        ax6.set_title('Spike')
        plt.show()
        
    return vp, vn, Q
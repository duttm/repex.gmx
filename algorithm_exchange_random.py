#!/usr/bin/env python3


# ------------------------------------------------------------------------------
#
def exchange_by_random(rid, cycle, ex_list, ex_data):
    '''
    We expect the following arguments:

      - ID of replica running this script
      - current cycle number
      - list of replica IDs in the exchange list
      - list of filename patterns (containing `%(rid)s`)

    We select random pairs of replicas from the replica list and pairwise
    exchange the file content of their `mdin` and `inpcrd` files
    '''

    import random
    random.shuffle(ex_list)

    while len(ex_list) >= 2:

        a = ex_list.pop()
        b = ex_list.pop()

        print('%s [%04d]: %s <-> %s' % (rid, cycle, a, b))

        for dname in ex_data:

            fa = dname % {'rid': a}
            fb = dname % {'rid': b}

            print(' %s <-> %s' % (fa, fb))

            with open(fa, 'r') as fin : data_a = fin.read()
            with open(fb, 'r') as fin : data_b = fin.read()
            with open(fa, 'w') as fout: fout.write(data_b)
            with open(fb, 'w') as fout: fout.write(data_a)


# ------------------------------------------------------------------------------


#!/usr/bin/env python

def exchange_by_temperature(rid, cycle, ex_list, dn_list):
    '''
    We expect the following arguments:

      - ID of replica running this script
      - current cycle number
      - list of replica IDs in the exchange list
      - list of file basenames to exchange on

    We select random pairs of replicas from the replica list and pairwise
    exchange the file content of their `dn_list`.
    '''
    import math,random
    def gibbs_exchange(r_i, ex_list, swap_matrix):  ###r_i here is NOT rid, but the r_i-th replica in ex_list 
        r_i = ex_list.index(r_i)
        print("gibbs sampling T exchange starting now")
        replicas = len(ex_list)
        #evaluate all i-j swap probabilities
        ps = [0.0]*(replicas)

        j = 0
        for r_j in range(replicas):
            ps[j] = -(swap_matrix[r_i][r_j] + swap_matrix[r_j][r_i] - 
                      swap_matrix[r_i][r_i] - swap_matrix[r_j][r_j]) 
            #print ps[j]
            j += 1
            
        new_ps = []
        for item in ps:
            if item > math.log(sys.float_info.max): new_item=sys.float_info.max
            elif item < math.log(sys.float_info.min) : new_item=0.0
            else :
                new_item = math.exp(item)
            new_ps.append(new_item)
        ps = new_ps
        #print ps
        # index of swap replica within replicas_waiting list
        j = replicas
        while j > (replicas - 1):
            j = weighted_choice_sub(ps)
            #print j
            
        
        r_j = j
        #print r_j
        return r_j      

    def reduced_potential(temperature, potential):

        Kb = 0.008314462175    #Boltzmann Constant in kJ/molK 
        if temperature != 0:
            beta = 1. / (Kb*temperature)
        else:
            beta = 1. / Kb     
        return float(beta * potential)

    def weighted_choice_sub(weights):  ### The weights are exchange probabilities
        """Adopted from asyncre-bigjob [1]
        """

        rnd = random.random() * sum(weights)
        for i, w in enumerate(weights):
            rnd -= w
            if rnd < 0:
                return i

    def build_swap_matrix(ex_list):

        temp = 0.0
        pot_eng = 0.0
        temperatures = []
        energies = []
        replicas = len(ex_list)
    ######---------------THIS section reads energy files, edit appropriately for your MD engine of choice----------------------------------

        for rid in ex_list:        

            with open('mdinfo.%s'%(rid),'r') as f: 
                lines = f.readlines()
            
                for i,j in enumerate(lines):
                    if "Temperature" in lines[i]:
                        temp = float(lines[i].split()[1])
                        temperatures.append(temp)
                    
                    elif "Potential" in lines[i]:
                        pot_eng = float(lines[i].split()[1])
                        energies.append(pot_eng)



        swap_matrix = [[ 0. for j in range(replicas)] for i in range(replicas)]
        print(swap_matrix)
        print(temperatures)
        print(energies)

        for i in range(replicas):

            for j in range(replicas):      
                print(i,j)
                swap_matrix[i][j] = reduced_potential(temperatures[j], energies[i])
        #print swap_matrix
        return swap_matrix

    swap_matrix=build_swap_matrix(ex_list)
    print("swap matrix is:", '\n',swap_matrix)


    #while len(ex_list) >= 2:

    final_exchange_pairs = []
    for r_i in ex_list:
        r_j = ex_list[gibbs_exchange(r_i, ex_list, swap_matrix)]
        final_exchange_pairs.append([r_i,r_j])

        a = r_i #ex_list.pop()
        b = r_j #ex_list.pop()

        print('%s [%04d]: %s <-> %s' % (rid, cycle, a, b))

        for dn in dn_list:
            fa = dn % {'rid': a}
            fb = dn % {'rid': b}


            print(' %s <-> %s' % (fa, fb))

            with open(fa, 'r') as fin : data_a = fin.read()
            with open(fb, 'r') as fin : data_b = fin.read()
            with open(fa, 'w') as fout: fout.write(data_b)
            with open(fb, 'w') as fout: fout.write(data_a)
        print(final_exchange_pairs)
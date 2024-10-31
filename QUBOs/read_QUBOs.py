""" reads json file with QUBOs - 1 train """
import pickle

# add file name
file_q = 'instance_qbits10_ppair2.0_psum2.0.pkl'


with open(file_q, 'rb') as fp:
    dict_read = pickle.load(fp)


print( dict_read  )

""" reads json file with QUBOs - 1 train """
import pickle


no_qbits = 4
ppair = 2.0
psum = 2.0

file_q = f'instance_qbits{no_qbits}_ppair{ppair}_psum{psum}.pkl'


with open(file_q, 'rb') as fp:
    dict_read = pickle.load(fp)


print( dict_read  )

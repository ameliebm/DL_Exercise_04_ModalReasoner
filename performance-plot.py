"""script performance-plot.py uses the matplotlib.pyplot module to plot the running times of the tableux algorithm implementation
in program tableux.py for four fourmula series."""

import matplotlib.pyplot as plt

# run with n = 5

n5 = [['0.000', '0.001', '0.005', '0.068', '1.136', '19.957'], 
      ['0.000', '0.000', '0.001', '0.001', '0.002', '0.003'], 
      ['0.000', '0.000', '0.001', '0.001', '0.004', '0.012'], 
      ['0.000', '0.000', '0.001', '0.003', '0.011', '0.047']]

# run with n = 6

n6 = [['0.000', '0.001', '0.005', '0.067', '1.139', '21.132', '348.168'], 
      ['0.000', '0.000', '0.001', '0.001', '0.002', '0.003', '0.005'], 
      ['0.000', '0.000', '0.000', '0.001', '0.003', '0.011', '0.047'],
      ['0.000', '0.000', '0.001', '0.002', '0.009', '0.040', '0.176']]

n6 = [[float(num) for num in series] for series in n6]

### plot

ou = n6
n = 6

series = range(1, n+2)

# linear
plt.figure()
plt.plot(series, ou[0], 'g^', label='series 1')
plt.plot(series, ou[1], 'ko', label='series 2')
plt.plot(series, ou[2], 'bs', label='series 3')
plt.plot(series, ou[3], 'r+', label='series 4')
#plt.show()
plt.yscale('linear')
plt.xlabel('formula in series')
plt.ylabel('performance measure [s]')
plt.title("Tableux formula series (linear scale)")
plt.legend()
plt.savefig(fname='performance-plot-linear.png')


# log 
plt.figure()
plt.plot(series, ou[0], 'g^', label='series 1')
plt.plot(series, ou[1], 'ko', label='series 2')
plt.plot(series, ou[2], 'bs', label='series 3')
plt.plot(series, ou[3], 'r+', label='series 4')
#plt.show()
plt.yscale('log')
plt.ylim(bottom=-1)
plt.xlabel('formula in series')
plt.ylabel('performance measure [s]')
plt.title("Tableux formula series (log scale)")
plt.legend()
plt.savefig(fname='performance-plot-log.png')
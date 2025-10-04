import numpy as np 
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

time_studied = np.array([2,4,5,6,20,60]).reshape(-1,1)
scores = np.array([10,15,35,44,65,95]).reshape(-1,1)


model = LinearRegression()
model.fit(time_studied,scores)


plt.scatter(time_studied, scores)
plt.plot(np.linspace(0,70,100), model.predict(np.linspace(0,70,100).reshape(-1,1)), 'r')
plt.ylim(0,100)
plt.show()
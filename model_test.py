import numpy as np
import pickle
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# Generate training data (x1 + x2) * 2 = y
X1 = [1,  2, 1,  3,  1,  1,  6,  5, 1,  4,  5, 0] 
X2 = [2,  3, 3,  5,  4,  2,  3,  3, 0,  2,  3, 1] 
y =  [6, 10, 8, 16, 10,  6, 18, 16, 2, 12, 16, 2] 

print(X1)
print(X2)
print(y)

# Shape into (n_samples, 2) for sklearn
X = np.vstack([X1, X2]).T

# Polynomial regression (degree 1)
poly = PolynomialFeatures(degree=1, include_bias=False)
X_poly = poly.fit_transform(X)

model = LinearRegression()
model.fit(X_poly, y)

x1_predict = [5]
x2_predict = [5]

X_predict = np.vstack([x1_predict, x2_predict]).T
y_predict = model.predict(poly.transform(X_predict))

print(f"{x1_predict} {x2_predict} y_predict: {y_predict}")

with open("my_model.pkl", "wb") as f:
    pickle.dump((poly, model), f)
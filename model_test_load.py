import pickle
import numpy as np

with open("my_model.pkl", "rb") as f:
    poly_loaded, model_loaded = pickle.load(f)

x1_predict_by_picle = [60]
x2_predict_by_picle = [15]

X_predict_by_picle = np.vstack([x1_predict_by_picle, x2_predict_by_picle]).T

y_predict_by_picle = model_loaded.predict(poly_loaded.transform(X_predict_by_picle))

print(f"{x1_predict_by_picle} {x2_predict_by_picle} y_predict_by_picle: {y_predict_by_picle}")
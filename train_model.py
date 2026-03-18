import joblib
from sklearn.linear_model import LogisticRegression

# sample dataset
X = [
    [90, 85, 80],
    [85, 80, 75],
    [70, 60, 65],
    [40, 45, 50],
    [30, 35, 40]
]

y = [1, 1, 1, 0, 0]   # 1 = pass , 0 = fail risk

model = LogisticRegression()
model.fit(X, y)

# save model
joblib.dump(model, "student_model.pkl")

print("Model trained and saved")
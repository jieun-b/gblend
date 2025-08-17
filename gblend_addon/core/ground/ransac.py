import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import RANSACRegressor

class PlaneModel(BaseEstimator, RegressorMixin):
    def fit(self, X, y=None):
        X_ = np.c_[X, np.ones(X.shape[0])]
        _, _, Vt = np.linalg.svd(X_)
        self.coef_ = Vt[-1, :3]
        self.intercept_ = Vt[-1, 3]
        return self

    def predict(self, X):
        return -(X @ self.coef_ + self.intercept_) / np.linalg.norm(self.coef_)

def fit_ransac_plane_3D(points_all, points_floor, residual_threshold=0.01):
    if len(points_floor) < 3:
        raise ValueError("Not enough floor points for RANSAC.")

    model = RANSACRegressor(
        estimator=PlaneModel(),
        residual_threshold=residual_threshold,
        max_trials=1000,
        min_samples=4,
    )
    model.fit(points_floor, np.zeros(len(points_floor)))

    a, b, c = model.estimator_.coef_
    normal = np.array([a, b, c])
    normal /= np.linalg.norm(normal)

    center_all = np.mean(points_all, axis=0)
    center_floor = np.mean(points_floor, axis=0)
    if np.dot(normal, center_floor - center_all) > 0:
        normal *= -1

    return normal

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


def poly_fit(x: np.array, y, degree = 4):
    
    """
    This function is used to to fit a curved line using polynomial regression
    
    Parameters:
        x (numpy array): The x-coordinates of the data points.
        y (numpy array): The y-coordinates of the data points.
        degree (int, optional): The degree of the highest polynomial power.
    
    Returns:
        tuple: A tuple of two numpy arrays, representing the x and y coordinates of the fitted curve.
    
    Example:
    
    x = np.arange(0, 30)
    y = [1, 3, 5, 7, 10, 9, 6, 12, 15, 23, 29, 43, 33, 64, 67, 60, 63, 69, 75, 87, 82, 88, 94, 101, 108, 133, 150, 162, 168, 176]
    x_curve, y_predicted = poly_fit(x, y, degree = 8)
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, label='Data points')
    plt.plot(x, y_predicted, c="red", label='Polynomial fit')
    plt.title('Polynomial Regression')
    plt.legend()
    plt.show()

    """
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    
    polynomial_features = poly.fit_transform(x.reshape(-1, 1))
    polynomial_reg_model = LinearRegression()
    polynomial_reg_model.fit(polynomial_features, y)
    
    y_predicted = polynomial_reg_model.predict(polynomial_features)
    
    return x, y_predicted
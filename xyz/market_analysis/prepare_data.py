import yfinance as yf
import pandas as pd
import numpy as np
from keras.src.layers import Dropout, Dense
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import keras
from keras import Sequential
from keras.api.layers import LSTM, Dropout, Dense


# Prepare the training data
def create_dataset(data, time_step):
    X, Y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:(i + time_step), 0])
        Y.append(data[i + time_step, 0])
    return np.array(X), np.array(Y)


def prepare_data(ticker_symbol='AAPL', start='2010-01-01', end='2023-01-01'):
    try:
        data = yf.download(ticker_symbol, start=start, end=end)
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker_symbol} in the given date range.")

        close_data = data['Close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(close_data)

        time_step = 60
        X, Y = create_dataset(scaled_data, time_step)
        X = X.reshape(X.shape[0], X.shape[1], 1)

        return X, Y, scaled_data, scaler, time_step, close_data, ticker_symbol, data

    except Exception as e:
        print(f"An error occurred: {e}")


def build_model(X):
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)),
        Dropout(0.2),
        LSTM(units=50, return_sequences=True),
        Dropout(0.2),
        LSTM(units=50),
        Dropout(0.2),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def predict_future(model, scaled_data, time_step, scaler, future_steps=30):
    last_data = scaled_data[-time_step:]
    future_predictions = []

    for _ in range(future_steps):
        last_data_reshaped = last_data.reshape(1, time_step, 1)
        predicted_value = model.predict(last_data_reshaped)
        future_predictions.append(predicted_value[0, 0])
        last_data = np.append(last_data[1:], predicted_value, axis=0)

    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
    return future_predictions


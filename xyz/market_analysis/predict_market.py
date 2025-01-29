import matplotlib.pyplot as plt
import pandas as pd
import prepare_data
from xyz.market_analysis.prepare_data import build_model, prepare_data, predict_future, create_dataset

X, Y, scaled_data, scaler, time_step, close_data, ticker_symbol, data = prepare_data('AAPL',
                                                                                     '2020-01-01',
                                                                                     '2024-11-05')
model = build_model(X)
model.fit(X, Y, epochs=50, batch_size=32, verbose=1)
future_steps = 180  # Number of steps to predict into the future

def predict_market():
    train_size = int(len(scaled_data) * 0.8)
    test_data = scaled_data[train_size - time_step:]

    X_test, Y_test = create_dataset(test_data, time_step)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)

    prediction_indices = data.index[train_size:]

    plt.figure(figsize=(10, 5))
    plt.plot(data.index[train_size:], close_data[train_size:], label='Actual Price')
    plt.plot(prediction_indices, predictions, label='Predicted Price')
    plt.title(f'{ticker_symbol} Stock Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()


def predict_future_market():
    # Predict future values
    future_predictions = predict_future(model, scaled_data, time_step, scaler, future_steps)

    # Plotting the results
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, close_data, label='Actual Price')
    future_indices = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=future_steps, freq='B')
    plt.plot(future_indices, future_predictions, label='Future Predictions', linestyle='--')
    plt.title(f'{ticker_symbol} Stock Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.tight_layout()  # Adjust layout
    plt.grid(True)  # Add grid for better readability
    plt.show()


predict_market()
predict_future_market()
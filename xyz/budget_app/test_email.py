import requests
import os

def test_email_processing():
  # URL of your Flask application
  url = 'http://localhost:5000/receive_email'

  # Test PDF file path
  pdf_path = 'paystubs/Paystub1.pdf'  # Update this path

  # Simulate email data
  email_data = {
      'sender': 'alex@example.com',
      'subject': 'Test Paystub Email'
  }

  # Prepare the file
  files = {
      'attachment': ('test_paystub.pdf', open(pdf_path, 'rb'), 'application/pdf')
  }

  # Send the request
  response = requests.post(url, data=email_data, files=files)

  # Print the response
  print(f"Status Code: {response.status_code}")
  print(f"Response: {response.text}")

  # Check the email log
  log_response = requests.get('http://localhost:5000/email-log')
  print("\nEmail Log:")
  print(log_response.json())

if __name__ == "__main__":
  test_email_processing()
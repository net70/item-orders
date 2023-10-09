from locust import HttpUser, task, between
from time import sleep

class MyUser(HttpUser):
    wait_time = between(1, 3)  # Define wait times between requests

    @task
    def make_request_with_payload(self):
        # Define your payload data as a dictionary
        payload = {
            'user_id': None,
            'first_name': 'nate',
            'last_name': 'maymon',
            'email': 'net7000man@gmail.com',
            'items': [
                {'item_id': '1', 'quantity': 1, 'price': 1.0}, 
                {'item_id': '2', 'quantity': 2, 'price': 2.0}, 
                {'item_id': '3', 'quantity': 3, 'price': 3.0}
            ],
            'total_cost': 6.0,
            'discount': 0.5
        }

        # Define the URL you want to test
        url = "http://localhost:8080/confirm_order/"

        # Define header
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'Content-Type': 'application/json'
        }

        # Send a POST request with the payload
        response = self.client.post(url, json=payload, headers=headers)
        sleep(3)

    # @task
    # def make_get_request(self):
    #     # Define the URL for a GET request
    #     url = "/another-api-endpoint"

    #     # Send a GET request
    #     response = self.client.get(url)

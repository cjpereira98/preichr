import requests

class SlackIntegration:
    @staticmethod
    def send_message(url, msg):
        """
        Sends a message to a Slack channel using a webhook URL.
        
        :param url: The Slack webhook URL.
        :param msg: The message to be sent to the Slack channel.
        :return: Response from the Slack API.
        """
        payload = msg

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")

        return response.text

# Example usage
if __name__ == "__main__":
    webhook_url = 'https://hooks.slack.com/services/your/webhook/url'
    message = 'Hello from SlackIntegration!'
    SlackIntegration.send_message(webhook_url, message)

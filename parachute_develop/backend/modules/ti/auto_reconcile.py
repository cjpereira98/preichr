import os
import sys
# Add the parent directory to the system path to allow importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from integrations.aft_transship_hub import AFTTransshipHubIntegration

def main():
    # Read the shipment IDs from reconciles.txt
    with open('reconciles.txt', 'r') as file:
        shipment_ids = file.read().splitlines()

    # Create an instance of the integration class
    aft_integration = AFTTransshipHubIntegration()

    # Close all shipment IDs with a single driver instance
    aft_integration.close_shipments(shipment_ids)

if __name__ == "__main__":
    main()

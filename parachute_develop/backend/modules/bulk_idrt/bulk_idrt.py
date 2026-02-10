import os
import sys
# Add the parent directory to the system path to allow importing integrations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from integrations.idrt import IDRTIntegration

def read_pallet_ids(file_path):
    """
    Read pallet IDs from the specified file.
    """
    try:
        with open(file_path, 'r') as file:
            pallet_ids = [line.strip() for line in file if line.strip()]
        return pallet_ids
    except Exception as e:
        print(f"Error reading pallet_ids.txt: {e}")
        return []

if __name__ == "__main__":
    # Path to the pallet_ids.txt file
    file_path = os.path.join(os.path.dirname(__file__), 'pallet_ids.txt')

    # Read pallet IDs from the file
    pallet_ids = read_pallet_ids(file_path)

    # Initialize the IDRT integration
    idrt_integration = IDRTIntegration()

    # Destination ID
    destination_id = "dz-P-StopLosingPallets"

    # Process all pallet IDs with the destination ID
    if pallet_ids:
        idrt_integration.process_pallets(pallet_ids, destination_id)
    else:
        print("No pallet IDs found in pallet_ids.txt.")

    # Close the driver after processing
    idrt_integration.close()

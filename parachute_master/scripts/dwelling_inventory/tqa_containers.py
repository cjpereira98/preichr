import os
import sys
import pandas as pd

# Add the parent directory to the system path to allow importing integrations within ampy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ampy.integrations.tqa import TQAIntegration

def read_container_data(filename):
    df = pd.read_csv(filename)
    return df['Container'].tolist()

if __name__ == "__main__":
    container_file = 'tqa_containers.csv'
    if os.path.exists(container_file):
        container_ids = read_container_data(container_file)
        tqa = TQAIntegration()
        tqa.tqa_containers(container_ids)
    else:
        print(f"{container_file} does not exist.")
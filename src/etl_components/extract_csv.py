import os
import pandas as pd
import json
import sys

from logger import logging
from exceptions import CustomError

from dataclasses import dataclass

@dataclass
class CSVExtractorConfig:
    train_csv_path : str = os.path.join("artifacts", "data", "train.csv")
    test_csv_path : str = os.path.join("artifacts", "data", "test.csv")

class CSVExtractor:
    def __init__(self):
        self.csvConfig = CSVExtractorConfig()

    def extract_csv(self):
        try:
            train_data = pd.read_csv(self.csvConfig.train_csv_path)
            logging.info("Training data successfully extracted from CSV.")
            
            test_data = pd.read_csv(self.csvConfig.test_csv_path)
            logging.info("Testing data successfully extracted from CSV.")
            
            return train_data, test_data
        
        except Exception as e:
            raise CustomError(str(e))


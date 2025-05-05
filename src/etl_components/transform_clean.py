import re
import os
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from logger import logging
from exceptions import CustomError

class CSVTransformerConfig:
    reference_data_path = os.path.join("artifacts", "data", "OpenDataSoft.csv")

class CSVTransformer:
    
    luxury_brands = [
    'Acura', 'Alfa', 'Aston', 'Audi', 'Bentley', 'BMW', 'Bugatti', 'Cadillac',
    'Ferrari', 'Genesis', 'INFINITI', 'Jaguar', 'Karma', 'Land', 'Lexus', 'Lincoln',
    'Lucid', 'Maserati', 'Maybach', 'McLaren', 'Mercedes-Benz', 'Porsche',
    'Polestar', 'Rolls-Royce', 'Rivian', 'Lotus', 'Lamborghini', 'Tesla', 'Volvo',
    'Saab'
    ]
    
    economy_brands = [
        'Buick', 'Chevrolet', 'Chrysler', 'Dodge', 'FIAT', 'Ford', 'GMC', 'Honda',
        'Hyundai', 'Jeep', 'Kia', 'Mazda', 'Mitsubishi', 'Nissan', 'Plymouth',
        'Pontiac', 'RAM', 'Saturn', 'Scion', 'smart', 'Subaru', 'Suzuki'
    ]
    
    borderline_brands = [
        'MINI', 'Volkswagen', 'Tesla', 'Buick', 'Lincoln'
    ]
    
    def __init__(self, train_data, test_data):
        
        self.transformerConfig = CSVTransformerConfig()
        self.train_data = train_data
        self.test_data = test_data
        
    def classify_segment(self, brand):
        if brand in self.luxury_brands:
            return 'Luxury'
        elif brand in self.economy_brands:
            return 'Economy'
        elif brand in self.borderline_brands:
            return 'Borderline'
        else:
            return 'Unknown'
        
    def baseModel_extraction(self, df, threshold=0.3):
        
        self.reference_data = pd.read_csv(self.transformerConfig.reference_data_path)
        logging.info("Reference data loaded from OpenDataSoft.")
        
        try:
            df['model'] = df['model'].astype(str).apply(lambda x: re.sub(r'(\d+)\s+i\b', r'\1i', x, flags=re.IGNORECASE))
            df['model'] = df['model'].astype(str).apply(lambda x: re.sub(r'(?<=\w)-(?=\w)', '', x))

            texts1 = df['model'].unique().tolist()
            texts2 = self.reference_data['Model'].astype(str).unique().tolist()

            vectorizer = TfidfVectorizer().fit(texts1 + texts2)
            tfidf_matrix1 = vectorizer.transform(texts1)
            tfidf_matrix2 = vectorizer.transform(texts2)

            cosine_sim = cosine_similarity(tfidf_matrix1, tfidf_matrix2)
            best_match_indices = cosine_sim.argmax(axis=1)
            similarity_scores = cosine_sim.max(axis=1)
            best_matches = [texts2[i] for i in best_match_indices]

            model_to_base_model_lookup = self.reference_data.drop_duplicates('Model').set_index('Model')['baseModel'].to_dict()

            match_df = pd.DataFrame({
                'original_model': texts1,
                'matched_Model': best_matches,
                'matched_baseModel': [model_to_base_model_lookup.get(m, '') for m in best_matches],
                'similarity_score': similarity_scores
            })

            filtered_matches = match_df[match_df['similarity_score'] >= threshold]
            model_to_base_model = dict(zip(filtered_matches['original_model'], filtered_matches['matched_baseModel']))

            df['baseModel'] = df['model'].map(model_to_base_model)
            logging.info(f"Base model mapping applied. {len(filtered_matches)} matched over {threshold} threshold.")
            return df
        except Exception as e:
            logging.error(f"Error during model mapping: {e}")
            raise CustomError(str(e))
        
    def generate_engine_attributes(self, df):
        try:
            # Normalize 'liter' to 'L'
            df['engine'] = df['engine'].astype(str).str.replace(
                r'(\d+(?:\.\d+)?)\s*liter', r'\1L', flags=re.IGNORECASE, regex=True
            )

            engine_series = df['engine']

            # Extract features
            df['horsePower'] = engine_series.str.extract(r'(\d+(?:\.\d+)?)\s*hp', flags=re.IGNORECASE)[0]
            df['horsePower'] = df['horsePower'].combine_first(
                engine_series.str.extract(r'/(\d{2,4})$', flags=re.IGNORECASE)[0]
            )

            df['displacement'] = engine_series.str.extract(r'(\d+(?:\.\d+)?)\s*[lL]', flags=re.IGNORECASE)

            df['battery_spec'] = engine_series.str.extract(r'(\d+(?:\.\d+)?(?:V|kW|Ah))', flags=re.IGNORECASE)

            df['fuel_type'] = engine_series.str.extract(
                r'\b(Electric|Diesel|Gasoline|Hybrid|Hydrogen|Flex|Flexible|Unleaded|Plug-In|Gas/Electric|Electric/Gas|Gasoline/Mild|Mild)\b',
                flags=re.IGNORECASE
            )

            df['boost_type'] = engine_series.str.findall(
                r'\b(Turbo|Twin Turbo|Supercharged|T/C|GTDI|Intercooled|SC|Dual)\b', flags=re.IGNORECASE
            ).apply(lambda x: ' '.join(sorted(set(map(str.upper, x)))) if x else None)

            # Cylinder type
            cyl_from_config = engine_series.str.extract(r'\b(V[0-9]{1,2}|I[0-9]{1,2}|W[0-9]{1,2}|H[0-9]{1,2})\b', flags=re.IGNORECASE)
            cyl_from_cylinder = engine_series.str.extract(r'(\S+)\s+Cylinder', flags=re.IGNORECASE)

            df['cylinder_type'] = cyl_from_config[0].combine_first(cyl_from_cylinder[0])
            df['cylinder_type'] = df['cylinder_type'].str.upper()
            df['cylinder_type'] = df['cylinder_type'].apply(
                lambda x: f"V{x}" if pd.notna(x) and x.isdigit() else x
            )
            df['cylinder_type'] = df['cylinder_type'].fillna('Unknown')

            # Convert numerics
            df['horsePower'] = pd.to_numeric(df['horsePower'], errors='coerce')
            df['displacement'] = pd.to_numeric(df['displacement'], errors='coerce')
            df['boost_type'] = df['boost_type'].fillna('Naturally Aspirated')

            logging.info(f"Engine attribute extraction completed successfully, Shape {df.shape}")
            
            return df.drop(['clean_title', 'id'], axis = 1)

        except Exception as e:
            logging.error(f"Error during engine attribute extraction: {e}")
            raise CustomError(str(e))


    def transform(self):
        try:
            self.train_data['car_segment'] = self.train_data['brand'].apply(self.classify_segment)
            logging.info("Brand segmentation applied on training data.")
            
            self.test_data['car_segment'] = self.test_data['brand'].apply(self.classify_segment)
            logging.info("Brand segmentation applied on testing data.")
            
            self.train_data = self.baseModel_extraction(self.train_data)
            logging.info("Base Model Transformation applied on training data.")
            
            self.test_data = self.baseModel_extraction(self.test_data)
            logging.info("Base Model Transformation applied on testing data.")
            
            self.train_data = self.generate_engine_attributes(self.train_data)
            logging.info("Engine attributes generated from training data.")
            
            self.test_data = self.generate_engine_attributes(self.test_data)
            logging.info("Engine attributes generated from testing data.")
            
            return self.train_data, self.test_data
        
        except Exception as e:
            logging.error(f"Error in transformation: {e}")
            raise CustomError(str(e))
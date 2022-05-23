import argparse
import json
import pandas as pd
import os
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, recall_score, 
    plot_confusion_matrix, precision_score, plot_roc_curve
)
from joblib import dump

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input-file', type=str, default=os.environ.get('INPUT-FILE'))
    parser.add_argument('input-path', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
    parser.add_argument('output-path', type=str, default=os.environ['SM_MODEL_DIR'])
    parser.add_argument('y-column', type=list, default=os.environ.get('Y_COLUMN'))
    parser.add_argument('drop-column', type=list, default=os.environ.get('DROP_COLUMN'))
    parser.add_argument('test-size', type=float, default=os.environ.get('TEST_SIZE'))
    parser.add_argument('estimators', type=int, default=os.environ.get('SM_HP_ESTIMATORS'))
    parser.add_argument('model-file', type=str, default=os.environ.get('MODEL_FILE'))


    args, _ = parser.parse_known_args()    
    return args
        
class CreditUser:

    def __init__(self) -> None:
        self.x = None
        self.y = None
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None
        self.x_val = None
        self.y_val = None
    
    def load_dataset(self, input_path: str , input_file: str,  y_column : list, drop_column: list) -> None:

        df = pd.read_parquet(os.path.join(input_path, input_file))

        df.fillna(0, inplace=True)

        self.y = df[y_column].astype('int')

        drop_column = drop_column + y_column

        self.x = df.drop(drop_column , axis=1, inplace=True)
    
    def split_dataset (self, test_size: float) -> None:
         self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x,self.y, 
                                                    stratify=self.y, test_size=test_size,
                                                    random_state = 123)

    def over_sampling(self) -> None:

        self.x_train, self.y_train = SMOTE().fit_resample(self.x_train, self.y_train)

        self.x_train = pd.DataFrame(self.x_train, columns=self.x.columns)

    

    
def main():

    args = parse_args()

    dataset = CreditUser()
    dataset = dataset.load_dataset(args.input_path, args.input_file, args.y_column, args.drop_column)
    dataset = dataset.split_dataset(args.test_size)

    model = RandomForestClassifier(n_estimators=args.estimators)

    model.fit(dataset.x_train , dataset.y_train )

    y_predict = model.predict(dataset.x_test)

    metrics = {}
    metrics['accuracy_score'] = accuracy_score(dataset.y_test, y_predict)
    metrics['precision_score'] = precision_score(dataset.y_test, y_predict)
    metrics['recall_score'] = recall_score(dataset.y_test, y_predict)

    with open('model-metrics.json' , 'w', encoding = 'utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)

    cfm_plot = plot_confusion_matrix(model, dataset.x_test, dataset.y_test)
    cfm_plot.savefig("confusion_matrix.png")  
    crc_plot = plot_roc_curve(model, dataset.x_test, dataset.y_test)
    cfm_plot.savefig("roc_curve.png")  

    dump(model, args.model_file) 

if __name__=='__main__':
    

    main()
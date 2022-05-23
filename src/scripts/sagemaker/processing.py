import argparse
import pandas as pd
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-file', type=str)
    parser.add_argument('--output-file', type=str)
    parser.add_argument('--input-path', type=str, default= '/opt/ml/processing/input')
    parser.add_argument('--output-path', type=str, default= '/opt/ml/processing/output')
    args, _ = parser.parse_known_args()    
    return args

def main():
    args = parse_args()

    df = pd.read_csv(os.path.join(args.input_path, args.data_file))

    df = df.sort_values(by=["id", "loan_date"]).reset_index(drop=True)

    df["loan_date"] = pd.to_datetime(df["loan_date"])

    df["nb_previous_loans"] = df.groupby("id")["loan_date"].rank(method="first") - 1

    df['avg_amount_loans_previous'] = (df.groupby('id')['loan_amount'].apply(lambda x: x.shift().expanding().mean()))

    df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce')

    df['age'] = (pd.to_datetime('today').normalize() - df['birthday']).dt.days // 365

    df['job_start_date'] = pd.to_datetime(df['job_start_date'], errors='coerce')

    df['years_on_the_job'] = (pd.to_datetime('today').normalize() - df['job_start_date']).dt.days // 365

    df['flag_own_car'] = df['flag_own_car'].apply(lambda x : 0 if x == 'N' else 1)

    df = df[['id', 'age', 'years_on_the_job', 'nb_previous_loans', 'avg_amount_loans_previous', 'flag_own_car', 'status']]

    df.to_parquet(os.path.join(args.output_path, args.output_file), index=False)    


if __name__=='__main__':

    main()
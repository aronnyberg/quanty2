import pandas as pd
import time
import datetime as dt

def pull_data(tickers, datecodes):
    failed_instruments = []
    for instrument in tickers:
        temp_dict = {}
        for datecode in datecodes:
            try:
                df = pd.read_csv(f"https://download.gatedata.org/spot/deals/{datecode}/{instrument}-{datecode}.csv.gz", compression='gzip', header=0, sep=',', quotechar='"')
                df.columns = ["timestamp", "dealid", "price", "amount", "side"]
                df['timestamp'] = df['timestamp'].apply(lambda x: dt.datetime.fromtimestamp(x).strftime('%Y-%m-%d-%H-%M'))
                df.to_csv(f"/Users/aronnyberg/code/quanty2/gateio_data/major_trade_data/{instrument}-{datecode}")
                time.sleep(2)
                print(f"{instrument}-{datecode} succeeded")
            except:
                failed_instruments.append(instrument)
                print(f"{instrument}-{datecode} failed")
                time.sleep(2)
    print(failed_instruments)
    with open('/Users/aronnyberg/code/quanty2/failed_downloads.txt', 'w') as outfile:
        outfile.write('\n'.join(str(i) for i in failed_instruments))

def datecodes_generator(start_month, end_month):
    datecode_list = []
    start_month = int(start_month)
    end_month = int(end_month)
    while start_month <= end_month:
        datecode_list.append(str(start_month))
        if start_month[-2:] == 12:
            start_month = (start_month[:4]*100)+1
        else:
            start_month +=1
    return datecode_list

'''/*
    Author : saj1919@hotmail.com
    Task : Stock market analysis
    DATA FORMAT :  ['Date' 'Open' 'High' 'Low' 'Last' 'Close' 'Total Trade Quantity' 'Turnover (Lacs)']
*/'''

import Quandl, traceback, operator
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import log
import pickle

class Stock_Analyzer:
    def __init__(self, company_code_file):
        self.auth_code = "H-NTSq6HZJqTQ_mAQH6f"
        self.company_codes = self.load_company_codes(company_code_file)
        self.file_df_nse = self.load_file_df("NSE")
        self.file_df_bse = self.load_file_df("BSE")
        
        print "\t\t\"Stock Trend Analyzer Tool v1.0\""
        print "\t\t\t\"by Swapnil Jadhav\""
        print "\n\tLoaded %s company codes (NSE and BSE)\n\n" % len(self.company_codes)
        print "\tOld NSE Data : %s, Old BSE Data : %s" % (len(self.file_df_nse), len(self.file_df_bse))
        
    def load_file_df(self, stock):
        temp_dict = {}
        for company, codes in self.company_codes.iteritems():
            try:
                if codes[stock.lower()] != "":
                    df = pickle.load(open("../data/%s/%s_%s" % (stock, stock, company), "r" ))
                    temp_dict["%s_%s"%(stock,company)] = df
            except:
                continue
        return temp_dict
    
    def load_company_codes(self, company_code_file):
        temp_company_codes = {}
        fr = open(company_code_file, 'r')
        for line in fr:
            parts = line.strip().split('\t')
            if len(parts) == 3:
                temp_company_codes[parts[0].strip()] = {'bse' : parts[1].strip(), 'nse' : parts[2].strip()}
            elif len(parts) == 2:
                temp_company_codes[parts[0].strip()] = {'bse' : parts[1].strip(), 'nse' : ""}
            else:
                pass
        fr.close()
        return temp_company_codes
    
    def get_KLD_score(self, ts):
        ts_list = np.array(ts['Close'].tolist())
        ts_list = ts_list[np.isfinite(ts_list)]
        ts_avg = ts_list.mean()
        
        ts_list = [(x/ts_avg) for x in ts_list]
        num = len(ts_list)
        
        decay_step = 100.0/num
        curr_decay = decay_step
        kld_score = 0
        for i in range(len(ts_list)-1):
            tmp_score = ts_list[i]*log(ts_list[i]/ts_list[i+1])*curr_decay/100.0
            curr_decay += decay_step
            kld_score += tmp_score
            # print i,ts_list[i],tmp_score
        if len(ts_list) == 1: return ts_avg
        return kld_score
        
    def download_save_quandle_data(self):
        cnt = 0
        for company, codes in self.company_codes.iteritems():
            if cnt < 100: cnt += 1
            else: break
            
            try:
                print "Processing %d %s-%s" % (cnt,company,codes)
                if codes['nse'] != "":
                    df = Quandl.get("NSE/"+codes['nse'], authtoken=self.auth_code)
                    pickle.dump(df, open( "../data/NSE/NSE_%s" % company, "w"))
                if codes['bse'] != "":
                    df = Quandl.get("XBOM/"+codes['bse'], authtoken=self.auth_code)
                    pickle.dump(df, open( "../data/BSE/BSE_%s" % company, "w"))                
            except:
                continue
    
    def get_market_trend(self, start_date, end_date, stock_market, time_window, data_type):
        company_score = {}
        cnt = 0
        for company, codes in self.company_codes.iteritems():
            try:          
                if stock_market == "NSE": company_code = codes['nse']
                elif stock_market == "BSE": company_code = codes['bse']
                else: return
                
                if company_code == "":
                    continue
                
                if data_type == "new" and cnt>10:break
                cnt+=1                
                
                if data_type == "new":
                    df = Quandl.get(stock_market+"/"+company_code, authtoken=self.auth_code)
                else:
                    if stock_market == "NSE": df = self.file_df_nse["%s_%s"%(stock_market,company)]
                    elif stock_market == "BSE": df = self.file_df_bse["%s_%s"%(stock_market,company)]
                df.fillna(0, inplace=True)
                ts = df.iloc[:,[4]]
                idx = pd.date_range(start_date, end_date)
                ts.index = pd.DatetimeIndex(ts.index)                
                ts = ts.reindex(idx, fill_value=float('nan'))
                if time_window == "w":
                    ts = ts.resample('W', how='mean')
                elif time_window == "m":
                    ts = ts.resample('M', how='mean')
                elif time_window == "q":
                    ts = ts.resample('Q', how='mean')
                elif time_window == "y":
                    ts = ts.resample('A', how='mean')                
                kld_score = self.get_KLD_score(ts)
                company_score[company] = kld_score
            except:
                continue
        sorted_company_score = sorted(company_score.items(), key=operator.itemgetter(1))
        
        print "\n\tTop Trending"
        for key, val in sorted_company_score[:5]:
            print "\t%20s%20s" % (key,val)
        
        print "\n\tBottom Trending"
        for key, val in sorted_company_score[-5:]:
            print "\t%20s%20s" % (key,val)
        
    def analyze_stock(self, stock_market, company_code):
        df = Quandl.get(stock_market+"/"+company_code, authtoken=self.auth_code)
        df.fillna(0, inplace=True)
        
        while True:
            print "\n\t1 : Check Time Series Graph"
            print "\t2 : Exit"
            user_input = raw_input("\t").strip()
            if user_input == "1":
                start_date = raw_input("\tStart Date [Format : mm-dd-yyyy] : ").strip()
                end_date = raw_input("\tEnd Date [Format : mm-dd-yyyy] : ").strip()
                
                ts = df.iloc[:,[4]]
                idx = pd.date_range(start_date, end_date)
                ts.index = pd.DatetimeIndex(ts.index)                
                ts = ts.reindex(idx, fill_value=float('nan'))  
                
                print "\n\t\t1 : Day vs Stock Value Graph (DEFAULT)"
                print "\t\t2 : Week vs Stock Value Graph"
                print "\t\t3 : Month vs Stock Value Graph"
                print "\t\t4 : Quarter vs Stock Value Graph"
                print "\t\t5 : Year vs Stock Value Graph"
                user_input = raw_input("\t\t").strip()
                
                if user_input == "2":
                    ts = ts.resample('W', how='mean')
                elif user_input == "3":
                    ts = ts.resample('M', how='mean')
                elif user_input == "4":
                    ts = ts.resample('Q', how='mean')
                elif user_input == "5":
                    ts = ts.resample('A', how='mean')
                
                self.get_KLD_score(ts)
                
                myplot = ts.plot(legend=False)
                myplot.set_ylabel('Stock Closing Prices')
                myplot.set_xlabel('Date Axis')
                plt.show()
                            
            elif user_input == "2":
                break

   
if __name__ == "__main__":
    obj = Stock_Analyzer("../data/company_codes.txt")
    
    while True:
        try:
            print "\n1 : Check Company Stock Analysis"
            print "2 : Check Trends"
            print "3 : Download & Save Quandle Data"
            print "4 : Exit"
            user_input = raw_input().strip()
            
            if user_input == "1":
                stock_market = raw_input('Enter Market Name : ').strip()
                company_code = raw_input('Enter Company Code : ').strip()
                obj.analyze_stock(stock_market, company_code)
            elif user_input == "2":
                start_date = raw_input("Start Date [Format : mm-dd-yyyy] : ").strip()
                end_date = raw_input("End Date [Format : mm-dd-yyyy] : ").strip()
                stock_market = raw_input('Enter Market Name (NSE or BSE): ').strip()
                time_window = raw_input('Enter analysis window type\ndaily-d, weekly-w, monthly-m, quarterly-q, yearly-y : ').strip()
                data_type = raw_input('Enter Data Type (new or old): ').strip()
                obj.get_market_trend(start_date, end_date, stock_market, time_window, data_type)
            elif user_input == "3":
                obj.download_save_quandle_data()
            elif user_input == "4":
                break
            else:
                print "ENTER CORRECT OPTION"
        except:
            continue
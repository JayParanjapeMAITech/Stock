from lxml import html
import requests
import time
import multiprocessing

# logging
import logging
logging.basicConfig(filename='log/exception_logging.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

from company_page import CompanyPage
from balance_sheet import BalanceSheet
from ratio_module import Ratio

def get_company_primary_stats(company, tree):
    pe_ratio = company.get_pe_ratio(tree)
    eps = company.get_eps(tree)
    price_of_stock = company.get_price_of_stock(tree)
    fifty_two_wk_high = company.get_fifty_two_wk_high(tree)
    fifty_two_wk_low = company.get_fifty_two_wk_low(tree)
    return {'pe_ratio': pe_ratio, 'eps': eps, 'price_of_stock': price_of_stock, 'fifty_two_wk_high': fifty_two_wk_high, 'fifty_two_wk_low': fifty_two_wk_low}

def company_page_analysis(stock_company):
    try:
        page = requests.get('http://money.rediff.com/%s' % stock_company)
        time.sleep(2)
        tree = html.fromstring(page.content)
        company = CompanyPage(tree)
        primary_stats = get_company_primary_stats(company, tree)
        if all([primary_stats.get('pe_ratio') > 0, primary_stats.get('pe_ratio') < 15, primary_stats.get('eps') > 0, primary_stats.get('price_of_stock') < ((primary_stats.get('fifty_two_wk_high') + primary_stats.get('fifty_two_wk_low'))/2)]):
        
        
            #get all links
            balance_sheet_link = company.get_balance_sheet_link(tree)
            dividend_link = company.get_dividend_link(tree)
            ratio_link = company.get_ratio_link(tree)
        
            # go to balance sheet page for further analysis
            balance_sheet_page = requests.get('%s' % ''.join(balance_sheet_link))
            balance_sheet_tree = html.fromstring(balance_sheet_page.content)
            balance_sheet = BalanceSheet(balance_sheet_tree)
            current_assets_loans_advances = balance_sheet.get_current_assets_loans_advances(balance_sheet_tree)
            current_liabilities_and_provisions = balance_sheet.get_current_liabilities_and_provisions(balance_sheet_tree)
            total_net_current_assets = balance_sheet.get_total_net_current_assets(balance_sheet_tree)
            if total_net_current_assets > current_liabilities_and_provisions:
                # go to ratio page
                ratio_page = requests.get('%s' % ''.join(ratio_link))
                ratio_tree = html.fromstring(ratio_page.content)
                ratio = Ratio(ratio_tree)
                if ratio.exists_dividend(ratio_tree):
                    print stock_company
                    
    except Exception as err:
        logger.error(err)
        
                
    return

if __name__ == '__main__':
    stock_companies = ["Amtek-Auto-Ltd", "Chambal-Fertilisers-Chemicals-Ltd"]
    companies_to_invest = []
    for stock_company in stock_companies:
        # print "operating on company", stock_company
        # companies_to_invest.append(company_page_analysis(stock_company))
        p = multiprocessing.Process(target=company_page_analysis, args=(stock_company,))
        companies_to_invest.append(p)
        p.start()
    print companies_to_invest
    

# if __name__ == '__main__':
    # main()
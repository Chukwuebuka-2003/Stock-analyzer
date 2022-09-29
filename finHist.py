#use pip on your terminal to install these packages
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import json

import yahoo_fin.stock_info as si

stockTicker = str(input('What is your desired stock:'))

print("")

stockTicker = stockTicker

ap = yf.Ticker(stockTicker)

stock_info = yf.Ticker(stockTicker).info

#get the outstanding shares

outstandShares = ap.info['sharesOutstanding']

print('The total shares of', stockTicker, 'is',outstandShares)

years = 3

polygon_api_key= 'USE YOUR OWN POLYGON API KEY'

stock_split_adjustment_minimum = 3


#get the Cummulative Annual Growth Rate (CAGR) of the stock
cagr = si.get_analysts_info(stockTicker)['Growth Estimates'][stockTicker][4]

print('The CAGR of', stockTicker, 'is', cagr)


#Now here's the tough work

#get the financials data


financials = ap.financials
cashFlow = ap.cashflow

total_cash_from_operating_activities = cashFlow.loc['Total Cash From Operating Activities']

capital_expenditure = cashFlow.loc['Capital Expenditures'] #get the capital expenditure

net_income = ap.financials.loc['Net Income']#get the net income statement

beta = ap.info['beta']#get the beta

income_tax_expense = ap.financials.loc['Income Tax Expense'] #get the income tax expense

market_cap = ap.info['marketCap'] #get the stock market cap

total_debt = ap.balance_sheet.loc['Total Current Liabilities'] #get the debt of the stock

income_before_tax = ap.financials.loc['Ebit']

print(stockTicker,'EBIT is',income_before_tax)

total_revenue = ap.financials.loc['Total Revenue']

shares_outstanding = ap.info['sharesOutstanding']

total_assets = ap.balance_sheet.loc['Total Current Assets']

current_year = datetime.now().year


#FCF = total cash from operating activities - capex + net borrowings

fcf= {}

for i in range(years+1):
    total_cash = total_cash_from_operating_activities[i]
    capex = capital_expenditure[i]

    net borrowings = financials.loc['Net Borrowings'][i]

    fcf[current_year - i] = total_cash + capex


print(stockTicker, 'net borrowings are', net borrowings)
#fcf to net income

fcf_to_net_income = { }

for i in range(1,years +1):
    year = current_year - i
    fcf_to_net_income[year] = fcf[year + i]/net_income[i]


print(fcf_to_net_income)


#Calculate the Quick float of a stock

quick_float = total_assets/total_debt

print(stockTicker, 'Quick Floats are',quick_float)



#Net profit margin

npm = net_income/total_revenue

print(stockTicker,'Net Profit Margins are',npm)


#Return on assets

roa = net_income/total_assets

print(stockTicker,'Return On Asset Investment',roa)


#Earnings per share of a stock

eps = total_cash_from_operating_activities/shares_outstanding

print(stockTicker,'Earnings per share', eps)



# Project future FCF

# We're trying to average past free cash flow growth
index = 0

past_growth = []

# Reverse To Get Oldest First

# Old not using FCF / Net Income
# for key, value in sorted(list(fcf.items()), key=lambda x:x[0], reverse=False):
# New
for key, value in sorted(list(fcf_to_net_income.items()), key=lambda x:x[0], reverse=False):
    if index == years: break 
    year = fcf[key]
    next_year = fcf[key + 1]
    current_growth = year / next_year * 100
    past_growth.append(current_growth)
    index += 1

fcf_growth_rate = 0.0
for past in past_growth: fcf_growth_rate += past
fcf_growth_rate /= years

print(stockTicker,' Average Growth Rate: ', str(round(fcf_growth_rate)) , '%')


# Project Revenue Growth Based On Net Income Margins
print(net_income)

list(net_income.keys())[i]
net_income_margins = {}

for i in range(1, years + 1):
    current_net_income = net_income[list(net_income.keys())[i]]
    current_revenue = total_revenue[list(total_revenue.keys())[i]]
    current_margin = current_net_income / current_revenue
    net_income_margins[current_year - i] = current_margin

# Calculate Average Net Income Growth Rate
net_income_growth_rate = 0.0
for year in net_income_margins:
    net_income_growth_rate += net_income_margins[year]
net_income_growth_rate /= years

net_income_growth_rate
print(stockTicker, ' Average Net Income Growth Rate: ' , str(round(net_income_growth_rate * 100)) , '%')



# Project future cash flow with past average growth rate

last_year_fcf = fcf[list(fcf.keys())[0]]
print(last_year_fcf, 'last year')

# future_fcf = {}

# Should we use FCF to Income or Net Income Margin

for i in range(years + 1):
    if(i == 0): continue
    current_fcf = current_fcf = last_year_fcf + last_year_fcf * (net_income_growth_rate)
    fcf[current_year + i] = current_fcf
    last_year_fcf = current_fcf

print(fcf)


cost_of_debt = 1 - (income_tax_expense[0] / income_before_tax[0])
weight_of_debt = total_debt[0] / (total_debt[0] + market_cap) * 100
weight_of_equity = 100 - (total_debt[0] / (total_debt[0] + market_cap) * 100)

capm = 0.025 + beta * (0.10 - 0.0232)
ror = (weight_of_debt * (1 - cost_of_debt) + weight_of_equity * capm)

print(stockTicker, 'cost of debt',str(round(cost_of_debt*100))  , '%')
print(stockTicker, ' weight of debt is', weight_of_debt, '%')


print(stockTicker, 'weight of equity is', weight_of_equity, '%')











# Calculate WACC using CAPM
cost_of_debt = 1 - (income_tax_expense[0] / income_before_tax[0])
weight_of_debt = total_debt[0] / (total_debt[0] + market_cap) * 100
weight_of_equity = 100 - (total_debt[0] / (total_debt[0] + market_cap) * 100)
capm = 0.025 + beta * (0.10 - 0.0232)
required_rate_of_return = (weight_of_debt * (1 - cost_of_debt) + weight_of_equity * capm) * 0.01
print(stockTicker,' Required Rate Of Return: ' , str(round(required_rate_of_return * 100)), '%')




#print(shares_outstanding, 'is the total number of outstanding shares')

perpetual_growth_rate = 0.025



# V0 = (FCF0 * (1 + Perpetual Growth Rate)) /  required rate of return //(WAAC)// - perpetual growth rate
terminal_value = (fcf[current_year] * (1 + perpetual_growth_rate)) / required_rate_of_return - perpetual_growth_rate
print('Terminal value is: ', str(terminal_value))


#get the discount fators of the stock
discount_factors = {}

for i in range(0, years + 1):
    year = current_year + i
    discount_factors[year] = (1 + required_rate_of_return)**(i + 1)

print(stockTicker,'discount factors',discount_factors)


projected_values = {}
for year_index in range(0, years + 1):
    year = current_year + year_index
    projected_values[year] = fcf[year] / discount_factors[year]

print(stockTicker,'projected values',projected_values)


total_fair_value = 0.0
for year in projected_values:
    total_fair_value += projected_values[year]

terminal_pv = terminal_value / discount_factors[current_year + years]
total_fair_value += terminal_pv
fair_value_of_equity = total_fair_value / shares_outstanding

print(total_fair_value, 'is the total fair value of',stockTicker)

print(stockTicker,'fair value',fair_value_of_equity)

response = requests.get('https://api.polygon.io/v2/reference/splits/' + stockTicker + '?apiKey=' + polygon_api_key)
content = response.text
stock_splits = pd.DataFrame(json.loads(content)['results'])
print(stock_splits.head())


total_splits = len(stock_splits.index)
if total_splits > 0:
    last_split = datetime.strptime(stock_splits.iloc[0]['exDate'], '%Y-%m-%d')
    if last_split.year >= current_year - stock_split_adjustment_minimum:
        for_factor = stock_splits.iloc[0]['forfactor']
        fair_value_of_equity = total_fair_value / (shares_outstanding / for_factor)
        
        
        
value_formatted = "${:,.1f}". format(fair_value_of_equity)
print(stockTicker, '\'s fair value is ', value_formatted, " a share")


#print(apple.history(period = '5d'))
#print(apple.info['forwardPE'])
#current_price = polygon_api_key(int['Price'])
#print("Current Price: ", current_price)



market_price = stock_info['regularMarketPrice']
previous_close_price = stock_info['regularMarketPreviousClose']
print(stockTicker,'market price ', market_price)
print(stockTicker, 'previous close price is', previous_close_price)
print(stockTicker, "Margin of Safety: ", (1-market_price/fair_value_of_equity)*100 , '%')


print(ap.calendar)

print(beta)
#response = requests.get('https://api.polygon.io/v2/reference/price/' + ticker + '?apiKey=' + polygon_api_key)
#content = response.text
#stock_price =int(content['results'])
#stock_price = pd.DataFrame(json.loads(content)['results'])
#print(stock_price)


# show splits
print(ap.splits)



print(ap.major_holders)

print(ap.institutional_holders)


x = ap.recommendations
x = x[x.index > '2022-06-01']
print(x)








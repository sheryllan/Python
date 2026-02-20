Hi,
 
Thanks for taking the time to do this test.
 
You will need your favourite Python IDE (preferably with Python 3.7 or later) and a git client.
 
There are 3 parts and the suggested times are only estimates, but if you struggle to finish in time, you should write some comments about what’s left to do and/or how you might improve things. You should attempt all questions.

Please think of this as a real world scenario, where the time constraint is absolute and the results are needed by the business. As such, you will need to manage your time such that you will get a result out to the business. 

To reiterate, anything left incomplete, or partially functional, as well as all assumptions and decisions needs to be explained in the comments in the code or via email, and are as crucial as the code itself.

Please restrict your code to using core Python libraries (i.e. no external imports such as pandas).

Once you are done, you should push your result back to github. If you have any issues, you can also send your zipped result to Tech-Test 'at' lmrpartners.com

Unfortunately we won’t be able to provide any assistance during the test, so if you are unsure of anything, just explain in the comments why you chose to do something in a particular way.

---
 
# 1: Position Capture (30 minutes coding)

You will need the following file: tradesUSD.csv (inside this repository)

Traders running their equity strategies independently for the fund wonder what stocks they have made the largest position change to during the day. They have compiled all their trades into one single file and now they are rushing to ask you to help with the rest. Please write python code that reads the supplied csv file, aggregates the trade notional values for each ticker and prints out the ten largest net buy and sell trades to the console. You can assume this code is run very infrequently and manually.
 
# 2: Best execution - Volume Weighted Average Price (30 minutes coding)
You will need the same file as the previous exercise.
You can write this one as an addition to the previous exercise.
Our compliance team has seen the report you created and have concerns whether these trades adhere to our best execution policy. They want a report produced that calculates the VWAP (Volume Weighted Average Price) per ticker for the trades in the supplied csv file and prints out the top 10 trades where the traded price is in percentage terms farther away from the calculated VWAP for that ticker. You can assume this code is run very infrequently and manually.
 
We use the following definitions:

VWAP= SUM( priceUSD * quantity ) / SUM(quantity)

*tip 1: quantity=abs(tradeValueUSD / priceUSD)

*tip 2: if there’s only 1 trade for a particular ticker, VWAP=PriceUSD
 
# 3: PnL Aggregation  (45 minutes coding)
 
In our trading system, a portfolio may contain positions which contribute to pnl. A portfolio may also contain another portfolio (sub/child portfolio).  
 
Take a look through the test classes in the `lmr.test.aggregation` module.
 
The two main classes are:
 
`PortfolioInfo` : Metadata about the portfolio, including its id, name and ids of the sub portfolios

`PortfolioPnl` : Details about the pnl for the positions in a single portfolio. Does not include the pnl from sub portfolios, i.e. it is current unaggregated
 
The TestData class will generate some sample data. The pnl values provided do not include the pnl from sub portfolios. Your task is to aggregate the portfolio hierarchy and print a report (to console) showing the portfolio hierarchy structure (eg, using indentation) along with the aggregated pnl.
 
Eg, if we have portfolios, A, B, C, D and E

| ID | Name | Sub portfolios | Daily Pnl |
| -- | ---- | -------------- | --------- |
| 1  | A | 2 (B), 3 (C) |100 |
| 2  | B | | 300 |
| 3 | C | 4 (D) | 250 |
| 4 | D | | 9 |
| 5 | E | | 140 |
 
Your report should print something like:

```
A – 659
   B – 300
   C – 259
      D - 9
E - 140
```
 
You must not change PortfolioInfo or PortfolioPnl classes, but can modify the Pnl class if you see fit.
 

 
## License

At CodeScreen, we strongly value the integrity and privacy of our assessments. As a result, this repository is under exclusive copyright, which means you **do not** have permission to share your solution to this test publicly (i.e., inside a public GitHub/GitLab repo, on Reddit, etc.). <br>

## Submitting your solution

Please push your changes to the `main branch` of this repository. You can push one or more commits. <br>

Once you are finished with the task, please click the `Submit Solution` link on <a href="https://app.codescreen.com/candidate/7a24aca9-1184-46a1-81c4-89a181bbc38a" target="_blank">this screen</a>.
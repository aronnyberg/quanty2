# These notebooks run a crypto football coin strategy

These notebooks include the full workflow exploring behind a quick-and-dirty crypto quant strategy. I've manually added these notebooks from a private repo.


Strategy Overview:
This strategy shorts football teams' crypto coins in anticipation of matchdays. This strategy extends from the academic literature, which points to the negative performance of football team stock prices on matchdays.
Specifically, this strategy opens a spread trade of buying bitcoin while shorting each football crypto coin on the day preceding each relevant team's football match. Buying bitcoin simultaneously aims to reduce beta, this strategy could be improved by dynamically hedging the beta however in practice, this strategy is difficult to deliver given the need to borrow these small, illiquid coins.

Strategy Performance:
Across 440 observations, the strategy achieves (?) a Sharpe ratio of -0.3. The strategy shows some promise however, given the large recent drawdown in the strategy which potentially could have been improved with risk management features added in.

![image](https://github.com/aronnyberg/quanty2/assets/53857832/0668a0dc-5acc-41b6-add5-d8eb92702a97)

Here the performance is broken down into strategy returns (strat_rets) and the isolated performance of the alpha-generating side (vwap) ie short only. In this case, hedging the crypto risk led to worse returns:

![image](https://github.com/aronnyberg/quanty2/assets/53857832/3ee86156-7d7c-4a08-8000-3238f22bf3d3)



Running the strategy:
1. Step 1 is to download the data, using gateio_download and matches_download

2. Step 2 is to process the data, using gateio_processing

3. Step 3 is to test, using football_test

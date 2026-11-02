# check1: train, status in ['disagree'], 50 of 431 items, seed 20261103

## 1. `AAL/2015/page_183.pdf-4`  (screen: disagree)

**Question:** what is the ratio of the professional fees to the other fees

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1.2` | `11.70588` | `divide(1990, 170)` |

**Gold facts**
- `text_12` as a result , during the year ended december 31 , 2013 , american recorded reorganization charges to adjust estimated allowed claim amounts previously recorded on rejected special facility revenue bonds of $ 180 million , allowed general unsecured claims related to the 1990 and 1994 series of special facility revenue bonds that financed certain improvements at john f .
- `table_5` the other of december 31 2013 is 170 ;

**Table**

|  | december 31 2013 |
| --- | --- |
| labor-related deemed claim ( 1 ) | $ 1733 |
| aircraft and facility financing renegotiations and rejections ( 2 ) ( 3 ) | 320 |
| fair value of conversion discount ( 4 ) | 218 |
| professional fees | 199 |
| other | 170 |
| total reorganization items net | $ 2640 |

<details><summary>Text before the table</summary>

table of contents notes to consolidated financial statements of american airlines , inc . certificate of incorporation ( the certificate of incorporation ) contains transfer restrictions applicable to certain substantial stockholders . although the purpose of these transfer restrictions is to prevent an ownership change from occurring , there can be no assurance that an ownership change will not occur even with these transfer restrictions . a copy of the certificate of incorporation was attached as exhibit 3.1 to a current report on form 8-k filed by aag with the sec on december 9 , 2013 . reorganization items , net reorganization items refer to revenues , expenses ( including professional fees ) , realized gains and losses and provisions for losses that are realized or incurred in the chapter 11 cases . the following table summarizes the components included in reorganization items , net on the consolidated statement of operations for the year ended december 31 , 2013 ( in millions ) : december 31 .
</details>

<details><summary>Text after the table</summary>

( 1 ) in exchange for employees 2019 contributions to the successful reorganization , including agreeing to reductions in pay and benefits , american agreed in the plan to provide each employee group a deemed claim , which was used to provide a distribution of a portion of the equity of the reorganized entity to those employees . each employee group received a deemed claim amount based upon a portion of the value of cost savings provided by that group through reductions to pay and benefits as well as through certain work rule changes . the total value of this deemed claim was approximately $ 1.7 billion . ( 2 ) amounts include allowed claims ( claims approved by the bankruptcy court ) and estimated allowed claims relating to ( i ) the rejection or modification of financings related to aircraft and ( ii ) entry of orders treated as unsecured claims with respect to facility agreements supporting certain issuances of special facility revenue bonds . the debtors recorded an estimated claim associated with the rejection or modification of a financing or facility agreement when the applicable motion was filed with the bankruptcy court to reject or modify such financing or facility agreement and the debtors believed that it was probable the motion would be approved , and there was sufficient information to estimate the claim . ( 3 ) pursuant to the plan , the debtors agreed to allow certain post-petition unsecured claims on obligations . as a result , during the year ended december 31 , 2013 , american recorded reorganization charges to adjust estimated allowed claim amounts previously recorded on rejected special facility revenue bonds of $ 180 million , allowed general unsecured claims related to the 1990 and 1994 series of special facility revenue bonds that financed certain improvements at john f . kennedy international airport ( jfk ) , and rejected bonds that financed certain improvements at chicago o 2019hare international airport ( ord ) , which are included in the table above . ( 4 ) the plan allowed unsecured creditors receiving aag series a preferred stock a conversion discount of 3.5% ( 3.5 % ) . accordingly , american recorded the fair value of such discount upon the confirmation of the plan by the bankruptcy court. .
</details>

## 2. `AAP/2016/page_26.pdf-3`  (screen: disagree)

**Question:** from january 3 2015 to december 31 , how much greater was the return for s&p retail index than for advance auto parts ? ( in a percentage )

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `43.9%` | `0.24039` | `subtract(244.64, 228.88), subtract(256.69, 196.06), divide(#0, 228.88), divide(#1, 196.06), subtract(#3, #2)` |

**Gold facts**
- `table_1` company/index the advance auto parts of december 31 2011 is $ 100.00 ; the advance auto parts of december 29 2012 is $ 102.87 ; the advance auto parts of december 28 2013 is $ 158.46 ; the advance auto parts of january 3 2015 is $ 228.88 ; the advance auto parts of january 2 2016 is $ 217.49 ; the advance auto parts of december 31 2016 is $ 244.64 ;
- `table_3` company/index the s&p retail index of december 31 2011 is 100.00 ; the s&p retail index of december 29 2012 is 122.23 ; the s&p retail index of december 28 2013 is 178.55 ; the s&p retail index of january 3 2015 is 196.06 ; the s&p retail index of january 2 2016 is 245.31 ; the s&p retail index of december 31 2016 is 256.69 ;
- `text_3` comparison of cumulative total return among advance auto parts , inc. , s&p 500 index and s&p retail index company/index december 31 , december 29 , december 28 , january 3 , january 2 , december 31 .

**Table**

| company/index | december 31 2011 | december 29 2012 | december 28 2013 | january 3 2015 | january 2 2016 | december 31 2016 |
| --- | --- | --- | --- | --- | --- | --- |
| advance auto parts | $ 100.00 | $ 102.87 | $ 158.46 | $ 228.88 | $ 217.49 | $ 244.64 |
| s&p 500 index | 100.00 | 114.07 | 152.98 | 174.56 | 177.01 | 198.18 |
| s&p retail index | 100.00 | 122.23 | 178.55 | 196.06 | 245.31 | 256.69 |

<details><summary>Text before the table</summary>

stock price performance the following graph shows a comparison of the cumulative total return on our common stock , the standard & poor 2019s 500 index and the standard & poor 2019s retail index . the graph assumes that the value of an investment in our common stock and in each such index was $ 100 on december 31 , 2011 , and that any dividends have been reinvested . the comparison in the graph below is based solely on historical data and is not intended to forecast the possible future performance of our common stock . comparison of cumulative total return among advance auto parts , inc. , s&p 500 index and s&p retail index company/index december 31 , december 29 , december 28 , january 3 , january 2 , december 31 .
</details>

<details><summary>Text after the table</summary>

.
</details>

## 3. `AAPL/2012/page_64.pdf-4`  (screen: disagree)

**Question:** in connection with tax matters , what was the increase in recognized interest expense between 2012 and 2011?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `126` | `0.0` | `subtract(140, 140)` |

**Gold facts**
- `text_3` in connection with tax matters , the company recognized interest expense in 2012 and 2011 of $ 140 million and $ 14 million , respectively , and in 2010 the company recognized an interest benefit of $ 43 million .

**Table**

|  | 2012 | 2011 | 2010 |
| --- | --- | --- | --- |
| beginning balance | $ 1375 | $ 943 | $ 971 |
| increases related to tax positions taken during a prior year | 340 | 49 | 61 |
| decreases related to tax positions taken during a prior year | -107 ( 107 ) | -39 ( 39 ) | -224 ( 224 ) |
| increases related to tax positions taken during the current year | 467 | 425 | 240 |
| decreases related to settlements with taxing authorities | -3 ( 3 ) | 0 | -102 ( 102 ) |
| decreases related to expiration of statute of limitations | -10 ( 10 ) | -3 ( 3 ) | -3 ( 3 ) |
| ending balance | $ 2062 | $ 1375 | $ 943 |

<details><summary>Text before the table</summary>

the aggregate changes in the balance of gross unrecognized tax benefits , which excludes interest and penalties , for 2012 , 2011 , and 2010 , is as follows ( in millions ) : .
</details>

<details><summary>Text after the table</summary>

the company includes interest and penalties related to unrecognized tax benefits within the provision for income taxes . as of september 29 , 2012 and september 24 , 2011 , the total amount of gross interest and penalties accrued was $ 401 million and $ 261 million , respectively , which is classified as non-current liabilities in the consolidated balance sheets . in connection with tax matters , the company recognized interest expense in 2012 and 2011 of $ 140 million and $ 14 million , respectively , and in 2010 the company recognized an interest benefit of $ 43 million . the company is subject to taxation and files income tax returns in the u.s . federal jurisdiction and in many state and foreign jurisdictions . for u.s . federal income tax purposes , all years prior to 2004 are closed . the internal revenue service ( the 201cirs 201d ) has completed its field audit of the company 2019s federal income tax returns for the years 2004 through 2006 and proposed certain adjustments . the company has contested certain of these adjustments through the irs appeals office . the irs is currently examining the years 2007 through 2009 . in addition , the company is also subject to audits by state , local and foreign tax authorities . in major states and major foreign jurisdictions , the years subsequent to 1989 and 2002 , respectively , generally remain open and could be subject to examination by the taxing authorities . management believes that an adequate provision has been made for any adjustments that may result from tax examinations . however , the outcome of tax audits cannot be predicted with certainty . if any issues addressed in the company 2019s tax audits are resolved in a manner not consistent with management 2019s expectations , the company could be required to adjust its provision for income tax in the period such resolution occurs . although timing of the resolution and/or closure of audits is not certain , the company believes it is reasonably possible that tax audit resolutions could reduce its unrecognized tax benefits by between $ 120 million and $ 170 million in the next 12 months . note 6 2013 shareholders 2019 equity and share-based compensation preferred stock the company has five million shares of authorized preferred stock , none of which is issued or outstanding . under the terms of the company 2019s restated articles of incorporation , the board of directors is authorized to determine or alter the rights , preferences , privileges and restrictions of the company 2019s authorized but unissued shares of preferred stock . dividend and stock repurchase program in 2012 , the board of directors of the company approved a dividend policy pursuant to which it plans to make , subject to subsequent declaration , quarterly dividends of $ 2.65 per share . on july 24 , 2012 , the board of directors declared a dividend of $ 2.65 per share to shareholders of record as of the close of business on august 13 , 2012 . the company paid $ 2.5 billion in conjunction with this dividend on august 16 , 2012 . no dividends were declared in the first three quarters of 2012 or in 2011 and 2010. .
</details>

## 4. `ALLE/2017/page_44.pdf-2`  (screen: disagree)

**Question:** what is the annualized return for the investment in the allegion plc during 2013-2017?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `8.95%` | `-0.96554` | `subtract(189.19, 100), divide(1, const_4), subtract(#1, 1), exp(#0, #2), subtract(#3, 1)` |

**Gold facts**
- `table_2` the s&p 500 of december 1 2013 is 100.00 ; the s&p 500 of december 31 2013 is 102.53 ; the s&p 500 of december 31 2014 is 116.57 ; the s&p 500 of december 31 2015 is 118.18 ; the s&p 500 of december 31 2016 is 132.31 ; the s&p 500 of december 31 2017 is 161.20 ;
- `text_0` performance graph the annual changes for the period shown december 1 , 2013 ( when our ordinary shares began trading ) to december 31 , 2017 in the graph on this page are based on the assumption that $ 100 had been invested in allegion plc ordinary shares , the standard & poor 2019s 500 stock index ( "s&p 500" ) and the standard & poor's 400 capital goods index ( "s&p 400 capital goods" ) on december 1 , 2013 , and that all quarterly dividends were reinvested .
- `table_1` the allegion plc of december 1 2013 is 100.00 ; the allegion plc of december 31 2013 is 102.20 ; the allegion plc of december 31 2014 is 129.03 ; the allegion plc of december 31 2015 is 154.37 ; the allegion plc of december 31 2016 is 150.97 ; the allegion plc of december 31 2017 is 189.19 ;

**Table**

|  | december 1 2013 | december 31 2013 | december 31 2014 | december 31 2015 | december 31 2016 | december 31 2017 |
| --- | --- | --- | --- | --- | --- | --- |
| allegion plc | 100.00 | 102.20 | 129.03 | 154.37 | 150.97 | 189.19 |
| s&p 500 | 100.00 | 102.53 | 116.57 | 118.18 | 132.31 | 161.20 |
| s&p 400 capital goods | 100.00 | 104.58 | 104.84 | 99.07 | 130.70 | 162.97 |

<details><summary>Text before the table</summary>

performance graph the annual changes for the period shown december 1 , 2013 ( when our ordinary shares began trading ) to december 31 , 2017 in the graph on this page are based on the assumption that $ 100 had been invested in allegion plc ordinary shares , the standard & poor 2019s 500 stock index ( "s&p 500" ) and the standard & poor's 400 capital goods index ( "s&p 400 capital goods" ) on december 1 , 2013 , and that all quarterly dividends were reinvested . the total cumulative dollar returns shown on the graph represent the value that such investments would have had on december 31 , 2017 . december 1 , december 31 , december 31 , december 31 , december 31 , december 31 .
</details>

<details><summary>Text after the table</summary>

.
</details>

## 5. `AMT/2016/page_57.pdf-3`  (screen: disagree)

**Question:** what is the total number of new sites acquired and constructed during 2015?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `6535` | `25370.0` | `add(11595, 2330), add(#0, 4910), add(#1, 6535)` |

**Gold facts**
- `table_1` new sites ( acquired or constructed ) the u.s . of 2016 is 65 ; the u.s . of 2015 is 11595 ; the u.s . of 2014 is 900 ;
- `table_2` new sites ( acquired or constructed ) the asia of 2016 is 43865 ; the asia of 2015 is 2330 ; the asia of 2014 is 1560 ;
- `table_3` new sites ( acquired or constructed ) the emea of 2016 is 665 ; the emea of 2015 is 4910 ; the emea of 2014 is 190 ;
- `table_4` new sites ( acquired or constructed ) the latin america of 2016 is 715 ; the latin america of 2015 is 6535 ; the latin america of 2014 is 5800 ;

**Table**

| new sites ( acquired or constructed ) | 2016 | 2015 | 2014 |
| --- | --- | --- | --- |
| u.s . | 65 | 11595 | 900 |
| asia | 43865 | 2330 | 1560 |
| emea | 665 | 4910 | 190 |
| latin america | 715 | 6535 | 5800 |

<details><summary>Text before the table</summary>

in emerging markets , such as ghana , india , nigeria and uganda , wireless networks tend to be significantly less advanced than those in the united states , and initial voice networks continue to be deployed in underdeveloped areas . a majority of consumers in these markets still utilize basic wireless services , predominantly on feature phones , while advanced device penetration remains low . in more developed urban locations within these markets , early-stage data network deployments are underway . carriers are focused on completing voice network build-outs while also investing in initial data networks as wireless data usage and smartphone penetration within their customer bases begin to accelerate . in markets with rapidly evolving network technology , such as south africa and most of the countries in latin america where we do business , initial voice networks , for the most part , have already been built out , and carriers are focused on 3g and 4g network build outs . consumers in these regions are increasingly adopting smartphones and other advanced devices , and , as a result , the usage of bandwidth-intensive mobile applications is growing materially . recent spectrum auctions in these rapidly evolving markets have allowed incumbent carriers to accelerate their data network deployments and have also enabled new entrants to begin initial investments in data networks . smartphone penetration and wireless data usage in these markets are growing rapidly , which typically requires that carriers continue to invest in their networks in order to maintain and augment their quality of service . finally , in markets with more mature network technology , such as germany and france , carriers are focused on deploying 4g data networks to account for rapidly increasing wireless data usage among their customer base . with higher smartphone and advanced device penetration and significantly higher per capita data usage , carrier investment in networks is focused on 4g coverage and capacity . we believe that the network technology migration we have seen in the united states , which has led to significantly denser networks and meaningful new business commencements for us over a number of years , will ultimately be replicated in our less advanced international markets . as a result , we expect to be able to leverage our extensive international portfolio of approximately 104470 communications sites and the relationships we have built with our carrier customers to drive sustainable , long-term growth . we have master lease agreements with certain of our tenants that provide for consistent , long-term revenue and reduce the likelihood of churn . our master lease agreements build and augment strong strategic partnerships with our tenants and have significantly reduced colocation cycle times , thereby providing our tenants with the ability to rapidly and efficiently deploy equipment on our sites . property operations new site revenue growth . during the year ended december 31 , 2016 , we grew our portfolio of communications real estate through the acquisition and construction of approximately 45310 sites . in a majority of our asia , emea and latin america markets , the revenue generated from newly acquired or constructed sites resulted in increases in both tenant and pass-through revenues ( such as ground rent or power and fuel costs ) and expenses . we continue to evaluate opportunities to acquire communications real estate portfolios , both domestically and internationally , to determine whether they meet our risk-adjusted hurdle rates and whether we believe we can effectively integrate them into our existing portfolio. .
</details>

<details><summary>Text after the table</summary>

property operations expenses . direct operating expenses incurred by our property segments include direct site level expenses and consist primarily of ground rent and power and fuel costs , some or all of which may be passed through to our tenants , as well as property taxes , repairs and maintenance . these segment direct operating expenses exclude all segment and corporate selling , general , administrative and development expenses , which are aggregated into one line item entitled selling , general , administrative and development expense in our consolidated statements of operations . in general , our property segments 2019 selling , general , administrative and development expenses do not significantly increase as a result of adding incremental tenants to our sites and typically increase only modestly year-over-year . as a result , leasing additional space to new tenants on our sites provides significant incremental cash flow . we may , however , incur additional segment selling , general , administrative and development expenses as we increase our presence in our existing markets or expand into new markets . our profit margin growth is therefore positively impacted by the addition of new tenants to our sites but can be temporarily diluted by our development activities. .
</details>

## 6. `AON/2018/page_41.pdf-1`  (screen: disagree)

**Question:** what was the average free cash flow provided by continuing operations from 2016 to 2018 in millions

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1201` | `1804.0` | `add(1446, 486), add(#0, 1673), add(#1, const_3), divide(#2, const_2)` |

**Gold facts**
- `table_3` years ended december 31 the free cash flow provided by continuing operations of 2018 is $ 1446 ; the free cash flow provided by continuing operations of 2017 is $ 486 ; the free cash flow provided by continuing operations of 2016 is $ 1673 ;

**Table**

| years ended december 31 | 2018 | 2017 | 2016 |
| --- | --- | --- | --- |
| cash provided by continuing operating activities | $ 1686 | $ 669 | $ 1829 |
| capital expenditures used for continuing operations | -240 ( 240 ) | -183 ( 183 ) | -156 ( 156 ) |
| free cash flow provided by continuing operations | $ 1446 | $ 486 | $ 1673 |

<details><summary>Text before the table</summary>

( 1 ) adjusted other income ( expense ) excludes pension settlement charges of $ 37 million , $ 128 million , and $ 220 million , for the years ended 2018 , 2017 , and 2016 , respectively . ( 2 ) adjusted items are generally taxed at the estimated annual effective tax rate , except for the applicable tax impact associated with estimated restructuring plan expenses , legacy litigation , accelerated tradename amortization , impairment charges and non-cash pension settlement charges , which are adjusted at the related jurisdictional rates . in addition , tax expense excludes the tax impacts from the sale of certain assets and liabilities previously classified as held for sale as well as the tax adjustments recorded to finalize the 2017 accounting for the enactment date impact of the tax reform act recorded pursuant torr sab 118 . ( 3 ) adjusted net income from discontinued operations excludes the gain on sale of discontinued operations of $ 82 million , $ 779 million , and $ 0 million for the years ended 2018 , 2017 , and 2016 , respectively . adjusted net income from discontinued operations excludes intangible asset amortization of $ 0 million , $ 11rr million , and $ 120 million for the twelve months ended december 31 , 2018 , 2017 , and 2016 , respectively . the effective tax rate was further adjusted for the applicable tax impact associated with the gain on sale and intangible asset amortization , as applicable . free cash flow we use free cash flow , defined as cash flow provided by operations minus capital expenditures , as a non-gaap measure of our core operating performance and cash generating capabilities of our business operations . this supplemental information related to free cash flow represents a measure not in accordance with u.s . gaap and should be viewed in addition to , not instead of , our financial statements . the use of this non-gaap measure does not imply or represent the residual cash flow for discretionary expenditures . a reconciliation of this non-gaap measure to cash flow provided by operations is as follows ( in millions ) : .
</details>

<details><summary>Text after the table</summary>

impact of foreign currency exchange rate fluctuations we conduct business in more than 120 countries and sovereignties and , because of this , foreign currency exchange rate fluctuations have a significant impact on our business . foreign currency exchange rate movements may be significant and may distort true period-to-period comparisons of changes in revenue or pretax income . therefore , to give financial statement users meaningful information about our operations , we have provided an illustration of the impact of foreign currency exchange rate fluctuations on our financial results . the methodology used to calculate this impact isolates the impact of the change in currencies between periods by translating the prior year 2019s revenue , expenses , and net income using the current year 2019s foreign currency exchange rates . translating prior year results at current year foreign currency exchange rates , currency fluctuations had a $ 0.08 favorable impact on net income per diluted share during the year ended december 31 , 2018 . currency fluctuations had a $ 0.12 favorable impact on net income per diluted share during the year ended december 31 , 2017 , when 2016 results were translated at 2017 rates . currency fluctuations had no impact on net income per diluted share during the year ended december 31 , 2016 , when 2015 results were translated at 2016 rates . translating prior year results at current year foreign currency exchange rates , currency fluctuations had a $ 0.09 favorable impact on adjusted net income per diluted share during the year ended december 31 , 2018 . currency fluctuations had a $ 0.08 favorable impact on adjusted net income per diluted share during the year ended december 31 , 2017 , when 2016 results were translated at 2017 rates . currency fluctuations had a $ 0.04 unfavorable impact on adjusted net income per diluted share during the year ended december 31 , 2016 , when 2015 results were translated at 2016 rates . these translations are performed for comparative purposes only and do not impact the accounting policies or practices for amounts included in the financial statements . competition and markets authority the u.k . 2019s competition regulator , the competition and markets authority ( the 201ccma 201d ) , conducted a market investigation into the supply and acquisition of investment consulting and fiduciary management services , including those offered by aon and its competitors in the u.k. , to assess whether any feature or combination of features in the target market prevents , restricts , or distorts competition . the cma issued a final report on december 12 , 2018 . the cma will draft a series of orders that will set out the detailed remedies , expected in first quarter of 2019 , when they will be subject to further public consultation . we do not anticipate the remedies to have a significant impact on the company 2019s consolidated financial position or business . financial conduct authority the fca is conducting a market study to assess how effectively competition is working in the wholesale insurance broker sector in the u.k . in which aon , through its subsidiaries , participates . the fca has indicated that the purpose of a market study is to assess the extent to which the market is working well in the interests of customers and to identify features of the market that may impact competition . depending on the study 2019s findings , the fca may require remedies in order to correct any features found .
</details>

## 7. `APD/2019/page_100.pdf-1`  (screen: disagree)

**Question:** what is the short-term debt as a percent of total debt , in 2019?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1.74%` | `0.0175` | `divide(58.2, 3326.0)` |

**Gold facts**
- `table_1` 30 september the short-term borrowings of 2019 is $ 58.2 ; the short-term borrowings of 2018 is $ 54.3 ;
- `table_5` 30 september the total debt of 2019 is $ 3326.0 ; the total debt of 2018 is $ 3812.6 ;

**Table**

| 30 september | 2019 | 2018 |
| --- | --- | --- |
| short-term borrowings | $ 58.2 | $ 54.3 |
| current portion of long-term debt ( a ) ( b ) | 40.4 | 406.6 |
| long-term debt | 2907.3 | 2967.4 |
| long-term debt 2013 related party ( b ) | 320.1 | 384.3 |
| total debt | $ 3326.0 | $ 3812.6 |

<details><summary>Text before the table</summary>

during the third quarter ended 30 june 2017 , we recognized a goodwill impairment charge of $ 145.3 and an intangible asset impairment charge of $ 16.8 associated with our lasa reporting unit . refer to note 11 , goodwill , and note 12 , intangible assets , for more information related to these charges and the associated fair value measurement methods and significant inputs/assumptions , which were classified as level 3 since unobservable inputs were utilized in the fair value measurements . 16 . debt the tables below summarize our outstanding debt at 30 september 2019 and 2018 : total debt .
</details>

<details><summary>Text after the table</summary>

( a ) fiscal year 2019 includes the current portion of long-term debt owed to a related party of $ 37.8 . ( b ) refer to note 7 , acquisitions , for additional information regarding related party debt . short-term borrowings short-term borrowings consisted of bank obligations of $ 58.2 and $ 54.3 at 30 september 2019 and 2018 , respectively . the weighted average interest rate of short-term borrowings outstanding at 30 september 2019 and 2018 was 3.7% ( 3.7 % ) and 5.0% ( 5.0 % ) , respectively. .
</details>

## 8. `AWK/2014/page_122.pdf-1`  (screen: disagree)

**Question:** what percentage of the company 2019s valuation allowance consisted of a discrete tax benefit in 2013?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `28.7%` | `0.21977` | `divide(2979, 13555)` |

**Gold facts**
- `table_6` balance at january 1 2012 the balance at december 31 2013 of $ 21579 is $ 13555 ;
- `text_5` included in 2013 is a discrete tax benefit totaling $ 2979 associated with an entity re-organization within the company 2019s market-based operations segment that allowed for the utilization of state net operating loss carryforwards and the release of an associated valuation allowance .

**Table**

| balance at january 1 2012 | $ 21579 |
| --- | --- |
| increases in current period tax positions | 2014 |
| decreases in current period tax positions | -2059 ( 2059 ) |
| balance at december 31 2012 | $ 19520 |
| increases in current period tax positions | 2014 |
| decreases in current period tax positions | -5965 ( 5965 ) |
| balance at december 31 2013 | $ 13555 |
| increases in current period tax positions | 2014 |
| decreases in current period tax positions | -3176 ( 3176 ) |
| balance at december 31 2014 | $ 10379 |

<details><summary>Text before the table</summary>

majority of the increased tax position is attributable to temporary differences . the increase in 2014 current period tax positions related primarily to the company 2019s change in tax accounting method filed in 2008 for repair and maintenance costs on its utility plant . the company does not anticipate material changes to its unrecognized tax benefits within the next year . if the company sustains all of its positions at december 31 , 2014 and 2013 , an unrecognized tax benefit of $ 9444 and $ 7439 , respectively , excluding interest and penalties , would impact the company 2019s effective tax rate . the following table summarizes the changes in the company 2019s valuation allowance: .
</details>

<details><summary>Text after the table</summary>

included in 2013 is a discrete tax benefit totaling $ 2979 associated with an entity re-organization within the company 2019s market-based operations segment that allowed for the utilization of state net operating loss carryforwards and the release of an associated valuation allowance . note 13 : employee benefits pension and other postretirement benefits the company maintains noncontributory defined benefit pension plans covering eligible employees of its regulated utility and shared services operations . benefits under the plans are based on the employee 2019s years of service and compensation . the pension plans have been closed for all employees . the pension plans were closed for most employees hired on or after january 1 , 2006 . union employees hired on or after january 1 , 2001 had their accrued benefit frozen and will be able to receive this benefit as a lump sum upon termination or retirement . union employees hired on or after january 1 , 2001 and non-union employees hired on or after january 1 , 2006 are provided with a 5.25% ( 5.25 % ) of base pay defined contribution plan . the company does not participate in a multiemployer plan . the company 2019s pension funding practice is to contribute at least the greater of the minimum amount required by the employee retirement income security act of 1974 or the normal cost . further , the company will consider additional contributions if needed to avoid 201cat risk 201d status and benefit restrictions under the pension protection act of 2006 . the company may also consider increased contributions , based on other financial requirements and the plans 2019 funded position . pension plan assets are invested in a number of actively managed and commingled funds including equity and bond funds , fixed income securities , guaranteed interest contracts with insurance companies , real estate funds and real estate investment trusts ( 201creits 201d ) . pension expense in excess of the amount contributed to the pension plans is deferred by certain regulated subsidiaries pending future recovery in rates charged for utility services as contributions are made to the plans . ( see note 6 ) the company also has unfunded noncontributory supplemental non-qualified pension plans that provide additional retirement benefits to certain employees. .
</details>

## 9. `AWK/2018/page_150.pdf-2`  (screen: disagree)

**Question:** at what tax rate was exercise proceeds taxed at in 2018?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `28.6%` | `14.0` | `multiply(2, 7)` |

**Gold facts**
- `table_2` the exercise proceeds of 2018 is 7 ; the exercise proceeds of 2017 is 11 ; the exercise proceeds of 2016 is 15 ;
- `table_3` the income tax benefit realized of 2018 is 2 ; the income tax benefit realized of 2017 is 3 ; the income tax benefit realized of 2016 is 6 ;

**Table**

|  | 2018 | 2017 | 2016 |
| --- | --- | --- | --- |
| intrinsic value | $ 9 | $ 10 | $ 18 |
| exercise proceeds | 7 | 11 | 15 |
| income tax benefit realized | 2 | 3 | 6 |

<details><summary>Text before the table</summary>

the following table provides the weighted average assumptions used in the black-scholes option-pricing model for grants and the resulting weighted average grant date fair value per share of stock options granted for the years ended december 31: .
</details>

<details><summary>Text after the table</summary>

stock units during 2018 , 2017 and 2016 , the company granted rsus to certain employees under the 2007 plan and 2017 omnibus plan , as applicable . rsus generally vest based on continued employment with the company over periods ranging from one to three years. .
</details>

## 10. `AWK/2018/page_172.pdf-4`  (screen: disagree)

**Question:** what percentage of future annual commitments related to minimum quantities of purchased water having non-cancelable are due after 2023?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `67%` | `957.0` | `add(65, 65), add(65, 64), add(57, 641), add(#0, #1), add(#3, #2)` |

**Gold facts**
- `table_1` the 2019 of amount is $ 65 ;
- `table_2` the 2020 of amount is 65 ;
- `table_3` the 2021 of amount is 65 ;
- `table_4` the 2022 of amount is 64 ;
- `table_5` the 2023 of amount is 57 ;
- `table_6` the thereafter of amount is 641 ;

**Table**

|  | amount |
| --- | --- |
| 2019 | $ 65 |
| 2020 | 65 |
| 2021 | 65 |
| 2022 | 64 |
| 2023 | 57 |
| thereafter | 641 |

<details><summary>Text before the table</summary>

totaled $ 12 million , $ 13 million and $ 9 million for 2018 , 2017 and 2016 , respectively . all of the company 2019s contributions are invested in one or more funds at the direction of the employees . note 16 : commitments and contingencies commitments have been made in connection with certain construction programs . the estimated capital expenditures required under legal and binding contractual obligations amounted to $ 419 million as of december 31 , 2018 . the company 2019s regulated subsidiaries maintain agreements with other water purveyors for the purchase of water to supplement their water supply . the following table provides the future annual commitments related to minimum quantities of purchased water having non-cancelable: .
</details>

<details><summary>Text after the table</summary>

the company enters into agreements for the provision of services to water and wastewater facilities for the united states military , municipalities and other customers . see note 3 2014revenue recognition for additional information regarding the company 2019s performance obligations . contingencies the company is routinely involved in legal actions incident to the normal conduct of its business . as of december 31 , 2018 , the company has accrued approximately $ 54 million of probable loss contingencies and has estimated that the maximum amount of losses associated with reasonably possible loss contingencies that can be reasonably estimated is $ 26 million . for certain matters , claims and actions , the company is unable to estimate possible losses . the company believes that damages or settlements , if any , recovered by plaintiffs in such matters , claims or actions , other than as described in this note 16 2014commitments and contingencies , will not have a material adverse effect on the company . west virginia elk river freedom industries chemical spill on june 8 , 2018 , the u.s . district court for the southern district of west virginia granted final approval of a settlement class and global class action settlement ( the 201csettlement 201d ) for all claims and potential claims by all putative class members ( collectively , the 201cplaintiffs 201d ) arising out of the january 2014 freedom industries , inc . chemical spill in west virginia . the effective date of the settlement is july 16 , 2018 . under the terms and conditions of the settlement , west virginia-american water company ( 201cwvawc 201d ) and certain other company affiliated entities ( collectively , the 201camerican water defendants 201d ) did not admit , and will not admit , any fault or liability for any of the allegations made by the plaintiffs in any of the actions that were resolved . under federal class action rules , claimants had the right , until december 8 , 2017 , to elect to opt out of the final settlement . less than 100 of the 225000 estimated putative class members elected to opt out from the settlement , and these claimants will not receive any benefit from or be bound by the terms of the settlement . in june 2018 , the company and its remaining non-participating general liability insurance carrier settled for a payment to the company of $ 20 million , out of a maximum of $ 25 million in potential coverage under the terms of the relevant policy , in exchange for a full release by the american water defendants of all claims against the insurance carrier related to the freedom industries chemical spill. .
</details>

## 11. `BDX/2017/page_32.pdf-4`  (screen: disagree)

**Question:** what is the percentage increase for total specified items from 2014-2015?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `67.52%` | `6.75163` | `subtract(1186, 153), divide(#0, 153)` |

**Gold facts**
- `table_1` millions of dollars except per share amounts the total specified items of years ended september 30 2017 is $ 1466 ; the total specified items of years ended september 30 2016 is $ 1261 ; the total specified items of years ended september 30 2015 is $ 1186 ; the total specified items of years ended september 30 2014 is $ 153 ; the total specified items of years ended september 30 2013 is $ 442 ;
- `text_5` management 2019s discussion and analysis of financial condition and results of operations. .

**Table**

| millions of dollars except per share amounts | years ended september 30 2017 | years ended september 30 2016 | years ended september 30 2015 | years ended september 30 2014 | years ended september 30 2013 |
| --- | --- | --- | --- | --- | --- |
| total specified items | $ 1466 | $ 1261 | $ 1186 | $ 153 | $ 442 |
| after-tax impact of specified items | $ 971 | $ 892 | $ 786 | $ 101 | $ 279 |
| impact of specified items on diluted earnings per share | $ -4.34 ( 4.34 ) | $ -4.10 ( 4.10 ) | $ -3.79 ( 3.79 ) | $ -0.51 ( 0.51 ) | $ -1.40 ( 1.40 ) |
| impact of dilution from share issuances | $ -0.54 ( 0.54 ) | $ 2014 | $ -0.02 ( 0.02 ) | $ 2014 | $ 2014 |

<details><summary>Text before the table</summary>

( a ) excludes discontinued operations . ( b ) earnings before interest expense and taxes as a percent of average total assets . ( c ) total debt as a percent of the sum of total debt , shareholders 2019 equity and non-current deferred income tax liabilities . the results above include the impact of the specified items detailed below . additional discussion regarding the specified items in fiscal years 2017 , 2016 and 2015 are provided in item 7 . management 2019s discussion and analysis of financial condition and results of operations. .
</details>

<details><summary>Text after the table</summary>

item 7 . management 2019s discussion and analysis of financial condition and results of operations the following commentary should be read in conjunction with the consolidated financial statements and accompanying notes . within the tables presented throughout this discussion , certain columns may not add due to the use of rounded numbers for disclosure purposes . percentages and earnings per share amounts presented are calculated from the underlying amounts . references to years throughout this discussion relate to our fiscal years , which end on september 30 . company overview description of the company and business segments becton , dickinson and company ( 201cbd 201d ) is a global medical technology company engaged in the development , manufacture and sale of a broad range of medical supplies , devices , laboratory equipment and diagnostic products used by healthcare institutions , life science researchers , clinical laboratories , the pharmaceutical industry and the general public . the company's organizational structure is based upon two principal business segments , bd medical ( 201cmedical 201d ) and bd life sciences ( 201clife sciences 201d ) . bd 2019s products are manufactured and sold worldwide . our products are marketed in the united states and internationally through independent distribution channels and directly to end-users by bd and independent sales representatives . we organize our operations outside the united states as follows : europe ; ema ( which includes the commonwealth of independent states , the middle east and africa ) ; greater asia ( which includes japan and asia pacific ) ; latin america ( which includes mexico , central america , the caribbean , and south america ) ; and canada . we continue to pursue growth opportunities in emerging markets , which include the following geographic regions : eastern europe , the middle east , africa , latin america and certain countries within asia pacific . we are primarily focused on certain countries whose healthcare systems are expanding , in particular , china and india . strategic objectives bd remains focused on delivering sustainable growth and shareholder value , while making appropriate investments for the future . bd management operates the business consistent with the following core strategies : 2022 to increase revenue growth by focusing on our core products , services and solutions that deliver greater benefits to patients , healthcare workers and researchers; .
</details>

## 12. `BLL/2010/page_33.pdf-3`  (screen: disagree)

**Question:** the segment sales decrease in 2010 was what percent of the decrease in 2009?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `87.3` | `0.6757` | `subtract(129.2, 41.9), divide(#0, 129.2)` |

**Gold facts**
- `text_11` segment sales in 2010 decreased $ 41.9 million compared to 2009 , primarily due to unfavorable foreign exchange effects of $ 93 million and price and mix changes , partially offset by higher sales volumes .
- `text_12` segment sales in 2009 as compared to 2008 were $ 129.2 million lower due to $ 110 million of unfavorable foreign exchange effects , partially offset by better commercial terms .

**Table**

| ( $ in millions ) | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| net sales | $ 1697.6 | $ 1739.5 | $ 1868.7 |
| segment earnings | $ 212.9 | $ 214.8 | $ 230.9 |
| business consolidation costs ( a ) | -3.2 ( 3.2 ) | 2212 | 2212 |
| total segment earnings | $ 209.7 | $ 214.8 | $ 230.9 |

<details><summary>Text before the table</summary>

page 20 of 100 segment sales were $ 100.7 million lower in 2009 than in 2008 , primarily as a result of the impact of lower aluminum prices partially offset by an increase in sales volumes . the higher sales volumes in 2009 were the result of incremental volumes from the four plants purchased from ab inbev , partially offset by certain plant closures and lower sales volumes in the existing business . segment earnings in 2010 were $ 122.3 million higher than in 2009 primarily due to a net $ 85 million impact related to the higher sales volumes and $ 45 million of product mix and improved manufacturing performance associated with higher production . also adding to the 2010 improvement was the effect of a $ 7 million out-of-period inventory charge in 2009 . the details of the out-of-period adjustment are included in note 7 to the consolidated financial statements included within item 8 of this report . segment earnings in 2009 were higher than in 2008 due to $ 12 million of earnings contribution from the four acquired plants and approximately $ 21 million of savings associated with plant closures . partially offsetting these favorable impacts were lower carbonated soft drink and beer can sales volumes ( excluding the newly acquired plants ) and approximately $ 25 million related to higher cost inventories in the first half of 2009 . metal beverage packaging , europe .
</details>

<details><summary>Text after the table</summary>

( a ) further details of these items are included in note 5 to the consolidated financial statements within item 8 of this report . the metal beverage packaging , europe , segment includes metal beverage packaging products manufactured in europe . ball packaging europe has manufacturing plants located in germany , the united kingdom , france , the netherlands , poland and serbia , and is the second largest metal beverage container business in europe . segment sales in 2010 decreased $ 41.9 million compared to 2009 , primarily due to unfavorable foreign exchange effects of $ 93 million and price and mix changes , partially offset by higher sales volumes . segment sales in 2009 as compared to 2008 were $ 129.2 million lower due to $ 110 million of unfavorable foreign exchange effects , partially offset by better commercial terms . sales volumes in 2009 were essentially flat compared to those in the prior year . segment earnings in 2010 decreased $ 1.9 million compared to 2009 , primarily the result of a $ 28 million increase related to higher sales volumes , offset by $ 18 million of negative effects from foreign currency translation and $ 12 million of higher inventory and other costs . while 2009 sales volumes were consistent with the prior year , the adverse effects of foreign currency translation , both within europe and on the conversion of the euro to the u.s . dollar , reduced segment earnings by $ 8 million . also contributing to lower segment earnings were higher cost inventory carried into 2009 and a change in sales mix , partially offset by better commercial terms in some of our contracts . on january 18 , 2011 , ball acquired aerocan s.a.s . ( aerocan ) , a leading european supplier of aluminum aerosol cans and bottles , for 20ac222.4 million ( approximately $ 300 million ) in cash and assumed debt . aerocan manufactures extruded aluminum aerosol cans and bottles , and the aluminum slugs used to make them , for customers in the personal care , pharmaceutical , beverage and food industries . it operates three aerosol can manufacturing plants 2013 one each in the czech republic , france and the united kingdom 2013 and is a 51 percent owner of a joint venture aluminum slug plant in france . the four plants employ approximately 560 people . the acquisition of aerocan will allow ball to enter a growing part of the metal packaging industry and to broaden the company 2019s market development efforts into a new customer base. .
</details>

## 13. `C/2010/page_272.pdf-2`  (screen: disagree)

**Question:** what was the ratio of the net terminations of structured notes to the decrease in long-term debt

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `0.86` | `0.86667` | `divide(1.3, 1.5)` |

**Gold facts**
- `text_5` the decrease in long-term debt of $ 1.5 billion is driven mainly by 2022 $ 1.3 billion of net terminations of structured notes .

**Table**

| in billions of dollars | aggregate cost | fair value | level 2 | level 3 |
| --- | --- | --- | --- | --- |
| december 31 2010 | $ 3.1 | $ 2.5 | $ 0.7 | $ 1.8 |
| december 31 2009 | $ 2.5 | $ 1.6 | $ 0.3 | $ 1.3 |

<details><summary>Text before the table</summary>

the significant changes from december 31 , 2008 to december 31 , 2009 in level 3 assets and liabilities are due to : a net decrease in trading securities of $ 10.8 billion that was driven by : 2022 net transfers of $ 6.5 billion , due mainly to the transfer of debt 2013 securities from level 3 to level 2 due to increased liquidity and pricing transparency ; and net settlements of $ 5.8 billion , due primarily to the liquidations of 2013 subprime securities of $ 4.1 billion . the change in net trading derivatives driven by : 2022 a net loss of $ 4.9 billion relating to complex derivative contracts , 2013 such as those linked to credit , equity and commodity exposures . these losses include both realized and unrealized losses during 2009 and are partially offset by gains recognized in instruments that have been classified in levels 1 and 2 ; and net increase in derivative assets of $ 4.3 billion , which includes cash 2013 settlements of derivative contracts in an unrealized loss position , notably those linked to subprime exposures . the decrease in level 3 investments of $ 6.9 billion primarily 2022 resulted from : a reduction of $ 5.0 billion , due mainly to paydowns on debt 2013 securities and sales of private equity investments ; the net transfer of investment securities from level 3 to level 2 2013 of $ 1.5 billion , due to increased availability of observable pricing inputs ; and net losses recognized of $ 0.4 billion due mainly to losses on non- 2013 marketable equity securities including write-downs on private equity investments . the decrease in securities sold under agreements to repurchase of 2022 $ 9.1 billion is driven by a $ 8.6 billion net transfers from level 3 to level 2 as effective maturity dates on structured repos have shortened . the decrease in long-term debt of $ 1.5 billion is driven mainly by 2022 $ 1.3 billion of net terminations of structured notes . transfers between level 1 and level 2 of the fair value hierarchy the company did not have any significant transfers of assets or liabilities between levels 1 and 2 of the fair value hierarchy during 2010 . items measured at fair value on a nonrecurring basis certain assets and liabilities are measured at fair value on a nonrecurring basis and therefore are not included in the tables above . these include assets measured at cost that have been written down to fair value during the periods as a result of an impairment . in addition , these assets include loans held-for-sale that are measured at locom that were recognized at fair value below cost at the end of the period . the fair value of loans measured on a locom basis is determined where possible using quoted secondary-market prices . such loans are generally classified as level 2 of the fair value hierarchy given the level of activity in the market and the frequency of available quotes . if no such quoted price exists , the fair value of a loan is determined using quoted prices for a similar asset or assets , adjusted for the specific attributes of that loan . the following table presents all loans held-for-sale that are carried at locom as of december 31 , 2010 and 2009 : in billions of dollars aggregate cost fair value level 2 level 3 .
</details>

<details><summary>Text after the table</summary>

.
</details>

## 14. `C/2016/page_120.pdf-3`  (screen: disagree)

**Question:** what was the percent of the increase in the high quality liquid assets ( hqla ) for citi from 2015 to 2016

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `3.7%` | `14.5` | `subtract(403.7, 389.2)` |

**Gold facts**
- `table_1` in billions of dollars the hqla of dec . 31 2016 is $ 403.7 ; the hqla of sept . 30 2016 is $ 403.8 ; the hqla of dec . 31 2015 is $ 389.2 ;

**Table**

| in billions of dollars | dec . 31 2016 | sept . 30 2016 | dec . 31 2015 |
| --- | --- | --- | --- |
| hqla | $ 403.7 | $ 403.8 | $ 389.2 |
| net outflows | 332.5 | 335.3 | 344.4 |
| lcr | 121% ( 121 % ) | 120% ( 120 % ) | 113% ( 113 % ) |
| hqla in excess of net outflows | $ 71.3 | $ 68.5 | $ 44.8 |

<details><summary>Text before the table</summary>

liquidity monitoring and measurement stress testing liquidity stress testing is performed for each of citi 2019s major entities , operating subsidiaries and/or countries . stress testing and scenario analyses are intended to quantify the potential impact of a liquidity event on the balance sheet and liquidity position , and to identify viable funding alternatives that can be utilized . these scenarios include assumptions about significant changes in key funding sources , market triggers ( such as credit ratings ) , potential uses of funding and political and economic conditions in certain countries . these conditions include expected and stressed market conditions as well as company- specific events . liquidity stress tests are conducted to ascertain potential mismatches between liquidity sources and uses over a variety of time horizons ( overnight , one week , two weeks , one month , three months , one year ) and over a variety of stressed conditions . liquidity limits are set accordingly . to monitor the liquidity of an entity , these stress tests and potential mismatches are calculated with varying frequencies , with several tests performed daily . given the range of potential stresses , citi maintains a series of contingency funding plans on a consolidated basis and for individual entities . these plans specify a wide range of readily available actions for a variety of adverse market conditions or idiosyncratic stresses . short-term liquidity measurement : liquidity coverage ratio ( lcr ) in addition to internal measures that citi has developed for a 30-day stress scenario , citi also monitors its liquidity by reference to the lcr , as calculated pursuant to the u.s . lcr rules . generally , the lcr is designed to ensure that banks maintain an adequate level of hqla to meet liquidity needs under an acute 30-day stress scenario . the lcr is calculated by dividing hqla by estimated net outflows over a stressed 30-day period , with the net outflows determined by applying prescribed outflow factors to various categories of liabilities , such as deposits , unsecured and secured wholesale borrowings , unused lending commitments and derivatives- related exposures , partially offset by inflows from assets maturing within 30 days . banks are required to calculate an add-on to address potential maturity mismatches between contractual cash outflows and inflows within the 30-day period in determining the total amount of net outflows . the minimum lcr requirement is 100% ( 100 % ) , effective january 2017 . in december 2016 , the federal reserve board adopted final rules which require additional disclosures relating to the lcr of large financial institutions , including citi . among other things , the final rules require citi to disclose components of its average hqla , lcr and inflows and outflows each quarter . in addition , the final rules require disclosure of citi 2019s calculation of the maturity mismatch add-on as well as other qualitative disclosures . the effective date for these disclosures is april 1 , 2017 . the table below sets forth the components of citi 2019s lcr calculation and hqla in excess of net outflows for the periods indicated : in billions of dollars dec . 31 , sept . 30 , dec . 31 .
</details>

<details><summary>Text after the table</summary>

note : amounts set forth in the table above are presented on an average basis . as set forth in the table above , citi 2019s lcr increased both year-over-year and sequentially . the increase year-over-year was driven by both an increase in hqla and a reduction in net outflows . sequentially , the increase was driven by a slight reduction in net outflows , as hqla remained largely unchanged . long-term liquidity measurement : net stable funding ratio ( nsfr ) in the second quarter of 2016 , the federal reserve board , the fdic and the occ issued a proposed rule to implement the basel iii nsfr requirement . the u.s.-proposed nsfr is largely consistent with the basel committee 2019s final nsfr rules . in general , the nsfr assesses the availability of a bank 2019s stable funding against a required level . a bank 2019s available stable funding would include portions of equity , deposits and long-term debt , while its required stable funding would be based on the liquidity characteristics of its assets , derivatives and commitments . standardized weightings would be required to be applied to the various asset and liabilities classes . the ratio of available stable funding to required stable funding would be required to be greater than 100% ( 100 % ) . while citi believes that it is compliant with the proposed u.s . nsfr rules as of december 31 , 2016 , it will need to evaluate any final version of the rules , which are expected to be released during 2017 . the proposed rules would require full implementation of the u.s . nsfr beginning january 1 , 2018. .
</details>

## 15. `CDNS/2018/page_32.pdf-4`  (screen: disagree)

**Question:** what is the total cash outflow for stock repurchase in the last three months of 2018 , ( in millions ) ?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `108.7` | `108681175.5` | `multiply(2521605, 43.10)` |

**Gold facts**
- `table_4` period the total of total numberof sharespurchased ( 1 ) is 2521605 ; the total of averageprice paidper share ( 2 ) is $ 43.10 ; the total of total number ofshares purchasedas part ofpublicly announcedplan or program is 2322925 ; the total of maximum dollarvalue of sharesauthorized for repurchase underpublicly announcedplan or program ( 1 ) ( in millions ) is ;

**Table**

| period | total numberof sharespurchased ( 1 ) | averageprice paidper share ( 2 ) | total number ofshares purchasedas part ofpublicly announcedplan or program | maximum dollarvalue of sharesauthorized for repurchase underpublicly announcedplan or program ( 1 ) ( in millions ) |
| --- | --- | --- | --- | --- |
| september 30 2018 2013 november 3 2018 | 543900 | $ 42.64 | 495543 | $ 254 |
| november 4 2018 2013 december 1 2018 | 650048 | $ 44.49 | 623692 | $ 226 |
| december 2 2018 2013 december 29 2018 | 1327657 | $ 42.61 | 1203690 | $ 175 |
| total | 2521605 | $ 43.10 | 2322925 |  |

<details><summary>Text before the table</summary>

issuer purchases of equity securities in january 2017 , our board of directors authorized the repurchase of shares of our common stock with a value of up to $ 525 million in the aggregate . as of december 29 , 2018 , $ 175 million remained available under this authorization . in february 2019 , our board of directors authorized the additional repurchase of shares of our common stock with a value of up to $ 500.0 million in the aggregate . the actual timing and amount of repurchases are subject to business and market conditions , corporate and regulatory requirements , stock price , acquisition opportunities and other factors . the following table presents repurchases made under our current authorization and shares surrendered by employees to satisfy income tax withholding obligations during the three months ended december 29 , 2018 : period total number of shares purchased ( 1 ) average price paid per share ( 2 ) total number of shares purchased as part of publicly announced plan or program maximum dollar value of shares authorized for repurchase under publicly announced plan or program ( 1 ) ( in millions ) september 30 , 2018 2013 november 3 , 2018 543900 $ 42.64 495543 $ 254 november 4 , 2018 2013 december 1 , 2018 650048 $ 44.49 623692 $ 226 december 2 , 2018 2013 december 29 , 2018 1327657 $ 42.61 1203690 $ 175 .
</details>

<details><summary>Text after the table</summary>

( 1 ) shares purchased that were not part of our publicly announced repurchase programs represent employee surrender of shares of restricted stock to satisfy employee income tax withholding obligations due upon vesting , and do not reduce the dollar value that may yet be purchased under our publicly announced repurchase programs . ( 2 ) the weighted average price paid per share of common stock does not include the cost of commissions. .
</details>

## 16. `CDNS/2018/page_82.pdf-1`  (screen: disagree)

**Question:** for acquisitions in 2017 what percentage of recorded a total acquired intangible assets was goodwill?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `118%` | `0.84701` | `divide(76.4, 90.2)` |

**Gold facts**
- `text_3` cadence recorded a total of $ 76.4 million of acquired intangible assets ( of which $ 71.5 million represents in-process technology ) , $ 90.2 million of goodwill and $ 19.6 million of net liabilities consisting primarily of deferred tax liabilities .

**Table**

|  | gross carryingamount ( in thousands ) |
| --- | --- |
| balance as of december 31 2016 | $ 572764 |
| goodwill resulting from acquisitions | 90218 |
| effect of foreign currency translation | 3027 |
| balance as of december 30 2017 | 666009 |
| effect of foreign currency translation | -3737 ( 3737 ) |
| balance as of december 29 2018 | $ 662272 |

<details><summary>Text before the table</summary>

note 8 . acquisitions during fiscal 2017 , cadence completed two business combinations for total cash consideration of $ 142.8 million , after taking into account cash acquired of $ 4.2 million . the total purchase consideration was allocated to the assets acquired and liabilities assumed based on their respective estimated fair values on the acquisition dates . cadence recorded a total of $ 76.4 million of acquired intangible assets ( of which $ 71.5 million represents in-process technology ) , $ 90.2 million of goodwill and $ 19.6 million of net liabilities consisting primarily of deferred tax liabilities . cadence will also make payments to certain employees , subject to continued employment and other performance-based conditions , through the fourth quarter of fiscal 2020 . during fiscal 2016 , cadence completed two business combinations for total cash consideration of $ 42.4 million , after taking into account cash acquired of $ 1.8 million . the total purchase consideration was allocated to the assets acquired and liabilities assumed based on their respective estimated fair values on the acquisition dates . cadence recorded a total of $ 23.6 million of goodwill , $ 23.2 million of acquired intangible assets and $ 2.6 million of net liabilities consisting primarily of deferred revenue . cadence will also make payments to certain employees , subject to continued employment and other conditions , through the second quarter of fiscal a trust for the benefit of the children of lip-bu tan , cadence 2019s chief executive officer ( 201cceo 201d ) and director , owned less than 3% ( 3 % ) of nusemi inc , one of the companies acquired in 2017 , and less than 2% ( 2 % ) of rocketick technologies ltd. , one of the companies acquired in 2016 . mr . tan and his wife serve as co-trustees of the trust and disclaim pecuniary and economic interest in the trust . the board of directors of cadence reviewed the transactions and concluded that it was in the best interests of cadence to proceed with the transactions . mr . tan recused himself from the board of directors 2019 discussion of the valuation of nusemi inc and rocketick technologies ltd . and on whether to proceed with the transactions . acquisition-related transaction costs there were no direct transaction costs associated with acquisitions during fiscal 2018 . transaction costs associated with acquisitions were $ 0.6 million and $ 1.1 million during fiscal 2017 and 2016 , respectively . these costs consist of professional fees and administrative costs and were expensed as incurred in cadence 2019s consolidated income statements . note 9 . goodwill and acquired intangibles goodwill the changes in the carrying amount of goodwill during fiscal 2018 and 2017 were as follows : gross carrying amount ( in thousands ) .
</details>

<details><summary>Text after the table</summary>

cadence completed its annual goodwill impairment test during the third quarter of fiscal 2018 and determined that the fair value of cadence 2019s single reporting unit substantially exceeded the carrying amount of its net assets and that no impairment existed. .
</details>

## 17. `CE/2007/page_125.pdf-4`  (screen: disagree)

**Question:** what is the percent of interest and penalties as part of the unrecognized tax benefits as of december 312007

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `18%` | `0.018` | `divide(36, 2000)` |

**Gold facts**
- `text_20` as of december 31 , 2007 , the company has recorded a liability of approximately $ 36 million for interest and penalties .
- `text_24` during the quarter ended march 31 , 2007 , the company received final assessments in germany for the prior examination period , 1997 to 2000 .

**Table**

|  | year ended december 31 2007 ( in $ millions ) |
| --- | --- |
| balance as of january 1 2007 | 193 |
| increases in tax positions for the current year | 2 |
| increases in tax positions for prior years | 28 |
| decreases in tax positions of prior years | -21 ( 21 ) |
| settlements | -2 ( 2 ) |
| balance as of december 31 2007 | 200 |

<details><summary>Text before the table</summary>

determined that it will primarily be subject to the ietu in future periods , and as such it has recorded tax expense of approximately $ 20 million in 2007 for the deferred tax effects of the new ietu system . as of december 31 , 2007 , the company had us federal net operating loss carryforwards of approximately $ 206 million which will begin to expire in 2023 . of this amount , $ 47 million relates to the pre-acquisition period and is subject to limitation . the remaining $ 159 million is subject to limitation as a result of the change in stock ownership in may 2006 . this limitation is not expected to have a material impact on utilization of the net operating loss carryforwards . the company also had foreign net operating loss carryforwards as of december 31 , 2007 of approximately $ 564 million for canada , germany , mexico and other foreign jurisdictions with various expiration dates . net operating losses in canada have various carryforward periods and began expiring in 2007 . net operating losses in germany have no expiration date . net operating losses in mexico have a ten year carryforward period and begin to expire in 2009 . however , these losses are not available for use under the new ietu tax regulations in mexico . as the ietu is the primary system upon which the company will be subject to tax in future periods , no deferred tax asset has been reflected in the balance sheet as of december 31 , 2007 for these income tax loss carryforwards . the company adopted the provisions of fin 48 effective january 1 , 2007 . fin 48 clarifies the accounting for income taxes by prescribing a minimum recognition threshold a tax benefit is required to meet before being recognized in the financial statements . fin 48 also provides guidance on derecognition , measurement , classification , interest and penalties , accounting in interim periods , disclosure and transition . as a result of the implementation of fin 48 , the company increased retained earnings by $ 14 million and decreased goodwill by $ 2 million . in addition , certain tax liabilities for unrecognized tax benefits , as well as related potential penalties and interest , were reclassified from current liabilities to long-term liabilities . liabilities for unrecognized tax benefits as of december 31 , 2007 relate to various us and foreign jurisdictions . a reconciliation of the beginning and ending amount of unrecognized tax benefits is as follows : year ended december 31 , 2007 ( in $ millions ) .
</details>

<details><summary>Text after the table</summary>

included in the unrecognized tax benefits of $ 200 million as of december 31 , 2007 is $ 56 million of tax benefits that , if recognized , would reduce the company 2019s effective tax rate . the company recognizes interest and penalties related to unrecognized tax benefits in the provision for income taxes . as of december 31 , 2007 , the company has recorded a liability of approximately $ 36 million for interest and penalties . this amount includes an increase of approximately $ 13 million for the year ended december 31 , 2007 . the company operates in the united states ( including multiple state jurisdictions ) , germany and approximately 40 other foreign jurisdictions including canada , china , france , mexico and singapore . examinations are ongoing in a number of those jurisdictions including , most significantly , in germany for the years 2001 to 2004 . during the quarter ended march 31 , 2007 , the company received final assessments in germany for the prior examination period , 1997 to 2000 . the effective settlement of those examinations resulted in a reduction to goodwill of approximately $ 42 million with a net expected cash outlay of $ 29 million . the company 2019s celanese corporation and subsidiaries notes to consolidated financial statements 2014 ( continued ) %%transmsg*** transmitting job : y48011 pcn : 122000000 ***%%pcmsg|f-49 |00023|yes|no|02/26/2008 22:07|0|0|page is valid , no graphics -- color : d| .
</details>

## 18. `CE/2017/page_37.pdf-2`  (screen: disagree)

**Question:** what is the total authorized the aggregate repurchase of common stock since february 2008 including the additional amount authorized in 2017 in billions

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `5.3` | `5.4` | `add(3.9, 1.5)` |

**Gold facts**
- `text_2` ( 2 ) our board of directors has authorized the aggregate repurchase of $ 3.9 billion of our common stock since february 2008 , including an increase of $ 1.5 billion on july 17 , 2017 .

**Table**

| period | totalnumberof sharespurchased ( 1 ) | averageprice paidper share | total numberof sharespurchased aspart of publiclyannounced program | approximatedollarvalue of sharesremaining thatmay bepurchased underthe program ( 2 ) |
| --- | --- | --- | --- | --- |
| october 1 - 31 2017 | 10676 | $ 104.10 | 2014 | $ 1531000000 |
| november 1 - 30 2017 | 924 | $ 104.02 | 2014 | $ 1531000000 |
| december 1 - 31 2017 | 38605 | $ 106.36 | 2014 | $ 1531000000 |
| total | 50205 |  | 2014 |  |

<details><summary>Text before the table</summary>

table of contents celanese purchases of its equity securities information regarding repurchases of our common stock during the three months ended december 31 , 2017 is as follows : period number of shares purchased ( 1 ) average price paid per share total number of shares purchased as part of publicly announced program approximate dollar value of shares remaining that may be purchased under the program ( 2 ) .
</details>

<details><summary>Text after the table</summary>

___________________________ ( 1 ) represents shares withheld from employees to cover their statutory minimum withholding requirements for personal income taxes related to the vesting of restricted stock units . ( 2 ) our board of directors has authorized the aggregate repurchase of $ 3.9 billion of our common stock since february 2008 , including an increase of $ 1.5 billion on july 17 , 2017 . see note 17 - stockholders' equity in the accompanying consolidated financial statements for further information. .
</details>

## 19. `CME/2012/page_103.pdf-1`  (screen: disagree)

**Question:** what is the percentage change in the balance of non-controlling interests from 2011 to 2012?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `14.9%` | `0.12995` | `subtract(80.8, 70.3), divide(#0, 80.8)` |

**Gold facts**
- `table_6` ( in millions ) the balance at december 31 of 2012 is $ 80.8 ; the balance at december 31 of 2011 is $ 70.3 ; the balance at december 31 of 2010 is $ 68.1 ;

**Table**

| ( in millions ) | 2012 | 2011 | 2010 |
| --- | --- | --- | --- |
| balance at january 1 | $ 70.3 | $ 68.1 | $ 2014 |
| contribution by dow jones | 2014 | 2014 | 675.0 |
| distribution to dow jones | 2014 | 2014 | -607.5 ( 607.5 ) |
| allocation of stock-based compensation | 2014 | 0.1 | 2014 |
| total comprehensive income attributable to redeemable non-controlling interest | 10.5 | 2.1 | 0.6 |
| balance at december 31 | $ 80.8 | $ 70.3 | $ 68.1 |

<details><summary>Text before the table</summary>

positions and collateral of the defaulting firm at each respective clearing organization , and taking into account any cross-margining loss sharing payments , any of the participating clearing organizations has a remaining liquidating surplus , and any other participating clearing organization has a remaining liquidating deficit , any additional surplus from the liquidation would be shared with the other clearing house to the extent that it has a remaining liquidating deficit . any remaining surplus funds would be passed to the bankruptcy trustee . mf global bankruptcy trust . the company provided a $ 550.0 million financial guarantee to the bankruptcy trustee of mf global to accelerate the distribution of funds to mf global customers . in the event that the trustee distributed more property in the second or third interim distributions than was permitted by the bankruptcy code and cftc regulations , the company will make a cash payment to the trustee for the amount of the erroneous distribution or distributions up to $ 550.0 million in the aggregate . a payment will only be made after the trustee makes reasonable efforts to collect the property erroneously distributed to the customer ( s ) . if a payment is made by the company , the company may have the right to seek reimbursement of the erroneously distributed property from the applicable customer ( s ) . the guarantee does not cover distributions made by the trustee to customers on the basis of their claims filed in the bankruptcy . because the trustee has now made payments to nearly all customers on the basis of their claims , the company believes that the likelihood of payment to the trustee is very remote . as a result , the guarantee liability is estimated to be immaterial at december 31 , 2012 . family farmer and rancher protection fund . in april 2012 , the company established the family farmer and rancher protection fund ( the fund ) . the fund is designed to provide payments , up to certain maximum levels , to family farmers , ranchers and other agricultural industry participants who use cme group agricultural products and who suffer losses to their segregated account balances due to their cme clearing member becoming insolvent . under the terms of the fund , farmers and ranchers are eligible for up to $ 25000 per participant . farming and ranching cooperatives are eligible for up to $ 100000 per cooperative . the fund has an aggregate maximum payment amount of $ 100.0 million . if payments to participants were to exceed this amount , payments would be pro-rated . clearing members and customers must register in advance with the company and provide certain documentation in order to substantiate their eligibility . peregrine financial group , inc . ( pfg ) filed for bankruptcy protection on july 10 , 2012 . pfg was not one of cme 2019s clearing members and its customers had not registered for the fund . accordingly , they were not technically eligible for payments from the fund . however , because the fund was newly implemented and because pfg 2019s customers included many agricultural industry participants for whom the program was designed , the company decided to waive certain terms and conditions of the fund , solely in connection with the pfg bankruptcy , so that otherwise eligible family farmers , ranchers and agricultural cooperatives could apply for and receive benefits from cme . based on the number of such pfg customers who applied and the estimated size of their claims , the company has recorded a liability in the amount of $ 2.1 million at december 31 , 2012 . 16 . redeemable non-controlling interest the following summarizes the changes in redeemable non-controlling interest for the years presented . non- controlling interests that do not contain redemption features are presented in the statements of equity. .
</details>

<details><summary>Text after the table</summary>

contribution by dow jones . . . . . . . . . . . 2014 2014 675.0 distribution to dow jones . . . . . . . . . . . 2014 2014 ( 607.5 ) allocation of stock- compensation . . . . 2014 0.1 2014 total comprehensive income attributable to redeemable non- controlling interest . . . . . . . . . . 10.5 2.1 0.6 balance at december 31 . . . . . . . . . $ 80.8 $ 70.3 $ 68.1 .
</details>

## 20. `DRE/2009/page_60.pdf-2`  (screen: disagree)

**Question:** what was the ratio of the net fair value of acquired assets and liabilities to the advances and equity

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `0.994` | `1.00513` | `add(173006, 34908), divide(#0, 206852)` |

**Gold facts**
- `table_1` net fair value of acquired assets and liabilities the less advances to acquired entities eliminated upon consolidation of $ 206852 is -173006 ( 173006 ) ;
- `table_2` net fair value of acquired assets and liabilities the less acquisition date carrying value of equity in acquired entities of $ 206852 is -34908 ( 34908 ) ;

**Table**

| net fair value of acquired assets and liabilities | $ 206852 |
| --- | --- |
| less advances to acquired entities eliminated upon consolidation | -173006 ( 173006 ) |
| less acquisition date carrying value of equity in acquired entities | -34908 ( 34908 ) |
| loss on business combination | $ -1062 ( 1062 ) |

<details><summary>Text before the table</summary>

58| | duke realty corporation annual report 2009 we recognized a loss of $ 1.1 million upon acquisition , which represents the difference between the fair value of the recognized assets and the carrying value of our pre-existing equity interest . the acquisition date fair value of the net recognized assets as compared to the acquisition date carrying value of our outstanding advances and accrued interest , as well as the acquisition date carrying value of our pre-existing equity interests , is shown as follows ( in thousands ) : .
</details>

<details><summary>Text after the table</summary>

since april 1 , 2009 , the results of operations for both acquired entities have been included in continuing operations in our consolidated financial statements . due to our significant pre-existing ownership and financing positions in the two acquired entities , the inclusion of their results of operations did not have a material effect on our operating income . acquisitions we acquired income producing real estate related assets of $ 32.1 million , $ 60.5 million and $ 219.9 million in 2009 , 2008 and 2007 , respectively . in december 2007 , in order to further establish our property positions around strategic port locations , we purchased a portfolio of five industrial buildings in seattle , virginia and houston , as well as approximately 161 acres of undeveloped land and a 12-acre container storage facility in houston . the total price was $ 89.7 million and was financed in part through assumption of secured debt that had a fair value of $ 34.3 million . of the total purchase price , $ 64.1 million was allocated to in-service real estate assets , $ 20.0 million was allocated to undeveloped land and the container storage facility , $ 5.4 million was allocated to lease related intangible assets , and the remaining amount was allocated to acquired working capital related assets and liabilities . the results of operations for the acquired properties since the date of acquisition have been included in continuing rental operations in our consolidated financial statements . all other acquisitions were not individually material . dispositions we disposed of income producing real estate related assets with gross proceeds of $ 267.0 million , $ 426.2 million and $ 590.4 million in 2009 , 2008 and 2007 , respectively . we sold five properties in 2009 and seven properties in 2008 to an unconsolidated joint venture . the gross proceeds totaled $ 84.3 million and $ 226.2 million for the years ended december 31 , 2009 and 2008 , respectively . in march 2007 , as part of our capital recycling program , we sold a portfolio of eight suburban office properties totaling 894000 square feet in the cleveland market . the sales price totaled $ 140.4 million , of which we received net proceeds of $ 139.3 million . we also sold a portfolio of twelve flex and light industrial properties in july 2007 , totaling 865000 square feet in the st . louis market , for a sales price of $ 65.0 million , of which we received net proceeds of $ 64.2 million . all other dispositions were not individually material . ( 4 ) related party transactions we provide property management , leasing , construction and other tenant related services to unconsolidated companies in which we have equity interests . for the years ended december 31 , 2009 , 2008 and 2007 , respectively , we earned management fees of $ 8.4 million , $ 7.8 million and $ 7.1 million , leasing fees of $ 4.2 million , $ 2.8 million and $ 4.2 million and construction and development fees of $ 10.2 million , $ 12.7 million and $ 13.1 million from these companies . we recorded these fees based on contractual terms that approximate market rates for these types of .
</details>

## 21. `ETR/2008/page_154.pdf-3`  (screen: disagree)

**Question:** what percent lower is the net present than the total payments value of lease payments?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `15.67%` | `1.18576` | `divide(350161, 295304)` |

**Gold facts**
- `table_7` the total of amount ( in thousands ) is 350161 ;
- `table_9` the present value of net minimum lease payments of amount ( in thousands ) is $ 295304 ;
- `text_0` entergy corporation and subsidiaries notes to financial statements as of december 31 , 2008 , system energy had future minimum lease payments ( reflecting an implicit rate of 5.13% ( 5.13 % ) ) , which are recorded as long-term debt as follows : amount ( in thousands ) .

**Table**

|  | amount ( in thousands ) |
| --- | --- |
| 2009 | $ 47760 |
| 2010 | 48569 |
| 2011 | 49437 |
| 2012 | 49959 |
| 2013 | 50546 |
| years thereafter | 103890 |
| total | 350161 |
| less : amount representing interest | 54857 |
| present value of net minimum lease payments | $ 295304 |

<details><summary>Text before the table</summary>

entergy corporation and subsidiaries notes to financial statements as of december 31 , 2008 , system energy had future minimum lease payments ( reflecting an implicit rate of 5.13% ( 5.13 % ) ) , which are recorded as long-term debt as follows : amount ( in thousands ) .
</details>

<details><summary>Text after the table</summary>

.
</details>

## 22. `ETR/2008/page_356.pdf-2`  (screen: disagree)

**Question:** what percent of the net change in revenue between 2006 and 2007 was due to fuel recovery?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `109%` | `1.09794` | `subtract(231.0, 192.2), divide(42.6, #0)` |

**Gold facts**
- `table_1` the 2006 net revenue of amount ( in millions ) is $ 192.2 ;
- `table_2` the fuel recovery of amount ( in millions ) is 42.6 ;
- `table_7` the 2007 net revenue of amount ( in millions ) is $ 231.0 ;

**Table**

|  | amount ( in millions ) |
| --- | --- |
| 2006 net revenue | $ 192.2 |
| fuel recovery | 42.6 |
| volume/weather | 25.6 |
| rider revenue | 8.5 |
| net wholesale revenue | -41.2 ( 41.2 ) |
| other | 3.3 |
| 2007 net revenue | $ 231.0 |

<details><summary>Text before the table</summary>

entergy new orleans , inc . management's financial discussion and analysis 2007 compared to 2006 net revenue consists of operating revenues net of : 1 ) fuel , fuel-related expenses , and gas purchased for resale , 2 ) purchased power expenses , and 3 ) other regulatory charges . following is an analysis of the change in net revenue comparing 2007 to 2006 . amount ( in millions ) .
</details>

<details><summary>Text after the table</summary>

the fuel recovery variance is due to the inclusion of grand gulf costs in fuel recoveries effective july 1 , 2006 . in june 2006 , the city council approved the recovery of grand gulf costs through the fuel adjustment clause , without a corresponding change in base rates ( a significant portion of grand gulf costs was previously recovered through base rates ) . the volume/weather variance is due to an increase in electricity usage in the service territory in 2007 compared to the same period in 2006 . the first quarter 2006 was affected by customer losses following hurricane katrina . entergy new orleans estimates that approximately 132000 electric customers and 86000 gas customers have returned and are taking service as of december 31 , 2007 , compared to approximately 95000 electric customers and 65000 gas customers as of december 31 , 2006 . billed retail electricity usage increased a total of 540 gwh compared to the same period in 2006 , an increase of 14% ( 14 % ) . the rider revenue variance is due primarily to a storm reserve rider effective march 2007 as a result of the city council's approval of a settlement agreement in october 2006 . the approved storm reserve has been set to collect $ 75 million over a ten-year period through the rider and the funds will be held in a restricted escrow account . the settlement agreement is discussed in note 2 to the financial statements . the net wholesale revenue variance is due to more energy available for resale in 2006 due to the decrease in retail usage caused by customer losses following hurricane katrina . in addition , 2006 revenue includes the sales into the wholesale market of entergy new orleans' share of the output of grand gulf , pursuant to city council approval of measures proposed by entergy new orleans to address the reduction in entergy new orleans' retail customer usage caused by hurricane katrina and to provide revenue support for the costs of entergy new orleans' share of grand other income statement variances 2008 compared to 2007 other operation and maintenance expenses decreased primarily due to : a provision for storm-related bad debts of $ 11 million recorded in 2007 ; a decrease of $ 6.2 million in legal and professional fees ; a decrease of $ 3.4 million in employee benefit expenses ; and a decrease of $ 1.9 million in gas operations spending due to higher labor and material costs for reliability work in 2007. .
</details>

## 23. `ETR/2011/page_398.pdf-2`  (screen: disagree)

**Question:** what will be the yearly interest expense for system energy vie for the note issued in 2012 , ( in millions ) ?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `2.0` | `49.9598` | `subtract(50, 4.02%)` |

**Gold facts**
- `text_2` system energy may refinance , redeem , or otherwise retire debt prior to maturity , to the extent market conditions and interest and dividend rates are favorable .
- `text_6` in february 2012 , system energy vie issued $ 50 million of 4.02% ( 4.02 % ) series h notes due february 2017 .

**Table**

| 2011 | 2010 | 2009 | 2008 |
| --- | --- | --- | --- |
| ( in thousands ) | ( in thousands ) | ( in thousands ) | ( in thousands ) |
| $ 120424 | $ 97948 | $ 90507 | $ 42915 |

<details><summary>Text before the table</summary>

system energy resources , inc . management 2019s financial discussion and analysis sources of capital system energy 2019s sources to meet its capital requirements include : internally generated funds ; cash on hand ; debt issuances ; and bank financing under new or existing facilities . system energy may refinance , redeem , or otherwise retire debt prior to maturity , to the extent market conditions and interest and dividend rates are favorable . all debt and common stock issuances by system energy require prior regulatory approval . debt issuances are also subject to issuance tests set forth in its bond indentures and other agreements . system energy has sufficient capacity under these tests to meet its foreseeable capital needs . in february 2012 , system energy vie issued $ 50 million of 4.02% ( 4.02 % ) series h notes due february 2017 . system energy used the proceeds to purchase additional nuclear fuel . system energy has obtained a short-term borrowing authorization from the ferc under which it may borrow , through october 2013 , up to the aggregate amount , at any one time outstanding , of $ 200 million . see note 4 to the financial statements for further discussion of system energy 2019s short-term borrowing limits . system energy has also obtained an order from the ferc authorizing long-term securities issuances . the current long-term authorization extends through july 2013 . system energy 2019s receivables from the money pool were as follows as of december 31 for each of the following years: .
</details>

<details><summary>Text after the table</summary>

see note 4 to the financial statements for a description of the money pool . nuclear matters system energy owns and operates grand gulf . system energy is , therefore , subject to the risks related to owning and operating a nuclear plant . these include risks from the use , storage , handling and disposal of high- level and low-level radioactive materials , regulatory requirement changes , including changes resulting from events at other plants , limitations on the amounts and types of insurance commercially available for losses in connection with nuclear operations , and technological and financial uncertainties related to decommissioning nuclear plants at the end of their licensed lives , including the sufficiency of funds in decommissioning trusts . in the event of an unanticipated early shutdown of grand gulf , system energy may be required to provide additional funds or credit support to satisfy regulatory requirements for decommissioning . after the nuclear incident in japan resulting from the march 2011 earthquake and tsunami , the nrc established a task force to conduct a review of processes and regulations relating to nuclear facilities in the united states . the task force issued a near term ( 90-day ) report in july 2011 that has made recommendations , which are currently being evaluated by the nrc . it is anticipated that the nrc will issue certain orders and requests for information to nuclear plant licensees by the end of the first quarter 2012 that will begin to implement the task force 2019s recommendations . these orders may require u.s . nuclear operators , including entergy , to undertake plant modifications or perform additional analyses that could , among other things , result in increased costs and capital requirements associated with operating entergy 2019s nuclear plants. .
</details>

## 24. `GPN/2017/page_30.pdf-1`  (screen: disagree)

**Question:** what is the total return if 1000000 is invested in global payments in may 31 , 2012 and liquidated in may 31 , 2015?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1467200` | `10753.28` | `subtract(246.72, const_1000), divide(1000000, 100), subtract(#1, #0)` |

**Gold facts**
- `table_1` the may 31 2012 of globalpayments is $ 100.00 ; the may 31 2012 of s&p500 index is $ 100.00 ; the may 31 2012 of s&pinformationtechnology index is $ 100.00 ;
- `table_4` the may 31 2015 of globalpayments is 246.72 ; the may 31 2015 of s&p500 index is 171.40 ; the may 31 2015 of s&pinformationtechnology index is 169.46 ;
- `text_1` the line graph assumes the investment of $ 100 in our common stock , the standard & poor 2019s 500 index and the standard & poor 2019s information technology index on may 31 , 2012 and assumes reinvestment of all dividends .

**Table**

|  | globalpayments | s&p500 index | s&pinformationtechnology index |
| --- | --- | --- | --- |
| may 31 2012 | $ 100.00 | $ 100.00 | $ 100.00 |
| may 31 2013 | 113.10 | 127.28 | 115.12 |
| may 31 2014 | 161.90 | 153.30 | 142.63 |
| may 31 2015 | 246.72 | 171.40 | 169.46 |
| may 31 2016 | 367.50 | 174.34 | 174.75 |
| december 31 2016 | 328.42 | 188.47 | 194.08 |
| december 31 2017 | 474.52 | 229.61 | 269.45 |

<details><summary>Text before the table</summary>

stock performance graph the following graph compares our cumulative shareholder returns with the standard & poor 2019s information technology index and the standard & poor 2019s 500 index for the year ended december 31 , 2017 , the 2016 fiscal transition period , and the years ended may 31 , 2016 , 2015 , 2014 and 2013 . the line graph assumes the investment of $ 100 in our common stock , the standard & poor 2019s 500 index and the standard & poor 2019s information technology index on may 31 , 2012 and assumes reinvestment of all dividends . 5/12 5/165/155/145/13 global payments inc . s&p 500 s&p information technology 12/16 12/17 comparison of 5 year cumulative total return* among global payments inc. , the s&p 500 index and the s&p information technology index * $ 100 invested on may 31 , 2012 in stock or index , including reinvestment of dividends . copyright a9 2018 standard & poor 2019s , a division of s&p global . all rights reserved . global payments 500 index information technology .
</details>

<details><summary>Text after the table</summary>

30 2013 global payments inc . | 2017 form 10-k annual report .
</details>

## 25. `GS/2015/page_76.pdf-2`  (screen: disagree)

**Question:** in millions for 2015 , 2014 , and 2013 , what were the largest amount of debt securities and loans?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `2264` | `2246.0` | `table_max(debt securities and loans, none)` |

**Gold facts**
- `table_2` $ in millions the debt securities and loans of year ended december 2015 is 1655 ; the debt securities and loans of year ended december 2014 is 2246 ; the debt securities and loans of year ended december 2013 is 2044 ;

**Table**

| $ in millions | year ended december 2015 | year ended december 2014 | year ended december 2013 |
| --- | --- | --- | --- |
| equity securities | $ 3781 | $ 4579 | $ 4974 |
| debt securities and loans | 1655 | 2246 | 2044 |
| total net revenues1 | 5436 | 6825 | 7018 |
| operating expenses | 2402 | 2819 | 2686 |
| pre-tax earnings | $ 3034 | $ 4006 | $ 4332 |

<details><summary>Text before the table</summary>

the goldman sachs group , inc . and subsidiaries management 2019s discussion and analysis investing & lending investing & lending includes our investing activities and the origination of loans to provide financing to clients . these investments and loans are typically longer-term in nature . we make investments , some of which are consolidated , directly and indirectly through funds and separate accounts that we manage , in debt securities and loans , public and private equity securities , and real estate entities . the table below presents the operating results of our investing & lending segment. .
</details>

<details><summary>Text after the table</summary>

1 . net revenues related to our consolidated investments , previously reported in other net revenues within investing & lending , are now reported in equity securities and debt securities and loans , as results from these activities ( $ 391 million for 2015 ) are no longer significant principally due to the sale of metro in the fourth quarter of 2014 . reclassifications have been made to previously reported amounts to conform to the current presentation . 2015 versus 2014 . net revenues in investing & lending were $ 5.44 billion for 2015 , 20% ( 20 % ) lower than 2014 . this decrease was primarily due to lower net revenues from investments in equities , principally reflecting the sale of metro in the fourth quarter of 2014 and lower net gains from investments in private equities , driven by corporate performance . in addition , net revenues in debt securities and loans were significantly lower , reflecting lower net gains from investments . although net revenues in investing & lending for 2015 benefited from favorable company-specific events , including sales , initial public offerings and financings , a decline in global equity prices and widening high-yield credit spreads during the second half of the year impacted results . concern about the outlook for the global economy continues to be a meaningful consideration for the global marketplace . if equity markets continue to decline or credit spreads widen further , net revenues in investing & lending would likely continue to be negatively impacted . operating expenses were $ 2.40 billion for 2015 , 15% ( 15 % ) lower than 2014 , due to lower depreciation and amortization expenses , primarily reflecting lower impairment charges related to consolidated investments , and a reduction in expenses related to the sale of metro in the fourth quarter of 2014 . pre-tax earnings were $ 3.03 billion in 2015 , 24% ( 24 % ) lower than 2014 . 2014 versus 2013 . net revenues in investing & lending were $ 6.83 billion for 2014 , 3% ( 3 % ) lower than 2013 . net revenues from investments in equity securities were lower due to a significant decrease in net gains from investments in public equities , as movements in global equity prices during 2014 were less favorable compared with 2013 , as well as significantly lower net revenues related to our consolidated investments , reflecting a decrease in operating revenues from commodities-related consolidated investments . these decreases were partially offset by an increase in net gains from investments in private equities , primarily driven by company-specific events . net revenues from debt securities and loans were higher than 2013 , reflecting a significant increase in net interest income , primarily driven by increased lending , and a slight increase in net gains , primarily due to sales of certain investments during 2014 . during 2014 , net revenues in investing & lending generally reflected favorable company-specific events , including initial public offerings and financings , and strong corporate performance , as well as net gains from sales of certain investments . operating expenses were $ 2.82 billion for 2014 , 5% ( 5 % ) higher than 2013 , reflecting higher compensation and benefits expenses , partially offset by lower expenses related to consolidated investments . pre-tax earnings were $ 4.01 billion in 2014 , 8% ( 8 % ) lower than 2013 . 64 goldman sachs 2015 form 10-k .
</details>

## 26. `GS/2017/page_76.pdf-4`  (screen: disagree)

**Question:** in billions for 2017 , 2016 , and 2015 , what was the average in alternative investments?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `151` | `152.0` | `table_average(alternative investments, none)` |

**Gold facts**
- `table_1` $ in billions the alternative investments of average for theyear ended december 2017 is $ 162 ; the alternative investments of average for theyear ended december 2016 is $ 149 ; the alternative investments of average for theyear ended december 2015 is $ 145 ;

**Table**

| $ in billions | average for theyear ended december 2017 | average for theyear ended december 2016 | average for theyear ended december 2015 |
| --- | --- | --- | --- |
| alternative investments | $ 162 | $ 149 | $ 145 |
| equity | 292 | 256 | 247 |
| fixed income | 633 | 578 | 530 |
| total long-term aus | 1087 | 983 | 922 |
| liquidity products | 330 | 326 | 272 |
| total aus | $ 1417 | $ 1309 | $ 1194 |

<details><summary>Text before the table</summary>

the goldman sachs group , inc . and subsidiaries management 2019s discussion and analysis the table below presents our average monthly assets under supervision by asset class . average for the year ended december $ in billions 2017 2016 2015 .
</details>

<details><summary>Text after the table</summary>

operating environment . during 2017 , investment management operated in an environment characterized by generally higher asset prices , resulting in appreciation in both equity and fixed income assets . in addition , our long- term assets under supervision increased from net inflows primarily in fixed income and alternative investment assets . these increases were partially offset by net outflows in liquidity products . as a result , the mix of average assets under supervision during 2017 shifted slightly from liquidity products to long-term assets under supervision as compared to the mix at the end of 2016 . in the future , if asset prices decline , or investors favor assets that typically generate lower fees or investors withdraw their assets , net revenues in investment management would likely be negatively impacted . following a challenging first quarter of 2016 , market conditions improved during the remainder of 2016 with higher asset prices resulting in full year appreciation in both equity and fixed income assets . also , our assets under supervision increased during 2016 from net inflows , primarily in fixed income assets , and liquidity products . the mix of our average assets under supervision shifted slightly compared with 2015 from long-term assets under supervision to liquidity products . management fees were impacted by many factors , including inflows to advisory services and outflows from actively-managed mutual funds . 2017 versus 2016 . net revenues in investment management were $ 6.22 billion for 2017 , 7% ( 7 % ) higher than 2016 , due to higher management and other fees , reflecting higher average assets under supervision , and higher transaction revenues . during the year , total assets under supervision increased $ 115 billion to $ 1.49 trillion . long- term assets under supervision increased $ 128 billion , including net market appreciation of $ 86 billion , primarily in equity and fixed income assets , and net inflows of $ 42 billion ( which includes $ 20 billion of inflows in connection with the verus acquisition and $ 5 billion of equity asset outflows in connection with the australian divestiture ) , primarily in fixed income and alternative investment assets . liquidity products decreased $ 13 billion ( which includes $ 3 billion of inflows in connection with the verus acquisition ) . operating expenses were $ 4.80 billion for 2017 , 3% ( 3 % ) higher than 2016 , primarily due to increased compensation and benefits expenses , reflecting higher net revenues . pre-tax earnings were $ 1.42 billion in 2017 , 25% ( 25 % ) higher than 2016 versus 2015 . net revenues in investment management were $ 5.79 billion for 2016 , 7% ( 7 % ) lower than 2015 . this decrease primarily reflected significantly lower incentive fees compared with a strong 2015 . in addition , management and other fees were slightly lower , reflecting shifts in the mix of client assets and strategies , partially offset by the impact of higher average assets under supervision . during 2016 , total assets under supervision increased $ 127 billion to $ 1.38 trillion . long-term assets under supervision increased $ 75 billion , including net inflows of $ 42 billion , primarily in fixed income assets , and net market appreciation of $ 33 billion , primarily in equity and fixed income assets . in addition , liquidity products increased $ 52 billion . operating expenses were $ 4.65 billion for 2016 , 4% ( 4 % ) lower than 2015 , due to decreased compensation and benefits expenses , reflecting lower net revenues . pre-tax earnings were $ 1.13 billion in 2016 , 17% ( 17 % ) lower than 2015 . geographic data see note 25 to the consolidated financial statements for a summary of our total net revenues , pre-tax earnings and net earnings by geographic region . goldman sachs 2017 form 10-k 63 .
</details>

## 27. `HOLX/2005/page_27.pdf-1`  (screen: disagree)

**Question:** what is the total number of votes that participated in this proposal?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `18813643` | `1273628.0` | `table_sum(17695228, 963202), add(#0, 155213)` |

**Gold facts**
- `table_1` for the 17695228 of against is 963202 ; the 17695228 of abstained is 155213 ; the 17695228 of broker non-votes is 0 ;

**Table**

| for | against | abstained | broker non-votes |
| --- | --- | --- | --- |
| 17695228 | 963202 | 155213 | 0 |

<details><summary>Text before the table</summary>

leased real property in september 2002 , we completed a sale/leaseback transaction for our 200000 square foot headquarters and manufacturing facility located in bedford , massachusetts and our 62500 square foot lorad manufacturing facility in danbury , connecticut . the lease for these facilities , including the associated land , has a term of 20 years , with four-five year renewal options . we sublease approximately 10000 square feet of the bedford facility to a subtenant , cmp media , under a lease which expires in may 2006 . we also sublease approximately 11000 square feet of the bedford facility to a subtenant , genesys conferencing , under a lease which expires in february we lease a 60000 square feet of office and manufacturing space in danbury , connecticut near our lorad manufacturing facility . this lease expires in december 2012 . we also lease a sales and service office in belgium . item 3 . legal proceedings . in march 2005 , we were served with a complaint filed on november 12 , 2004 by oleg sokolov with the united states district court for the district of connecticut alleging that our htc 2122 grid infringes u.s . patent number 5970118 . the plaintiff is seeking to preliminarily and permanently enjoin us from infringing the patent , as well as damages resulting from the alleged infringement , treble damages and reasonable attorney fees , and such other and further relief as may be available . on april 25 , 2005 , we filed an answer and counterclaims in response to the complaint in which we denied the plaintiff 2019s allegations and , among other things , sought declaratory relief with respect to the patent claims and damages , as well as other relief . on october 28 , 1998 , the plaintiff had previously sued lorad , asserting , among other things , that lorad had misappropriated the plaintiff 2019s trade secrets relating to the htc grid . this previous case was dismissed on august 28 , 2000 . the dismissal was affirmed by the appellate court of the state of connecticut , and the united states supreme court refused to grant certiorari . we do not believe that we infringe any valid or enforceable patents of the plaintiff . however , while we intend to vigorously defend our interests , ongoing litigation can be costly and time consuming , and we cannot guarantee that we will prevail . item 4 . submission of matters to a vote of security holders . at a special meeting of stockholders held november 15 , 2005 , our stockholders approved a proposal to amend our certificate of incorporation to increase the number of shares of common stock the company has authority to issue from 30 million to 90 million . the voting results for the proposal , not adjusted for the effect of the stock split , were as follows: .
</details>

<details><summary>Text after the table</summary>

as a result of the amendment , the previously announced two-for-one stock split to be effected as a stock dividend , was paid on november 30 , 2005 to stockholders of record on november 16 , 2005. .
</details>

## 28. `HOLX/2005/page_27.pdf-2`  (screen: disagree)

**Question:** what portion of the votes support the proposal?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `94.1%` | `13.89356` | `table_sum(17695228, 963202), add(#0, 155213), divide(17695228, #1)` |

**Gold facts**
- `table_1` for the 17695228 of against is 963202 ; the 17695228 of abstained is 155213 ; the 17695228 of broker non-votes is 0 ;

**Table**

| for | against | abstained | broker non-votes |
| --- | --- | --- | --- |
| 17695228 | 963202 | 155213 | 0 |

<details><summary>Text before the table</summary>

leased real property in september 2002 , we completed a sale/leaseback transaction for our 200000 square foot headquarters and manufacturing facility located in bedford , massachusetts and our 62500 square foot lorad manufacturing facility in danbury , connecticut . the lease for these facilities , including the associated land , has a term of 20 years , with four-five year renewal options . we sublease approximately 10000 square feet of the bedford facility to a subtenant , cmp media , under a lease which expires in may 2006 . we also sublease approximately 11000 square feet of the bedford facility to a subtenant , genesys conferencing , under a lease which expires in february we lease a 60000 square feet of office and manufacturing space in danbury , connecticut near our lorad manufacturing facility . this lease expires in december 2012 . we also lease a sales and service office in belgium . item 3 . legal proceedings . in march 2005 , we were served with a complaint filed on november 12 , 2004 by oleg sokolov with the united states district court for the district of connecticut alleging that our htc 2122 grid infringes u.s . patent number 5970118 . the plaintiff is seeking to preliminarily and permanently enjoin us from infringing the patent , as well as damages resulting from the alleged infringement , treble damages and reasonable attorney fees , and such other and further relief as may be available . on april 25 , 2005 , we filed an answer and counterclaims in response to the complaint in which we denied the plaintiff 2019s allegations and , among other things , sought declaratory relief with respect to the patent claims and damages , as well as other relief . on october 28 , 1998 , the plaintiff had previously sued lorad , asserting , among other things , that lorad had misappropriated the plaintiff 2019s trade secrets relating to the htc grid . this previous case was dismissed on august 28 , 2000 . the dismissal was affirmed by the appellate court of the state of connecticut , and the united states supreme court refused to grant certiorari . we do not believe that we infringe any valid or enforceable patents of the plaintiff . however , while we intend to vigorously defend our interests , ongoing litigation can be costly and time consuming , and we cannot guarantee that we will prevail . item 4 . submission of matters to a vote of security holders . at a special meeting of stockholders held november 15 , 2005 , our stockholders approved a proposal to amend our certificate of incorporation to increase the number of shares of common stock the company has authority to issue from 30 million to 90 million . the voting results for the proposal , not adjusted for the effect of the stock split , were as follows: .
</details>

<details><summary>Text after the table</summary>

as a result of the amendment , the previously announced two-for-one stock split to be effected as a stock dividend , was paid on november 30 , 2005 to stockholders of record on november 16 , 2005. .
</details>

## 29. `HUM/2017/page_45.pdf-1`  (screen: disagree)

**Question:** what was the percent of the growth in the stock total return performance for hum from 2013 to 2014

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `41%` | `62.0` | `subtract(214, 152)` |

**Gold facts**
- `table_1` the hum of 12/31/2012 is $ 100 ; the hum of 12/31/2013 is $ 152 ; the hum of 12/31/2014 is $ 214 ; the hum of 12/31/2015 is $ 267 ; the hum of 12/31/2016 is $ 307 ; the hum of 12/31/2017 is $ 377 ;

**Table**

|  | 12/31/2012 | 12/31/2013 | 12/31/2014 | 12/31/2015 | 12/31/2016 | 12/31/2017 |
| --- | --- | --- | --- | --- | --- | --- |
| hum | $ 100 | $ 152 | $ 214 | $ 267 | $ 307 | $ 377 |
| s&p 500 | $ 100 | $ 132 | $ 150 | $ 153 | $ 171 | $ 208 |
| peer group | $ 100 | $ 137 | $ 175 | $ 186 | $ 188 | $ 238 |

<details><summary>Text before the table</summary>

stock total return performance the following graph compares our total return to stockholders with the returns of the standard & poor 2019s composite 500 index ( 201cs&p 500 201d ) and the dow jones us select health care providers index ( 201cpeer group 201d ) for the five years ended december 31 , 2017 . the graph assumes an investment of $ 100 in each of our common stock , the s&p 500 , and the peer group on december 31 , 2012 , and that dividends were reinvested when paid. .
</details>

<details><summary>Text after the table</summary>

the stock price performance included in this graph is not necessarily indicative of future stock price performance. .
</details>

## 30. `IP/2014/page_66.pdf-4`  (screen: disagree)

**Question:** what was the average net sales for north american consumer packaging from 2012

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `2.0` | `4.5` | `add(2.0, 2.0), add(#0, 2.0), add(#1, const_3), divide(#2, const_2)` |

**Gold facts**
- `text_39` north american consumer packaging net sales were $ 2.0 billion in 2014 compared with $ 2.0 billion in 2013 and $ 2.0 billion in 2012 .

**Table**

| in millions | 2014 | 2013 | 2012 |
| --- | --- | --- | --- |
| sales | $ 3403 | $ 3435 | $ 3170 |
| operating profit | 178 | 161 | 268 |

<details><summary>Text before the table</summary>

russia and europe . average sales price realizations for uncoated freesheet paper decreased in both europe and russia , reflecting weak economic conditions and soft market demand . in russia , sales prices in rubles increased , but this improvement is masked by the impact of the currency depreciation against the u.s . dollar . input costs were significantly higher for wood in both europe and russia , partially offset by lower chemical costs . planned maintenance downtime costs were $ 11 million lower in 2014 than in 2013 . manufacturing and other operating costs were favorable . entering 2015 , sales volumes in the first quarter are expected to be seasonally weaker in russia , and about flat in europe . average sales price realizations for uncoated freesheet paper are expected to remain steady in europe , but increase in russia . input costs should be lower for oil and wood , partially offset by higher chemicals costs . indian papers net sales were $ 178 million in 2014 , $ 185 million ( $ 174 million excluding excise duties which were included in net sales in 2013 and prior periods ) in 2013 and $ 185 million ( $ 178 million excluding excise duties ) in 2012 . operating profits were $ 8 million ( a loss of $ 12 million excluding a gain related to the resolution of a legal contingency ) in 2014 , a loss of $ 145 million ( a loss of $ 22 million excluding goodwill and trade name impairment charges ) in 2013 and a loss of $ 16 million in 2012 . average sales price realizations improved in 2014 compared with 2013 due to the impact of price increases implemented in 2013 . sales volumes were flat , reflecting weak economic conditions . input costs were higher , primarily for wood . operating costs and planned maintenance downtime costs were lower in 2014 . looking ahead to the first quarter of 2015 , sales volumes are expected to be seasonally higher . average sales price realizations are expected to decrease due to competitive pressures . asian printing papers net sales were $ 59 million in 2014 , $ 90 million in 2013 and $ 85 million in 2012 . operating profits were $ 0 million in 2014 and $ 1 million in both 2013 and 2012 . u.s . pulp net sales were $ 895 million in 2014 compared with $ 815 million in 2013 and $ 725 million in 2012 . operating profits were $ 57 million in 2014 compared with $ 2 million in 2013 and a loss of $ 59 million in 2012 . sales volumes in 2014 increased from 2013 for both fluff pulp and market pulp reflecting improved market demand . average sales price realizations increased significantly for fluff pulp , while prices for market pulp were also higher . input costs for wood and energy were higher . operating costs were lower , but planned maintenance downtime costs were $ 1 million higher . compared with the fourth quarter of 2014 , sales volumes in the first quarter of 2015 , are expected to decrease for market pulp , but be slightly higher for fluff pulp . average sales price realizations are expected to to be stable for fluff pulp and softwood market pulp , while hardwood market pulp prices are expected to improve . input costs should be flat . planned maintenance downtime costs should be about $ 13 million higher than in the fourth quarter of 2014 . consumer packaging demand and pricing for consumer packaging products correlate closely with consumer spending and general economic activity . in addition to prices and volumes , major factors affecting the profitability of consumer packaging are raw material and energy costs , freight costs , manufacturing efficiency and product mix . consumer packaging net sales in 2014 decreased 1% ( 1 % ) from 2013 , but increased 7% ( 7 % ) from 2012 . operating profits increased 11% ( 11 % ) from 2013 , but decreased 34% ( 34 % ) from 2012 . excluding sheet plant closure costs , costs associated with the permanent shutdown of a paper machine at our augusta , georgia mill and costs related to the sale of the shorewood business , 2014 operating profits were 11% ( 11 % ) lower than in 2013 , and 30% ( 30 % ) lower than in 2012 . benefits from higher average sales price realizations and a favorable mix ( $ 60 million ) were offset by lower sales volumes ( $ 11 million ) , higher operating costs ( $ 9 million ) , higher planned maintenance downtime costs ( $ 12 million ) , higher input costs ( $ 43 million ) and higher other costs ( $ 7 million ) . in addition , operating profits in 2014 include $ 8 million of costs associated with sheet plant closures , while operating profits in 2013 include costs of $ 45 million related to the permanent shutdown of a paper machine at our augusta , georgia mill and $ 2 million of costs associated with the sale of the shorewood business . consumer packaging .
</details>

<details><summary>Text after the table</summary>

north american consumer packaging net sales were $ 2.0 billion in 2014 compared with $ 2.0 billion in 2013 and $ 2.0 billion in 2012 . operating profits were $ 92 million ( $ 100 million excluding sheet plant closure costs ) in 2014 compared with $ 63 million ( $ 110 million excluding paper machine shutdown costs and costs related to the sale of the shorewood business ) in 2013 and $ 165 million ( $ 162 million excluding a gain associated with the sale of the shorewood business in 2012 ) . coated paperboard sales volumes in 2014 were lower than in 2013 reflecting weaker market demand . the business took about 41000 tons of market-related downtime in 2014 compared with about 24000 tons in 2013 . average sales price realizations increased year- .
</details>

## 31. `IPG/2015/page_24.pdf-3`  (screen: disagree)

**Question:** what is the average number of total shares purchased in october and november?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1683444.5` | `1633444.5` | `add(2140511, 1126378), divide(#0, 2)` |

**Gold facts**
- `table_1` the october 1 - 31 of total number ofshares ( or units ) purchased1 is 2140511 ; the october 1 - 31 of average price paidper share ( or unit ) 2 is $ 20.54 ; the october 1 - 31 of total number ofshares ( or units ) purchased as part ofpublicly announcedplans or programs3 is 2139507 ; the october 1 - 31 of maximum number ( or approximate dollar value ) of shares ( or units ) that may yet be purchased under the plans or programs3 is $ 227368014 ;
- `table_2` the november 1 - 30 of total number ofshares ( or units ) purchased1 is 1126378 ; the november 1 - 30 of average price paidper share ( or unit ) 2 is $ 22.95 ; the november 1 - 30 of total number ofshares ( or units ) purchased as part ofpublicly announcedplans or programs3 is 1124601 ; the november 1 - 30 of maximum number ( or approximate dollar value ) of shares ( or units ) that may yet be purchased under the plans or programs3 is $ 201557625 ;
- `text_2` total number of shares ( or units ) purchased 1 average price paid per share ( or unit ) 2 total number of shares ( or units ) purchased as part of publicly announced plans or programs 3 maximum number ( or approximate dollar value ) of shares ( or units ) that may yet be purchased under the plans or programs 3 .

**Table**

|  | total number ofshares ( or units ) purchased1 | average price paidper share ( or unit ) 2 | total number ofshares ( or units ) purchased as part ofpublicly announcedplans or programs3 | maximum number ( or approximate dollar value ) of shares ( or units ) that may yet be purchased under the plans or programs3 |
| --- | --- | --- | --- | --- |
| october 1 - 31 | 2140511 | $ 20.54 | 2139507 | $ 227368014 |
| november 1 - 30 | 1126378 | $ 22.95 | 1124601 | $ 201557625 |
| december 1 - 31 | 1881992 | $ 22.97 | 1872650 | $ 158553178 |
| total | 5148881 | $ 21.96 | 5136758 |  |

<details><summary>Text before the table</summary>

transfer agent and registrar for common stock the transfer agent and registrar for our common stock is : computershare shareowner services llc 480 washington boulevard 29th floor jersey city , new jersey 07310 telephone : ( 877 ) 363-6398 sales of unregistered securities not applicable . repurchase of equity securities the following table provides information regarding our purchases of our equity securities during the period from october 1 , 2015 to december 31 , 2015 . total number of shares ( or units ) purchased 1 average price paid per share ( or unit ) 2 total number of shares ( or units ) purchased as part of publicly announced plans or programs 3 maximum number ( or approximate dollar value ) of shares ( or units ) that may yet be purchased under the plans or programs 3 .
</details>

<details><summary>Text after the table</summary>

1 included shares of our common stock , par value $ 0.10 per share , withheld under the terms of grants under employee stock-based compensation plans to offset tax withholding obligations that occurred upon vesting and release of restricted shares ( the 201cwithheld shares 201d ) . we repurchased 1004 withheld shares in october 2015 , 1777 withheld shares in november 2015 and 9342 withheld shares in december 2015 . 2 the average price per share for each of the months in the fiscal quarter and for the three-month period was calculated by dividing the sum of the applicable period of the aggregate value of the tax withholding obligations and the aggregate amount we paid for shares acquired under our stock repurchase program , described in note 5 to the consolidated financial statements , by the sum of the number of withheld shares and the number of shares acquired in our stock repurchase program . 3 in february 2015 , the board authorized a share repurchase program to repurchase from time to time up to $ 300.0 million , excluding fees , of our common stock ( the 201c2015 share repurchase program 201d ) . on february 12 , 2016 , we announced that our board had approved a new share repurchase program to repurchase from time to time up to $ 300.0 million , excluding fees , of our common stock . the new authorization is in addition to any amounts remaining for repurchase under the 2015 share repurchase program . there is no expiration date associated with the share repurchase programs. .
</details>

## 32. `JPM/2010/page_219.pdf-3`  (screen: disagree)

**Question:** in 2010 what was the percent of the securities borrowed accounted for at fair value

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `11.3%` | `0.00011` | `divide(14.0, 123587)` |

**Gold facts**
- `table_2` december 31 ( in millions ) the securities borrowed ( b ) of 2010 is 123587 ; the securities borrowed ( b ) of 2009 is 119630 ;
- `text_13` ( b ) includes securities borrowed of $ 14.0 billion and $ 7.0 billion accounted for at fair value at december 31 , 2010 and 2009 , respectively .

**Table**

| december 31 ( in millions ) | 2010 | 2009 |
| --- | --- | --- |
| securities purchased under resale agreements ( a ) | $ 222302 | $ 195328 |
| securities borrowed ( b ) | 123587 | 119630 |
| securities sold under repurchase agreements ( c ) | $ 262722 | $ 245692 |
| securities loaned | 10592 | 7835 |

<details><summary>Text before the table</summary>

jpmorgan chase & co./2010 annual report 219 note 13 2013 securities financing activities jpmorgan chase enters into resale agreements , repurchase agreements , securities borrowed transactions and securities loaned transactions ( collectively , 201csecurities financing agree- ments 201d ) primarily to finance the firm 2019s inventory positions , ac- quire securities to cover short positions , accommodate customers 2019 financing needs , and settle other securities obligations . securities financing agreements are treated as collateralized financings on the firm 2019s consolidated balance sheets . resale and repurchase agreements are generally carried at the amounts at which the securities will be subsequently sold or repurchased , plus accrued interest . securities borrowed and securities loaned transactions are generally carried at the amount of cash collateral advanced or received . where appropriate under applicable ac- counting guidance , resale and repurchase agreements with the same counterparty are reported on a net basis . fees received or paid in connection with securities financing agreements are recorded in interest income or interest expense . the firm has elected the fair value option for certain securities financing agreements . for a further discussion of the fair value option , see note 4 on pages 187 2013189 of this annual report . the securities financing agreements for which the fair value option has been elected are reported within securities purchased under resale agreements ; securities loaned or sold under repurchase agreements ; and securities borrowed on the consolidated bal- ance sheets . generally , for agreements carried at fair value , current-period interest accruals are recorded within interest income and interest expense , with changes in fair value reported in principal transactions revenue . however , for financial instru- ments containing embedded derivatives that would be separately accounted for in accordance with accounting guidance for hybrid instruments , all changes in fair value , including any interest elements , are reported in principal transactions revenue . the following table details the firm 2019s securities financing agree- ments , all of which are accounted for as collateralized financings during the periods presented. .
</details>

<details><summary>Text after the table</summary>

( a ) includes resale agreements of $ 20.3 billion and $ 20.5 billion accounted for at fair value at december 31 , 2010 and 2009 , respectively . ( b ) includes securities borrowed of $ 14.0 billion and $ 7.0 billion accounted for at fair value at december 31 , 2010 and 2009 , respectively . ( c ) includes repurchase agreements of $ 4.1 billion and $ 3.4 billion accounted for at fair value at december 31 , 2010 and 2009 , respectively . the amounts reported in the table above have been reduced by $ 112.7 billion and $ 121.2 billion at december 31 , 2010 and 2009 , respectively , as a result of agreements in effect that meet the specified conditions for net presentation under applicable accounting guidance . jpmorgan chase 2019s policy is to take possession , where possible , of securities purchased under resale agreements and of securi- ties borrowed . the firm monitors the market value of the un- derlying securities that it has received from its counterparties and either requests additional collateral or returns a portion of the collateral when appropriate in light of the market value of the underlying securities . margin levels are established initially based upon the counterparty and type of collateral and moni- tored on an ongoing basis to protect against declines in collat- eral value in the event of default . jpmorgan chase typically enters into master netting agreements and other collateral arrangements with its resale agreement and securities bor- rowed counterparties , which provide for the right to liquidate the purchased or borrowed securities in the event of a customer default . as a result of the firm 2019s credit risk mitigation practices described above on resale and securities borrowed agreements , the firm did not hold any reserves for credit impairment on these agreements as of december 31 , 2010 and 2009 . for a further discussion of assets pledged and collateral received in securities financing agreements see note 31 on pages 280 2013 281 of this annual report. .
</details>

## 33. `K/2013/page_27.pdf-3`  (screen: disagree)

**Question:** what was the average cash flow from 2011 to 2013 in millions

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1132` | `1699.5` | `add(1170, 1225), add(1001, #0), add(#1, const_3), divide(#2, const_2)` |

**Gold facts**
- `table_3` ( dollars in millions ) the cash flow of 2013 is $ 1170 ; the cash flow of 2012 is $ 1225 ; the cash flow of 2011 is $ 1001 ;

**Table**

| ( dollars in millions ) | 2013 | 2012 | 2011 |
| --- | --- | --- | --- |
| net cash provided by operating activities | $ 1807 | $ 1758 | $ 1595 |
| additions to properties | -637 ( 637 ) | -533 ( 533 ) | -594 ( 594 ) |
| cash flow | $ 1170 | $ 1225 | $ 1001 |
| year-over-year change | ( 4.5 ) % (  % ) | 22.4% ( 22.4 % ) |  |

<details><summary>Text before the table</summary>

general market conditions affecting trust asset performance , future discount rates based on average yields of high quality corporate bonds and our decisions regarding certain elective provisions of the we currently project that we will make total u.s . and foreign benefit plan contributions in 2014 of approximately $ 57 million . actual 2014 contributions could be different from our current projections , as influenced by our decision to undertake discretionary funding of our benefit trusts versus other competing investment priorities , future changes in government requirements , trust asset performance , renewals of union contracts , or higher-than-expected health care claims cost experience . we measure cash flow as net cash provided by operating activities reduced by expenditures for property additions . we use this non-gaap financial measure of cash flow to focus management and investors on the amount of cash available for debt repayment , dividend distributions , acquisition opportunities , and share repurchases . our cash flow metric is reconciled to the most comparable gaap measure , as follows: .
</details>

<details><summary>Text after the table</summary>

year-over-year change ( 4.5 ) % (  % ) 22.4% ( 22.4 % ) the decrease in cash flow ( as defined ) in 2013 compared to 2012 was due primarily to higher capital expenditures . the increase in cash flow in 2012 compared to 2011 was driven by improved performance in working capital resulting from the one-time benefit derived from the pringles acquisition , as well as changes in the level of capital expenditures during the three-year period . investing activities our net cash used in investing activities for 2013 amounted to $ 641 million , a decrease of $ 2604 million compared with 2012 primarily attributable to the $ 2668 million acquisition of pringles in 2012 . capital spending in 2013 included investments in our supply chain infrastructure , and to support capacity requirements in certain markets , including pringles . in addition , we continued the investment in our information technology infrastructure related to the reimplementation and upgrade of our sap platform . net cash used in investing activities of $ 3245 million in 2012 increased by $ 2658 million compared with 2011 , due to the acquisition of pringles in 2012 . cash paid for additions to properties as a percentage of net sales has increased to 4.3% ( 4.3 % ) in 2013 , from 3.8% ( 3.8 % ) in 2012 , which was a decrease from 4.5% ( 4.5 % ) in financing activities our net cash used by financing activities was $ 1141 million for 2013 , compared to net cash provided by financing activities of $ 1317 million for 2012 and net cash used in financing activities of $ 957 million for 2011 . the increase in cash provided from financing activities in 2012 compared to 2013 and 2011 , was primarily due to the issuance of debt related to the acquisition of pringles . total debt was $ 7.4 billion at year-end 2013 and $ 7.9 billion at year-end 2012 . in february 2013 , we issued $ 250 million of two-year floating-rate u.s . dollar notes , and $ 400 million of ten-year 2.75% ( 2.75 % ) u.s . dollar notes , resulting in aggregate net proceeds after debt discount of $ 645 million . the proceeds from these notes were used for general corporate purposes , including , together with cash on hand , repayment of the $ 750 million aggregate principal amount of our 4.25% ( 4.25 % ) u.s . dollar notes due march 2013 . in may 2012 , we issued $ 350 million of three-year 1.125% ( 1.125 % ) u.s . dollar notes , $ 400 million of five-year 1.75% ( 1.75 % ) u.s . dollar notes and $ 700 million of ten-year 3.125% ( 3.125 % ) u.s . dollar notes , resulting in aggregate net proceeds after debt discount of $ 1.442 billion . the proceeds of these notes were used for general corporate purposes , including financing a portion of the acquisition of pringles . in may 2012 , we issued cdn . $ 300 million of two-year 2.10% ( 2.10 % ) fixed rate canadian dollar notes , using the proceeds from these notes for general corporate purposes , which included repayment of intercompany debt . this repayment resulted in cash available to be used for a portion of the acquisition of pringles . in december 2012 , we repaid $ 750 million five-year 5.125% ( 5.125 % ) u.s . dollar notes at maturity with commercial paper . in april 2011 , we repaid $ 945 million ten-year 6.60% ( 6.60 % ) u.s . dollar notes at maturity with commercial paper . in may 2011 , we issued $ 400 million of seven-year 3.25% ( 3.25 % ) fixed rate u.s . dollar notes , using the proceeds of $ 397 million for general corporate purposes and repayment of commercial paper . in november 2011 , we issued $ 500 million of five-year 1.875% ( 1.875 % ) fixed rate u . s . dollar notes , using the proceeds of $ 498 million for general corporate purposes and repayment of commercial paper. .
</details>

## 34. `L/2010/page_41.pdf-2`  (screen: disagree)

**Question:** what percent of the illinois properties relate to data centers?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `5.6%` | `0.05789` | `add(46903, 763322), divide(46903, #0)` |

**Gold facts**
- `table_9` location the 4267 meridian parkwayaurora illinois of size ( square feet ) is 46903 ; the 4267 meridian parkwayaurora illinois of principal usage is data center ;
- `table_1` location the 333 s . wabash avenuechicago illinois of size ( square feet ) is 763322 ; the 333 s . wabash avenuechicago illinois of principal usage is principal executive offices of cna ;

**Table**

| location | size ( square feet ) | principal usage |
| --- | --- | --- |
| 333 s . wabash avenuechicago illinois | 763322 | principal executive offices of cna |
| 401 penn streetreading pennsylvania | 190677 | property and casualty insurance offices |
| 2405 lucien waymaitland florida | 116948 | property and casualty insurance offices |
| 40 wall streetnew york new york | 114096 | property and casualty insurance offices |
| 1100 ward avenuehonolulu hawaii | 104478 | property and casualty insurance offices |
| 101 s . phillips avenuesioux falls south dakota | 83616 | property and casualty insurance offices |
| 600 n . pearl streetdallas texas | 65752 | property and casualty insurance offices |
| 1249 s . river roadcranbury new jersey | 50366 | property and casualty insurance offices |
| 4267 meridian parkwayaurora illinois | 46903 | data center |
| 675 placentia avenuebrea california | 46571 | property and casualty insurance offices |

<details><summary>Text before the table</summary>

item 1 . business cna financial corporation 2013 ( continued ) unpredictability in the law , insurance underwriting is expected to continue to be difficult in commercial lines , professional liability and other specialty coverages . the dodd-frank wall street reform and consumer protection act expands the federal presence in insurance oversight and may increase the regulatory requirements to which cna may be subject . the act 2019s requirements include streamlining the state-based regulation of reinsurance and nonadmitted insurance ( property or casualty insurance placed from insurers that are eligible to accept insurance , but are not licensed to write insurance in a particular state ) . the act also establishes a new federal insurance office within the u.s . department of the treasury with powers over all lines of insurance except health insurance , certain long term care insurance and crop insurance , to , among other things , monitor aspects of the insurance industry , identify issues in the regulation of insurers that could contribute to a systemic crisis in the insurance industry or the overall financial system , coordinate federal policy on international insurance matters and preempt state insurance measures under certain circumstances . the act calls for numerous studies and contemplates further regulation . the patient protection and affordable care act and the related amendments in the health care and education reconciliation act may increase cna 2019s operating costs and underwriting losses . this landmark legislation may lead to numerous changes in the health care industry that could create additional operating costs for cna , particularly with respect to workers 2019 compensation and long term care products . these costs might arise through the increased use of health care services by claimants or the increased complexities in health care bills that could require additional levels of review . in addition , due to the expected number of new participants in the health care system and the potential for additional malpractice claims , cna may experience increased underwriting risk in the lines of business that provide management and professional liability insurance to individuals and businesses engaged in the health care industry . the lines of business that provide professional liability insurance to attorneys , accountants and other professionals who advise clients regarding the health care reform legislation may also experience increased underwriting risk due to the complexity of the legislation . properties : the chicago location owned by ccc , a wholly owned subsidiary of cna , houses cna 2019s principal executive offices . cna owns or leases office space in various cities throughout the united states and in other countries . the following table sets forth certain information with respect to cna 2019s principal office locations : location ( square feet ) principal usage 333 s . wabash avenue 763322 principal executive offices of cna chicago , illinois 401 penn street 190677 property and casualty insurance offices reading , pennsylvania 2405 lucien way 116948 property and casualty insurance offices maitland , florida 40 wall street 114096 property and casualty insurance offices new york , new york 1100 ward avenue 104478 property and casualty insurance offices honolulu , hawaii 101 s . phillips avenue 83616 property and casualty insurance offices sioux falls , south dakota 600 n . pearl street 65752 property and casualty insurance offices dallas , texas 1249 s . river road 50366 property and casualty insurance offices cranbury , new jersey 4267 meridian parkway 46903 data center aurora , illinois 675 placentia avenue 46571 property and casualty insurance offices brea , california cna leases its office space described above except for the chicago , illinois building , the reading , pennsylvania building , and the aurora , illinois building , which are owned. .
</details>

<details><summary>Text after the table</summary>

item 1 . business cna financial corporation 2013 ( continued ) unpredictability in the law , insurance underwriting is expected to continue to be difficult in commercial lines , professional liability and other specialty coverages . the dodd-frank wall street reform and consumer protection act expands the federal presence in insurance oversight and may increase the regulatory requirements to which cna may be subject . the act 2019s requirements include streamlining the state-based regulation of reinsurance and nonadmitted insurance ( property or casualty insurance placed from insurers that are eligible to accept insurance , but are not licensed to write insurance in a particular state ) . the act also establishes a new federal insurance office within the u.s . department of the treasury with powers over all lines of insurance except health insurance , certain long term care insurance and crop insurance , to , among other things , monitor aspects of the insurance industry , identify issues in the regulation of insurers that could contribute to a systemic crisis in the insurance industry or the overall financial system , coordinate federal policy on international insurance matters and preempt state insurance measures under certain circumstances . the act calls for numerous studies and contemplates further regulation . the patient protection and affordable care act and the related amendments in the health care and education reconciliation act may increase cna 2019s operating costs and underwriting losses . this landmark legislation may lead to numerous changes in the health care industry that could create additional operating costs for cna , particularly with respect to workers 2019 compensation and long term care products . these costs might arise through the increased use of health care services by claimants or the increased complexities in health care bills that could require additional levels of review . in addition , due to the expected number of new participants in the health care system and the potential for additional malpractice claims , cna may experience increased underwriting risk in the lines of business that provide management and professional liability insurance to individuals and businesses engaged in the health care industry . the lines of business that provide professional liability insurance to attorneys , accountants and other professionals who advise clients regarding the health care reform legislation may also experience increased underwriting risk due to the complexity of the legislation . properties : the chicago location owned by ccc , a wholly owned subsidiary of cna , houses cna 2019s principal executive offices . cna owns or leases office space in various cities throughout the united states and in other countries . the following table sets forth certain information with respect to cna 2019s principal office locations : location ( square feet ) principal usage 333 s . wabash avenue 763322 principal executive offices of cna chicago , illinois 401 penn street 190677 property and casualty insurance offices reading , pennsylvania 2405 lucien way 116948 property and casualty insurance offices maitland , florida 40 wall street 114096 property and casualty insurance offices new york , new york 1100 ward avenue 104478 property and casualty insurance offices honolulu , hawaii 101 s . phillips avenue 83616 property and casualty insurance offices sioux falls , south dakota 600 n . pearl street 65752 property and casualty insurance offices dallas , texas 1249 s . river road 50366 property and casualty insurance offices cranbury , new jersey 4267 meridian parkway 46903 data center aurora , illinois 675 placentia avenue 46571 property and casualty insurance offices brea , california cna leases its office space described above except for the chicago , illinois building , the reading , pennsylvania building , and the aurora , illinois building , which are owned. .
</details>

## 35. `LMT/2013/page_46.pdf-3`  (screen: disagree)

**Question:** what was average operating margins for mfc from 2011 to 2013?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `10.7%` | `0.165` | `table_average(operating margins, none)` |

**Gold facts**
- `table_3` the operating margins of 2013 is 18.4% ( 18.4 % ) ; the operating margins of 2012 is 16.8% ( 16.8 % ) ; the operating margins of 2011 is 14.3% ( 14.3 % ) ;

**Table**

|  | 2013 | 2012 | 2011 |
| --- | --- | --- | --- |
| net sales | $ 7757 | $ 7457 | $ 7463 |
| operating profit | 1431 | 1256 | 1069 |
| operating margins | 18.4% ( 18.4 % ) | 16.8% ( 16.8 % ) | 14.3% ( 14.3 % ) |
| backlog at year-end | 15000 | 14700 | 14400 |

<details><summary>Text before the table</summary>

warfighter information network-tactical ( win-t ) ; command , control , battle management and communications ( c2bmc ) ; and twic ) . partially offsetting the decreases were higher net sales of approximately $ 140 million from qtc , which was acquired early in the fourth quarter of 2011 ; and about $ 65 million from increased activity on numerous other programs , primarily federal cyber security programs and ptds operational support . is&gs 2019 operating profit for 2012 decreased $ 66 million , or 8% ( 8 % ) , compared to 2011 . the decrease was attributable to lower operating profit of approximately $ 50 million due to the favorable impact of the odin contract completion in 2011 ; about $ 25 million due to an increase in reserves for performance issues related to an international airborne surveillance system in 2012 ; and approximately $ 20 million due to lower volume on certain programs ( primarily c2bmc and win-t ) . partially offsetting the decreases was an increase in operating profit due to higher risk retirements of approximately $ 15 million from the twic program ; and about $ 10 million due to increased activity on numerous other programs , primarily federal cyber security programs and ptds operational support . operating profit for the jtrs program was comparable as a decrease in volume was offset by a decrease in reserves . adjustments not related to volume , including net profit booking rate adjustments and other matters described above , were approximately $ 20 million higher for 2012 compared to 2011 . backlog backlog decreased in 2013 compared to 2012 primarily due to lower orders on several programs ( such as eram and ngi ) , higher sales on certain programs ( the national science foundation antarctic support and the disa gsm-o ) , and declining activities on several smaller programs primarily due to the continued downturn in federal information technology budgets . backlog decreased in 2012 compared to 2011 primarily due to the substantial completion of various programs in 2011 ( primarily odin , u.k . census , and jtrs ) . trends we expect is&gs 2019 net sales to decline in 2014 in the high single digit percentage range as compared to 2013 primarily due to the continued downturn in federal information technology budgets . operating profit is also expected to decline in 2014 in the high single digit percentage range consistent with the expected decline in net sales , resulting in margins that are comparable with 2013 results . missiles and fire control our mfc business segment provides air and missile defense systems ; tactical missiles and air-to-ground precision strike weapon systems ; logistics and other technical services ; fire control systems ; mission operations support , readiness , engineering support , and integration services ; and manned and unmanned ground vehicles . mfc 2019s major programs include pac-3 , thaad , multiple launch rocket system , hellfire , joint air-to-surface standoff missile ( jassm ) , javelin , apache fire control system ( apache ) , sniper ae , low altitude navigation and targeting infrared for night ( lantirn ae ) , and sof clss . mfc 2019s operating results included the following ( in millions ) : .
</details>

<details><summary>Text after the table</summary>

2013 compared to 2012 mfc 2019s net sales for 2013 increased $ 300 million , or 4% ( 4 % ) , compared to 2012 . the increase was primarily attributable to higher net sales of approximately $ 450 million for air and missile defense programs ( thaad and pac-3 ) due to increased production volume and deliveries ; about $ 70 million for fire control programs due to net increased deliveries and volume ; and approximately $ 55 million for tactical missile programs due to net increased deliveries . the increases were partially offset by lower net sales of about $ 275 million for various technical services programs due to lower volume driven by the continuing impact of defense budget reductions and related competitive pressures . the increase for fire control programs was primarily attributable to increased deliveries on the sniper ae and lantirn ae programs , increased volume on the sof clss program , partially offset by lower volume on longbow fire control radar and other programs . the increase for tactical missile programs was primarily attributable to increased deliveries on jassm and other programs , partially offset by fewer deliveries on the guided multiple launch rocket system and javelin programs. .
</details>

## 36. `LMT/2014/page_45.pdf-1`  (screen: disagree)

**Question:** what was the percent of the change in the operating profit from 2013 to 2014

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `2.3%` | `0.00063` | `divide(1649, 1612), divide(#0, 1612)` |

**Gold facts**
- `table_2` the operating profit of 2014 is 1649 ; the operating profit of 2013 is 1612 ; the operating profit of 2012 is 1699 ;

**Table**

|  | 2014 | 2013 | 2012 |
| --- | --- | --- | --- |
| net sales | $ 14920 | $ 14123 | $ 14953 |
| operating profit | 1649 | 1612 | 1699 |
| operating margins | 11.1% ( 11.1 % ) | 11.4% ( 11.4 % ) | 11.4% ( 11.4 % ) |
| backlog at year-end | $ 27600 | $ 28000 | $ 30100 |

<details><summary>Text before the table</summary>

2014 , 2013 and 2012 . the decrease in our consolidated net adjustments for 2014 compared to 2013 was primarily due to a decrease in profit booking rate adjustments at our aeronautics , mfc and mst business segments . the increase in our consolidated net adjustments for 2013 as compared to 2012 was primarily due to an increase in profit booking rate adjustments at our mst and mfc business segments and , to a lesser extent , the increase in the favorable resolution of contractual matters for the corporation . the consolidated net adjustments for 2014 are inclusive of approximately $ 650 million in unfavorable items , which include reserves recorded on certain training and logistics solutions programs at mst and net warranty reserve adjustments for various programs ( including jassm and gmlrs ) at mfc as described in the respective business segment 2019s results of operations below . the consolidated net adjustments for 2013 and 2012 are inclusive of approximately $ 600 million and $ 500 million in unfavorable items , which include a significant profit reduction on the f-35 development contract in both years , as well as a significant profit reduction on the c-5 program in 2013 , each as described in our aeronautics business segment 2019s results of operations discussion below . aeronautics our aeronautics business segment is engaged in the research , design , development , manufacture , integration , sustainment , support and upgrade of advanced military aircraft , including combat and air mobility aircraft , unmanned air vehicles and related technologies . aeronautics 2019 major programs include the f-35 lightning ii joint strike fighter , c-130 hercules , f-16 fighting falcon , f-22 raptor and the c-5m super galaxy . aeronautics 2019 operating results included the following ( in millions ) : .
</details>

<details><summary>Text after the table</summary>

2014 compared to 2013 aeronautics 2019 net sales for 2014 increased $ 797 million , or 6% ( 6 % ) , compared to 2013 . the increase was primarily attributable to higher net sales of approximately $ 790 million for f-35 production contracts due to increased volume and sustainment activities ; about $ 55 million for the f-16 program due to increased deliveries ( 17 aircraft delivered in 2014 compared to 13 delivered in 2013 ) partially offset by contract mix ; and approximately $ 45 million for the f-22 program due to increased risk retirements . the increases were partially offset by lower net sales of approximately $ 55 million for the f-35 development contract due to decreased volume , partially offset by the absence in 2014 of the downward revision to the profit booking rate that occurred in 2013 ; and about $ 40 million for the c-130 program due to fewer deliveries ( 24 aircraft delivered in 2014 compared to 25 delivered in 2013 ) and decreased sustainment activities , partially offset by contract mix . aeronautics 2019 operating profit for 2014 increased $ 37 million , or 2% ( 2 % ) , compared to 2013 . the increase was primarily attributable to higher operating profit of approximately $ 85 million for the f-35 development contract due to the absence in 2014 of the downward revision to the profit booking rate that occurred in 2013 ; about $ 75 million for the f-22 program due to increased risk retirements ; approximately $ 50 million for the c-130 program due to increased risk retirements and contract mix , partially offset by fewer deliveries ; and about $ 25 million for the c-5 program due to the absence in 2014 of the downward revisions to the profit booking rate that occurred in 2013 . the increases were partially offset by lower operating profit of approximately $ 130 million for the f-16 program due to decreased risk retirements , partially offset by increased deliveries ; and about $ 70 million for sustainment activities due to decreased risk retirements and volume . operating profit was comparable for f-35 production contracts as higher volume was offset by lower risk retirements . adjustments not related to volume , including net profit booking rate adjustments and other matters , were approximately $ 105 million lower for 2014 compared to 2013 . 2013 compared to 2012 aeronautics 2019 net sales for 2013 decreased $ 830 million , or 6% ( 6 % ) , compared to 2012 . the decrease was primarily attributable to lower net sales of approximately $ 530 million for the f-16 program due to fewer aircraft deliveries ( 13 aircraft delivered in 2013 compared to 37 delivered in 2012 ) partially offset by aircraft configuration mix ; about $ 385 million for the c-130 program due to fewer aircraft deliveries ( 25 aircraft delivered in 2013 compared to 34 in 2012 ) partially offset by increased sustainment activities ; approximately $ 255 million for the f-22 program , which includes about $ 205 million due to .
</details>

## 37. `MRO/2003/page_65.pdf-2`  (screen: disagree)

**Question:** what were average state and local income taxes after federal income tax effects for the three year period , in millions?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1.2` | `3.03333` | `table_average(state and local income taxes after federal income tax effects, none)` |

**Gold facts**
- `table_3` the state and local income taxes after federal income tax effects of 2003 is 2.2 ; the state and local income taxes after federal income tax effects of 2002 is 3.9 ; the state and local income taxes after federal income tax effects of 2001 is 3.0 ;

**Table**

|  | 2003 | 2002 | 2001 |
| --- | --- | --- | --- |
| statutory tax rate | 35.0% ( 35.0 % ) | 35.0% ( 35.0 % ) | 35.0% ( 35.0 % ) |
| effects of foreign operations ( a ) | -0.4 ( 0.4 ) | 5.6 | -0.7 ( 0.7 ) |
| state and local income taxes after federal income tax effects | 2.2 | 3.9 | 3.0 |
| other federal tax effects | -0.2 ( 0.2 ) | -2.4 ( 2.4 ) | -0.2 ( 0.2 ) |
| effective tax rate | 36.6% ( 36.6 % ) | 42.1% ( 42.1 % ) | 37.1% ( 37.1 % ) |

<details><summary>Text before the table</summary>

expenditures and acquisitions of leased properties are funded by the original contributor of the assets , but no change in ownership interest may result from these contributions . an excess of ashland funded improvements over marathon funded improvements results in a net gain and an excess of marathon funded improvements over ashland funded improvements results in a net loss . cost of revenues increased by $ 8.718 billion in 2003 from 2002 and $ 367 million in 2002 from 2001 . the increases in the oerb segment were primarily a result of higher natural gas and liquid hydrocarbon costs . the increases in the rm&t segment primarily reflected higher acquisition costs for crude oil , refined products , refinery charge and blend feedstocks and increased manufacturing expenses . selling , general and administrative expenses increased by $ 107 million in 2003 from 2002 and $ 125 million in 2002 from 2001 . the increase in 2003 was primarily a result of increased employee benefits ( caused by increased pension expense resulting from changes in actuarial assumptions and a decrease in realized returns on plan assets ) and other employee related costs . also , marathon changed assumptions in the health care cost trend rate from 7.5% ( 7.5 % ) to 10% ( 10 % ) , resulting in higher retiree health care costs . additionally , during 2003 , marathon recorded a charge of $ 24 million related to organizational and business process changes . the increase in 2002 primarily reflected increased employee related costs . inventory market valuation reserve is established to reduce the cost basis of inventories to current market value . the 2002 results of operations include credits to income from operations of $ 71 million , reversing the imv reserve at december 31 , 2001 . for additional information on this adjustment , see 201cmanagement 2019s discussion and analysis of critical accounting estimates 2013 net realizable value of inventories 201d on page 31 . net interest and other financial costs decreased by $ 82 million in 2003 from 2002 , following an increase of $ 96 million in 2002 from 2001 . the decrease in 2003 is primarily due to an increase in capitalized interest related to increased long-term construction projects , the favorable effect of interest rate swaps , the favorable effect of interest on tax deficiencies and increased interest income on investments . the increase in 2002 was primarily due to higher average debt levels resulting from acquisitions and the separation . additionally , included in net interest and other financing costs are foreign currency gains of $ 13 million and $ 8 million for 2003 and 2002 and losses of $ 5 million for 2001 . loss from early extinguishment of debt in 2002 was attributable to the retirement of $ 337 million aggregate principal amount of debt , resulting in a loss of $ 53 million . as a result of the adoption of statement of financial accounting standards no . 145 201crescission of fasb statements no . 4 , 44 , and 64 , amendment of fasb statement no . 13 , and technical corrections 201d ( 201csfas no . 145 201d ) , the loss from early extinguishment of debt that was previously reported as an extraordinary item ( net of taxes of $ 20 million ) has been reclassified into income before income taxes . the adoption of sfas no . 145 had no impact on net income for 2002 . minority interest in income of map , which represents ashland 2019s 38 percent ownership interest , increased by $ 129 million in 2003 from 2002 , following a decrease of $ 531 million in 2002 from 2001 . map income was higher in 2003 compared to 2002 as discussed below in the rm&t segment . map income was significantly lower in 2002 compared to 2001 as discussed below in the rm&t segment . provision for income taxes increased by $ 215 million in 2003 from 2002 , following a decrease of $ 458 million in 2002 from 2001 , primarily due to $ 720 million increase and $ 1.356 billion decrease in income before income taxes . the effective tax rate for 2003 was 36.6% ( 36.6 % ) compared to 42.1% ( 42.1 % ) and 37.1% ( 37.1 % ) for 2002 and 2001 . the higher rate in 2002 was due to the united kingdom enactment of a supplementary 10 percent tax on profits from the north sea oil and gas production , retroactively effective to april 17 , 2002 . in 2002 , marathon recognized a one-time noncash deferred tax adjustment of $ 61 million as a result of the rate increase . the following is an analysis of the effective tax rate for the periods presented: .
</details>

<details><summary>Text after the table</summary>

( a ) the deferred tax effect related to the enactment of a supplemental tax in the u.k . increased the effective tax rate 7.0 percent in 2002. .
</details>

## 38. `MRO/2015/page_56.pdf-2`  (screen: disagree)

**Question:** what were average yearly capital expenditures for corporate , in millions?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `36.5` | `44.66667` | `table_average(corporate, none)` |

**Gold facts**
- `table_4` ( in millions ) the corporate of year ended december 31 , 2015 is 25 ; the corporate of year ended december 31 , 2014 is 51 ; the corporate of year ended december 31 , 2013 is 58 ;

**Table**

| ( in millions ) | year ended december 31 , 2015 | year ended december 31 , 2014 | year ended december 31 , 2013 |
| --- | --- | --- | --- |
| north america e&p | $ 2553 | $ 4698 | $ 3649 |
| international e&p | 368 | 534 | 456 |
| oil sands mining ( a ) | -10 ( 10 ) | 212 | 286 |
| corporate | 25 | 51 | 58 |
| total capital expenditures | 2936 | 5495 | 4449 |
| change in capital expenditure accrual | 540 | -335 ( 335 ) | -6 ( 6 ) |
| additions to property plant and equipment | $ 3476 | $ 5160 | $ 4443 |

<details><summary>Text before the table</summary>

borrowings reflect net proceeds received from the issuance of senior notes in june 2015 . see liquidity and capital resources below for additional information . in november 2015 , we repaid our $ 1 billion 0.90% ( 0.90 % ) senior notes upon maturity . in october 2015 , we announced an adjustment to our quarterly dividend . see capital requirements below for additional information . additions to property , plant and equipment are our most significant use of cash and cash equivalents . the following table shows capital expenditures related to continuing operations by segment and reconciles to additions to property , plant and equipment as presented in the consolidated statements of cash flows for 2015 , 2014 and 2013: .
</details>

<details><summary>Text after the table</summary>

( a ) reflects reimbursements earned from the governments of canada and alberta related to funds previously expended for quest ccs capital equipment . quest ccs was successfully completed and commissioned in the fourth quarter of 2015 . during 2014 , we acquired 29 million shares at a cost of $ 1 billion and in 2013 acquired 14 million shares at a cost of $ 500 million . there were no share repurchases in 2015 . see item 8 . financial statements and supplementary data 2013 note 23 to the consolidated financial statements for discussion of purchases of common stock . liquidity and capital resources on june 10 , 2015 , we issued $ 2 billion aggregate principal amount of unsecured senior notes which consist of the following series : 2022 $ 600 million of 2.70% ( 2.70 % ) senior notes due june 1 , 2020 2022 $ 900 million of 3.85% ( 3.85 % ) senior notes due june 1 , 2025 2022 $ 500 million of 5.20% ( 5.20 % ) senior notes due june 1 , 2045 interest on each series of senior notes is payable semi-annually beginning december 1 , 2015 . we used the aggregate net proceeds to repay our $ 1 billion 0.90% ( 0.90 % ) senior notes on november 2 , 2015 , and the remainder for general corporate purposes . in may 2015 , we amended our $ 2.5 billion credit facility to increase the facility size by $ 500 million to a total of $ 3.0 billion and extend the maturity date by an additional year such that the credit facility now matures in may 2020 . the amendment additionally provides us the ability to request two one-year extensions to the maturity date and an option to increase the commitment amount by up to an additional $ 500 million , subject to the consent of any increasing lenders . the sub-facilities for swing-line loans and letters of credit remain unchanged allowing up to an aggregate amount of $ 100 million and $ 500 million , respectively . fees on the unused commitment of each lender , as well as the borrowing options under the credit facility , remain unchanged . our main sources of liquidity are cash and cash equivalents , internally generated cash flow from operations , capital market transactions , our committed revolving credit facility and sales of non-core assets . our working capital requirements are supported by these sources and we may issue either commercial paper backed by our $ 3.0 billion revolving credit facility or draw on our $ 3.0 billion revolving credit facility to meet short-term cash requirements or issue debt or equity securities through the shelf registration statement discussed below as part of our longer-term liquidity and capital management . because of the alternatives available to us as discussed above , we believe that our short-term and long-term liquidity is adequate to fund not only our current operations , but also our near-term and long-term funding requirements including our capital spending programs , dividend payments , defined benefit plan contributions , repayment of debt maturities and other amounts that may ultimately be paid in connection with contingencies . general economic conditions , commodity prices , and financial , business and other factors could affect our operations and our ability to access the capital markets . a downgrade in our credit ratings could negatively impact our cost of capital and our ability to access the capital markets , increase the interest rate and fees we pay on our unsecured revolving credit facility , restrict our access to the commercial paper market , or require us to post letters of credit or other forms of collateral for certain .
</details>

## 39. `NKE/2015/page_37.pdf-2`  (screen: disagree)

**Question:** what percent of the total for all years was due to contributions form the year 2020?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `5%` | `0.05642` | `divide(873, 15473)` |

**Gold facts**
- `table_7` description of commitment ( in millions ) the total of description of commitment 2016 is $ 5678 ; the total of description of commitment 2017 is $ 1573 ; the total of description of commitment 2018 is $ 1384 ; the total of description of commitment 2019 is $ 1125 ; the total of description of commitment 2020 is $ 873 ; the total of description of commitment thereafter is $ 4840 ; the total of total is $ 15473 ;

**Table**

| description of commitment ( in millions ) | description of commitment 2016 | description of commitment 2017 | description of commitment 2018 | description of commitment 2019 | description of commitment 2020 | description of commitment thereafter | total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| operating leases | $ 447 | $ 423 | $ 371 | $ 311 | $ 268 | $ 1154 | $ 2974 |
| capital leases | 2 | 2 | 1 | 2014 | 2014 | 2014 | 5 |
| long-term debt ( 1 ) | 142 | 77 | 55 | 36 | 36 | 1451 | 1797 |
| endorsement contracts ( 2 ) | 1009 | 919 | 882 | 706 | 533 | 2143 | 6192 |
| product purchase obligations ( 3 ) | 3735 | 2014 | 2014 | 2014 | 2014 | 2014 | 3735 |
| other ( 4 ) | 343 | 152 | 75 | 72 | 36 | 92 | 770 |
| total | $ 5678 | $ 1573 | $ 1384 | $ 1125 | $ 873 | $ 4840 | $ 15473 |

<details><summary>Text before the table</summary>

part ii were issued in an initial aggregate principal amount of $ 500 million at a 2.25% ( 2.25 % ) fixed , annual interest rate and will mature on may 1 , 2023 . the 2043 senior notes were issued in an initial aggregate principal amount of $ 500 million at a 3.625% ( 3.625 % ) fixed , annual interest rate and will mature on may 1 , 2043 . interest on the senior notes is payable semi-annually on may 1 and november 1 of each year . the issuance resulted in gross proceeds before expenses of $ 998 million . on november 1 , 2011 , we entered into a committed credit facility agreement with a syndicate of banks which provides for up to $ 1 billion of borrowings with the option to increase borrowings to $ 1.5 billion with lender approval . the facility matures november 1 , 2017 . as of and for the periods ended may 31 , 2015 and 2014 , we had no amounts outstanding under our committed credit facility . we currently have long-term debt ratings of aa- and a1 from standard and poor 2019s corporation and moody 2019s investor services , respectively . if our long- term debt ratings were to decline , the facility fee and interest rate under our committed credit facility would increase . conversely , if our long-term debt rating were to improve , the facility fee and interest rate would decrease . changes in our long-term debt rating would not trigger acceleration of maturity of any then-outstanding borrowings or any future borrowings under the committed credit facility . under this committed revolving credit facility , we have agreed to various covenants . these covenants include limits on our disposal of fixed assets , the amount of debt secured by liens we may incur , as well as a minimum capitalization ratio . in the event we were to have any borrowings outstanding under this facility and failed to meet any covenant , and were unable to obtain a waiver from a majority of the banks in the syndicate , any borrowings would become immediately due and payable . as of may 31 , 2015 , we were in full compliance with each of these covenants and believe it is unlikely we will fail to meet any of these covenants in the foreseeable future . liquidity is also provided by our $ 1 billion commercial paper program . during the year ended may 31 , 2015 , we did not issue commercial paper , and as of may 31 , 2015 , there were no outstanding borrowings under this program . we may issue commercial paper or other debt securities during fiscal 2016 depending on general corporate needs . we currently have short-term debt ratings of a1+ and p1 from standard and poor 2019s corporation and moody 2019s investor services , respectively . as of may 31 , 2015 , we had cash , cash equivalents and short-term investments totaling $ 5.9 billion , of which $ 4.2 billion was held by our foreign subsidiaries . included in cash and equivalents as of may 31 , 2015 was $ 968 million of cash collateral received from counterparties as a result of hedging activity . cash equivalents and short-term investments consist primarily of deposits held at major banks , money market funds , commercial paper , corporate notes , u.s . treasury obligations , u.s . government sponsored enterprise obligations and other investment grade fixed income securities . our fixed income investments are exposed to both credit and interest rate risk . all of our investments are investment grade to minimize our credit risk . while individual securities have varying durations , as of may 31 , 2015 the weighted average remaining duration of our short-term investments and cash equivalents portfolio was 79 days . to date we have not experienced difficulty accessing the credit markets or incurred higher interest costs . future volatility in the capital markets , however , may increase costs associated with issuing commercial paper or other debt instruments or affect our ability to access those markets . we believe that existing cash , cash equivalents , short-term investments and cash generated by operations , together with access to external sources of funds as described above , will be sufficient to meet our domestic and foreign capital needs in the foreseeable future . we utilize a variety of tax planning and financing strategies to manage our worldwide cash and deploy funds to locations where they are needed . we routinely repatriate a portion of our foreign earnings for which u.s . taxes have previously been provided . we also indefinitely reinvest a significant portion of our foreign earnings , and our current plans do not demonstrate a need to repatriate these earnings . should we require additional capital in the united states , we may elect to repatriate indefinitely reinvested foreign funds or raise capital in the united states through debt . if we were to repatriate indefinitely reinvested foreign funds , we would be required to accrue and pay additional u.s . taxes less applicable foreign tax credits . if we elect to raise capital in the united states through debt , we would incur additional interest expense . off-balance sheet arrangements in connection with various contracts and agreements , we routinely provide indemnification relating to the enforceability of intellectual property rights , coverage for legal issues that arise and other items where we are acting as the guarantor . currently , we have several such agreements in place . however , based on our historical experience and the estimated probability of future loss , we have determined that the fair value of such indemnification is not material to our financial position or results of operations . contractual obligations our significant long-term contractual obligations as of may 31 , 2015 and significant endorsement contracts , including related marketing commitments , entered into through the date of this report are as follows: .
</details>

<details><summary>Text after the table</summary>

( 1 ) the cash payments due for long-term debt include estimated interest payments . estimates of interest payments are based on outstanding principal amounts , applicable fixed interest rates or currently effective interest rates as of may 31 , 2015 ( if variable ) , timing of scheduled payments and the term of the debt obligations . ( 2 ) the amounts listed for endorsement contracts represent approximate amounts of base compensation and minimum guaranteed royalty fees we are obligated to pay athlete , sport team and league endorsers of our products . actual payments under some contracts may be higher than the amounts listed as these contracts provide for bonuses to be paid to the endorsers based upon athletic achievements and/or royalties on product sales in future periods . actual payments under some contracts may also be lower as these contracts include provisions for reduced payments if athletic performance declines in future periods . in addition to the cash payments , we are obligated to furnish our endorsers with nike product for their use . it is not possible to determine how much we will spend on this product on an annual basis as the contracts generally do not stipulate a specific amount of cash to be spent on the product . the amount of product provided to the endorsers will depend on many factors , including general playing conditions , the number of sporting events in which they participate and our own decisions regarding product and marketing initiatives . in addition , the costs to design , develop , source and purchase the products furnished to the endorsers are incurred over a period of time and are not necessarily tracked separately from similar costs incurred for products sold to customers. .
</details>

## 40. `PKG/2005/page_29.pdf-4`  (screen: disagree)

**Question:** what was the change in total corrugated products volume sold in billion square feet from 2004 compared to 2003?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `0.8` | `1.8` | `subtract(29.9, 28.1)` |

**Gold facts**
- `text_3` total corrugated products volume sold increased 6.6% ( 6.6 % ) to 29.9 billion square feet in 2004 compared to 28.1 billion square feet in 2003 .

**Table**

| ( in millions ) | for the year ended december 31 , 2004 | for the year ended december 31 , 2003 | change |
| --- | --- | --- | --- |
| net sales | $ 1890.1 | $ 1735.5 | $ 154.6 |
| income before interest and taxes | $ 140.5 | $ 96.9 | $ 43.6 |
| interest expense net | -29.6 ( 29.6 ) | -121.8 ( 121.8 ) | 92.2 |
| income ( loss ) before taxes | 110.9 | -24.9 ( 24.9 ) | 135.8 |
| ( provision ) benefit for income taxes | -42.2 ( 42.2 ) | 10.5 | -52.7 ( 52.7 ) |
| net income ( loss ) | $ 68.7 | $ -14.4 ( 14.4 ) | $ 83.1 |

<details><summary>Text before the table</summary>

year ended december 31 , 2004 compared to year ended december 31 , 2003 the historical results of operations of pca for the years ended december 31 , 2004 and 2003 are set forth below : for the year ended december 31 , ( in millions ) 2004 2003 change .
</details>

<details><summary>Text after the table</summary>

net sales net sales increased by $ 154.6 million , or 8.9% ( 8.9 % ) , for the year ended december 31 , 2004 from the year ended december 31 , 2003 . net sales increased due to improved sales volumes and prices of corrugated products and containerboard compared to 2003 . total corrugated products volume sold increased 6.6% ( 6.6 % ) to 29.9 billion square feet in 2004 compared to 28.1 billion square feet in 2003 . on a comparable shipment-per-workday basis , corrugated products sales volume increased 7.0% ( 7.0 % ) in 2004 from 2003 . excluding pca 2019s acquisition of acorn in february 2004 , corrugated products volume was 5.3% ( 5.3 % ) higher in 2004 than 2003 and up 5.8% ( 5.8 % ) compared to 2003 on a shipment-per-workday basis . shipments-per-workday is calculated by dividing our total corrugated products volume during the year by the number of workdays within the year . the larger percentage increase was due to the fact that 2004 had one less workday ( 251 days ) , those days not falling on a weekend or holiday , than 2003 ( 252 days ) . containerboard sales volume to external domestic and export customers increased 6.8% ( 6.8 % ) to 475000 tons for the year ended december 31 , 2004 from 445000 tons in 2003 . income before interest and taxes income before interest and taxes increased by $ 43.6 million , or 45.1% ( 45.1 % ) , for the year ended december 31 , 2004 compared to 2003 . included in income before interest and taxes for the year ended december 31 , 2004 is income of $ 27.8 million , net of expenses , attributable to a dividend paid to pca by stv , the timberlands joint venture in which pca owns a 311 20443% ( 20443 % ) ownership interest . included in income before interest and taxes for the year ended december 31 , 2003 is a $ 3.3 million charge for fees and expenses related to the company 2019s debt refinancing which was completed in july 2003 , and a fourth quarter charge of $ 16.0 million to settle certain benefits related matters with pactiv corporation dating back to april 12 , 1999 when pca became a stand-alone company , as described below . during the fourth quarter of 2003 , pactiv notified pca that we owed pactiv additional amounts for hourly pension benefits and workers 2019 compensation liabilities dating back to april 12 , 1999 . a settlement of $ 16.0 million was negotiated between pactiv and pca in december 2003 . the full amount of the settlement was accrued in the fourth quarter of 2003 . excluding these special items , operating income decreased $ 3.4 million in 2004 compared to 2003 . the $ 3.4 million decrease in income before interest and taxes was primarily attributable to increased energy and transportation costs ( $ 19.2 million ) , higher recycled and wood fiber costs ( $ 16.7 million ) , increased salary expenses related to annual increases and new hires ( $ 5.7 million ) , and increased contractual hourly labor costs ( $ 5.6 million ) , which was partially offset by increased sales volume and sales prices ( $ 44.3 million ) . .
</details>

## 41. `PPG/2013/page_76.pdf-1`  (screen: disagree)

**Question:** during 2013 , what was the decline in net sales in disco?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `-93%` | `-0.93602` | `subtract(108, 1688), divide(#0, 1688)` |

**Gold facts**
- `table_1` millions the net sales of year-ended 2013 is $ 108 ; the net sales of year-ended 2012 is $ 1688 ; the net sales of year-ended 2011 is $ 1732 ;

**Table**

| millions | year-ended 2013 | year-ended 2012 | year-ended 2011 |
| --- | --- | --- | --- |
| net sales | $ 108 | $ 1688 | $ 1732 |
| income from operations before income tax | $ 2014 | $ 345 | $ 376 |
| net gain from separation and merger of commodity chemicals business | 2192 | 2014 | 2014 |
| income tax expense | -5 ( 5 ) | 117 | 126 |
| income from discontinued operations net of tax | $ 2197 | $ 228 | $ 250 |
| less : net income attributable to non-controlling interests discontinued operations | $ 2014 | $ -13 ( 13 ) | $ -13 ( 13 ) |
| net income from discontinued operations ( attributable to ppg ) | $ 2197 | $ 215 | $ 237 |

<details><summary>Text before the table</summary>

74 2013 ppg annual report and form 10-k 22 . separation and merger transaction on january 28 , 2013 , the company completed the previously announced separation of its commodity chemicals business and merger of its wholly-owned subsidiary , eagle spinco inc. , with a subsidiary of georgia gulf corporation in a tax ef ficient reverse morris trust transaction ( the 201ctransaction 201d ) . pursuant to the merger , eagle spinco , the entity holding ppg's former commodity chemicals business , became a wholly-owned subsidiary of georgia gulf . the closing of the merger followed the expiration of the related exchange offer and the satisfaction of certain other conditions . the combined company formed by uniting georgia gulf with ppg's former commodity chemicals business is named axiall corporation ( 201caxiall 201d ) . ppg holds no ownership interest in axiall . ppg received the necessary ruling from the internal revenue service and as a result this transaction was generally tax free to ppg and its shareholders in the united states and canada . under the terms of the exchange offer , 35249104 shares of eagle spinco common stock were available for distribution in exchange for shares of ppg common stock accepted in the offer . following the merger , each share of eagle spinco common stock automatically converted into the right to receive one share of axiall corporation common stock . accordingly , ppg shareholders who tendered their shares of ppg common stock as part of this offer received 3.2562 shares of axiall common stock for each share of ppg common stock accepted for exchange . ppg was able to accept the maximum of 10825227 shares of ppg common stock for exchange in the offer , and thereby , reduced its outstanding shares by approximately 7% ( 7 % ) . the completion of this exchange offer was a non-cash financing transaction , which resulted in an increase in "treasury stock" at a cost of $ 1.561 billion based on the ppg closing stock price on january 25 , 2013 . under the terms of the transaction , ppg received $ 900 million of cash and 35.2 million shares of axiall common stock ( market value of $ 1.8 billion on january 25 , 2013 ) which was distributed to ppg shareholders by the exchange offer as described above . in addition , ppg received $ 67 million in cash for a preliminary post-closing working capital adjustment under the terms of the transaction agreements . the net assets transferred to axiall included $ 27 million of cash on the books of the business transferred . in the transaction , ppg transferred environmental remediation liabilities , defined benefit pension plan assets and liabilities and other post-employment benefit liabilities related to the commodity chemicals business to axiall . during the first quarter of 2013 , ppg recorded a gain of $ 2.2 billion on the transaction reflecting the excess of the sum of the cash proceeds received and the cost ( closing stock price on january 25 , 2013 ) of the ppg shares tendered and accepted in the exchange for the 35.2 million shares of axiall common stock over the net book value of the net assets of ppg's former commodity chemicals business . the transaction resulted in a net partial settlement loss of $ 33 million associated with the spin out and termination of defined benefit pension liabilities and the transfer of other post-retirement benefit liabilities under the terms of the transaction . the company also incurred $ 14 million of pretax expense , primarily for professional services related to the transaction in 2013 as well as approximately $ 2 million of net expense related to certain retained obligations and post-closing adjustments under the terms of the transaction agreements . the net gain on the transaction includes these related losses and expenses . the results of operations and cash flows of ppg's former commodity chemicals business for january 2013 and the net gain on the transaction are reported as results from discontinued operations for the year -ended december 31 , 2013 . in prior periods presented , the results of operations and cash flows of ppg's former commodity chemicals business have been reclassified from continuing operations and presented as results from discontinued operations . ppg will provide axiall with certain transition services for up to 24 months following the closing date of the transaction . these services include logistics , purchasing , finance , information technology , human resources , tax and payroll processing . the net sales and income before income taxes of the commodity chemicals business that have been reclassified and reported as discontinued operations are presented in the table below: .
</details>

<details><summary>Text after the table</summary>

income from discontinued operations , net of tax $ 2197 $ 228 $ 250 less : net income attributable to non- controlling interests , discontinued operations $ 2014 $ ( 13 ) $ ( 13 ) net income from discontinued operations ( attributable to ppg ) $ 2197 $ 215 $ 237 during 2012 , $ 21 million of business separation costs are included within "income from discontinued operations , net." notes to the consolidated financial statements .
</details>

## 42. `RCL/2017/page_38.pdf-1`  (screen: disagree)

**Question:** what was the percentage change in the performance of the company's common stock for royal caribbean cruises ltd from 2013 to 2014

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `76.9%` | `109.33` | `subtract(251.44, 142.11)` |

**Gold facts**
- `table_1` the royal caribbean cruises ltd . of 12/12 is 100.00 ; the royal caribbean cruises ltd . of 12/13 is 142.11 ; the royal caribbean cruises ltd . of 12/14 is 251.44 ; the royal caribbean cruises ltd . of 12/15 is 313.65 ; the royal caribbean cruises ltd . of 12/16 is 260.04 ; the royal caribbean cruises ltd . of 12/17 is 385.47 ;

**Table**

|  | 12/12 | 12/13 | 12/14 | 12/15 | 12/16 | 12/17 |
| --- | --- | --- | --- | --- | --- | --- |
| royal caribbean cruises ltd . | 100.00 | 142.11 | 251.44 | 313.65 | 260.04 | 385.47 |
| s&p 500 | 100.00 | 132.39 | 150.51 | 152.59 | 170.84 | 208.14 |
| dow jones us travel & leisure | 100.00 | 145.48 | 169.28 | 179.27 | 192.85 | 238.77 |

<details><summary>Text before the table</summary>

performance graph the following graph compares the total return , assuming reinvestment of dividends , on an investment in the company , based on performance of the company's common stock , with the total return of the standard & poor's 500 composite stock index and the dow jones united states travel and leisure index for a five year period by measuring the changes in common stock prices from december 31 , 2012 to december 31 , 2017. .
</details>

<details><summary>Text after the table</summary>

the stock performance graph assumes for comparison that the value of the company's common stock and of each index was $ 100 on december 31 , 2012 and that all dividends were reinvested . past performance is not necessarily an indicator of future results. .
</details>

## 43. `SNA/2013/page_59.pdf-2`  (screen: disagree)

**Question:** what was the average cash dividends paid per common share from 2011 to 2013

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `1.426` | `3.64` | `add(1.58, 1.40), add(1.30, #0), add(#1, const_3), divide(#2, const_2)` |

**Gold facts**
- `table_1` the cash dividends paid per common share of 2013 is $ 1.58 ; the cash dividends paid per common share of 2012 is $ 1.40 ; the cash dividends paid per common share of 2011 is $ 1.30 ;

**Table**

|  | 2013 | 2012 | 2011 |
| --- | --- | --- | --- |
| cash dividends paid per common share | $ 1.58 | $ 1.40 | $ 1.30 |
| cash dividends paid as a percent of prior-year retained earnings | 4.5% ( 4.5 % ) | 4.4% ( 4.4 % ) | 4.7% ( 4.7 % ) |

<details><summary>Text before the table</summary>

net cash used by investing activities in 2013 also included $ 38.2 million for the may 13 , 2013 acquisition of challenger . see note 2 to the consolidated financial statements for information on the challenger acquisition . capital expenditures in 2013 , 2012 and 2011 totaled $ 70.6 million , $ 79.4 million and $ 61.2 million , respectively . capital expenditures in 2013 included continued investments related to the company 2019s execution of its strategic value creation processes around safety , quality , customer connection , innovation and rci initiatives . capital expenditures in all three years included spending to support the company 2019s strategic growth initiatives . in 2013 , the company continued to invest in new product , efficiency , safety and cost reduction initiatives to expand and improve its manufacturing capabilities worldwide . in 2012 , the company completed the construction of a fourth factory in kunshan , china , following the 2011 construction of a new engineering and research and development facility in kunshan . capital expenditures in all three years also included investments , particularly in the united states , in new product , efficiency , safety and cost reduction initiatives , as well as investments in new production and machine tooling to enhance manufacturing operations , and ongoing replacements of manufacturing and distribution equipment . capital spending in all three years also included spending for the replacement and enhancement of the company 2019s global enterprise resource planning ( erp ) management information systems , as well as spending to enhance the company 2019s corporate headquarters and research and development facilities in kenosha , wisconsin . snap-on believes that its cash generated from operations , as well as its available cash on hand and funds available from its credit facilities will be sufficient to fund the company 2019s capital expenditure requirements in 2014 . financing activities net cash used by financing activities was $ 137.8 million in 2013 , $ 127.0 million in 2012 and $ 293.7 million in 2011 . net cash used by financing activities in 2011 reflects the august 2011 repayment of $ 200 million of unsecured 6.25% ( 6.25 % ) notes upon maturity with available cash . proceeds from stock purchase and option plan exercises totaled $ 29.2 million in 2013 , $ 46.8 million in 2012 and $ 25.7 million in 2011 . snap-on has undertaken stock repurchases from time to time to offset dilution created by shares issued for employee and franchisee stock purchase plans , stock options and other corporate purposes . in 2013 , snap-on repurchased 926000 shares of its common stock for $ 82.6 million under its previously announced share repurchase programs . as of 2013 year end , snap-on had remaining availability to repurchase up to an additional $ 191.7 million in common stock pursuant to its board of directors 2019 ( the 201cboard 201d ) authorizations . the purchase of snap-on common stock is at the company 2019s discretion , subject to prevailing financial and market conditions . snap-on repurchased 1180000 shares of its common stock for $ 78.1 million in 2012 ; snap-on repurchased 628000 shares of its common stock for $ 37.4 million in 2011 . snap-on believes that its cash generated from operations , available cash on hand , and funds available from its credit facilities , will be sufficient to fund the company 2019s share repurchases , if any , in 2014 . snap-on has paid consecutive quarterly cash dividends , without interruption or reduction , since 1939 . cash dividends paid in 2013 , 2012 and 2011 totaled $ 92.0 million , $ 81.5 million and $ 76.7 million , respectively . on november 8 , 2013 , the company announced that its board increased the quarterly cash dividend by 15.8% ( 15.8 % ) to $ 0.44 per share ( $ 1.76 per share per year ) . quarterly dividends declared in 2013 were $ 0.44 per share in the fourth quarter and $ 0.38 per share in the first three quarters ( $ 1.58 per share for the year ) . quarterly dividends declared in 2012 were $ 0.38 per share in the fourth quarter and $ 0.34 per share in the first three quarters ( $ 1.40 per share for the year ) . quarterly dividends in 2011 were $ 0.34 per share in the fourth quarter and $ 0.32 per share in the first three quarters ( $ 1.30 per share for the year ) . .
</details>

<details><summary>Text after the table</summary>

cash dividends paid as a percent of prior-year retained earnings 4.5% ( 4.5 % ) 4.4% ( 4.4 % ) snap-on believes that its cash generated from operations , available cash on hand and funds available from its credit facilities will be sufficient to pay dividends in 2014 . off-balance-sheet arrangements except as included below in the section labeled 201ccontractual obligations and commitments 201d and note 15 to the consolidated financial statements , the company had no off-balance-sheet arrangements as of 2013 year end . 2013 annual report 49 .
</details>

## 44. `SNPS/2013/page_61.pdf-2`  (screen: disagree)

**Question:** what is the percentual decrease observed in the balance between 2012 and 2013?\\n

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `0.052%` | `-0.00051` | `subtract(1975971, 1976987), divide(#0, 1976987)` |

**Gold facts**
- `table_4` the balance at october 31 2012 of ( in thousands ) is $ 1976987 ;
- `table_7` the balance at october 31 2013 of ( in thousands ) is $ 1975971 ;

**Table**

|  | ( in thousands ) |
| --- | --- |
| balance at october 31 2011 | $ 1289286 |
| additions | 687195 |
| other adjustments ( 1 ) | 506 |
| balance at october 31 2012 | $ 1976987 |
| additions | 2014 |
| other adjustments ( 1 ) | -1016 ( 1016 ) |
| balance at october 31 2013 | $ 1975971 |

<details><summary>Text before the table</summary>

synopsys , inc . notes to consolidated financial statements 2014continued acquired identifiable intangible assets of $ 107.3 million , resulting in total goodwill of $ 257.6 million . identifiable intangible assets are being amortized over three to eight years . acquisition-related costs directly attributable to the business combination were $ 6.6 million for fiscal 2012 and were expensed as incurred in the consolidated statements of operations . these costs consisted primarily of employee separation costs and professional services . acquisition of magma design automation , inc . ( magma ) on february 22 , 2012 , the company acquired magma , a chip design software provider , at a per- share price of $ 7.35 . additionally , the company assumed unvested restricted stock units ( rsus ) and stock options , collectively called 201cequity awards . 201d the aggregate purchase price was approximately $ 550.2 million . this acquisition enables the company to more rapidly meet the needs of leading-edge semiconductor designers for more sophisticated design tools . the company allocated the total purchase consideration of $ 550.2 million ( including $ 6.8 million related to equity awards assumed ) to the assets acquired and liabilities assumed based on their respective fair values at the acquisition date , including acquired identifiable intangible assets of $ 184.3 million , resulting in total goodwill of $ 316.3 million . identifiable intangible assets are being amortized over three to ten years . acquisition-related costs directly attributable to the business combination totaling $ 33.5 million for fiscal 2012 were expensed as incurred in the consolidated statements of operations and consist primarily of employee separation costs , contract terminations , professional services , and facilities closure costs . other fiscal 2012 acquisitions during fiscal 2012 , the company acquired five other companies , including emulation & verification engineering , s.a . ( eve ) , for cash and allocated the total purchase consideration of $ 213.2 million to the assets acquired and liabilities assumed based on their respective fair values , resulting in total goodwill of $ 118.1 million . acquired identifiable intangible assets totaling $ 73.3 million were valued using appropriate valuation methods such as income or cost methods and are being amortized over their respective useful lives ranging from one to eight years . during fiscal 2012 , acquisition-related costs totaling $ 6.8 million were expensed as incurred in the consolidated statements of operations . fiscal 2011 acquisitions during fiscal 2011 , the company completed two acquisitions for cash and allocated the total purchase consideration of $ 37.4 million to the assets and liabilities acquired based on their respective fair values at the acquisition date resulting in goodwill of $ 30.6 million . acquired identifiable intangible assets of $ 9.3 million are being amortized over two to ten years . note 4 . goodwill and intangible assets goodwill: .
</details>

<details><summary>Text after the table</summary>

.
</details>

## 45. `STT/2009/page_109.pdf-3`  (screen: disagree)

**Question:** what was the average gross gains from sales of available-for-sale securities from 2007 to 2009

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `180.7` | `272.5` | `add(418, 100), add(#0, 24), add(#1, const_3), divide(#2, const_2)` |

**Gold facts**
- `table_1` ( in millions ) the gross gains from sales of available-for-sale securities of 2009 is $ 418 ; the gross gains from sales of available-for-sale securities of 2008 is $ 100 ; the gross gains from sales of available-for-sale securities of 2007 is $ 24 ;

**Table**

| ( in millions ) | 2009 | 2008 | 2007 |
| --- | --- | --- | --- |
| gross gains from sales of available-for-sale securities | $ 418 | $ 100 | $ 24 |
| gross losses from sales of available-for-sale securities | -50 ( 50 ) | -32 ( 32 ) | -17 ( 17 ) |
| gross losses from other-than-temporary impairment | -1155 ( 1155 ) | -122 ( 122 ) | -34 ( 34 ) |
| losses not related to credit ( 1 ) | 928 | 2014 | 2014 |
| net impairment losses | -227 ( 227 ) | -122 ( 122 ) | -34 ( 34 ) |
| gains ( losses ) related to investment securities net | $ 141 | $ -54 ( 54 ) | $ -27 ( 27 ) |

<details><summary>Text before the table</summary>

in connection with our assessment of impairment we recorded gross other-than-temporary impairment of $ 1.15 billion for 2009 , compared to $ 122 million for 2008 . of the total recorded , $ 227 million related to credit and was recognized in our consolidated statement of income . the remaining $ 928 million related to factors other than credit , more fully discussed below , and was recognized , net of related taxes , in oci in our consolidated statement of condition . the $ 227 million was composed of $ 151 million associated with expected credit losses , $ 54 million related to management 2019s decision to sell the impaired securities prior to their recovery in value , and $ 22 million related to adverse changes in the timing of expected future cash flows from the securities . the majority of the impairment losses related to non-agency securities collateralized by mortgages , for which management concluded had experienced credit losses based on the present value of the securities 2019 expected future cash flows . these securities are classified as asset-backed securities in the foregoing investment securities tables . as described in note 1 , management periodically reviews the fair values of investment securities to determine if other-than-temporary impairment has occurred . this review encompasses all investment securities and includes such quantitative factors as current and expected future interest rates and the length of time that a security 2019s cost basis has exceeded its fair value , and includes investment securities for which we have issuer- specific concerns regardless of quantitative factors . gains and losses related to investment securities were as follows for the years ended december 31: .
</details>

<details><summary>Text after the table</summary>

( 1 ) these losses were recognized as a component of oci ; see note 12 . we conduct periodic reviews to evaluate each security that is impaired . impairment exists when the current fair value of an individual security is below its amortized cost basis . for debt securities available for sale and held to maturity , other-than-temporary impairment is recorded in our consolidated statement of income when management intends to sell ( or may be required to sell ) securities before they recover in value , or when management expects the present value of cash flows expected to be collected to be less than the amortized cost of the impaired security ( a credit loss ) . our review of impaired securities generally includes : 2022 the identification and evaluation of securities that have indications of possible other-than-temporary impairment , such as issuer-specific concerns including deteriorating financial condition or bankruptcy ; 2022 the analysis of expected future cash flows of securities , based on quantitative and qualitative factors ; 2022 the analysis of the collectability of those future cash flows , including information about past events , current conditions and reasonable and supportable forecasts ; 2022 the analysis of individual impaired securities , including consideration of the length of time the security has been in an unrealized loss position and the anticipated recovery period ; 2022 the discussion of evidential matter , including an evaluation of factors or triggers that could cause individual securities to be deemed other-than-temporarily impaired and those that would not support other-than-temporary impairment ; and 2022 documentation of the results of these analyses . factors considered in determining whether impairment is other than temporary include : 2022 the length of time the security has been impaired; .
</details>

## 46. `TROW/2009/page_24.pdf-3`  (screen: disagree)

**Question:** what was the change in capital gain distributions received between 2007 and 2008 as a percent of the capital gain distributions received in 2007?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `-33%` | `-0.74661` | `multiply(16.5, const_m1), divide(#0, 22.1)` |

**Gold facts**
- `table_1` the capital gain distributions received of 2007 is $ 22.1 ; the capital gain distributions received of 2008 is $ 5.6 ; the capital gain distributions received of change is $ -16.5 ( 16.5 ) ;

**Table**

|  | 2007 | 2008 | change |
| --- | --- | --- | --- |
| capital gain distributions received | $ 22.1 | $ 5.6 | $ -16.5 ( 16.5 ) |
| other than temporary impairments recognized | -.3 ( .3 ) | -91.3 ( 91.3 ) | -91.0 ( 91.0 ) |
| net gains ( losses ) realized onfund dispositions | 5.5 | -4.5 ( 4.5 ) | -10.0 ( 10.0 ) |
| net gain ( loss ) recognized on fund holdings | $ 27.3 | $ -90.2 ( 90.2 ) | $ -117.5 ( 117.5 ) |

<details><summary>Text before the table</summary>

administrative fees , which increased $ 5.8 million to $ 353.9 million , are generally offset by related operating expenses that are incurred to provide services to the funds and their investors . our largest expense , compensation and related costs , increased $ 18.4 million or 2.3% ( 2.3 % ) from 2007 . this increase includes $ 37.2 million in salaries resulting from an 8.4% ( 8.4 % ) increase in our average staff count and an increase of our associates 2019 base salaries at the beginning of the year . at december 31 , 2008 , we employed 5385 associates , up 6.0% ( 6.0 % ) from the end of 2007 , primarily to add capabilities and support increased volume-related activities and other growth over the past few years . over the course of 2008 , we slowed the growth of our associate base from earlier plans and the prior year . we also reduced our annual bonuses $ 27.6 million versus the 2007 year in response to unfavorable financial market conditions that negatively impacted our operating results . the balance of the increase is attributable to higher employee benefits and employment-related expenses , including an increase of $ 5.7 million in stock-based compensation . after higher spending during the first quarter of 2008 versus 2007 , investor sentiment in the uncertain and volatile market environment caused us to reduce advertising and promotion spending , which for the year was down $ 3.8 million from 2007 . occupancy and facility costs together with depreciation expense increased $ 18 million , or 12% ( 12 % ) compared to 2007 . we expanded and renovated our facilities in 2008 to accommodate the growth in our associates to meet business demands . other operating expenses were up $ 3.3 million from 2007 . we increased our spending $ 9.8 million , primarily for professional fees and information and other third-party services . reductions in travel and charitable contributions partially offset these increases . our non-operating investment activity resulted in a net loss of $ 52.3 million in 2008 as compared to a net gain of $ 80.4 million in 2007 . this change of $ 132.7 million is primarily attributable to losses recognized in 2008 on our investments in sponsored mutual funds , which resulted from declines in financial market values during the year. .
</details>

<details><summary>Text after the table</summary>

we recognized other than temporary impairments of our investments in sponsored mutual funds because of declines in fair value below cost for an extended period . the significant declines in fair value below cost that occurred in 2008 were generally attributable to adverse market conditions . in addition , income from money market and bond fund holdings was $ 19.3 million lower than in 2007 due to the significantly lower interest rate environment of 2008 . lower interest rates also led to substantial capital appreciation on our $ 40 million holding of u.s . treasury notes that we sold in december 2008 at a $ 2.6 million gain . the 2008 provision for income taxes as a percentage of pretax income is 38.4% ( 38.4 % ) , up from 37.7% ( 37.7 % ) in 2007 , primarily to reflect changes in state income tax rates and regulations and certain adjustments made prospectively based on our annual income tax return filings for 2007 . c a p i t a l r e s o u r c e s a n d l i q u i d i t y . during 2009 , stockholders 2019 equity increased from $ 2.5 billion to $ 2.9 billion . we repurchased nearly 2.3 million common shares for $ 67 million in 2009 . tangible book value is $ 2.2 billion at december 31 , 2009 , and our cash and cash equivalents and our mutual fund investment holdings total $ 1.4 billion . given the availability of these financial resources , we do not maintain an available external source of liquidity . on january 20 , 2010 , we purchased a 26% ( 26 % ) equity interest in uti asset management company and an affiliate for $ 142.4 million . we funded the acquisition from our cash holdings . in addition to the pending uti acquisition , we had outstanding commitments to fund other investments totaling $ 35.4 million at december 31 , 2009 . we presently anticipate funding 2010 property and equipment expenditures of about $ 150 million from our cash balances and operating cash inflows . 22 t . rowe price group annual report 2009 .
</details>

## 47. `V/2013/page_113.pdf-1`  (screen: disagree)

**Question:** what is the percentage change in fair value of option from 2012 to 2013?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `31.6%` | `9.38` | `subtract(39.03, 29.65)` |

**Gold facts**
- `table_5` the fair value per option granted of 2013 is $ 39.03 ; the fair value per option granted of 2012 is $ 29.65 ; the fair value per option granted of 2011 is $ 27.50 ;

**Table**

|  | 2013 | 2012 | 2011 |
| --- | --- | --- | --- |
| expected term ( in years ) ( 1 ) | 6.08 | 6.02 | 5.16 |
| risk-free rate of return ( 2 ) | 0.8% ( 0.8 % ) | 1.2% ( 1.2 % ) | 1.2% ( 1.2 % ) |
| expected volatility ( 3 ) | 29.3% ( 29.3 % ) | 34.9% ( 34.9 % ) | 33.4% ( 33.4 % ) |
| expected dividend yield ( 4 ) | 0.9% ( 0.9 % ) | 0.9% ( 0.9 % ) | 0.8% ( 0.8 % ) |
| fair value per option granted | $ 39.03 | $ 29.65 | $ 27.50 |

<details><summary>Text before the table</summary>

visa inc . notes to consolidated financial statements 2014 ( continued ) september 30 , 2013 ( 4 ) participating securities are unvested share-based payment awards that contain non-forfeitable rights to dividends or dividend equivalents , such as the company 2019s restricted stock awards , restricted stock units and earned performance-based shares . note 16 2014share-based compensation the company 2019s 2007 equity incentive compensation plan , or the eip , authorizes the compensation committee of the board of directors to grant non-qualified stock options ( 201coptions 201d ) , restricted stock awards ( 201crsas 201d ) , restricted stock units ( 201crsus 201d ) and performance-based shares to its employees and non- employee directors , for up to 59 million shares of class a common stock . shares available for award may be either authorized and unissued or previously issued shares subsequently acquired by the company . the eip will continue to be in effect until all of the common stock available under the eip is delivered and all restrictions on those shares have lapsed , unless the eip is terminated earlier by the company 2019s board of directors . no awards may be granted under the plan on or after 10 years from its effective date . share-based compensation cost is recorded net of estimated forfeitures on a straight-line basis for awards with service conditions only , and on a graded-vesting basis for awards with service , performance and market conditions . the company 2019s estimated forfeiture rate is based on an evaluation of historical , actual and trended forfeiture data . for fiscal 2013 , 2012 , and 2011 , the company recorded share-based compensation cost of $ 179 million , $ 147 million and $ 154 million , respectively , in personnel on its consolidated statements of operations . the amount of capitalized share-based compensation cost was immaterial during fiscal 2013 , 2012 and 2011 . options options issued under the eip expire 10 years from the date of grant and vest ratably over three years from the date of grant , subject to earlier vesting in full under certain conditions . during fiscal 2013 , 2012 and 2011 , the fair value of each stock option was estimated on the date of grant using a black-scholes option pricing model with the following weighted-average assumptions: .
</details>

<details><summary>Text after the table</summary>

( 1 ) based on a set of peer companies that management believes is generally comparable to visa . ( 2 ) based upon the zero coupon u.s . treasury bond rate over the expected term of the awards . ( 3 ) based on the average of the company 2019s implied and historical volatility . as the company 2019s publicly-traded stock history is relatively short , historical volatility relies in part on the historical volatility of a group of peer companies that management believes is generally comparable to visa . the relative weighting between visa historical volatility and the historical volatility of the peer companies is based on the percentage of years visa stock price information has been available since its initial public offering compared to the expected term . the expected volatilities ranged from 27% ( 27 % ) to 29% ( 29 % ) in fiscal 2013 . ( 4 ) based on the company 2019s annual dividend rate on the date of grant. .
</details>

## 48. `VNO/2010/page_88.pdf-2`  (screen: disagree)

**Question:** what was the average price of the the nareit all equity index from 2005 to 2009

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `102.2` | `258.0` | `add(100, 135), add(#0, 114), add(#1, 71), add(#2, 91), add(#3, const_5), divide(#4, const_2)` |

**Gold facts**
- `table_3` the the nareit all equity index of 2005 is 100 ; the the nareit all equity index of 2006 is 135 ; the the nareit all equity index of 2007 is 114 ; the the nareit all equity index of 2008 is 71 ; the the nareit all equity index of 2009 is 91 ; the the nareit all equity index of 2010 is 116 ;

**Table**

|  | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 |
| --- | --- | --- | --- | --- | --- | --- |
| vornado realty trust | 100 | 151 | 113 | 81 | 100 | 124 |
| s&p 500 index | 100 | 116 | 122 | 77 | 97 | 112 |
| the nareit all equity index | 100 | 135 | 114 | 71 | 91 | 116 |

<details><summary>Text before the table</summary>

performance graph the following graph is a comparison of the five-year cumulative return of our common shares , the standard & poor 2019s 500 index ( the 201cs&p 500 index 201d ) and the national association of real estate investment trusts 2019 ( 201cnareit 201d ) all equity index ( excluding health care real estate investment trusts ) , a peer group index . the graph assumes that $ 100 was invested on december 31 , 2005 in our common shares , the s&p 500 index and the nareit all equity index and that all dividends were reinvested without the payment of any commissions . there can be no assurance that the performance of our shares will continue in line with the same or similar trends depicted in the graph below. .
</details>

<details><summary>Text after the table</summary>

.
</details>

## 49. `WRK/2018/page_106.pdf-2`  (screen: disagree)

**Question:** by what percent did the value of reductions increase between 2016 and 2018?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `275.9%` | `0.34808` | `divide(40.6, 10.8), divide(#0, 10.8)` |

**Gold facts**
- `text_6` these valuation allowances have been recorded due to uncertainty regarding our ability to generate sufficient taxable income in the appropriate taxing jurisdiction .
- `table_4` the reductions of 2018 is -40.6 ( 40.6 ) ; the reductions of 2017 is -24.8 ( 24.8 ) ; the reductions of 2016 is -10.8 ( 10.8 ) ;

**Table**

|  | 2018 | 2017 | 2016 |
| --- | --- | --- | --- |
| balance at beginning of fiscal year | $ 219.1 | $ 177.2 | $ 100.2 |
| increases | 50.8 | 54.3 | 24.8 |
| allowances related to purchase accounting ( 1 ) | 0.1 | 12.4 | 63.0 |
| reductions | -40.6 ( 40.6 ) | -24.8 ( 24.8 ) | -10.8 ( 10.8 ) |
| balance at end of fiscal year | $ 229.4 | $ 219.1 | $ 177.2 |

<details><summary>Text before the table</summary>

westrock company notes to consolidated financial statements fffd ( continued ) at september 30 , 2018 and september 30 , 2017 , gross net operating losses for foreign reporting purposes of approximately $ 698.4 million and $ 673.7 million , respectively , were available for carryforward . a majority of these loss carryforwards generally expire between fiscal 2020 and 2038 , while a portion have an indefinite carryforward . the tax effected values of these net operating losses are $ 185.8 million and $ 182.6 million at september 30 , 2018 and 2017 , respectively , exclusive of valuation allowances of $ 161.5 million and $ 149.6 million at september 30 , 2018 and 2017 , respectively . at september 30 , 2018 and 2017 , we had state tax credit carryforwards of $ 64.8 million and $ 54.4 million , respectively . these state tax credit carryforwards generally expire within 5 to 10 years ; however , certain state credits can be carried forward indefinitely . valuation allowances of $ 56.1 million and $ 47.3 million at september 30 , 2018 and 2017 , respectively , have been provided on these assets . these valuation allowances have been recorded due to uncertainty regarding our ability to generate sufficient taxable income in the appropriate taxing jurisdiction . the following table represents a summary of the valuation allowances against deferred tax assets for fiscal 2018 , 2017 and 2016 ( in millions ) : .
</details>

<details><summary>Text after the table</summary>

( 1 ) amounts in fiscal 2018 and 2017 relate to the mps acquisition . adjustments in fiscal 2016 relate to the combination and the sp fiber acquisition . consistent with prior years , we consider a portion of our earnings from certain foreign subsidiaries as subject to repatriation and we provide for taxes accordingly . however , we consider the unremitted earnings and all other outside basis differences from all other foreign subsidiaries to be indefinitely reinvested . accordingly , we have not provided for any taxes that would be due . as of september 30 , 2018 , we estimate our outside basis difference in foreign subsidiaries that are considered indefinitely reinvested to be approximately $ 1.5 billion . the components of the outside basis difference are comprised of purchase accounting adjustments , undistributed earnings , and equity components . except for the portion of our earnings from certain foreign subsidiaries where we provided for taxes , we have not provided for any taxes that would be due upon the reversal of the outside basis differences . however , in the event of a distribution in the form of dividends or dispositions of the subsidiaries , we may be subject to incremental u.s . income taxes , subject to an adjustment for foreign tax credits , and withholding taxes or income taxes payable to the foreign jurisdictions . as of september 30 , 2018 , the determination of the amount of unrecognized deferred tax liability related to any remaining undistributed foreign earnings not subject to the transition tax and additional outside basis differences is not practicable. .
</details>

## 50. `ZBH/2004/page_44.pdf-2`  (screen: disagree)

**Question:** what was the total change in gross margins between december 31 , 2003 and december 312004?

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `5.7%` | `1.0837` | `divide(73.8, 68.1)` |

**Gold facts**
- `table_5` three month period ended december 31 2003 gross margin the year ended december 31 2004 gross margin of 68.1% ( 68.1 % ) is 73.8% ( 73.8 % ) ;

**Table**

| three month period ended december 31 2003 gross margin | 68.1% ( 68.1 % ) |
| --- | --- |
| inventory step-up charge | 4.1 |
| increased average selling prices | 1.8 |
| operating segment and product category mix | 0.2 |
| other | -0.4 ( 0.4 ) |
| year ended december 31 2004 gross margin | 73.8% ( 73.8 % ) |

<details><summary>Text before the table</summary>

z i m m e r h o l d i n g s , i n c . a n d s u b s i d i a r i e s 2 0 0 4 f o r m 1 0 - k for the same 2003 period . amortization expense increased togross profit $ 39.1 million , or 1.3 percent of sales , during the year ended gross profit as a percentage of net sales was december 31 , 2004 compared to $ 10.9 million , or less than 73.8 percent in 2004 , compared to 72.8 percent in 2003 and 1 percent of sales , during the year ended december 31 , 2003 . 68.1 percent for the three month period ended december 31 , the increase was primarily due to amortization expense 2003 ( the first quarter of combined zimmer and centerpulse related to centerpulse and implex finite lived intangible operations ) . the following table reconciles the gross margin assets . in addition , during 2004 the company continued to for the year ended december 31 , 2004 and for the three introduce or expand strategic programs and activities . in month period ended december 31 , 2003 . 2004 , the zimmer institute and its satellite locations were well utilized with over 1400 surgeons trained , compared tothree month period ended december 31 , 2003 500 surgeons trained in 2003 . these surgeon training costsgross margin 68.1% ( 68.1 % ) are recognized in sg&a . the company also recognizedinventory step-up charge 4.1 approximately $ 5 million of sarbanes-oxley complianceincreased average selling prices 1.8 expenses , including consultant fees and increased audit fees.operating segment and product category mix 0.2 these increases were partially offset by expense synergiesother ( 0.4 ) realized from the centerpulse acquisition and controlled .
</details>

<details><summary>Text after the table</summary>

spending . the company has begun to realize synergies from the centerpulse acquisition and expects to pursue additionaldecreased centerpulse and implex inventory step-up synergy opportunities . the company estimates that over thecharges as a percentage of net sales during 2004 next two years it will be able to reduce annual sg&a as a ( $ 59.4 million , or 2.0 percent of net sales ) compared to the percentage of net sales to 38.9 percent or lower , representingthree month period ended december 31 , 2003 ( $ 42.7 million , a 200 basis point improvement over the fourth quarter ofor 6.1 percent of net sales ) and increases in average selling 2003 ( the first quarter of combined zimmer and centerpulseprices were the primary contributors to improved gross operations ) .margins . in addition , operating segment mix and product acquisition and integration expenses related to thecategory mix both had a positive impact on gross margins acquisitions of centerpulse and implex were $ 81.1 milliondue to higher sales growth in the more profitable americas compared to $ 79.6 million for the same 2003 period andsegment compared to europe and asia pacific , higher sales included $ 24.4 million of sales agent and lease contractgrowth of reconstructive implants and the continued shift to termination expenses , $ 24.2 million of integration consultingpremium products . offsetting these favorable impacts were a expenses , $ 9.4 million of employee severance and retentionvariety of other items , including increased royalty expenses expenses , $ 7.8 million of professional fees , $ 5.2 million ofand higher losses on foreign exchange contracts included in personnel expenses and travel for full-time integration teamcost of products sold , partially offset by reduced members , $ 4.3 million of costs related to integrating themanufacturing costs due to automation , vertical integration company 2019s information technology systems , $ 2.9 million ofand process improvements . costs related to relocation of facilities , and $ 2.9 million of operating expenses other miscellaneous acquisition and integration expenses . r&d as a percentage of net sales was 5.6 percent for operating profit , income taxes and net earnings years ended december 31 , 2004 and 2003 . r&d increased to operating profit for the year ended december 31 , 2004$ 166.7 million from $ 105.8 million reflecting a full year of increased 69 percent to $ 763.2 million from $ 450.7 million incenterpulse research and development expenses and the comparable 2003 period . operating profit growth wasincreased spending on active projects focused on areas of driven by zimmer standalone sales growth , operating profitstrategic significance . the company 2019s pipeline includes 146 contributed by centerpulse , effectively controlled operatingprojects with a total investment equal to or greater than expenses and the absence of in-process research and$ 1 million . of the 146 projects , approximately two-thirds development expense in 2004 compared to $ 11.2 million ininvolve new platforms , mis or other technologies . for 2003 . these favorable items were partially offset byexample , the company 2019s orthobiological research group in centerpulse and implex inventory step-up of $ 59.4 million inaustin , texas is developing innovative solutions for hip 2004 compared to $ 42.7 million in 2003 and intangible assetfracture and cartilage regeneration . during 2004 , the amortization of $ 39.1 million in 2004 versus $ 10.9 million incompany delivered more than 40 major development projects 2003.to market . the company has strategically targeted r&d the effective tax rate on earnings before income taxesspending to be at the high end of what management believes minority interest and cumulative effect of change into be an average of 4-6 percent for the industry . the accounting principle decreased to 25.9 percent for the yearcompany expects over the next few years to invest in ended december 31 , 2004 from 33.6 percent for the sameresearch and development at approximately 5.5 percent to period in 2003 . a major component of the decrease6 percent of sales . ( 4.7 percent , or $ 34.5 million ) was the result of revaluingsg&a as a percentage of net sales was 39.9 percent for deferred taxes of acquired centerpulse operations due to athe year ended december 31 , 2004 compared to 38.8 percent reduction in the ongoing swiss tax rate . the major reasons .
</details>

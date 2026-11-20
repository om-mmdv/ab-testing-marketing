\# Marketing A/B Test Analysis



Statistical analysis of an online advertising experiment: did showing ads

increase the conversion rate compared with a control group that saw a neutral

public service announcement (PSA)?



Dataset: \[Marketing A/B Testing](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing)

on Kaggle (588,101 users). The CSV is not included in this repository.



\## Key findings



| Group | Users | Conversions | Conversion rate |

|---|---|---|---|

| Ad (treatment) | 564,577 | 14,423 | 2.555% |

| PSA (control) | 23,524 | 420 | 1.785% |



\- The difference is \*\*+0.769 percentage points\*\* (95% CI: 0.587 to 0.936),

&#x20; a relative lift of \*\*43%\*\*.

\- Two-proportion z-test: z = 7.37, \*\*p = 1.7e-13\*\*. The result is statistically

&#x20; significant.

\- A bootstrap (5,000 resamples) gives almost the same interval

&#x20; (0.596 to 0.944 pp), so the conclusion does not depend on the test used.

\- The ad produced about \*\*4,300 extra purchases\*\* (plausible range roughly

&#x20; 3,400 to 5,300), which is about 30% of all purchases in the ad group.



!\[Conversion by group](assets/conversion\_by\_group.png)



!\[Bootstrap](assets/bootstrap\_difference.png)



\## Who responds to the ad?



!\[Uplift by ads seen](assets/uplift\_by\_ads.png)



The effect is concentrated among users who saw many ads:



| Ads seen | Uplift (pp) |

|---|---|

| 1-20 | about 0 (not distinguishable from zero) |

| 21-50 | +0.74 |

| 51-100 | +5.86 |

| 100+ | +5.25 |



Breakdowns by weekday and by hour show a mostly positive but noisy picture;

the control group is small in each segment, so these results should be treated

as hypotheses rather than conclusions.



!\[Uplift by weekday](assets/uplift\_by\_day.png)



\## Project structure



```

src/

├── data.py       # loading and cleaning

├── explore.py    # data quality checks, group comparison

├── analysis.py   # z-test and confidence interval

├── impact.py     # bootstrap and practical impact

└── segments.py   # uplift by ads seen, weekday, hour

```



\## Installation



```bash

git clone https://github.com/om-mmdv/ab-testing-marketing.git

cd ab-testing-marketing

python -m venv venv

venv\\Scripts\\activate        # Windows

source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

```



Download `marketing\_AB.csv` from Kaggle and put it into the `data/` folder.



\## Usage



```bash

python -m src.explore

python -m src.analysis

python -m src.impact

python -m src.segments

```



\## Limitations



\- \*\*Unequal groups:\*\* 96% of users are in the ad group, so the control group

&#x20; gives a less precise estimate (this is why intervals are wide in segments).

\- \*\*Not a verified randomization:\*\* we only know the groups look similar on

&#x20; total ads seen; weekday shares differ slightly between groups.

\- \*\*Number of ads is not randomly assigned:\*\* active users see more ads and

&#x20; buy more. We compare ad and PSA only within the same bucket of ads seen,

&#x20; but this does not prove causality.

\- \*\*Multiple comparisons:\*\* many segments were examined, so some differences

&#x20; may appear by chance.

\- \*\*Missing information:\*\* there is no data on revenue or ad cost, so we

&#x20; cannot compute return on investment.



\## Possible improvements



\- Compare revenue, not only conversion

\- Run a follow-up experiment that randomizes the number of ads shown

\- Correct p-values for multiple comparisons in the segment analysis


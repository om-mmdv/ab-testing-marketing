# Marketing A/B Test Analysis

**Live demo:** https://YOUR-APP-LINK.streamlit.app/

Statistical analysis of an online advertising experiment: did showing ads increase the conversion rate compared with a control group that saw a neutral public service announcement (PSA)? Includes an interactive Streamlit dashboard.

Dataset: [Marketing A/B Testing](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing) on Kaggle (588,101 users). The CSV is not included; the dashboard uses a small aggregated file, data/summary.csv.

## Key findings

| Group | Users | Conversions | Conversion rate |
|---|---|---|---|
| Ad (treatment) | 564,577 | 14,423 | 2.555% |
| PSA (control) | 23,524 | 420 | 1.785% |

- The difference is +0.769 percentage points (95% CI: 0.587 to 0.936), a relative lift of 43%.
- Two-proportion z-test: z = 7.37, p = 1.7e-13. The result is statistically significant.
- A bootstrap (5,000 resamples) gives almost the same interval (0.596 to 0.944 pp).
- The ad produced about 4,300 extra purchases (plausible range 3,400 to 5,300), roughly 30% of all purchases in the ad group.

## Who responds to the ad?

| Ads seen | Uplift (pp) |
|---|---|
| 1-20 | about 0 (not distinguishable from zero) |
| 21-50 | +0.74 |
| 51-100 | +5.86 |
| 100+ | +5.25 |

Breakdowns by weekday and hour are mostly positive but noisy, so they should be treated as hypotheses.

## Dashboard

Three tabs: overall result with an adjustable significance level, segment uplift (ads seen, weekday, hour) and a calculator for your own experiment.

```bash
streamlit run app.py
```

## Installation

```bash
git clone https://github.com/om-mmdv/ab-testing-marketing.git
cd ab-testing-marketing
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Put marketing_AB.csv into data/, then run: python -m src.explore, analysis, impact, segments, export.

## Limitations

- Unequal groups: 96% of users are in the ad group, so the control estimate is less precise.
- Randomization is not verified; groups only look similar on total ads seen.
- The number of ads is not randomly assigned: active users see more ads and buy more.
- Many segments were examined, so some differences may appear by chance.
- No revenue or cost data, so no return on investment.

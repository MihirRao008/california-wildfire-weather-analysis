# Interview Guide: California Wildfire Risk & Weather Analysis

This guide covers how to explain the project clearly and honestly. Before an interview, reopen the notebooks
and make sure you can explain each step in your own words. The answers below are starting points; put them in
your own voice.

---

## The 30-second version

> "I analyzed about 250,000 California wildfires from 1992 to 2020 using the U.S. Forest Service's national fire
> database. I matched each fire to NASA daily weather data for the location and day it was discovered. Then I
> looked at how temperature, humidity, wind, and rainfall relate to how large fires became. Hotter and drier days
> were consistently associated with a higher chance of a fire growing past 100 acres. For example, 3.4% of fires
> on the hottest days reached that size, compared with 0.9% on the coolest days. But weather on the discovery
> day explained only about 3.5% of the variation in fire size. My main takeaway was that weather alone is a weak
> predictor and that fuel, terrain, and firefighting response matter a lot."

---

## Common questions

### "What was your project?"
A data analysis project on whether weather conditions are associated with wildfire size in California. I
cleaned and merged two government datasets, explored patterns by year, month, and location, measured
correlations, and built a simple predictive model to test how much weather explains.

### "Why did you choose this topic?"
I'm from the Bay Area, where wildfire smoke and fire seasons affect everyone. I also wanted a project with real,
messy public data where I'd have to combine two sources and not just analyze a pre-cleaned file.

### "Where did the data come from?"
- **Wildfires:** the Fire Program Analysis Fire-Occurrence Database (FPA FOD), 6th edition, published by the
  USDA Forest Service. It combines federal, state, and local fire reports from 1992–2020. I filtered it to the
  251,881 California records.
- **Weather:** the NASA POWER daily API, which provides modeled weather (from the MERRA-2 reanalysis) on a
  global grid. I pulled daily max temperature, humidity, wind speed, and precipitation for the 176 grid points
  nearest the fires.

*Why these?* Both come from federal scientific agencies, both are free and well documented, and the FPA FOD
includes small fires. That was important: if I only had big fires, I couldn't compare them against fires that
stayed small.

### "How did you clean the data?"
- Loaded California rows from a SQLite database with a SQL query.
- Converted dates stored as text (`2/2/2005`) into real dates.
- Checked for duplicate records (none) and impossible values. I removed one fire located outside California.
- **Kept** the 38% of fires with no county listed, because dropping them would lose over a third of the data,
  and I could still locate them by latitude and longitude.
- For the weather data, replaced NASA's `-999` "missing" code, converted units (°C→°F, m/s→mph), and calculated
  total rain over the previous 7 days.
- Printed row counts before and after each step so no data disappeared without me noticing.

### "How did you combine the datasets?"
NASA's weather comes on a grid, with a point every 0.5° of latitude and 0.625° of longitude (about 55 km apart).
For each fire I rounded its coordinates to the nearest grid point. Then I joined on that grid point plus the
discovery date. I used a **left join** so every fire was kept, and all 251,880 fires found a weather match.

*Why not the nearest weather station?* Most stations don't record humidity, and station records have gaps. The
grid approach is simpler and complete, but less precise, and I list that as a limitation.

### "What was the hardest part?"
Two good options:
- **The skewed fire sizes.** The median fire is 0.2 acres but the largest is 589,368 acres. Averages were
  misleading, so I switched to medians, the share of fires reaching 100+ acres, and a log transform.
- **Matching the datasets.** I had to understand how NASA's grid works to connect a fire's exact location to
  the right weather data.

### "What did you discover?"
- 93% of fires burn under 10 acres. The 2.2% that reach 100+ acres account for **97.5% of all area burned**.
- Hotter and drier discovery days were associated with more large fires: 0.9% → 3.4% from the coolest to the
  hottest tenth of days, and 3.7% → 0.6% from the driest to the most humid tenth.
- Combining conditions: 1.4% of fires became large on days that were not hot, dry, or windy, vs. about 3.5% on
  days meeting two or three of those conditions.
- July has the most fires, but August and June have the highest share of fires that grow large.
- 2020 burned by far the most area (4.25 million acres).
- Weather explained only a small part of fire size overall.

### "What statistical methods did you use?"
Descriptive statistics (medians, counts, percentages by group), Pearson and Spearman correlation, and comparing
the share of large fires across deciles of each weather variable.

### "Why did you use correlation? Why Spearman?"
Correlation gives one number (−1 to +1) for how strongly two variables move together. **Pearson** measures a
straight-line relationship and is thrown off by extreme values. On raw acres it was nearly zero for every
variable, because a few giant fires dominate it. **Spearman** correlates the *ranks* instead of the values, so it
works well for skewed data. My strongest result was ρ = 0.13 for temperature, which is weak.

### "Why doesn't correlation equal causation?"
Two things can move together because of a third factor. Hot days happen in summer, when vegetation is driest,
more people are outdoors, and lightning storms occur. Any of those could explain part of the temperature
relationship. My data is observational, with no experiment and no control for fuel or terrain, so I describe
associations only.

### "Why did you log-transform fire size?"
Fire size ranges from 0.001 to 589,368 acres. On a normal scale, almost all fires are squashed near zero and a
handful of giants control every average or regression line. `log(1 + acres)` spreads the values out (0.1 acres
becomes 0.1, 100 acres becomes 4.6, 100,000 acres becomes 11.5). I used `log1p` so a size of zero would still
work.

### "What machine learning model did you use?"
I predicted log fire size from temperature, humidity, wind, rain that day, rain in the prior week, and month,
with three models:
1. A **baseline** that always predicts the average, which any real model has to beat.
2. **Linear Regression**, because it's simple and interpretable.
3. A **Random Forest**, many decision trees averaged together, which can capture curved relationships and
   interactions such as "hot *and* dry."

### "How did you evaluate it?"
- An 80/20 train/test split, so the models were scored on data they never saw.
- Three metrics:
  - **MAE**, the average error.
  - **RMSE**, which punishes big misses more.
  - **R²**, the share of variation explained compared with predicting the average.
- Results: the Random Forest had R² = 0.035 and Linear Regression had R² = 0.019.
- I also did a stricter test, training on 1992–2014 and predicting 2015–2020. There neither model beat the
  baseline (R² ≈ 0). That told me the small gains didn't hold up for future years.

*If asked "isn't that a bad model?"*: "Yes, as a predictor it's weak, and that's the finding. It shows that
discovery-day weather alone can't explain fire size. I think reporting that honestly is more useful than tuning
the model to look better."

### "What does feature importance tell you?"
In the Random Forest, temperature had the highest importance (0.34), then wind (0.22) and humidity (0.19).
Importance only means the model found a variable useful for splitting the data. It doesn't mean the variable
causes large fires. This built-in measure also tends to favor variables with many distinct values, and it splits
credit between correlated variables like temperature and humidity.

### "What limitations does the project have?"
- Weather is a ~55 km grid average, not the conditions at the fire.
- I only used discovery-day weather, but big fires burn for days or weeks.
- Daily-average wind and humidity miss afternoon extremes and gusts.
- No data on fuel/vegetation, terrain, or firefighting response.
- Missing counties (38%) and causes (38%), plus reporting that changed over time.
- Observational data, so the results are associations, not causes.

### "What would you improve with more time?"
- Add fuel and vegetation data (LANDFIRE), a drought index, and elevation/slope.
- Use higher-resolution weather (gridMET, 4 km) over the whole burn period.
- Reframe the model as predicting the *probability* a fire becomes large (classification).
- Match fires to counties spatially using coordinates to fill in missing counties.

### "What code did you personally write?"
**Answer this honestly.** This project was built with help from an AI assistant. If you're asked, say so, and
then show that you understand it:

> "I used an AI assistant to help build it, and I went through every step to make sure I understand it. For
> example, I can walk you through how the grid matching works, or why I chose Spearman over Pearson."

To make this answer strong, do some of the work yourself before interviews:
- Rerun each notebook and read every cell's output.
- Change something and see what happens. For example, change the "large fire" threshold from 100 to 1,000
  acres in `src/data_cleaning.py`, or add a new chart.
- Be ready to explain any single function in `src/` line by line.

Claiming you wrote everything alone is risky: interviewers often ask you to modify code live or explain a
specific line.

---

## Key numbers to remember

| Fact | Value |
|---|---|
| California fires analyzed | 251,880 (1992–2020) |
| Fires reaching 100+ acres | 2.2% of fires, 97.5% of acres burned |
| Median / largest fire | 0.2 acres / 589,368 acres |
| Strongest correlation (Spearman) | temperature, ρ = 0.13 |
| Large-fire share, coolest → hottest tenth of days | 0.9% → 3.4% |
| Large-fire share, driest → most humid tenth | 3.7% → 0.6% |
| Random Forest R² (random split / future years) | 0.035 / ≈ 0 |
| Worst year for area burned | 2020 (4.25 million acres) |

## Terms to know

- **Reanalysis:** weather data produced by combining observations with a weather model to fill in a complete grid.
- **Left join:** a merge that keeps every row from the left table (the fires), even if there's no match.
- **Decile:** one of 10 equal-sized groups after sorting by a variable.
- **Overfitting:** when a model memorizes training data and does worse on new data. I checked by comparing
  training R² (0.064) with test R² (0.035).
- **Right-skewed:** most values are small, with a long tail of a few very large values.

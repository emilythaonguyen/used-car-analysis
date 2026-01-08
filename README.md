# US Used Car Affordability Analysis

An end-to-end data engineering and analytics project that determines the most affordable US states to purchase a used car. The project scrapes live data from four different web sources, integrates insurance premiums, and calculates a **Weighted Affordability Score** based on five key economic metrics.

## 📊 The Affordability Model

Buying a car isn't just about the sticker price. This project uses a weighted ranking system to evaluate states across five dimensions:

| Metric | Weight | Description |
| :--- | :--- | :--- |
| **Used Car Price** | 30% | The average listing price for used vehicles in the state. |
| **Sales Tax** | 30% | State-level automotive sales tax rates. |
| **Insurance** | 30% | Average annual full-coverage insurance premiums (2025 data). |
| **Doc Fees** | 5% | Dealer documentation and administrative fees. |
| **Registration** | 5% | State-level vehicle registration and title fees. |

## 🚀 Key Features

* **Dynamic Web Scraping**: Custom-built `scrape_table` function using `BeautifulSoup` to handle varied HTML structures, currency cleaning, and percentage parsing.
* **Data Integration**: Merges datasets from four different web domains and a local insurance CSV, using `pandas` for robust data joining and cleaning.
* **Outlier Detection**: Implements the Interquartile Range (IQR) method to identify states with extreme costs (e.g., states with no sales tax or exceptionally high registration fees).
* **Interactive Visualization**: Generates US Choropleth maps using `Plotly Express` to visualize the geographic distribution of "Weighted Rank" vs. "Total Cost."



## 🛠️ Tech Stack

* **Python 3.x**
* **Libraries**: 
    * `pandas`: Data manipulation and merging.
    * `BeautifulSoup4` & `requests`: Web scraping.
    * `Plotly`: Interactive geospatial visualizations.
    * `us`: State name and abbreviation standardization.

## 📂 Project Structure

* `main.py`: The full script containing scraping, cleaning, and analysis logic.
* `car-insurance-rates-by-state-2025.csv`: Supporting insurance dataset.
* `used_car_affordability.csv`: The final exported dataset.
* `weighted_score_map.html`: Interactive map of the final rankings.
* `total_cost_map.html`: Interactive map of the raw total costs.

## 🏁 Getting Started

1.  **Install dependencies**:
    ```bash
    pip install pandas beautifulsoup4 requests us plotly
    ```
2.  **Run the analysis**:
    ```bash
    python used_cars.py
    ```
3.  **View results**: The script will print the "Top 10" and "Bottom 10" states to the console and generate two HTML maps for visual analysis.

---

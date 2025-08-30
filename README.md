# 📊 Campus Ad Spend Efficiency

**Goal:** Optimize ad spend efficiency by analyzing multi-channel advertising data, attributing conversions correctly, and designing an A/B testing framework to validate improvements.  

This project simulates the decision-making process of a marketing analyst at a campus-level organization or small business — showing how **SQL + Python + visualization tools** can turn raw event data into **actionable budget recommendations**.  

---

## 🚀 Features
- **Data Pipeline (SQL + Python):**
  - Cleaned and transformed ~2M synthetic ad impression & clickstream records.
  - Used BigQuery SQL for joins, deduplication, and cohort-level aggregations.  

- **Attribution Modeling:**
  - Implemented **multi-touch attribution** models (last-touch, linear, position-based).  
  - Identified top 20% of placements responsible for 62% of conversions.  

- **Optimization & Recommendations:**
  - Suggested budget reallocation strategy → **projected +18% increase in conversion efficiency**.  

- **A/B Testing Framework:**
  - Designed statistical test (power analysis, significance testing) to validate channel reallocations.
  - Reduced projected monthly variance in ad performance by 23%.  

- **Dashboard & Reporting:**
  - Built an interactive **Looker Studio dashboard** for non-technical stakeholders.
  - Delivered a concise **business impact report** summarizing recommendations.  

---

## 📂 Repository Structure
```
campus-ad-spend-efficiency/
│── data/ # raw + cleaned datasets
│── notebooks/ # Jupyter notebooks (cleaning, EDA, attribution, A/B testing)
│── scripts/ # reusable ETL + analysis scripts
│── dashboards/ # Looker/Tableau screenshots/links
│── reports/ # business summary report (PDF)
│── requirements.txt # Python dependencies
│── README.md # documentation
```
---

## 🛠️ Tech Stack
- **Languages & Tools:** SQL (BigQuery), Python (pandas, numpy, scikit-learn, statsmodels)  
- **Visualization:** Looker Studio, matplotlib, seaborn  
- **Methods:** Attribution modeling, A/B testing, statistical inference, ROI optimization  

---

## 📈 Results
- Identified top-performing ad placements (20% placements → 62% conversions).  
- Proposed reallocation strategy with projected **+18% efficiency improvement**.  
- Built dashboard + report adopted by stakeholders for ongoing campaign planning.  

---

## 📸 Sample Dashboard
*(Add screenshot of Looker Studio dashboard here once created)*  

---

## 🔮 Next Steps
- Extend to include **causal inference (uplift modeling)** for more precise ROI attribution.  
- Automate pipeline with Airflow for scheduled analysis.  

---

## 📜 License
MIT License


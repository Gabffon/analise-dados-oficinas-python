# Auto Repair Shop Database Management & Data Analytics Pipeline

An end-to-end Python database management system (DBMS) designed to aggregate multi-source data, execute automated ETL pipelines, perform statistical outlier detection, and deliver predictive analytics for automotive maintenance.

Developed for the *Introdução à Engenharia e Ciência de Dados* course at the **University of Coimbra**.

---

## 🛠️ Key Technical Features

- **Multi-Source Data Ingestion (ETL):** Automated pipeline reading structured configuration data from `JSON` files and batch vehicle records (600+ entries) from `CSV` files using `Pandas`.
- **Relational Database Architecture:** Built an in-memory/persistent `SQLite3` database with a 1-to-N relational schema linking repair shops (`Oficinas`) to vehicles (`Veiculos`) using Primary and Foreign Keys.
- **Statistical Data Cleaning & Anomaly Detection:** 
  - Applied `NumPy` vectorization to identify mileage outliers ($\mu + 2\sigma$ rule) and replace them with median values.
  - Imputed missing brake disc thickness measurements (`-1` flags) with dynamic dataset means.
- **Predictive Maintenance Logic:** Evaluated mathematical decision thresholds ($KM > 15.0$, $ED < 20.0$) to flag vehicles requiring mechanical inspection.
- **Interactive Mechanic Dashboard & Reporting:** Created query functions to inspect individual vehicles, log manual mechanic overrides, and generate time-series operational reports including per capita vehicle metrics.

---

## 🚀 Tech Stack & Tools

- **Language:** Python 3
- **Data Manipulation & Math:** `Pandas`, `NumPy`
- **Database Engine:** `SQLite3` (Relational SQL)
- **Data Formats:** JSON, CSV, SQL Tables

---

## 💻 How to Run

1. Place `oficina_dados.json` and `veiculos_dados.csv` in the root directory.
2. Execute the main script:
   ```bash
   python main.py

   ---

### 2. Descrição (em Português)

Pode substituir a descrição genérica no seu currículo por esta, que reflete exatamente as ferramentas utilizadas no script:

*   **Sistema Integrado de Gestão e Análise de Dados de Oficinas** | *Python, SQLite3, Pandas, NumPy*
    *   Desenvolveu um pipeline **ETL** completo em **Python** para integração de dados multi-fonte (**JSON** e **CSV**) em base de dados relacional **SQLite3**.
    *   Implementou algoritmos em **NumPy** para limpeza de dados, imputação de valores ausentes e tratamento de *outliers* ($\mu + 2\sigma$).
    *   Criou um motor de regras de negócio em **Pandas** para predição automática de revisões mecânicas e geração de relatórios estatísticos por período.

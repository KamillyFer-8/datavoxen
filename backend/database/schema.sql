PRAGMA foreign_keys = ON;
PRAGMA user_version = 1;
CREATE TABLE studies (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, studio TEXT NOT NULL,
    nature TEXT NOT NULL, study_date TEXT NOT NULL, months INTEGER NOT NULL CHECK (months = 12)
);
CREATE TABLE model_versions (
    id TEXT PRIMARY KEY, study_id TEXT NOT NULL REFERENCES studies(id), checksum TEXT NOT NULL,
    assumptions_json TEXT NOT NULL CHECK (json_valid(assumptions_json))
);
CREATE TABLE products (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, price REAL NOT NULL CHECK (price > 0),
    unit_cost REAL NOT NULL CHECK (unit_cost >= 0), base REAL NOT NULL CHECK (base >= 0 AND base < 1)
);
CREATE TABLE strategies (
    id TEXT PRIMARY KEY CHECK (id IN ('A','B','C')), name TEXT NOT NULL,
    production REAL NOT NULL CHECK (production >= 0), content REAL NOT NULL CHECK (content >= 0)
);
CREATE TABLE strategy_products (
    strategy_id TEXT NOT NULL REFERENCES strategies(id), product_id TEXT NOT NULL REFERENCES products(id),
    position INTEGER NOT NULL, PRIMARY KEY (strategy_id, product_id)
);
CREATE TABLE scenarios (id TEXT PRIMARY KEY, parameters_json TEXT NOT NULL CHECK (json_valid(parameters_json)));
CREATE TABLE reference_runs (
    id TEXT PRIMARY KEY, model_version TEXT NOT NULL REFERENCES model_versions(id),
    strategy TEXT NOT NULL REFERENCES strategies(id), scenario TEXT NOT NULL REFERENCES scenarios(id),
    parameters_json TEXT NOT NULL CHECK (json_valid(parameters_json)),
    summary_json TEXT NOT NULL CHECK (json_valid(summary_json)),
    none_probability REAL NOT NULL CHECK (none_probability BETWEEN 0 AND 1),
    UNIQUE (model_version, strategy, scenario)
);
CREATE TABLE monthly_results (
    run_id TEXT NOT NULL REFERENCES reference_runs(id), month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    new REAL NOT NULL, active REAL NOT NULL, p_buy REAL NOT NULL, buyers REAL NOT NULL,
    units_traje REAL NOT NULL, units_efeito REAL NOT NULL, units_colecao REAL NOT NULL,
    units_passe REAL NOT NULL, units_sazonal REAL NOT NULL,
    gross REAL NOT NULL, refunds REAL NOT NULL, platform REAL NOT NULL, tax REAL NOT NULL,
    net REAL NOT NULL, variable REAL NOT NULL, production REAL NOT NULL, content REAL NOT NULL,
    operations REAL NOT NULL, marketing REAL NOT NULL, costs REAL NOT NULL, flow REAL NOT NULL,
    cash REAL NOT NULL, usable_cash REAL NOT NULL, cumulative_flow REAL NOT NULL,
    PRIMARY KEY (run_id, month)
);
CREATE TABLE cohort_results (
    run_id TEXT NOT NULL REFERENCES reference_runs(id), cohort_month INTEGER NOT NULL CHECK (cohort_month BETWEEN 1 AND 12),
    horizon_months INTEGER NOT NULL, acquired REAL NOT NULL, active_player_months REAL NOT NULL,
    gross REAL NOT NULL, contribution_before_CAC REAL NOT NULL, contribution_per_acquired REAL NOT NULL,
    CAC REAL NOT NULL, net_after_CAC REAL NOT NULL, PRIMARY KEY (run_id, cohort_month)
);
CREATE TABLE product_results (
    run_id TEXT NOT NULL REFERENCES reference_runs(id), product_id TEXT NOT NULL REFERENCES products(id),
    price REAL NOT NULL, probability REAL NOT NULL, units REAL NOT NULL, gross REAL NOT NULL,
    PRIMARY KEY (run_id, product_id)
);
CREATE TABLE sources (
    id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL, consulted_at TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TABLE benchmarks (
    id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id),
    game TEXT NOT NULL, product TEXT NOT NULL, offer_type TEXT NOT NULL, price REAL NOT NULL,
    currency TEXT NOT NULL, channel TEXT NOT NULL, consulted_at TEXT NOT NULL,
    verification_status TEXT NOT NULL, limitations TEXT NOT NULL
);
CREATE VIEW financial_comparison AS
SELECT r.id, r.strategy, r.scenario,
    json_extract(r.summary_json,'$.gross') AS gross, json_extract(r.summary_json,'$.net') AS net,
    json_extract(r.summary_json,'$.costs') AS costs, json_extract(r.summary_json,'$.flow') AS flow,
    json_extract(r.summary_json,'$.cash') AS cash
FROM reference_runs r;

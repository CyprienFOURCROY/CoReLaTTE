import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"].copy()
    df_se = tables["ii_se"].copy()
    df_nna = tables["ii_nna"].copy()

    # Compute overall average age (ignore missing)
    avg_age = df_portad["edad"].mean()

    # Filter adults (18+) whose age is above overall average
    ppl = df_portad[df_portad["edad"].notna() & (df_portad["edad"] >= 18) & (df_portad["edad"] > avg_age)].copy()

    # Ensure one row per household in household-level tables
    df_su = df_su.drop_duplicates(subset=["folio"])
    df_se = df_se.drop_duplicates(subset=["folio"])
    df_nna = df_nna.drop_duplicates(subset=["folio"])

    # Household filters
    hh_su = df_su[df_su["su01"] == 1.0][["folio", "su234"]]
    hh_se = df_se[df_se["se01e"] == 1.0][["folio"]]
    hh_nna = df_nna[df_nna["nna01"] == 1.0][["folio"]]

    # Merge individual-level filtered data with household conditions
    m = ppl.merge(hh_su, on="folio", how="inner")
    m = m.merge(hh_se, on="folio", how="inner")
    m = m.merge(hh_nna, on="folio", how="inner")

    # Drop missing state codes just in case
    m = m[m["ent"].notna()].copy()

    # Aggregate by state
    out = (
        m.groupby("ent", as_index=False)
         .agg(num_individuals=("folio", "size"), avg_seed_expense=("su234", "mean"))
    )

    # Present state as integer if possible
    try:
        out["ent"] = out["ent"].astype("Int64")
    except Exception:
        pass

    return out
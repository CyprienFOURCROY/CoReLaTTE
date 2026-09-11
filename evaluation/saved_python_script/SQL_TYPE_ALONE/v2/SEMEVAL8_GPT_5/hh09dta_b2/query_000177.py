import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_in = tables["ii_in"]

    # Household-level state (ent) by folio
    hh_ent = df_portad.loc[:, ["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates(subset=["folio"])

    # Relevant subsets
    crh_sub = df_crh.loc[:, ["folio", "crh04_1", "crh04_2"]]
    in_sub = df_in.loc[:, ["folio", "in02a10"]]

    # Merge to single HH-level dataset for required variables
    merged = (
        crh_sub.merge(in_sub, on="folio", how="inner")
        .merge(hh_ent, on="folio", how="inner")
    )

    # Filters
    has_debt_value = (merged["crh04_1"] == 1) & (merged["crh04_2"].notna())
    has_positive_prog = merged["in02a10"].notna() & (merged["in02a10"] > 0)

    eligible = merged[has_debt_value & has_positive_prog].copy()

    # Average among other states (not Oaxaca ent != 20)
    avg_other = eligible.loc[eligible["ent"] != 20, "in02a10"].mean()

    # Oaxaca households meeting threshold
    result = eligible[
        (eligible["ent"] == 20) & (eligible["in02a10"] >= avg_other)
    ].loc[:, ["folio", "crh04_2", "in02a10"]].copy()

    return result
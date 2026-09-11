import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_se = tables["ii_se"].copy()
    df_crh = tables["ii_crh"].copy()
    df_nna = tables["ii_nna"].copy()

    # Households that experienced disease/accident/hospitalization in last 5 years
    se_yes = df_se.loc[df_se["se01b"] == 1.0, ["folio"]].drop_duplicates()

    # Adult presence (age >= 18) and state per household
    port_sub = df_portad[["folio", "ent", "edad"]].copy()
    port_sub["is_adult"] = port_sub["edad"] >= 18
    adult_info = (
        port_sub.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), is_adult=("is_adult", "any"))
    )
    adult_yes = adult_info.loc[adult_info["is_adult"] == True, ["folio", "ent"]]

    # Households with reported value for total debts + interests
    debt = df_crh[["folio", "crh04_1", "crh04_2"]].copy()
    debt_yes = debt.loc[(debt["crh04_1"] == 1.0) & (debt["crh04_2"].notna()), ["folio", "crh04_2"]]

    # Merge eligibility: experienced event + has adult + reported debt value
    eligible = (
        se_yes.merge(adult_yes, on="folio", how="inner")
        .merge(debt_yes, on="folio", how="inner")
    )

    if eligible.empty:
        return pd.DataFrame(columns=["ent", "nna_business", "avg_total_debt", "num_households"])

    # Map non-ag business ownership
    nna = df_nna[["folio", "nna01"]].copy()
    nna_map = {1.0: "Yes", 2.0: "No"}
    nna["nna_business"] = nna["nna01"].map(nna_map)
    eligible = eligible.merge(nna[["folio", "nna_business"]], on="folio", how="left")
    eligible["nna_business"] = eligible["nna_business"].fillna("Unknown")

    # Overall average debt among eligible households
    overall_avg = eligible["crh04_2"].mean()

    # Filter households whose debt exceeds overall average
    above_avg = eligible.loc[eligible["crh04_2"] > overall_avg].copy()

    if above_avg.empty:
        return pd.DataFrame(columns=["ent", "nna_business", "avg_total_debt", "num_households"])

    # Aggregate by state and non-ag business ownership
    result = (
        above_avg.groupby(["ent", "nna_business"], as_index=False)
        .agg(avg_total_debt=("crh04_2", "mean"), num_households=("folio", "nunique"))
    )

    return result
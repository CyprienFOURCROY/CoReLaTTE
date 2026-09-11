import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "edad"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy()
    df_in = tables["ii_in"][["folio", "in01a10_1", "in02a10"]].copy()

    # Households with at least one member aged 60+
    senior_cond = df_portad["edad"].notna() & (df_portad["edad"] >= 60)
    senior_hh = df_portad.loc[senior_cond, ["folio"]].drop_duplicates()

    # Households with reported positive total debts + interests
    debt_cond = (df_crh["crh04_1"] == 1) & df_crh["crh04_2"].notna() & (df_crh["crh04_2"] > 0)
    debt_hh = df_crh.loc[debt_cond, ["folio", "crh04_2"]]

    # Senior households with positive debt
    senior_debt_hh = senior_hh.merge(debt_hh, on="folio", how="inner")

    if senior_debt_hh.empty:
        return pd.DataFrame({"average_in02a10": [float("nan")]})

    # Average debt among senior households with positive debt
    avg_debt = senior_debt_hh["crh04_2"].mean()

    # Households above this average
    above_avg_hh = senior_debt_hh.loc[senior_debt_hh["crh04_2"] > avg_debt, ["folio"]].drop_duplicates()
    if above_avg_hh.empty:
        return pd.DataFrame({"average_in02a10": [float("nan")]})

    # Among these, consider only households that reported receiving Other Government Program
    rec = df_in.merge(above_avg_hh, on="folio", how="inner")
    rec = rec.loc[(rec["in01a10_1"] == 1) & (rec["in02a10"].notna()), "in02a10"]

    avg_in02a10 = rec.mean() if not rec.empty else float("nan")

    return pd.DataFrame({"average_in02a10": [avg_in02a10]})
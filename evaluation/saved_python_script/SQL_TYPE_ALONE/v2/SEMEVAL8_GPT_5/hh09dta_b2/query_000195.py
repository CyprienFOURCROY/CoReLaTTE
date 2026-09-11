import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh04_1", "crh04_2"]].copy().drop_duplicates(subset=["folio"])
    df_se = tables["ii_se"][["folio", "se01a"]].copy().drop_duplicates(subset=["folio"])

    # Oaxaca households (ent == 20) and oldest member >= 65
    oax = df_portad[df_portad["ent"] == 20][["folio", "edad"]]
    oax_max_age = oax.groupby("folio", as_index=False)["edad"].max().rename(columns={"edad": "max_edad"})
    oax_old = oax_max_age[oax_max_age["max_edad"] >= 65][["folio"]]

    # Households reporting a death in last 5 years
    se_death = df_se[df_se["se01a"] == 1][["folio"]]

    # Average total debts + interests among Oaxaca households with reported amounts
    oax_folios = oax[["folio"]].drop_duplicates()
    oax_crh = oax_folios.merge(df_crh, on="folio", how="left")
    avg_val = oax_crh.loc[(oax_crh["crh04_1"] == 1) & (oax_crh["crh04_2"].notna()), "crh04_2"].mean()

    # Eligible households: Oaxaca, oldest >=65, death reported, and debts > average (with reported amount)
    elig = oax_old.merge(se_death, on="folio", how="inner").merge(df_crh, on="folio", how="left")
    cond = (elig["crh04_1"] == 1) & (elig["crh04_2"].notna()) & (elig["crh04_2"] > avg_val)
    count = int(elig.loc[cond, "folio"].nunique())

    return pd.DataFrame({"count": [count]})
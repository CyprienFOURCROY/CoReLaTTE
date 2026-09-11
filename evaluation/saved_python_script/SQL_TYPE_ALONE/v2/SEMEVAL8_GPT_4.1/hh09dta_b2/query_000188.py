def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_crh = tables["ii_crh"]

    # 1. Households that reported a death of a member in the last five years (se01a == 1)
    deaths = df_se[df_se["se01a"] == 1][["folio"]]

    # 2. Households that provided a value for total debts plus interests (crh04_2 not null)
    debts = df_crh[df_crh["crh04_2"].notnull()][["folio"]]

    # 3. Intersection: households with both
    hh_death_debt = pd.merge(deaths, debts, on="folio", how="inner")

    # 4. Add state info
    hh_death_debt_state = pd.merge(hh_death_debt, df_portad[["folio", "ent"]], on="folio", how="left")

    # 5. For each household, check if at least one person aged 60 or older
    # Get all folios in the filtered set
    folios_set = set(hh_death_debt_state["folio"].unique())
    # Subset portad to only those folios
    df_portad_sub = df_portad[df_portad["folio"].isin(folios_set)]
    # For each folio, check if any edad >= 60
    aged_60plus = df_portad_sub.groupby("folio")["edad"].max().reset_index()
    aged_60plus["has_60plus"] = aged_60plus["edad"] >= 60

    # Merge this info back to the household list
    hh_death_debt_state = pd.merge(hh_death_debt_state, aged_60plus[["folio", "has_60plus"]], on="folio", how="left")

    # 6. For each state, count:
    #   - number of such households with at least one person aged 60 or older
    #   - total number of such households
    result = (
        hh_death_debt_state.groupby("ent")
        .agg(
            households_with_60plus=("has_60plus", lambda x: int(x.sum())),
            total_households=("folio", "nunique"),
        )
        .reset_index()
        .rename(columns={"ent": "state"})
        .sort_values("state")
    )

    return result
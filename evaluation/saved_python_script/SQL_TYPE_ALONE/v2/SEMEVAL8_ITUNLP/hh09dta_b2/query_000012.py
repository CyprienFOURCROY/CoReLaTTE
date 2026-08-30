import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"].copy()
    df_crh = tables["ii_crh"].copy()

    # Household size and state per household
    hh_size = df_portad.groupby("folio").size().rename("hh_size").reset_index()
    hh_ent = df_portad.groupby("folio", as_index=False)["ent"].first()
    hh_info = hh_size.merge(hh_ent, on="folio", how="left")
    hh_info = hh_info[hh_info["ent"].notna()]

    # Households that use plot/land
    su_use = df_su[df_su["su01"] == 1][["folio"]].dropna()

    # Households with positive total debt (debts + interest)
    crh_pos_debt = df_crh[df_crh["crh04_2"].notna() & (df_crh["crh04_2"] > 0)][["folio", "crh04_2"]]

    # Eligible households (both conditions)
    eligible = su_use.merge(crh_pos_debt, on="folio", how="inner")
    # Ensure unique per household (if duplicates exist, average the debt)
    eligible = eligible.groupby("folio", as_index=False).agg(crh04_2=("crh04_2", "mean"))

    # Attach state and hh size
    eligible = eligible.merge(hh_info, on="folio", how="inner")

    # Aggregate by state
    result = (
        eligible.groupby("ent", as_index=False)
        .agg(
            average_total_debt=("crh04_2", "mean"),
            average_household_size=("hh_size", "mean"),
            households=("folio", "nunique"),
        )
        .sort_values("average_total_debt", ascending=False)
        .reset_index(drop=True)
    )

    return result
def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_crh = tables["ii_crh"]

    # 1. Find households with at least one member aged 60+ who feels unsafe/very unsafe at home
    # Merge portad (age, ent, folio) with vlh (feel safe at home)
    df_age = df_portad[["folio", "ent", "edad"]].copy()
    df_vlh_sel = df_vlh[["folio", "vlh04"]].copy()
    df_age_vlh = df_age.merge(df_vlh_sel, on="folio", how="left")

    # Filter for age >= 60 and vlh04 in [3, 4] (unsafe, very unsafe)
    mask_60plus_unsafe = (df_age_vlh["edad"] >= 60) & (df_age_vlh["vlh04"].isin([3.0, 4.0]))
    df_60plus_unsafe = df_age_vlh.loc[mask_60plus_unsafe, ["folio", "ent"]].drop_duplicates()

    # 2. For these households, get total debts+interest (crh04_2)
    df_crh_debt = df_crh[["folio", "crh04_2"]].copy()
    # Only keep households in our filtered set
    df_debt = df_60plus_unsafe.merge(df_crh_debt, on="folio", how="left")

    # Only keep rows with a valid debt value (not null, not negative)
    df_debt = df_debt[~df_debt["crh04_2"].isnull()]
    df_debt = df_debt[df_debt["crh04_2"] >= 0]

    # 3. Compute overall average for this group
    overall_avg = df_debt["crh04_2"].mean()

    # 4. Compute state-level averages for states at or above overall average
    state_avg = df_debt.groupby("ent")["crh04_2"].mean().reset_index()
    state_avg = state_avg[state_avg["crh04_2"] >= overall_avg]

    # 5. Find the state with the highest average
    if not state_avg.empty:
        idxmax = state_avg["crh04_2"].idxmax()
        top_state = state_avg.loc[idxmax, "ent"]
        top_avg = state_avg.loc[idxmax, "crh04_2"]
        return pd.DataFrame({"state": [top_state], "average_total_household_debt": [top_avg]})
    else:
        return pd.DataFrame({"state": [np.nan], "average_total_household_debt": [np.nan]})
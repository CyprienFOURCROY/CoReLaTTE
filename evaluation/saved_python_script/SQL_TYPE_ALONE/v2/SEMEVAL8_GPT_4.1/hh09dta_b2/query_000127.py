def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_se = tables["ii_se"]
    df_vlh = tables["ii_vlh"]

    # Define the shock columns
    shock_cols = [
        "se01a",  # death of HHM
        "se01b",  # serious illness/accident/hospitalization
        "se01c",  # unemployment/business failure
        "se01d",  # loss of dwelling/business to natural disaster
        "se01e",  # total crop loss
        "se01f",  # loss/robbery/death of animals
    ]

    # Households with any shock (value == 1 in any shock col)
    df_se_shock = df_se.copy()
    shock_any = (df_se_shock[shock_cols] == 1).any(axis=1)
    shock_none = (df_se_shock[shock_cols] == 1).sum(axis=1) == 0

    # Merge with break-in/robbery counts since 2005
    df_vlh_sel = df_vlh[["folio", "vlh18a"]].copy()

    # Merge shocks with break-in counts
    df_shock = df_se_shock.loc[shock_any, ["folio"]].merge(df_vlh_sel, on="folio", how="left")
    df_no_shock = df_se_shock.loc[shock_none, ["folio"]].merge(df_vlh_sel, on="folio", how="left")

    # Compute average vlh18a among households with NO shocks
    avg_vlh18a_no_shock = df_no_shock["vlh18a"].mean(skipna=True)

    # Households with any shock and vlh18a > avg_vlh18a_no_shock
    mask = (df_shock["vlh18a"] > avg_vlh18a_no_shock)
    result = df_shock.loc[mask, ["folio", "vlh18a"]].reset_index(drop=True)

    return result
import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].drop_duplicates(subset=["folio"])
    df_su = tables["ii_su"][["folio", "su01"]]
    df_nna = tables["ii_nna"][["folio", "nna01"]]
    df_in = tables["ii_in"][["folio", "in02a10"]]

    # Land-using households in Oaxaca (20) or Puebla (21)
    df_land = df_su[df_su["su01"] == 1.0][["folio"]]
    df_states = df_portad[df_portad["ent"].isin([20.0, 21.0])][["folio"]]
    base_states_land = pd.merge(df_states, df_land, on="folio", how="inner")

    # Compute average direct payment among land-using households in those states (positive amounts only)
    state_land_in = pd.merge(base_states_land, df_in, on="folio", how="left")
    pos_payments = state_land_in["in02a10"]
    avg_payment = pos_payments[(pos_payments.notna()) & (pos_payments > 0)].mean()

    # Households that also own/share a non-ag business (nna01 == 1)
    df_business = df_nna[df_nna["nna01"] == 1.0][["folio"]]
    target = pd.merge(base_states_land, df_business, on="folio", how="inner")
    target = pd.merge(target, df_in, on="folio", how="left")

    # Filter: positive payment and above average
    result = target[(target["in02a10"].notna()) & (target["in02a10"] > 0)]
    if pd.notna(avg_payment):
        result = result[result["in02a10"] > avg_payment]
    else:
        # If no average (no positive payments in base), no household can be above average
        result = result.iloc[0:0]

    result = result[["folio", "in02a10"]].drop_duplicates().sort_values(by="in02a10", ascending=False).reset_index(drop=True)
    return result
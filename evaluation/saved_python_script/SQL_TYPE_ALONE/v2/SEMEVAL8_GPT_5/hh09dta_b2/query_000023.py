import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["edad", "ent", "folio", "ls"]].copy()
    df_inr = tables["ii_inr"][["folio", "inr02c"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Filter Oaxaca individuals
    df_portad_oxa = df_portad[df_portad["ent"] == 20.0].copy()

    # Households that produced/sold meat
    hh_meat = df_inr[df_inr["inr02c"] == 1.0][["folio"]].drop_duplicates()

    # Individuals in Oaxaca living in households that produced/sold meat
    ind_oxa_meat = df_portad_oxa.merge(hh_meat, on="folio", how="inner")

    if ind_oxa_meat.empty:
        return pd.DataFrame(columns=["folio", "ls", "edad", "in02a10"]).astype(
            {"folio": "object", "ls": "object", "edad": "float64", "in02a10": "float64"}
        )

    # Mean age among these individuals
    mean_age = ind_oxa_meat["edad"].mean()

    # Average amount from Other Government Program among these households
    hh_set = ind_oxa_meat["folio"].dropna().unique()
    avg_in02a10 = df_in[df_in["folio"].isin(hh_set)]["in02a10"].mean()

    # Merge amount into individuals
    ind_oxa_meat_amt = ind_oxa_meat.merge(df_in, on="folio", how="left")

    # Filter by age >= mean_age and amount > average
    filt = (ind_oxa_meat_amt["edad"] >= mean_age) & (ind_oxa_meat_amt["in02a10"] > avg_in02a10)
    res = ind_oxa_meat_amt.loc[filt, ["folio", "ls", "edad", "in02a10"]]

    # Top 10 oldest
    res = res.sort_values(by=["edad", "in02a10"], ascending=[False, False]).head(10)

    return res.reset_index(drop=True)
import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_su = tables["ii_su"][["folio", "su237"]].copy()
    df_nna = tables["ii_nna"][["folio", "nna02"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh08a"]].copy()

    # Filter households in Oaxaca (ent == 20)
    oaxaca_hhs = df_portad[df_portad["ent"] == 20.0][["folio"]]

    # Compute Oaxaca state average of agricultural worker expenses (su237)
    oax_su = oaxaca_hhs.merge(df_su, on="folio", how="left")
    state_avg = oax_su["su237"].mean(skipna=True)

    # Merge needed variables and filter households with su237 above state average
    df = (
        oax_su.merge(df_nna, on="folio", how="left")
              .merge(df_vlh, on="folio", how="left")
    )
    df = df[df["su237"] > state_avg]

    # Group by number of non-ag businesses in last 12 months and knowledge of robbery in last 5 years
    result = (
        df.groupby(["nna02", "vlh08a"])
          .agg(avg_worker_expense=("su237", "mean"),
               household_count=("folio", "nunique"))
          .reset_index()
    )

    return result
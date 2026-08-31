import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_in = tables["ii_in"][["folio", "in03a", "in02a10"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh18a"]].copy()

    mean_breakins = df_vlh["vlh18a"].mean(skipna=True)

    hh = df_in.merge(df_vlh, on="folio", how="inner")
    hh_sel = hh[
        (hh["vlh04"].isin([3.0, 4.0])) &
        (hh["in03a"] == 1.0) &
        (hh["in02a10"] > 0) &
        (hh["vlh18a"] > mean_breakins)
    ][["folio"]]

    adults = df_portad[df_portad["edad"] >= 18]
    df = adults.merge(hh_sel, on="folio", how="inner")

    if df.empty:
        return pd.DataFrame(columns=["ent", "average_age", "num_adults"])

    result = (
        df.groupby("ent", as_index=False)
          .agg(average_age=("edad", "mean"), num_adults=("edad", "size"))
          .sort_values("average_age", ascending=False)
    )
    return result
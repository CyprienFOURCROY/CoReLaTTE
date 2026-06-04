import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]]
    df_se = tables["ii_se"][["folio", "se01d"]]
    df_su = tables["ii_su"][["folio", "su01"]]

    se_disaster = df_se[df_se["se01d"] == 1.0]
    su_plot = df_su[df_su["su01"] == 1.0]

    qualifying_households = pd.merge(se_disaster, su_plot, on="folio", how="inner")[["folio"]]
    individuals = pd.merge(df_portad, qualifying_households, on="folio", how="inner")

    g = individuals.groupby("ent")
    result = pd.DataFrame({
        "average_age": g["edad"].mean(),
        "num_individuals": g.size()
    }).reset_index()

    result = result.sort_values("average_age", ascending=False).reset_index(drop=True)
    return result
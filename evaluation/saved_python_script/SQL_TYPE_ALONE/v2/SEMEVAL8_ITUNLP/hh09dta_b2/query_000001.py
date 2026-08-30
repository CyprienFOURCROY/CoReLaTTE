import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]]
    df_vlh = tables["ii_vlh"][["folio", "vlh08a", "vlh04", "vlh06"]]

    df = pd.merge(df_vlh, df_portad, on="folio", how="inner")

    df_yes = df[df["vlh08a"] == 1].copy()
    if df_yes.empty:
        return pd.DataFrame(columns=["ent", "avg_feel_safe", "avg_leave_lights", "n_households"])

    df_yes["vlh06"] = df_yes["vlh06"].replace(9, np.nan)

    result = (
        df_yes.groupby("ent", as_index=False)
        .agg(
            avg_feel_safe=("vlh04", "mean"),
            avg_leave_lights=("vlh06", "mean"),
            n_households=("folio", "size"),
        )
    )

    result = result[result["n_households"] >= 5]
    result = result.sort_values(by=["avg_feel_safe", "avg_leave_lights", "ent"], ascending=[True, True, True]).reset_index(drop=True)

    return result
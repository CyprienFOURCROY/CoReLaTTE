import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].drop_duplicates(subset=["folio"])
    df_in = tables["ii_in"][["folio", "in03a", "in03b", "in01a10_1", "in02a10"]]
    df_nna = tables["ii_nna"][["folio", "nna01"]]
    df_crh = tables["ii_crh"][["folio", "crh03_1"]]

    base = df_in.merge(df_nna, on="folio", how="inner")

    mask = (
        (base["nna01"] == 1) &
        (base["in03a"] == 1) &
        (base["in03b"] == 3) &
        (base["in01a10_1"] == 1)
    )

    subset = base[mask & base["in02a10"].notna()]
    avg_direct_amt = subset["in02a10"].mean()

    final_hh = base[mask & (base["in02a10"] > avg_direct_amt)]

    final_hh = final_hh.merge(df_portad, on="folio", how="left")
    final_hh = final_hh.merge(df_crh, on="folio", how="left")
    final_hh["paid_any"] = final_hh["crh03_1"] == 1

    result = final_hh.groupby("ent", as_index=False).agg(
        total_households=("folio", "nunique"),
        paid_on_debts=("paid_any", "sum")
    )
    result["paid_on_debts"] = result["paid_on_debts"].astype("int64")

    return result
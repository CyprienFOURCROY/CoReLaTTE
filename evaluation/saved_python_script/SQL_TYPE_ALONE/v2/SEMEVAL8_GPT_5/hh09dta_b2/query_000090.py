import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    hh_ent = df_portad.groupby("folio", as_index=False)["ent"].first()

    df_ah = tables["ii_ah"][["folio", "ah03e"]].copy()
    df_ah["own_elect"] = (df_ah["ah03e"] == 1.0).astype("int64")
    hh_own_cnt = df_ah.groupby("folio", as_index=False)["own_elect"].sum().rename(columns={"own_elect": "num_owners_elect"})

    df_crh = tables["ii_crh"][["folio", "crh02_1"]].copy()
    owed = df_crh[df_crh["crh02_1"] == 1.0][["folio"]].drop_duplicates()

    df_in = tables["ii_in"][["folio", "in01a10_1"]].copy()
    no_part = df_in[df_in["in01a10_1"] == 3.0][["folio"]].drop_duplicates()

    hh = owed.merge(no_part, on="folio", how="inner")
    hh = hh.merge(hh_own_cnt, on="folio", how="left")
    hh["num_owners_elect"] = hh["num_owners_elect"].fillna(0)

    hh = hh.merge(hh_ent, on="folio", how="left")

    result = hh.groupby("ent", as_index=False)["num_owners_elect"].mean()
    result = result.rename(columns={"num_owners_elect": "avg_members_own_electronic_devices"})
    return result
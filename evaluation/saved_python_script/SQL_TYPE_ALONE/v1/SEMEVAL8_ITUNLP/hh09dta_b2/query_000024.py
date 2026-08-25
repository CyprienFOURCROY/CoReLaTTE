import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ls", "edad", "ent"]]
    df_se = tables["ii_se"][["folio", "se01b"]]
    df_in = tables["ii_in"][["folio", "in01a10_1", "in01a10_2", "in02a10"]]

    # Individuals in Oaxaca (ent == 20)
    oaxaca_individuals = df_portad[df_portad["ent"] == 20][["folio", "ls", "edad"]]

    # Households with illness/accident/hospitalization in last 5 years
    hh_illness = df_se[df_se["se01b"] == 1][["folio"]].drop_duplicates()

    # Households that received income from Other Government Program in last 12 months
    cond_received = (
        (df_in["in01a10_1"] == 1) |
        (df_in["in01a10_2"] > 0) |
        (df_in["in02a10"] > 0)
    )
    hh_other_prog = df_in[cond_received][["folio"]].drop_duplicates()

    # Households satisfying both conditions
    hh_selected = hh_illness.merge(hh_other_prog, on="folio", how="inner")

    # Join back to individuals in Oaxaca
    result = oaxaca_individuals.merge(hh_selected, on="folio", how="inner")[["folio", "ls", "edad"]].drop_duplicates()

    return result.reset_index(drop=True)
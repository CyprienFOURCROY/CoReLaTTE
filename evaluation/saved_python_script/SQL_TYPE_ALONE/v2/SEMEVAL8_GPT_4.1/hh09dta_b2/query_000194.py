def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]

    # Merge to get age, state, and device ownership per individual
    df = pd.merge(
        df_portad[["edad", "ent", "folio", "ls"]],
        df_ah[["folio", "ls", "ah03e"]],
        on=["folio", "ls"],
        how="inner"
    )

    # Only keep individuals in households that own an electronic device (ah03e == 1)
    df_device = df[df["ah03e"] == 1]

    # Count 18-24 year olds in device-owning households per state
    mask_18_24 = (df_device["edad"] >= 18) & (df_device["edad"] <= 24)
    count_18_24 = df_device[mask_18_24].groupby("ent").size()

    # Count total individuals in device-owning households per state
    count_total = df_device.groupby("ent").size()

    # Compute average 18-24 count across states
    avg_18_24 = count_18_24.mean()

    # Select states with above-average 18-24 count
    states_above_avg = count_18_24[count_18_24 > avg_18_24].index

    # Prepare result DataFrame
    result = pd.DataFrame({
        "state": count_18_24.index,
        "num_18_24": count_18_24.values,
        "total_in_device_households": count_total.reindex(count_18_24.index).values
    })

    # Filter to only states above average and sort
    result = result[result["state"].isin(states_above_avg)]
    result = result.sort_values("num_18_24", ascending=False).reset_index(drop=True)

    return result
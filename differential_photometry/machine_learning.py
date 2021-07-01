def normalize_data(df):
    df_mean = df.mean()
    df_std = df.std()
    df_norm = (df - df_mean) / df_std
    return df_norm

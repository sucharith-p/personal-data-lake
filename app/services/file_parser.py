import pandas as pd
import io

async def parse_and_infer(file):
    content = await file.read()

    if file.filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))

    elif file.filename.endswith(".json"):
        try:
            df = pd.read_json(io.BytesIO(content), lines=True)
        except ValueError:
            df = pd.read_json(io.BytesIO(content))  # fallback for standard JSON arrays

    elif file.filename.endswith(".parquet"):
        df = pd.read_parquet(io.BytesIO(content), engine="pyarrow")

    else:
        raise ValueError("Unsupported file format")

    schema = df.dtypes.apply(lambda t: str(t)).to_dict()
    return df, schema
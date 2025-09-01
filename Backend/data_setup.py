import os
import xarray as xr
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# -----------------------------
# Configurations
# -----------------------------
DATA_FOLDER = "./data/"   # Folder containing NetCDF files
DB_FILE = "argo.db"       # SQLite database file
ENGINE = create_engine(f"sqlite:///{DB_FILE}")

# -----------------------------
# Step 1: Collect files
# -----------------------------
files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".nc")]

profiles_list = []
measurements_list = []

# -----------------------------
# Step 2: Process each NetCDF file
# -----------------------------
for file in files:
    file_path = os.path.join(DATA_FOLDER, file)
    print(f"Processing {file_path} ...")
    
    ds = xr.open_dataset(file_path, decode_times=True)
    
    # Extract profile metadata (fall back to filename if PLATFORM_NUMBER not found)
    profile_id = (
        str(ds["PLATFORM_NUMBER"].values[0])
        if "PLATFORM_NUMBER" in ds
        else os.path.basename(file)
    )
    
    lat = float(np.ravel(ds["LATITUDE"].values)[0])
    lon = float(np.ravel(ds["LONGITUDE"].values)[0])
    time = pd.to_datetime(np.ravel(ds["JULD"].values)[0])
    
    profiles_list.append({
        "profile_id": profile_id,
        "lat": lat,
        "lon": lon,
        "time_utc": time
    })
    
    # Extract depth + measurements
    depth = np.ravel(ds["PRES"].values)
    temp = np.ravel(ds["TEMP"].values)
    sal = np.ravel(ds["PSAL"].values)
    
    # Mask invalid rows (NaNs)
    mask = (~np.isnan(depth)) & (~np.isnan(temp)) & (~np.isnan(sal))
    
    for d, t, s in zip(depth[mask], temp[mask], sal[mask]):
        measurements_list.append({
            "profile_id": profile_id,
            "depth": float(d),
            "temperature": float(t),
            "salinity": float(s)
        })

# -----------------------------
# Step 3: Convert to DataFrames
# -----------------------------
profiles_df = pd.DataFrame(profiles_list).drop_duplicates(subset=["profile_id"])
measurements_df = pd.DataFrame(measurements_list)

# ✅ Rename columns to match SQLAlchemy model
profiles_df = profiles_df.rename(
    columns={
        "time_utc": "date",
        "lat": "latitude",
        "lon": "longitude",
        "profile_id": "platform"   # PLATFORM_NUMBER becomes platform
    }
)

measurements_df = pd.DataFrame(measurements_list)

# -----------------------------
# Step 4: Save to SQLite
# -----------------------------
# When saving DataFrames, set id column to profile_id for clarity
profiles_df.to_sql("profiles", ENGINE, if_exists="replace", index=False)
measurements_df.to_sql("measurements", ENGINE, if_exists="replace", index=False)


print("✅ Data setup complete!")
print(f"Profiles stored: {len(profiles_df)}")
print(f"Measurements stored: {len(measurements_df)}")

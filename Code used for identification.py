__author__ = "Weiqi Liu"
__copyright__ = "Copyright (C) 2025 Weiqi Liu"
__license__ = "NIEER"
__version__ = "2025.03"
__Reference paper__ == "Anthropogenic shift towards higher risk of flash drought over China"


def flash_slow_drought_identify(arr):
    """
    Identify flash drought and slow drought events based on soil moisture time series.
    
    Parameters:
        arr (list or np.array): Time series of soil moisture percentages.
    
    Returns:
        flash_drought (np.array): Array with flash drought periods.
        fd_indices (list): Indices of flash drought events.
        slow_drought (np.array): Array with slow drought periods.
        sd_indices (list): Indices of slow drought events.
    """
    fd_sequences, fd_indices = [], []
    sd_sequences, sd_indices = [], []
    n = len(arr)
    i = 0  # Initialize index pointer

    while i < n:
        if 20 < arr[i] < 40 and arr[i - 1] > 40:  # Identify drought onset
            sequence, seq_indices = [arr[i]], [i]
            i += 1
            valid = False  # Track if sequence contains values below 20%

            # Identify decreasing phase above 20%
            while i < n and arr[i] > 20:
                if arr[i] < 40:
                    sequence.append(arr[i])
                    seq_indices.append(i)
                else:
                    break  # Terminate if moisture increases back
                i += 1

            # Identify period where soil moisture is below 20%
            while i < n and arr[i] < 20:
                sequence.append(arr[i])
                seq_indices.append(i)
                valid = True  # Ensure there is at least one value below 20%
                i += 1

            if valid and len(sequence) >= 3:  # 3 = minimum duration 4 pentad - end of a pentad
                first_below_20_index, first_below_20_value = next(
                    ((i, x) for i, x in enumerate(sequence) if x < 20), (None, None)
                )
                sequence.append(arr[i])
                seq_indices.append(i)
                # Determine drought type based on decline speed
                if (arr[seq_indices[0]-1] - first_below_20_value) / first_below_20_index > 5 and all(sequence[i] > sequence[i + 1] for i in range(first_below_20_index)):

                    fd_sequences.append(sequence)
                    fd_indices.append(seq_indices)
                else:
                    sd_sequences.append(sequence)
                    sd_indices.append(seq_indices)
        else:
            i += 1

    # Create arrays to store flash and slow drought periods
    flash_drought = np.full(len(arr), np.nan)
    for idx in [item for sublist in fd_indices for item in sublist]:
        flash_drought[idx] = arr[idx]

    slow_drought = np.full(len(arr), np.nan)
    for idx in [item for sublist in sd_indices for item in sublist]:
        slow_drought[idx] = arr[idx]

    return flash_drought, fd_indices, slow_drought, sd_indices

def FlashDrought_Period(arr, indices_list):
    """
    Label the periods of flash drought events.
    """
    labels = [np.nan] * len(arr)
    if not indices_list:
        return labels

    for indice in indices_list:
        if indice:
            min_index = min(indice, key=lambda idx: arr[idx])  # Identify lowest moisture index
            labels[indice[0] - 1] = "before"  # Mark pre-drought
            labels[indice[0]] = "onset"  # Start of drought

            for j in range(1, len(indice)):
                if indice[j] <= min_index and arr[indice[j]] < arr[indice[j - 1]] - 5:
                    labels[indice[j]] = "onset"
                else:
                    for k in indice[j:]:
                        labels[k] = "recovery"
                    break

            try:
                labels[indice[-1] + 1] = "after"
            except IndexError:
                labels[indice[-1]] = "recovery"
    return labels

def SlowDrought_Period(arr, indices_list):
    """
    Label the periods of slow drought events.
    """
    labels = [np.nan] * len(arr)
    if not indices_list:
        return labels

    for indice in indices_list:
        if indice:
            min_index = min(indice, key=lambda idx: arr[idx])
            labels[indice[0] - 1] = "before"
            labels[indice[0]] = "onset"

            for j in range(1, len(indice)):
                if indice[j] <= min_index:
                    labels[indice[j]] = "onset"
                else:
                    labels[indice[j]] = "recovery"

            try:
                labels[indice[-1] + 1] = "after"
            except IndexError:
                labels[indice[-1]] = "recovery"
    return labels

# Define the data path
Path = 'FluxNet/AmeriFlux/'

# Example: Reading station information (adjust the path as needed)
excel_path = Path + "US-MOz.csv"

# Read the CSV file into a DataFrame
df = pd.read_csv(excel_path, encoding='utf-8')
print("File successfully loaded.")

# Process the time dimension
# Convert 'TIMESTAMP' column to datetime format
# The format '%Y%m%d' corresponds to 'YYYYMMDD' (e.g., 20240101)
df['date'] = pd.to_datetime(df['TIMESTAMP'], format='%Y%m%d')

# Extract the month from the date column
df['Month'] = df['date'].dt.month

# Extract the year from the date column
df['Year'] = df['date'].dt.year

# Remove leap day (February 29) to ensure consistency in yearly comparisons
df = df[(df['date'].dt.month != 2) | (df['date'].dt.day != 29)]

# Sort the DataFrame by date in ascending order
df_sorted = df.sort_values(by='date', ascending=True)

# Set 'date' as the index while keeping the original DataFrame unchanged
df = df_sorted.set_index('date', inplace=False)

# Ensure soil moisture values are valid (keep only non-negative values)
df['SWC_F_MDS_1'] = df['SWC_F_MDS_1'].where(df['SWC_F_MDS_1'] >= 0)

# Extract year from the index
df['year'] = df.index.year  # Ensure index is DatetimeIndex and add a year column

# Compute moving averages: Calculate 5-day averages within each year
df = df.groupby('year').apply(
    lambda x: x.resample('5D').agg({
        'SWC_F_MDS_1': 'mean',  # Compute mean for soil moisture values
    }).shift(0)  # No shift applied, keeping values aligned
).reset_index(level=0, drop=True)

# Set the 'date' column as the index
df['date'] = df.index

# Check if the year of each row is a leap year, creating a new column 'is_leap_year' with boolean values (True for leap years, False for non-leap years)
df['is_leap_year'] = df['date'].dt.is_leap_year

# Modify the 'date' column based on conditions:
# If the month is greater than February (i.e., March and later) and the year is a leap year, 
# add one day to the date (adjust dates after February to account for the leap day, i.e., 29th February).
# Otherwise, keep the original date unchanged.
df['date'] = df['date'].apply(lambda x: x + pd.Timedelta(days=1) if x.month > 2 and x.is_leap_year else x)
# Extract the month from the date column
df['Month'] = df['date'].dt.month

# Extract the year from the date column
df['Year'] = df['date'].dt.year
# Extract the day from the index (assuming the index is a datetime index)
df['Day'] = df['date'].dt.day
# Set 'date' as the index so that the data can be processed by date
df.set_index('date', inplace=True)
df['Percentile'] = df.groupby(['Month', 'Day'])['SWC_F_MDS_1'].transform(convert_to_percentile)

flash_drought , fd_indices,slow_drought ,   sd_indices=flash_slow_drought_identify(df['Percentile'].values)

FD_Period = FlashDrought_Period(flash_drought, fd_indices)
SD_Period = SlowDrought_Period(slow_drought, sd_indices)
df['flashdrought']=flash_drought
df['FD_Period']=FD_Period

df['slowdrought']=slow_drought
df['SD_Period']=SD_Period

df['date'] = df.index
df['date'] = pd.to_datetime(df['date'])
df.to_csv('result.csv', index=False)

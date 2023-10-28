import pandas as pd


def ewma(x_arr, time_arr, alpha, init=0.0):
  """Exponentially-weighted moving average.
  
  Behaves like O2 consumption or training load - takes a while to reach
  steady-state when starting out. This is different than the pandas EWMA
  implementation, which keeps the first value of x-arr as the first
  value of the average.
  
  Args:
    x_arr (list(float)): A series of values to calculate a EWMA of.
    time_arr (list(datetime.timedelta, datetime.datetime, or datetime.date)):
      Times corresponding to each value of x_arr.
    alpha (float): Decay coefficient for the EWMA. Must be 0 <= alpha <= 1.
      The smaller the alpha, the more important old values are to the
      average, or in other words longer the average's memory.
  """
  time_arr = pd.Series(time_arr)

  # Convert to timedelta with first value at 0.
  timedelta_array = time_arr - time_arr[0]

  # Convert to decimal days
  delta_day_decimal_array = [d.total_seconds() / 86400 for d in timedelta_array]

  # Initialize the moving average
  x_avg_arr = [init + x_arr[0] * alpha]

  # Recursively calculate the average at each time step
  for i in range(1, len(x_arr)):
    x_avg_arr.append(
      x_avg_arr[i-1] * (1 - alpha) ** (delta_day_decimal_array[i] - delta_day_decimal_array[i-1])
      + x_arr[i] * alpha
    )

  return x_avg_arr


def ewma_pandas(x_series, half_life, time_series=None):
  """Exponentially-weighted moving average.
  
  Behaves like O2 consumption - takes a while to reach steady-state
  when starting out.

  Args:
    x_series (pandas.Series): Values to make a EWMA of.
    half_life (int, str, or pandas.timedelta): half-life of the EWMA.
      If int, and time_series is provided, assumed to be integer seconds.
    time_series (pandas.Series): integer seconds from the start of the
      activity. If present, these will be used as coordinates over which
      we take the moving average. Default None.
  """

  # (no longer necessary) Calculate alpha from half-life.
  # alpha = 1 - math.exp(-math.log(2) / half_life)
  # alpha = 1 - math.exp(-1 / tau)

  x_series_pad = pd.concat([pd.Series([0.0]), x_series])

  if time_series is None:
    ewm_pad = x_series_pad.ewm(
      # alpha=(1 - math.exp(-1 / tau)),
      # halflife=(-1.0 * math.log(0.5) * tau),
      halflife=half_life,
      adjust=False,
      ignore_na=True,
    ).mean()

    return ewm_pad[1:]
  

def ewma_halflife(x_series, half_life, time_series=None):
  """Exponentially-weighted moving average.
  
  Behaves like O2 consumption - takes a while to reach steady-state
  when starting out.

  Args:
    x_series (pandas.Series): Values to make a EWMA of.
    half_life (int, str, or pandas.timedelta): half-life of the EWMA.
      If int, and time_series is provided, assumed to be integer seconds.
    time_series (pandas.Series): integer seconds from the start of the
      activity. If present, these will be used as coordinates over which
      we take the moving average. Default None.
  """

  # (no longer necessary) Calculate alpha from half-life.
  # alpha = 1 - math.exp(-math.log(2) / half_life)
  # alpha = 1 - math.exp(-1 / tau)

  x_series_pad = pd.concat([pd.Series([0.0]), x_series])

  if time_series is None:
    ewm_pad = x_series_pad.ewm(
      # alpha=(1 - math.exp(-1 / tau)),
      # halflife=(-1.0 * math.log(0.5) * tau),
      halflife=half_life,
      adjust=False,
      ignore_na=True,
    ).mean()

    return ewm_pad[1:]
  else:
    # Assume we are working with seconds.
    if isinstance(half_life, (int, float)):
      half_life = pd.to_timedelta(half_life, unit='s')
    elif isinstance(half_life, str):
      half_life = pd.to_timedelta(half_life)

    # Initialize the moving average so it takes off from 0 and tends
    # toward steady-state.
    num_padding = int(half_life.seconds * 40)
    x_series_pad = pd.Series(
      [0.0 for i in range(num_padding)] + x_series.to_list()
    )
    time_series = time_series - time_series[0]
    time_series_pad = pd.Series(
      [i for i in range(num_padding)] + (time_series + num_padding).to_list(),
    ).apply(pd.to_datetime, unit='s')

    # time_series_pad = pd.concat([
    #   pd.Series([0], dtype='datetime64[s]'),
    #   (time_series + 1).apply(pd.to_datetime, unit='s')
    # ])

    ewm_pad = x_series_pad.ewm(
      # alpha=(1 - math.exp(-1 / tau)),
      # halflife=(-1.0 * math.log(0.5) * tau),
      halflife=half_life,
      times=time_series_pad,
      adjust=False,
      ignore_na=True,
    ).mean()

    ewm = ewm_pad[num_padding:]
    ewm.index = x_series.index

    return ewm
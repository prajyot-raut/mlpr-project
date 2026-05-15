# MLPR Project

## Estimating Solar Panel Efficiency Using Weather and Pollution Data

### Abstract

The project focuses on estimating Global Horizontal Irradiance (GHI) using pollution, weather, and solar geometry data, addressing a major challenge in India where air pollution significantly reduces the sunlight reaching the Earth’s surface. Accurate GHI forecasting is important for solar energy planning and power generation optimization. Existing studies typically combine only weather and pollution data or weather and solar geometry, while few use station-level pollution telemetry for large-scale forecasting across India.

To address this gap, the project proposes a nationwide GHI forecasting pipeline using hourly CPCB PM2.5 and PM10 data, ERA5 weather variables, and computed solar geometry features such as solar zenith and azimuth angles. Multiple machine learning models including XGBoost, LightGBM, and LSTM were explored, along with preprocessing techniques such as cyclical time encoding, temporal lag feature engineering, and Yeo-Johnson normalization. One major challenge involved aligning large-scale multi-source datasets while balancing dataset reduction with maintaining nationwide robustness.

Among all models, the LSTM achieved the best performance with an R² score of 0.8669 and MAE of 39.1769 W/m². The proposed system demonstrates strong potential for pollution-aware solar forecasting and scalable deployment for solar energy planning.

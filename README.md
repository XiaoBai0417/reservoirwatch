# Reservoirwatch
This repository contains the example code accompanying the research paper titled "Near Real-Time Tracking of Global Reservoirs." This code serves as a framework illustrating the primary methodologies discussed in the paper, including data preprocessing, application of mapping algorithms, and other essential components necessary for the analysis of geospatial data.

## Description
The provided scripts perform a series of analyses detailed in the research, including data preprocessing, and result visualization. These scripts are intended to provide a transparent, reproducible snapshot of the research conducted.

The scripts provided here offer a range of functionalities:
- `MDNWI.js` and `SDWI.js`: JavaScript implementations for mapping water bodies using the Modified Normalized Difference Water Index (MDNWI) and Synthetic Aperture Radar Sentinel-1 Dual-Polarized Water Index (SDWI), respectively.
- `get_pois.py`: A utility for retrieving Point of Interest (POI) data from mapping APIs, encapsulating functionality from both `poi_data_retrieval` and `coordinates_converter`.
- `contour_detection.py`: Determines the boundaries of reservoirs based on collected point data, essential for detailed hydrological analysis.
-  export_reservoir_area.js：To optimize computational efficiency and manage large datasets effectively, this script employs batch processing to divide the dataset into smaller segments for parallel processing.



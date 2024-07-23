// Define the area of interest (AOI) with geographical boundaries
var region = ee.FeatureCollection('projects/deft-tube-316203/assets/tiegang')
// Set the time range
var startDate = '2022-01-01';
var endDate = '2022-12-31';

// Import Sentinel-2 data
var sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR')
  .filterDate(startDate, endDate)
  .filterBounds(region)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) // Filter images with less than 10% cloud coverage
  .median().clip(region); // Use median compositing to reduce the impact of clouds

// Calculate mNDWI
var mNDWI = sentinel2.normalizedDifference(['B3', 'B11']).rename('MNDWI');

// Set the threshold for water detection
var waterThreshold = 0.0; // mNDWI values greater than 0 are considered water

// Apply the threshold to identify water bodies
var waterMask = mNDWI.gt(waterThreshold).selfMask();

// Visualization parameters
var visualization = {
  bands: ['MNDWI'],
  min: -1,
  max: 1,
  palette: ['white', 'blue']
};

// Add layers to the map
Map.centerObject(region, 10);
Map.addLayer(mNDWI, visualization, 'MNDWI');


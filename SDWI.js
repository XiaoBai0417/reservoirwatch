var tegang_reservoir = ee.FeatureCollection('projects/deft-tube-316203/assets/tiegang');

function SDWI(Sen1) {
  var VH = Sen1.select("VH");
  var VV = Sen1.select("VV");
  var product = VV.multiply(VH).multiply(10);
  var logged = product.log();
  var sdwi = logged.subtract(8);
  return sdwi;
}

// Filter the dataset based on the reservoir boundary
var Sl = ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(tegang_reservoir);

// Initialize an empty list
var classifiyearhb = [];

// Loop to extract water body areas from 2015 to 2024
var visParams = {
  min: 0,
  max: 1,
  palette: ['white', 'blue']
};

for (var year = 2015; year <= 2024; year++) {
  print(year);
  var startDate = ee.Date.fromYMD(year, 1, 1);
  var endDate = ee.Date.fromYMD(year, 7, 1);
  var distyear = Sl.filterDate(startDate, endDate).mean().clip(tegang_reservoir);
  var yearLabel = "SDWI" + year;
  var SDWIyear = SDWI(distyear);
  print(SDWIyear);
  var mask = SDWIyear.gte(-0.3);
  var water = mask.updateMask(mask);
  Map.addLayer(water, visParams, yearLabel);
}

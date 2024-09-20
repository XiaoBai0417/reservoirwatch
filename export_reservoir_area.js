// To enhance computational efficiency and manage large datasets effectively, this script processes reservoir data in batches.
// Dividing the dataset into smaller parts allows for parallel processing, reducing overall processing time and memory consumption.
// This batch processing approach ensures that each segment of the dataset receives focused computational resources, leading to faster and more reliable outputs.
// Initialize the FeatureCollection for global reservoirs from a user-specific asset and set the analysis parameters.

var reservoirs = ee.FeatureCollection('users/hexinyue33/sample_reservoir');
var interval = 30; // Set the time interval.
var increment = 'day'; // Specify the units for the time interval as days.
var start = '2024-03-18'; // Define the start date for the image collection.
var end = '2024-09-20'; // Define the end date for the image collection.

// Convert the start date to an Earth Engine date object and calculate the millisecond increment for the sequence.
var startDate = ee.Date(start);
var secondDate = startDate.advance(interval, increment).millis(); // Calculate the date after the interval.
var increase = secondDate.subtract(startDate.millis()); // Calculate the interval in milliseconds.
var date_list = ee.List.sequence(startDate.millis(), ee.Date(end).millis(), increase); // Create a sequence of dates for image collection.

// Function to update reservoir features, aiming to enhance processing speed by dividing the workload into manageable parts.
function updata_reservoirs(feat_col, start_, parts, buffer_res, smooth_res, reduce_res, out_name){
  var arr = ee.List([])
  var collectionSize = feat_col.size(); // Determine the total number of features in the collection.
  var partitionSize = collectionSize.divide(parts).toInt(); // Calculate the number of features per batch.
  // Compute the total number of files to be generated based on the number of parts and remaining features.
  var file_numbers = (ee.Number(parts).add((collectionSize.subtract(partitionSize.multiply(parts))).divide(partitionSize).toInt())).add(1).toInt();
  print(out_name, collectionSize, partitionSize, file_numbers) // Output the batch details to the console.
  file_numbers = file_numbers.getInfo() // Retrieve the total file number count for iteration control.
  
  // Iterate through each batch for processing.
  for (var sign = start_;sign<file_numbers;sign++){
      var start = ee.Number(sign).multiply(partitionSize) // Calculate the starting index for the current batch.
      var part1 = feat_col.toList(partitionSize, start); // Convert the current batch of features to a list for processing.
      part1 = ee.FeatureCollection(part1) // Convert the list back to a feature collection.

      // Function to calculate water areas using Sentinel-1 SAR data.
      var calu = function(feat){
        var new_region = feat.geometry().bounds() // Get the bounding box of the feature.
        new_region = ee.Feature(new_region).buffer(100).geometry() // Buffer the bounding box to include surrounding context.
        var buffer = feat.geometry().buffer(buffer_res) // Buffer the feature geometry for spatial operations.
        // Map function to collect Sentinel-1 images over specified dates, filter by polarisation, and take the minimum value.
        var s1 = date_list.map(function(date){
          var s1_image =  ee.ImageCollection('COPERNICUS/S1_GRD')
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filterBounds(new_region).filterDate(ee.Date(date), ee.Date(date).advance(interval, increment))
            .min().clip(buffer).set('system:time_start',ee.Date(date).millis())
          return s1_image
        });

        var s1_img_col = ee.ImageCollection(s1) // Convert the list of images to an image collection.
        var temp_cols = ee.ImageCollection(s1_img_col) // Duplicate collection for further processing.
        var tmp_weak_mean = temp_cols.map(function(image){
            return image.set('nums',image.bandNames().size())
        });
        var new_img_cols = tmp_weak_mean.filterMetadata("nums","greater_than",2) // Filter images with more than two bands.

        // Process each image for water detection and area calculation.
        new_img_cols = new_img_cols.map(function(image){
          image = image.addBands(image.select('VV').focal_median(parseFloat(smooth_res.toString()),'circle','meters').rename('VV_smoothed'))
          image = image.addBands(image.select('VH').focal_median(parseFloat(smooth_res.toString()),'circle','meters').rename('VH_smoothed'))
          var VH = image.select("VH_smoothed");
          var VV = image.select("VV_smoothed");
          var x = VV.multiply(VH).multiply(10);
          var y=(x).log();
          var sdwi=y.subtract(8);
          sdwi = sdwi.select('VV_smoothed')
          var sdwi_water_area = sdwi.gte(0.3).selfMask()
          var sdwi_stad_area = sdwi.gte(-100).selfMask()

          var last_sdwi = ee.Image([sdwi_water_area.select('VV_smoothed').rename('sdwi_water_area'), 
          sdwi_stad_area.select('VV_smoothed').rename('sdwi_stad_area')]);
          last_sdwi = last_sdwi.set('system:time_start',ee.Date(image.get('system:time_start')))
          return last_sdwi
        })

        // Aggregate results for each image and export to CSV.
        var roi_sum = new_img_cols.map(function(image) {
            var ff = ee.Feature(null, {'date': ee.Date(image.get('system:time_start'))})
            var area_image = image.select('sdwi_water_area').multiply(ee.Image.pixelArea())
            var stats = area_image.reduceRegion({
              reducer: ee.Reducer.sum(),
              geometry: buffer,
              scale: reduce_res,
              maxPixels: 1e13,
              });
              ff = ff.set('water_area', stats.get('sdwi_water_area'))

            var area_image2 = image.select('sdwi_stad_area').multiply(ee.Image.pixelArea())
            var stats2 = area_image2.reduceRegion({
              reducer: ee.Reducer.sum(),
              geometry: buffer,
              scale: reduce_res,
              maxPixels: 1e13,
              });
              ff = ff.set('stad_area', stats2.get('sdwi_stad_area'))

            return ff})
            
        var roi_result = roi_sum.sort('date', true) // Sort results by date.

        var areas = roi_result.aggregate_array('water_area')
        var areas2 = roi_result.aggregate_array('stad_area')
        var dates = roi_result.aggregate_array('date')

        var fff = ee.Feature(null);
        fff = fff.set('ID', feat.get("ID"))
        fff = fff.set('water_area', areas)
        fff = fff.set('stad_area', areas2)
        fff = fff.set('date', dates)
        return fff
      }

      var new_name = sign.toString() + "_" + out_name
      var out = part1.map(calu) // Map the calculation function over each feature in the batch.
      Export.table.toDrive({
          collection: out,
          description: new_name,
          folder:"update_reservoir_" + "2024-03-18" + "-to-" + "2024-09-20",
          fileFormat: 'CSV'
      });
  }
}

// Filter reservoirs based on their ID and apply the processing function.
var roi = reservoirs.filterMetadata("ID","greater_than",0).filterMetadata("ID","less_than",1000)
updata_reservoirs(roi, 0, 10, 10, 10, 10, "ID_1000")

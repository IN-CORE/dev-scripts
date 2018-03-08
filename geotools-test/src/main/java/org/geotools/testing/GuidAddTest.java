package org.geotools.testing;

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.geotools.data.DataStore;
import org.geotools.data.DataStoreFinder;
import org.geotools.data.DefaultTransaction;
import org.geotools.data.FileDataStore;
import org.geotools.data.FileDataStoreFinder;
import org.geotools.data.Transaction;
import org.geotools.data.shapefile.ShapefileDataStore;
import org.geotools.data.shapefile.ShapefileDataStoreFactory;
import org.geotools.data.simple.SimpleFeatureCollection;
import org.geotools.data.simple.SimpleFeatureIterator;
import org.geotools.data.simple.SimpleFeatureSource;
import org.geotools.data.simple.SimpleFeatureStore;
import org.geotools.feature.AttributeTypeBuilder;
import org.geotools.feature.DefaultFeatureCollection;
import org.geotools.feature.simple.SimpleFeatureBuilder;
import org.geotools.feature.simple.SimpleFeatureTypeBuilder;
import org.opengis.feature.simple.SimpleFeature;
import org.opengis.feature.simple.SimpleFeatureType;

public class GuidAddTest {
	public static long startTime;
	public static long endTime;

	public static void main(String[] args) throws IOException {
		startTime = System.nanoTime();
		// input file

		String UNI_ID_SHP = "guid";

		String outFileName = "out_test";
		String outShpFileExt = "shp";
		String outGeoPkgFileExt = "gpkg";
		String outDir = "D:/data-temp/testing";

		File dataFile = new File("D:/data-temp/testing/slope_clip_polygon_wgs84.shp");
		dataFile.setReadOnly();
		FileDataStore store = FileDataStoreFinder.getDataStore(dataFile);

		SimpleFeatureSource source = store.getFeatureSource();

		SimpleFeatureCollection featureCollection = source.getFeatures();
		store.dispose();

		SimpleFeatureIterator simpleFeatureIterator = featureCollection.features();

		SimpleFeatureType sft = featureCollection.getSchema();

		SimpleFeatureTypeBuilder sftBuilder = new SimpleFeatureTypeBuilder();
		sftBuilder.init(sft);

		AttributeTypeBuilder build = new AttributeTypeBuilder();
		build.setNillable(false);
		build.setBinding(String.class);
		build.setLength(36);
		sftBuilder.add(build.buildDescriptor(UNI_ID_SHP));
		SimpleFeatureType newSft = sftBuilder.buildFeatureType();

		DefaultFeatureCollection newCollection = new DefaultFeatureCollection();

		try {
			while (simpleFeatureIterator.hasNext()) {
				SimpleFeature inputFeature = simpleFeatureIterator.next();
				SimpleFeatureBuilder sfb = new SimpleFeatureBuilder(newSft);
				sfb.init(inputFeature);
				UUID uuid = UUID.randomUUID();

				sfb.set(UNI_ID_SHP, uuid.toString());
				SimpleFeature newFeature = sfb.buildFeature(null);
				newCollection.add(newFeature);
			}
		} finally {
			simpleFeatureIterator.close();
			// store.dispose();
		}

		endTime = System.nanoTime();
		long elapsedTime = endTime - startTime;
		double seconds = (double) elapsedTime / 1000000000.0;
		System.out.println("Time for processing is " + Double.toString(seconds));

		outToShpFile(new File(outDir + File.separator + outFileName + "." + outShpFileExt), newSft, newCollection);
		outToGeoPkg(outDir + File.separator + outFileName + "." + outGeoPkgFileExt, newSft, newCollection);

	}

	public static DataStore getShapefileDataStore(URL shpUrl, Boolean spatialIndex) throws IOException {
		Map<String, Object> map = new HashMap<String, Object>();
		map.put("url", shpUrl);
		// map.put("create spatial index", spatialIndex);
		// map.put("enable spatial index", spatialIndex);

		return DataStoreFinder.getDataStore(map);
	}

	public static File outToShpFile(File pathFile, SimpleFeatureType schema, DefaultFeatureCollection collection)
			throws IOException {
		ShapefileDataStoreFactory dataStoreFactory = new ShapefileDataStoreFactory();

		Map<String, Serializable> params = new HashMap<String, Serializable>();
		params.put("url", pathFile.toURI().toURL());
		params.put("create spatial index", Boolean.TRUE);
		params.put("enable spatial index", Boolean.TRUE);
		ShapefileDataStore newDataStore = (ShapefileDataStore) dataStoreFactory.createNewDataStore(params);
		newDataStore.createSchema(schema);

		Transaction transaction = new DefaultTransaction("create");

		String typeName = newDataStore.getTypeNames()[0];
		SimpleFeatureSource featureSource = newDataStore.getFeatureSource(typeName);

		if (featureSource instanceof SimpleFeatureStore) {
			SimpleFeatureStore featureStore = (SimpleFeatureStore) featureSource;

			featureStore.setTransaction(transaction);
			try {
				featureStore.addFeatures(collection);
				transaction.commit();

			} catch (Exception problem) {
				problem.printStackTrace();
				transaction.rollback();

			} finally {
				transaction.close();
			}
		} else {
			System.out.println(typeName + " does not support read/write access");
			System.exit(1);
		}

		endTime = System.nanoTime();
		long elapsedTime = endTime - startTime;
		double seconds = (double) elapsedTime / 1000000000.0;
		System.out.println("Time for total processing is " + Double.toString(seconds));

		return pathFile;
	}

	public static void outToGeoPkg(String pathFile, SimpleFeatureType schema, DefaultFeatureCollection collection)
			throws IOException {

		Map params = new HashMap();
		params.put("dbtype", "geopkg");
		params.put("database", pathFile);

		DataStore newDataStore = DataStoreFinder.getDataStore(params);

		newDataStore.createSchema(schema);

		Transaction transaction = new DefaultTransaction("create");

		String typeName = newDataStore.getTypeNames()[0];
		SimpleFeatureSource featureSource = newDataStore.getFeatureSource(typeName);

		if (featureSource instanceof SimpleFeatureStore) {
			SimpleFeatureStore featureStore = (SimpleFeatureStore) featureSource;

			featureStore.setTransaction(transaction);
			try {
				featureStore.addFeatures(collection);
				transaction.commit();

			} catch (Exception problem) {
				problem.printStackTrace();
				transaction.rollback();

			} finally {
				transaction.close();
			}
		} else {
			System.out.println(typeName + " does not support read/write access");
			System.exit(1);
		}

		endTime = System.nanoTime();
		long elapsedTime = endTime - startTime;
		double seconds = (double) elapsedTime / 1000000000.0;
		System.out.println("Time for total processing is " + Double.toString(seconds));

	}
}

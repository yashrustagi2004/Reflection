// Switch to Reflection database (creates it if it doesn't exist)
db = db.getSiblingDB("Reflection");

// Create collections
db.createCollection("users");
db.createCollection("user_questions");
db.createCollection("resources");

// Verify collections were created
print("\n✅ Collections created successfully:");
db.getCollectionNames().forEach(function(col) {
  print("  - " + col);
});

// Show collection stats
print("\n📊 Collection stats:");
["users", "user_questions", "resources"].forEach(function(collName) {
  var stats = db.getCollection(collName).stats();
  print("  " + collName + ": " + stats.count + " documents");
});

// List all databases
print("\n🗄️  All databases:");
db.adminCommand("listDatabases").databases.forEach(function(database) {
  print("  - " + database.name + " (" + (database.sizeOnDisk / 1024).toFixed(2) + " KB)");
});

print("\n✅ MongoDB initialization complete!");

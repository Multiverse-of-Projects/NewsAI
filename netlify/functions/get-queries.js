const { MongoClient } = require("mongodb");
 
let cachedClient = null;
 
async function getMongoClient() {
  if (cachedClient) return cachedClient;
 
  const username = process.env.MONGO_USERNAME;
  const password = process.env.MONGO_PASSWORD;
  const uri = `mongodb+srv://${username}:${password}@devasy23.a8hxla5.mongodb.net/?retryWrites=true&w=majority&appName=Devasy23`;
 
  const client = new MongoClient(uri, {
    serverSelectionTimeoutMS: 10000,
    socketTimeoutMS: 30000,
  });
  await client.connect();
  cachedClient = client;
  return client;
}
 
exports.handler = async function (event) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  };
 
  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 204, headers, body: "" };
  }
 
  try {
    const client = await getMongoClient();
    const db = client.db(process.env.DB_NAME);
    const collection = db.collection("News_Articles_Ids");
 
    const docs = await collection
      .find({}, { projection: { query: 1, _id: 0 } })
      .toArray();
    const queries = docs.map((d) => d.query).filter(Boolean);
 
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ queries }),
    };
  } catch (err) {
    console.error("get-queries error:", err);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: "Failed to fetch queries", detail: err.message }),
    };
  }
};
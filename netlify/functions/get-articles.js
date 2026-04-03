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
 
  const query = event.queryStringParameters?.query;
  if (!query) {
    return {
      statusCode: 400,
      headers,
      body: JSON.stringify({ error: "Missing required query parameter: query" }),
    };
  }
 
  try {
    const client = await getMongoClient();
    const db = client.db(process.env.DB_NAME);
 
    // Step 1: Get article IDs for this query
    const idsDoc = await db
      .collection("News_Articles_Ids")
      .findOne({ query });
 
    if (!idsDoc || !idsDoc.ids || idsDoc.ids.length === 0) {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({ error: "No articles found for the given query" }),
      };
    }
 
    const articleIds = idsDoc.ids;
 
    // Step 2: Fetch articles
    const articles = await db
      .collection("News_Articles")
      .find(
        { id: { $in: articleIds } },
        {
          projection: {
            _id: 0,
            id: 1,
            title: 1,
            description: 1,
            content: 1,
            url: 1,
            urltoimage: 1,
            publishedat: 1,
            source: 1,
            summary: 1,
            keywords: 1,
            sentiment: 1,
            sentiment_score: 1,
          },
        }
      )
      .toArray();
 
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ articles, query }),
    };
  } catch (err) {
    console.error("get-articles error:", err);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: "Failed to fetch articles", detail: err.message }),
    };
  }
};
az functionapp create \
  --resource-group ai-skincare-reccommender \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4 \
  --os-type Linux \
  --name skincare-recommender-xyz123 \
  --storage-account skinstorage123

func azure functionapp publish skincare-recommender-xyz123

curl -X POST https://skincare-recommender-xyz123.azurewebsites.net/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"skin_type":"dry", "age":"30", "concern":"wrinkles"}'

curl -X POST http://localhost:7071/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"skin_type":"dry", "age":"30", "concern":"wrinkles"}'
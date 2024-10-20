# tAIsty - AI Powered Dining Delight

### Team: Coxwave  
### Theme: Building on WhatsApp

## Project Overview

**tAIsty** is an AI-driven solution designed to revolutionize the restaurant industry by enhancing the dining experience with personalized meal suggestions, interactive menu exploration, nutritional insights, and smart upselling. This project addresses challenges like diverse customer preferences, dietary restrictions, and limited staff while delivering a personalized experience to customers.

### Key Features

- **Personalized Meal Suggestions**  
  - AI analyzes past orders and preferences.
  - Considers dietary restrictions and allergies.
  - Suggests dishes tailored to customer tastes.
  - Learns and adapts over time.

- **Interactive Menu Exploration**  
  - Customers can ask questions about dishes.
  - Provides detailed information on ingredients and preparation methods.
  - Includes wine pairing suggestions.

- **Smart Upselling**  
  - Recommends complementary appetizers and desserts.
  - Promotes special deals to increase average order value.

- **Customer Feedback Loop**  
  - Helps refine menu recommendations and identify popular dishes.


## Technical Architecture

- **WhatsApp Webhook Integration**: Seamless interaction via WhatsApp chat.
- **AWS Lambda**: Powers backend logic and function calls for efficiency.
- **Qdrant**: Handles image search and filtering, leveraging embeddings for retrieval.
- **Llama 3.2-90B (TogetherAI)**: The core AI model behind menu recommendations and customer interactions.

### Framework Workflow

1. **AI Planner**: Detects user intent and routes the request to either the ADD or REMOVE agent.
2. **ADD/REMOVE Agents**: Adjusts the filter based on user preferences and dietary restrictions (e.g., vegan, spicy, etc.).
3. **Image Embedding**: Uses CLIP/VIT-B-32 to calculate embeddings for dish images.
4. **Qdrant Retrieval**: Searches metadata and performs semantic search using image embeddings.
5. **LLM Responder**: Generates conversational responses and provides dish suggestions with photos.


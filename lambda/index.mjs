import axios from 'axios';

export const handler = async (event) => {
  try {
    // Log the entire event for debugging
    console.log("Received event:", JSON.stringify(event, null, 2));

    // Parse the event body
    const body = event.body ? JSON.parse(event.body) : null;

    // Validate the parsed body and check if required fields are present
    if (!body || !body.phoneNumber) {
      return {
        statusCode: 400,
        body: JSON.stringify({ success: false, message: 'Invalid request. phoneNumber or accessToken missing.' }),
      };
    }

    const phoneNumber = body.phoneNumber;
    const accessToken = body.accessToken;

    // Define the API URL and headers
    const url = 'https://graph.facebook.com/v20.0/400364753169115/messages';
    const headers = {
      'Authorization': 'Bearer ' + process.env.access_token,
      'Content-Type': 'application/json',
    };

    // Define the payload (data to be sent)
    const data = {
      messaging_product: "whatsapp",
      to: phoneNumber,
      type: "template",
      template: {
        name: "welcome",
        language: {
          code: "en", // use correct language code
        },
      },
    };

    // Make the POST request using axios
    const response = await axios.post(url, data, { headers });
    console.log("Response from WhatsApp API:", response.data);

    // Return success response
    return {
      statusCode: 200,
      body: JSON.stringify({ success: true, data: response.data }),
    };
  } catch (error) {
    console.error("Error processing request:", error);

    // Return error response
    return {
      statusCode: 500,
      body: JSON.stringify({ success: false, error: "Internal Server Error" }),
    };
  }
};

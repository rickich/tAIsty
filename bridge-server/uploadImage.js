const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
require('dotenv').config(); // Load environment variables from .env

// Function to upload media to WhatsApp API
const uploadImageToWhatsApp = async (fileName, phoneNumberId, target, title) => {
  try {
    const accessToken = process.env.ACCESS_TOKEN; // WhatsApp access token from .env

    // Path to your file (assuming it is accessible in the server environment)
    const filePath = `./assets/${fileName}`; // Update this to point to your actual image path

    // Read the image file
    const file = fs.createReadStream(filePath);

    // Create form data
    const form = new FormData();
    form.append('file', file);
    form.append('type', 'image/png'); // Change the MIME type based on your file type
    form.append('messaging_product', 'whatsapp');

    // Send POST request to the WhatsApp API to upload media
    const response = await axios.post(
      `https://graph.facebook.com/v21.0/${phoneNumberId}/media`,
      form,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${accessToken}`,
          ...form.getHeaders(),
        },
      }
    );

    console.log("🚀 ~ uploadImageToWhatsApp ~ response:", response.data);

    // Send image message to WhatsApp
    await axios({
      method: 'POST',
      url: `https://graph.facebook.com/v20.0/${phoneNumberId}/messages`,
      data: {
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to: target,
        type: 'image',
        image: {
          id: response.data.id,
          caption: title,
        },
      },
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error uploading media:', error.message);
    throw new Error('Media upload failed');
  }
};

module.exports = uploadImageToWhatsApp;

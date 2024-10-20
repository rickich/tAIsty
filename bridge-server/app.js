const express = require('express');
const axios = require('axios');
const fs = require('fs');
require('dotenv').config(); // Load environment variables from .env
const uploadImageToWhatsApp = require('./uploadImage');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse incoming form data
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Webhook to handle incoming WhatsApp messages
app.post('/webhook', async (req, res) => {
  const body = req.body;

  if (body.object) {
    if (body.entry &&
        body.entry[0].changes &&
        body.entry[0].changes[0].value.messages &&
        body.entry[0].changes[0].value.messages[0]
    ) {
      const msgObj = body.entry[0].changes[0].value.messages[0];
      console.log("🚀 ~ app.post ~ msgObj:", msgObj);
      const phoneNumberId = body.entry[0].changes[0].value.metadata.phone_number_id;
      const from = msgObj.from;
      const msgType = msgObj.type;
      const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
      const messageTimestamp = parseInt(msgObj.timestamp, 10); // Convert the timestamp to an integer
      
      // Check if the message timestamp is within the last 2 minutes (120 seconds)
      if (currentTime - messageTimestamp > 120) {
        console.log('Message is older than 2 minutes. Ignoring.');
        return res.status(400).json({ error: 'Message too old to process' });
      }

      if (msgType === 'text') {
        const msgBody = msgObj.text.body;
        console.log(`Received message: ${msgBody} from ${from}`);

        try {
          // Call external API to get recommendations or message content
          const response = await axios.post('http://114.110.129.71:8000/api/v1/chat', {
            session_id: from+'2',
            message: msgBody,
            limit: 10,
            image: ''
          }, {
            headers: {
              'accept': 'application/json',
              'Content-Type': 'application/json',
            },
            timeout: 100000,
          });

          const recommendations = response.data.recommendations;

          // If recommendations exist, process and send them
          if (recommendations && recommendations.length > 0) {
            for (const rec of recommendations) {
              await uploadImageToWhatsApp(rec.file, phoneNumberId, from, rec.name);
            }
          }

          // Send text response back to WhatsApp
          await sendMessageToWhatsApp(phoneNumberId, from, response.data.message);

          return res.status(200).json({ status: 'Message processed successfully' });
        } catch (error) {
          console.error('Error processing request:', error.message);
          return res.status(500).json({ success: false, error: 'Internal Server Error' });
        }
      }
      
      if (msgType === 'image') {
        // Handle image messages here
        const mediaId = msgObj.image.id;
        const mediaCaption = msgObj.image.caption??"";
        const mimeType = msgObj.image.mime_type??"image/jpeg"
        
        try {
          const accessToken = process.env.ACCESS_TOKEN; // WhatsApp access token from .env

          // Get media metadata (JSON that contains the actual URL)
          const metadataResponse = await axios.get(`https://graph.facebook.com/v21.0/${mediaId}`, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
            timeout: 100000,
          });

          const mediaMetadata = metadataResponse.data;
          const mediaUrl = mediaMetadata.url;  // This is the actual image URL

          // Download the actual image using the URL from the metadata
          const mediaFilePath = './downloaded_image.jpeg'; // Change this to your desired file path
          await downloadFile(mediaUrl, mediaFilePath,accessToken);

          // Convert the downloaded image to base64
          const base64Image = await convertToBase64(mediaFilePath,mimeType);
          console.log("🚀 ~ app.post ~ base64Image:", base64Image)

          // Use base64Image in your request
          const response = await axios.post('http://114.110.129.71:8000/api/v1/chat', {
            session_id: from+'2',
            message: mediaCaption,
            limit: 10,
            image: base64Image // Send the base64 image
          }, {
            headers: {
              'accept': 'application/json',
              'Content-Type': 'application/json',
            },
            timeout: 100000,
          });

          const recommendations = response.data.recommendations;

          // If recommendations exist, process and send them
          if (recommendations && recommendations.length > 0) {
            for (const rec of recommendations) {
              await uploadImageToWhatsApp(rec.file, phoneNumberId, from, rec.name);
            }
          }

          // Send text response back to WhatsApp
          await sendMessageToWhatsApp(phoneNumberId, from, response.data.message);

          return res.status(200).json({ status: 'Message processed successfully' });
        } catch (error) {
          console.error('Error processing request:', error.message);
          return res.status(500).json({ success: false, error: 'Internal Server Error' });
        }
      }
    }
  }

  // Return a 404 if the event is not from a WhatsApp message
  return res.sendStatus(404);
});

// Function to download a file from a URL and save it locally
const downloadFile = async (url, outputLocationPath,accessToken) => {
  const writer = fs.createWriteStream(outputLocationPath);

  const response = await axios({
    url,
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    responseType: 'stream', // This is important to get the data as a stream
  },);

  // Pipe the response data (stream) into the file
  response.data.pipe(writer);

  return new Promise((resolve, reject) => {
    writer.on('finish', resolve);
    writer.on('error', reject);
  });
};

// Function to convert a local file to base64
const convertToBase64 = async (filePath,mimeType) => {
  try {
    const fileBuffer = fs.readFileSync(filePath); // Read file as a buffer
    const base64Image = fileBuffer.toString('base64'); // Convert to base64
    return `data:${mimeType};base64,${base64Image}`;
  } catch (error) {
    console.error('Error converting image to base64:', error.message);
    throw new Error('Failed to convert image to base64');
  }
};

// Function to send message to WhatsApp
const sendMessageToWhatsApp = async (phoneNumberId, to, message) => {
  const accessToken = process.env.ACCESS_TOKEN;
  try {
    await axios({
      method: 'POST',
      url: `https://graph.facebook.com/v20.0/${phoneNumberId}/messages`,
      data: {
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to,
        text: { body: message },
      },
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });
    console.log(`Message sent to ${to}`);
  } catch (error) {
    console.error('Error sending message:', error.message);
    throw new Error('Failed to send message');
  }
};

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});


// const express = require('express');
// const uploadImageToWhatsApp = require('./uploadImage');
// const axios = require('axios');
// const fs = require('fs');
// require('dotenv').config(); // Load environment variables from .env

// const app = express();
// const PORT = process.env.PORT || 3000;

// // Middleware to parse incoming form data
// app.use(express.json());
// app.use(express.urlencoded({ extended: true }));

// // Webhook verification endpoint
// app.get('/webhook', (req, res) => {
//   const VERIFY_TOKEN = 'taisty'; // Your verify token

//   // Parse the query params
//   const mode = req.query['hub.mode'];
//   const token = req.query['hub.verify_token'];
//   const challenge = req.query['hub.challenge'];

//   // Check if a token and mode were sent
//   if (mode && token) {
//     // Check the mode and token sent are correct
//     if (mode === 'subscribe' && token === VERIFY_TOKEN) {
//       console.log('WEBHOOK_VERIFIED');
//       return res.status(200).send(challenge); // Return the challenge string if verified
//     }
//   }

//   // Respond with '403 Forbidden' if verification fails
//   return res.sendStatus(403);
// });

// // Webhook to handle incoming WhatsApp messages
// app.post('/webhook', async (req, res) => {
//   const body = req.body;

//   if (body.object) {
//     if (body.entry &&
//         body.entry[0].changes &&
//         body.entry[0].changes[0].value.messages &&
//         body.entry[0].changes[0].value.messages[0]
//     ) {
//       const msgObj = body.entry[0].changes[0].value.messages[0];
//       console.log("🚀 ~ app.post ~ msgObj:", msgObj);
//       const phoneNumberId = body.entry[0].changes[0].value.metadata.phone_number_id;
//       const from = msgObj.from;
//       const msgType = msgObj.type;

//       // Get the current time and message timestamp
//       const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
//       const messageTimestamp = parseInt(msgObj.timestamp, 10); // Convert the timestamp to an integer
      
//       // Check if the message timestamp is within the last 2 minutes (120 seconds)
//       if (currentTime - messageTimestamp > 120) {
//         console.log('Message is older than 2 minutes. Ignoring.');
//         return res.status(400).json({ error: 'Message too old to process' });
//       }

//       if (msgType === 'text') {
//         const msgBody = msgObj.text.body;
//         console.log(`Received message: ${msgBody} from ${from}`);

//         try {
//           // Call external API to get recommendations or message content
//           const response = await axios.post('http://114.110.129.71:8000/api/v1/chat', {
//             session_id: phoneNumberId,
//             message: msgBody,
//             limit: 10,
//             image: ''
//           }, {
//             headers: {
//               'accept': 'application/json',
//               'Content-Type': 'application/json',
//             },
//             timeout: 100000,
//           });

//           const recommendations = response.data.recommendations;

//           // If recommendations exist, process and send them
//           if (recommendations && recommendations.length > 0) {
//             for (const rec of recommendations) {
//               await uploadImageToWhatsApp(rec.file, phoneNumberId, from, rec.name);
//             }
//           }

//           // Send text response back to WhatsApp
//           await sendMessageToWhatsApp(phoneNumberId, from, response.data.message);

//           return res.status(200).json({ status: 'Message processed successfully' });
//         } catch (error) {
//           console.error('Error processing request:', error.message);
//           return res.status(500).json({ success: false, error: 'Internal Server Error' });
//         }
//       } else if (msgType === 'image') {
//         // Handle image messages here
//         const mediaId = msgObj.image.id;
//         const mediaCaption = msgObj.image.caption;

//         try {
//           const accessToken = process.env.ACCESS_TOKEN; // WhatsApp access token from .env

//           // Construct the download URL for the media
//           const downloadURL = `https://graph.facebook.com/v21.0/${mediaId}/?access_token=${accessToken}`;

//           // Download the media file and save it locally
//           const mediaFilePath = './media_file'; // Change this to your desired file path
//           await downloadFile(downloadURL, mediaFilePath);

//           // Read and convert to base64
//           const base64Image = await convertToBase64(mediaFilePath);

//           const response = await axios.post('http://114.110.129.71:8000/api/v1/chat', {
//             session_id: phoneNumberId,
//             message: mediaCaption,
//             limit: 10,
//             image: base64Image // Send the base64 image
//           }, {
//             headers: {
//               'accept': 'application/json',
//               'Content-Type': 'application/json',
//             },
//             timeout: 100000,
//           });

//           const recommendations = response.data.recommendations;

//           // If recommendations exist, process and send them
//           if (recommendations && recommendations.length > 0) {
//             for (const rec of recommendations) {
//               await uploadImageToWhatsApp(rec.file, phoneNumberId, from, rec.name);
//             }
//           }

//           // Send text response back to WhatsApp
//           await sendMessageToWhatsApp(phoneNumberId, from, response.data.message);

//           return res.status(200).json({ status: 'Message processed successfully' });
//         } catch (error) {
//           console.error('Error processing request:', error.message);
//           return res.status(500).json({ success: false, error: 'Internal Server Error' });
//         }
//       }
//     }
//   }

//   // Return a 404 if the event is not from a WhatsApp message
//   return res.sendStatus(404);
// });

// // Function to download a file from a URL and save it locally
// const downloadFile = async (url, outputLocationPath) => {
//   const writer = fs.createWriteStream(outputLocationPath);

//   const response = await axios({
//     url,
//     method: 'GET',
//     responseType: 'stream', // This is important to get the data as a stream
//   });

//   response.data.pipe(writer);

//   return new Promise((resolve, reject) => {
//     writer.on('finish', resolve);
//     writer.on('error', reject);
//   });
// };

// // Function to convert a local file to base64
// const convertToBase64 = async (filePath) => {
//   try {
//     const fileBuffer = fs.readFileSync(filePath); // Read file as a buffer
//     const base64Image = fileBuffer.toString('base64'); // Convert to base64
//     return base64Image;
//   } catch (error) {
//     console.error('Error converting image to base64:', error.message);
//     throw new Error('Failed to convert image to base64');
//   }
// };

// // Function to send message to WhatsApp
// const sendMessageToWhatsApp = async (phoneNumberId, to, message) => {
//   const accessToken = process.env.ACCESS_TOKEN;
//   try {
//     await axios({
//       method: 'POST',
//       url: `https://graph.facebook.com/v20.0/${phoneNumberId}/messages`,
//       data: {
//         messaging_product: 'whatsapp',
//         recipient_type: 'individual',
//         to,
//         text: { body: message },
//       },
//       headers: {
//         Authorization: `Bearer ${accessToken}`,
//         'Content-Type': 'application/json',
//       },
//     });
//     console.log(`Message sent to ${to}`);
//   } catch (error) {
//     console.error('Error sending message:', error.message);
//     throw new Error('Failed to send message');
//   }
// };

// // Start the server
// app.listen(PORT, () => {
//   console.log(`Server is running on port ${PORT}`);
// });

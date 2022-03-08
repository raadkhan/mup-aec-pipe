const functions = require("firebase-functions");

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions
//
// exports.helloWorld = functions.https.onRequest((request, response) => {
//   functions.logger.info("Hello logs!", {structuredData: true});
//   response.send("Hello from Firebase!");
// });

// The Firebase Admin SDK to access Firestore.
const admin = require('firebase-admin');
admin.initializeApp();

const {Storage} = require('@google-cloud/storage');

// The ID of your GCS bucket
 const bucketName = 'muop2021';

// The path to your file to upload
 const filePath = 'path/to/your/file';

// The new ID for your GCS file
 const destFileName = 'your-new-file-name.png';

// Imports the Google Cloud client library


// Listens for new messages added to /messages/:documentId/original and creates an
// uppercase version of the message to /messages/:documentId/uppercase
exports.makeUppercase = functions.firestore.document('/messages/{documentId}')
    .onCreate(
    async (snap, context) => {
     // Instantiate the GCP Storage instance
   /*  var gcs = new Storage({
         projectId: "capstonemuop",
         keyFileName:'./capstonemuop-f4ae9508f8bc.json'}
         )
         bucket = gcs.bucket('muop2021');
     */
     const base64data = snap.data().base64encode;
     console.log(base64data);
     
     // Upload the image to the bucket
     try {
         console.log("trying try block")

        // Step 2: Upload to Firestore Storage
        await uploadLocalFileToStorage(base64data);

        // Step 3: Update `collection` 
        return snap.ref.set({decoded:true},{merge: true});
    }
    catch(error) {
        console.log("error on downloading and uploading remote media file to storage: " + error);
    }

    });


async function uploadLocalFileToStorage(base64data) {
   /* const imageBucket = "images/";
    var gcs = new Storage({
        projectId: "capstonemuop",
        keyFileName:'./capstonemuop-f4ae9508f8bc.json'});
    var bucket = gcs.bucket('muop2021');
   // const bucket = admin.storage().bucket();
    const destination = 'uploadedimage.png';
    
    try {
         // Uploads a local file to the bucket
         await bucket.upload('./dogs.png', {
                destination: destination, 
         });
    
        console.log('Successfully uploaded file');
     }
    catch (e) {
        throw new Error("uploadLocalFileToStorage failed: " + e);
    } */
  
   var stream = require('stream');
   var bufferStream = new stream.PassThrough();
   bufferStream.end(Buffer.from(base64data, 'base64'));


    var gcs = new Storage({
    projectId: "capstonemuop",
    keyFileName:'./capstonemuop-f4ae9508f8bc.json'});
    var bucket = gcs.bucket('muop2021');

    var file = bucket.file('decodedimage.jpg');

    bufferStream.pipe(file.createWriteStream({
        metadata: {
          contentType: 'image/jpeg',
          metadata: {
            custom: 'metadata'
          }
        },
        validation: "md5"
      }))
      .on('error', function(err) {})
      .on('finish', function() {
        console.log("upload successful")
      });


 }
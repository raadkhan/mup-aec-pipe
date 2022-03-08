# mup-aec(asset, edge, cloud)-pipe
the software to connect the asset (a Raspberry Pi with a day/night fisheye camera), the edge (a mangOH Yellow), and the cloud (Cloud Firestore on Firebase) to the MUP (Monitoring Unoccupied Properties) pipeline, Octave by Sierra Wireless.

## asset software
a modified TFLite classifier to detect and capture human intruders at the property.

## edge software
a Python script to transmit the asset's shot of the human intruder to the pipeline via the edge.

## cloud software
a Firebase Cloud Function to detect and alert the owner about anomalies at the property seen by the edge.

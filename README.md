# Simple Data Tokenisation Service using GCP Cloud Functions and Firestore

A GCP based data tokenisation service which takes in a key and returns a token of the same data type using a de-identification function. The de-identification process is described below:  

![De-Identification Sequence Diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/gamma-data/gcp-data-tokenisation-as-a-service/master/de-identification.puml)  

The re-identification process takes in a token and returns the associated natural key, the re-identification process is described here:  

![Re-Identification Sequence Diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/gamma-data/gcp-data-tokenisation-as-a-service/master/re-identification.puml)  

## Deployment

Deploy the de-identification and re-identification functions using the `gcloud functions deploy` command

```bash
cd deidentification_fn
gcloud functions deploy deidentification_fn --entry-point main --runtime python37 --trigger-http --allow-unauthenticated
cd reidentification_fn
gcloud functions deploy reidentification_fn --entry-point main --runtime python37 --trigger-http --allow-unauthenticated
```

> you will need to assign the "Google Cloud Functions Service Agent" service account a role that has sufficient privelges to upload staged function artefacts to GCS  

## Deployment


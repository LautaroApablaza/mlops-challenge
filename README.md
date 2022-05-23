# MLOps Challenge

## 1. Introduction
The main objectives of this project are:

1. Build a scalable data pipeline for feature engineering & training machine learning model using good CI/CD practices. 
2. Create an API to serve those features
3. Create a prediction service that uses the created features


I have tried to create a solution that use the AWS Serverless Application Model (AWS SAM) to create a Step Functions workflow with different SageMaker Job´s. They allows us to train ML models, deploy ML models, test results, and expose an inference endpoint. Step function also provides a way to wait for human approval before the state transitions can progress towards the creation of the final model inference endpoint’s.

However, this project only represents a draft of the final solution since due to lack of time I could not finish and test the automation of the pipeline. I consider that it represents a large part of the work to be developed but even so it needs to be improved,



<br />

## 2. Architecture

This project was built using Amazon Web Services together with the github repository service. Below you can see an overall of the architecture:


<br />

![This is an image](assets\mlops-architecture.PNG)


<br />

### **Components:**

**AWS CodePipeline:** CodePipeline has several stages defined in CloudFormation, which allows you to obtain the latest version of the code in the repository and build the necessary services.

**AWS CodeBuild:** This solution uses AWS CodeBuild to build the source code from GitHub.

**Amazon S3:** Artifacts created throughout the pipeline as well as the data for the model is stored in an Simple Storage Service (S3) Bucket.

**AWS CloudFormation:** This solution uses the AWS CloudFormation Template language, in either YAML or JSON, to create each resource including a custom resource.

**AWS Step Functions:** This solutions creates AWS StepFunctions to orchestrate Amazon SageMaker training and processing jobs.

**Amazon SageMaker:** This solution uses Amazon SageMaker to train and deploy the machine learning model. Also, uses SageMaker jobs to process the data and create a Feature Store.

**AWS CodeDeploy:** This solution uses AWS CodeDeploy to automate shifting traffic between the AWS Lambda functions. This is used indirectly when the The AWS Serverless Application Model (AWS SAM) builds the necessary services.

**Amazon API Gateway:** This solutions creates HTTPS REST API endpoints for AWS Lambda functions that allows us to serve the users features and invoke deployed Amazon SageMaker Endpoint.

**Amazon Lambda:** This solution uses AWS lambda to execute the logic that allows us to:
 - Notify the user of the different stages that the pipeline is running,
 - Make predictions based on the features of the users.

**AWS Simple Notification Service:** Some of the stages defined on the Step Function workflow
send emails with different useful links to the user.  


<br />

## 3. Step Function workflow

The following diagram describes the flow of the Step Function StateMachine. There are several points where the StateMachine has to poll and wait for a task to complete.

![This is an image](assets\state-machine.PNG)


<br />

The pipeline contains the following stages:

**Processing Job:** Create and run a processing job in SageMaker to manipulate and transform the raw data into features that can be used in the model training . It stores the processed data in a parquet file. 

**Features store Job:** The processed data is registered in SageMaker Feature Store, which is a purpose-built repository. It uses the 'id' column as the record identifier key and the 'loan_date' column as the Event Time feature. With this service, you can store and access features so it’s much easier to name, organize, and reuse them across teams.

**Training Job:** Create and run a training job in SageMaker using the processed data and a python script which specify how to do the job. In this case, it trains a RandomForests classification algorithm. In addition, some metrics of the model are calculated and saved in the S3 bucket to evaluate its performance.

**Email Metrics, Request Approval:** This task invoke a lambda function that send a message to
the users who can evaluate the performance of the model and decide to register or discard it

**Model Registry:** In this stage the trained model is registered in SageMaker Model Registry.

**Create Endpoint Config:** This task is necessary for the next step. We define the hardware needed to serve the model

**Create Endpoint:** The trained model is available on a SageMaker endpoint and can be used for inferences.

**Create Endpoint:** This task invoke a lambda function that send an email with the API's link where the model can be used. 

<br />

## 4. Endpoints

For this solution was created one HTTPS API Gateway which routes the incoming traffic to the different lambda functions. Specifically, 3 endpoints were created:

1. **Feature Store endpoint:** Given an id, it returns 5 features which help to describe the credit status of clients. The endpoint returns information about the last loan made for the a given user id. 

2. **Sagemaker Endpoint:** Given an id, it returns the prediction of the credit risk using the previously trained model and the feature store endpoint.

3. **Response to Model Approval:** This endpoint is used to obtain the decision of the user regarding the model and its performance.

<br />

## 5. Folder Structure

- **assets:** In this folder you can find the images used to create this file
- **documents:**  In this folder you can find the raw dataset and the Jupyter notebooks of the feature engineering and training stages.
- **src**:
    - **scripts:** In this folder you can find Python scripts.
        - **sagemaker:**: Python scripts which are executed by the different SageMaker jobs.
        - **functions:**: Python scripts which are executed by the different Lambda functions.
    - **templates:** Cloud Formation templates needed to deploy all the resources
        - **statemachine:** JSON template used to define all the stages on the Step Function workflow.

<br />

## 6. To review

- CI/CD: Need to define and test the pipeline of the code. Decouple the deploy of the different resources.
- Tests: No unit tests or integration tests were defined
- Python Scripts: The code structure can be improved. I was trying to implement an object-oriented architecture.
- Model: A job or a task that evaluates the health of the model could be added.


<br />


# shopify-api-report
![alt text](<images/cover.png>)


### 1. Create DynamoDB Table
1. Sign-in to https://aws.amazon.com/console/
2. Navigate to `DynamoDB` > `Table` > `Create Table`
3. Name it `shopify-api`. Under `Partition key`, enter `id`, change `String` to `Number`, leave the rest default and `Create Table`.
![alt text](<images/dynamodb_table.png>)

### 2. Get Shopify API Access Token
1. Sign-in to https://www.shopify.com/login?ui_locales=en
2. `Settings` > `Apps and sales channels` > `Develop apps`
![alt text](<images/shopify1.png>)
3. `Create an app`
4. Under `Over view` > `Configure Admin API scopes` > grant all the read permissions > `Save`
![alt text](<images/shopify2.png>)
5. `API credentials` > `Install app`
![alt text](<images/shopify3.png>)
6. You can now `Reveal token once` to retreive Shopify API Access Token later for our lambda function.
![alt text](<images/shopify4.png>)

If you lost this key, simply `Uninstal app` and `Install app` again. Shopify will allow you to reveal a new key.

### 3. Create a Role for Lambda Function
1. Navigate to `IAM` > `Roles` > `Create role`
2. `Trusted entity type` = `AWS service` > `Use case` = `Lambda`
3. Under `Add permission` > `AmazonDynamoDBFullAccess`

### 4. Setup Lambda Layer
My python code in Lambda Function will use `requests` which doesn't included within AWS library by default. This step will require pip and 7zip

1. Install `requests` library into a folder using `pip install requests` and zip it using `7zip`
2. Navigate to `Lambda` > create a new layer > upload the zip file

You can refer to Step 4 in this [project](https://github.com/nhatvo1502/twilio-microservice) with step-by-step

### 5. Create Lambda Function
I used Python for this project

1. Navigate to `Lambda` > `Create function`
2. Copy and paste the code from `shopify_api.py` abd make sure the DynamoDB Table name matches with `Step 1`
3. `Configuration` > `Environment variables` > Create `ACCESS_TOKEN` with the value retrieved from `Step 2` > Create 'STORE_NAME` with value of your Shopify store name
![alt text](<images/lambda_environmentvars.png>)
4. `Permissions` > `Edit` > Under `Existing role` select role that created from `Step 3`
5. Assign layer created from `Step 4`

### 5. Testing
1. I used PostMan to make sure my API URL is correct. Make sure to include `created_at_min` and `created_at_max` with the value format as ISO8061 on the `Params`
![alt text](<images/testing_postman1.png>)

2. and `X-Shopify-Access-Token` where value is a API from `Step 2` on `Headers`
![alt text](<images/testing_postman2.png>)
3. Once the URL is working, I tested Lambda Function to make sure my logic also working
4. Depends on how much orders within that day, Lambda can take up to a few minutes of runtime. I change my `Timeout` value to 5 min. This setting can be found under `Configuration` > `General configuration`.
![alt text](<images/testing_timeout_config.png>)
5. If everything works correctly, there should be some records in DynamoDB Table
![alt text](<images/testing_dynamodb.png>)

### 6. Create Scheduler
1. On `AWS Services Console`, navigate to `Amazon EventBridge` > `Schedules` > `Create schedule`
2. `Recurring schedule` > `Rate-based scedule` > Enter Value = `1` and Unit = `days` > `Next`
![alt text](<images/scheduler1.png>)
3. Our target is `AWS Lambda Invoke` > Under `Lambda function` select our function from `Step 5` 
![alt text](<images/scheduler2.png>)

### 7. Create IAM User for Amazon DynamoDB ODBC Driver
The ODBC Driver is a universal driver that will help connect our AWS DynamoDB Table to Power BI. It will need a user with access into our AWS table.

1. Navigate to `AWS IAM` > `Create user` > name it `DynamoDB-ODBC-driver`
2. Select `Attach policies directly` > grant `AmazonDynamoDBFullAccess`
![alt text](<images/7-permission.png>)
3. Select this role > go to `Security credentials` > `Create access key` > `Third-party service` > `Next`
![alt text](<images/7-accesskey.png>)
4. Note this down for `Step 8`

### 8. Download and configure CDATA Amazon DynamoDB ODBC Driver
1. Navigate to https://www.cdata.com/odbc/#drivers
2. Search "dynamodb"
![alt text](<images/odbc1.png>)
3. Download > Download trial
![alt text](<images/odbc2.png>)
4. To Configure Data Source, use AWS Access Key and AWS Secret Key from `Step 7`
5. Click `Test Connection`. If the permission is setup properly, it should be connected
![alt text](<images/odbc3.png>)

### 9. Connect to Power BI
1. Download Power BI Desktop (online version doesn't support ODBC at this moment)
2. `File` > `Get Data` > `Get Data to get Started` > `Other` > `ODBC`
![alt text](<images/bi1.png>)
3. Leave it default `CDATA AmazonDynamoDB Source` > `OK`
![alt text](<images/bi2.png>)
4. Default for both admin and password for `CDATA AmazonDynamoDB Source` should be `admin`
5. Expanding until the our table appears > select > `load`
![alt text](<images/bi3.png>)
6. After succesfully loading the dataset in, it's ready to be processed and visualized
![alt text](<images/bi4.png>)
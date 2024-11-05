import json
from datetime import datetime, timedelta
import os
import requests
import boto3
import re
from decimal import Decimal

#Environment Variables
store_name = os.environ.get("STORE_NAME")
access_token = os.environ.get("ACCESS_TOKEN")

#Declare dynamodb variables
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('shopify-db')

def lambda_handler(event, context):
    #URL
    ytd = datetime.utcnow() - timedelta(hours=8) - timedelta(days=1)
    year = ytd.year
    month = ytd.month
    day = ytd.day
    created_at_min = f'{year}-{month}-{day}T00:01:00-07:00'
    created_at_max = f'{year}-{month}-{day}T23:59:59-07:00'
    url = f'https://{store_name}.myshopify.com/admin/api/2024-10/orders.json?status=any&created_at_min={created_at_min}&created_at_max={created_at_max}'
     
    #HEADERS
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    
    #INVOKE
    result, total_orders, error_code = invoke(url=url, headers=headers)

    #WRITE TO DATABASE
    writeDB(result)

    #Logging
    print('url = ' + url)
    print('total_orders = ' + str(total_orders))
    print('error_code = ' + error_code)
    
    #RETURN
    return {
        'statusCode': 200,
        'url': url,
        'total_orders': total_orders,
        'error_code': error_code
    }

def invoke(url='', headers={}):
    '''
    Input: URL, headers
    Output: orders[json], total_order[int], error_code[str]
    Purpose: invoke CURL with URL and headers
    '''
    result = []
    error_code = 'None'
    total_order = 0
    if url!='' and len(headers)>0:
        response = requests.get(url, headers = headers)
        parsed_data = json.loads(response.text, parse_float=Decimal)
        result = parsed_data['orders']
        total_order += len(result)
        link = response.headers.get('link', None)
        if link!=None:
            url = url_extractor(link)
            if url!='':
                next_result, next_total_order, next_error_code = invoke(url = url, headers = headers)
                result.extend(next_result)
                total_order+=next_total_order
                error_code = next_error_code
    else:
        error_code = 'Missing parameters: url or headers'
    return result, total_order, error_code

def url_extractor(link):
    url_pattern = r'https?://[^\s/$.?#].[^\s]*'
    urls = re.findall(url_pattern, link)
    trimmed_urls = [url[:-2] for url in urls]
    if "next" in link and "previous" in link:
        return trimmed_urls[1]
    elif "next" in link:
        return trimmed_urls[0]
    else:
        return ''

def writeDB(order_list):
    for order in order_list:
        table.put_item(
            Item=order
        )
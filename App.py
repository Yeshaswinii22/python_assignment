from flask import Flask, request, redirect, url_for, render_template
import boto3
import os
from dotenv import load_dotenv
from urllib.parse import unquote
from botocore.exceptions import ClientError
load_dotenv()
app = Flask(__name__)
#app.aws_secret_key='sample project'
#AWS_ACCESS_key_id='AWS_ACCESS_KEY_ID'
aws_access_key=os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key=os.getenv('AWS_SECERT_ACCESS_KEY')
s3 = boto3.client('s3',aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_key)
@app.route('/')
#refering to index page
def index():
    buckets = s3.list_buckets()['Buckets']
    return render_template('index.html', buckets=buckets)

@app.route('/list/<bucket_name>')
def list_bucket(bucket_name):
    contents = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
    return render_template('index.html', contents=contents, bucket_name=bucket_name,buckets=s3.list_buckets()['Buckets'])

#creating the bucket
@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['bucket_name']
    try:
    #location={'LocationConstraint':"eu-north-1"}
        s3.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        return str(e), 400
    return redirect(url_for('index'))
#deleting the bucket
@app.route('/delete_bucket/<bucket_name>', methods=['POST'])
def delete_bucket(bucket_name):
    try:
        s3.delete_bucket(Bucket=bucket_name)
    except ClientError as e:
        return str(e), 400
    return redirect(url_for('index'))
#creating the folder for bucket
@app.route('/create_folder/<bucket_name>', methods=['POST'])
def create_folder(bucket_name):
    folder_name = request.form['folder_name']
    try:
        s3.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
    except ClientError as e:
        return str(e), 400
    return redirect(url_for('list_bucket', bucket_name=bucket_name))
#uploding the files to bucket
@app.route('/upload/<bucket_name>', methods=['POST'])
def upload_file(bucket_name):
    file = request.files['file']
    if file:
        s3.upload_fileobj(file, bucket_name, file.filename)
    return redirect(url_for('list_bucket', bucket_name=bucket_name))
#delete the file from the bucket
@app.route('/delete_file/<bucket_name>/<file_name>', methods=['POST'])
def delete_file(bucket_name, file_name):
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
    except ClientError as e:
        return str(e), 400
    return redirect(url_for('list_bucket', bucket_name=bucket_name))
#copy the bucket 
@app.route('/copy_file/<bucket_name>/<file_name>', methods=['POST'])
def copy_file(bucket_name, file_name):
    destination_bucket = request.form['destination_bucket']
    copy_source = {'Bucket': bucket_name, 'Key': file_name}
    try:
        s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=file_name)
    except ClientError as e:
        return str(e), 400
    return redirect(url_for('list_bucket', bucket_name=bucket_name))
#move the bucket 
@app.route('/move_file/<bucket_name>/<file_name>', methods=['POST'])
def move_file(bucket_name, file_name):
    destination_bucket = request.form['destination_bucket']
    copy_source = {'Bucket': bucket_name, 'Key': file_name}
    try:
        s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=file_name)
        s3.delete_object(Bucket=bucket_name, Key=file_name)
    except ClientError as e:
        return str(e), 400
    return redirect(url_for('list_bucket', bucket_name=bucket_name))
#delete the folder from bucket
@app.route('/delete_folder/<bucket_name>/<path:folder_key>', methods=['POST'])
def delete_folder(bucket_name, folder_key):
    folder_key = unquote(folder_key)
    s3.delete_object(Bucket=bucket_name, Key=folder_key)
    return redirect(url_for('list_bucket', bucket_name=bucket_name))
if __name__ == '__main__':
    app.run(debug=True,port=5002)
from flask import current_app, flash
import boto3, botocore
from botocore.exceptions import NoCredentialsError

def upload_to_aws(local_file, bucket, s3_file):
	s3 = boto3.client(
		's3', 
		aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'], 
		aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
	)

	try:
		# s3.upload_file(local_file, bucket, s3_file)
		s3.upload_fileobj(local_file, bucket, s3_file, ExtraArgs={ 'ACL': 'public-read' })
		print("Upload Successful")
		return True
	except FileNotFoundError:
		print("The file was not found")
		return False
	except NoCredentialsError:
		print("Credentials not available")
		return False
	except Exception as e:
		# This is a catch all other exception, edit this part to fit your needs.
		print("You have a file upload error: ", e)
		return flash(f"There was an error uploading the file. Please try again. If issue doesn't resolve contact website administrator", 'btn-danger')
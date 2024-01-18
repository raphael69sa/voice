import os
import boto3
from pydub import AudioSegment
import assemblyai as aai

# Replace with your AssemblyAI API token
aai.settings.api_key = "add8a8fa81b0439499ba66ee69412924"

# Specify the AWS region where your S3 bucket is located
aws_region = 'us-east-1'  # Replace with the actual region of your S3 bucket

# Set your AWS credentials
aws_access_key_id = 'AKIA34NPKEVSV6GJUK4F'
aws_secret_access_key = 'aPMZaQH7fOksdtHqBMBcQcbmxcnZ3/jwdVI7dvUO'

# AWS S3 configuration
s3 = boto3.client('s3')
bucket_name = 'decipher'
input_folder = 'Voice'
output_folder = 'Transcribed'

def transcribe_audio():
    try:
        # Define the transcription configuration
        config = aai.TranscriptionConfig()

        # List objects (audio files) in the input folder
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=input_folder)
        for obj in objects.get('Contents', []):
            object_key = obj['Key']

            # Check if the object is an audio file (you may need to adjust the condition)
            if object_key.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):

                # Download the audio file from S3
                file_name = os.path.basename(object_key)
                input_file_path = f'/tmp/{file_name}'  # Temporarily store the file locally
                s3.download_file(bucket_name, object_key, input_file_path)

                # Convert MP3 to WAV if it's an MP3 file
                if file_name.lower().endswith('.mp3'):
                    audio = AudioSegment.from_mp3(input_file_path)
                    input_file_path = input_file_path[:-4] + '.wav'
                    audio.export(input_file_path, format='wav')

                # Transcribe the current audio file
                transcriber = aai.Transcriber()
                transcript = transcriber.transcribe(input_file_path, config=config)

                # Specify the output file path for this transcription in S3
                output_file_key = f'{output_folder}/{os.path.splitext(file_name)[0]}_transcription.txt'

                # Upload the transcription result to S3
                with open(input_file_path, 'rb') as transcript_file:
                    s3.upload_fileobj(transcript_file, bucket_name, output_file_key)

                # Clean up temporary files
                os.remove(input_file_path)

                # Delete the audio file from S3
                s3.delete_object(Bucket=bucket_name, Key=object_key)

        return "Audio transcription process completed."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    print(transcribe_audio())

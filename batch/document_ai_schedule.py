from google.cloud import documentai_v1


def sample_batch_process_documents():
    # Create a client
    client = documentai_v1.DocumentProcessorServiceClient()

    # Initialize request argument(s)
    request = documentai_v1.BatchProcessRequest(
        name="name_value",
    )

    # Make the request
    operation = client.batch_process_documents(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)


if __name__ == '__main__':
    sample_batch_process_documents(
        './ocr_test_file/20220322035514_information_mcz_twitterphoto_3_1506117114830405635-converted.pdf')

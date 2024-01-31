import boto3
import gzip
from configparser import ConfigParser
import os
import bz2
import json
import os
import json
import requests
from typing import Tuple


def decompress_file(input_path, output_path):
    try:
        with bz2.BZ2File(input_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                f_out.write(f_in.read())
        print(f"File decompressed successfully to {output_path}")
        # Remove the input file after successful decompression
        os.remove(input_path)
        print(f"Input file {input_path} removed after decompression")
    except Exception as e:
        print(f"Error decompressing file: {e}")


def download_newspaper_files_from_s3(
    bucket_name: str,
    newspaper_name: str,
    year: str,
    month: str,
    date: str,
    issue_version: str,
    local_directory: str,
    config_file_path: str,
) -> Tuple[str, str]:
    """
    Downloads newspaper files (pages and issues) from an S3 bucket and extracts them.

    Args:
        bucket_name (str): Name of the S3 bucket.
        newspaper_name (str): Name of the newspaper.
        year (str): Year of the newspaper issue.
        month (str): Month of the newspaper issue.
        date (str): Date of the newspaper issue.
        issue_version (str): Version of the newspaper issue.
        local_directory (str): Local directory to save the downloaded files.
        config_file_path (str): Path to the configuration file.

    Returns:
        Tuple[str, str]: Paths to the downloaded pages and issues files.

    Example:
        >>> pages_path, issues_path = download_newspaper_files_from_s3(
        ...     'my_bucket', 'newspaper', '2022', '01', '01', 'v1',
        ...     '/path/to/save/files', '/path/to/config/file'
        ... )
    """
    # Read the configuration from the .s3cfg file
    config_parser = ConfigParser()
    config_parser.read(config_file_path)

    # Get the values from the [default] section
    access_key = config_parser.get("default", "access_key")
    secret_key = config_parser.get("default", "secret_key")

    session = boto3.Session(
        aws_access_key_id=access_key, aws_secret_access_key=secret_key
    )
    s3 = session.client("s3", endpoint_url="https://os.zhdk.cloud.switch.ch")

    try:
        # Download pages file
        pages_key = f"{newspaper_name}/pages/{newspaper_name}-{year}/{newspaper_name}-{year}-{month}-{date}-{issue_version}-pages.jsonl.bz2"
        print(f"pages key to be downloaded = {pages_key}")
        issues_key = f"{newspaper_name}/issues/{newspaper_name}-{year}-issues.jsonl.bz2"
        print(f"issues key to be downloaded = {issues_key}")

        print("\nDownloading the pages JSONL from s3 .....")
        pages_local_path = f"{local_directory}/{newspaper_name}-{year}-{month}-{date}-{issue_version}/pages"

        if not os.path.exists(pages_local_path):
            os.makedirs(pages_local_path)

        pages_local_path = os.path.join(
            pages_local_path,
            f"{newspaper_name}-{year}-{month}-{date}-{issue_version}-pages.jsonl.bz2",
        )
        print(f"pages_local_path is {pages_local_path}")
        s3.download_file(bucket_name, pages_key, pages_local_path)
        uncompressed_pages_local_path = pages_local_path.rsplit(".bz2", 1)[0]
        decompress_file(pages_local_path, uncompressed_pages_local_path)

        # Download issues file
        print("\nDownloading the Issues JSONL from s3 .....")
        issues_local_path = (
            f"{local_directory}/{newspaper_name}-{year}-{month}-{date}-{issue_version}"
        )

        if not os.path.exists(issues_local_path):
            os.makedirs(issues_local_path)

        issues_local_path = os.path.join(
            issues_local_path, f"{newspaper_name}-{year}-issues.jsonl.bz2"
        )
        print(f"issues_local_path is {issues_local_path}")
        s3.download_file(bucket_name, issues_key, issues_local_path)
        uncompressed_issues_local_path = issues_local_path.rsplit(".bz2", 1)[0]
        decompress_file(issues_local_path, uncompressed_issues_local_path)

        print(
            f"\nSUCCESS: Pages and Issues JSONL downloaded and decompressed successfully to {local_directory}\n"
        )

        return str(uncompressed_pages_local_path), str(uncompressed_issues_local_path)

    except Exception as e:
        print(f"Error downloading files: {e}")


def extract_pages(jsonl_path: str) -> None:
    """
    Extracts individual pages from a JSONL file and saves them as separate JSON files.

    Args:
        jsonl_path (str): Path to the JSONL file.

    Returns:
        None

    Example:
        >>> extract_pages('/path/to/pages.jsonl')
    """
    directory_path = os.path.dirname(jsonl_path)
    # Ensure the directory exists, create it if it doesn't
    try:
        print("Extracting all pages from pages.jsonl .....")
        with open(jsonl_path, "r") as f:
            records = [json.loads(line) for line in f]

        for record in records:
            record_id = record.get("id", "unknown_id")

            output_file_path = f"{directory_path}/{record_id}.json"
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            with open(output_file_path, "w") as f_out:
                json.dump(record, f_out, indent=2)

        print(
            f"SUCCESS: Required pages extracted from JSONL and successfully saved as individual JSON files to : {directory_path}"
        )
    except Exception as e:
        print(f"Error extracting and saving records: {e}")


def extract_issues(
    jsonl_path: str,
    newspaper_name: str,
    year: str,
    month: str,
    date: str,
    issue_version: str,
) -> None:
    """
    Extracts the required issue from an issues JSONL file and saves it as a separate JSON file.

    Args:
        jsonl_path (str): Path to the issues JSONL file.
        newspaper_name (str): Name of the newspaper.
        year (str): Year of the issue.
        month (str): Month of the issue.
        date (str): Date of the issue.
        issue_version (str): Version of the issue.

    Returns:
        None

    Example:
        >>> extract_issues('/path/to/issues.jsonl', 'example_newspaper', '2022', '01', '01', 'a')
    """
    print("\nExtracting required Issue from issues.jsonl .....")
    target_id = f"{newspaper_name}-{year}-{month}-{date}-{issue_version}"

    output_directory = os.path.dirname(jsonl_path)
    output_file_path = os.path.join(output_directory, f"{target_id}.json")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(jsonl_path, "r") as jsonl_file:
        records = [json.loads(line) for line in jsonl_file]

    matching_records = [record for record in records if record.get("id") == target_id]

    if not matching_records:
        print(f"No record found with ID: {target_id}")
        return None

    # Extract the first matching record (assuming there's only one)
    extracted_record = matching_records[0]

    with open(output_file_path, "w") as json_file:
        json.dump(extracted_record, json_file, indent=2)

    print(
        f"SUCCESS: Required Issue extracted from JSONL and sucessfully saved as JSON file to : {output_directory}"
    )


def download_images(pages_directory: str, images_directory: str) -> None:
    """
    Downloads IIIF images corresponding to pages from JSON files inside the given directory.

    Args:
        pages_directory (str): Path to the directory containing JSON files with IIIF links.
        images_directory (str): Directory to save the downloaded images.

    Returns:
        None

    Example:
        >>> download_images('/path/to/pages', '/path/to/images')
    """
    # Iterate through all JSON files inside pages/
    print("\nExtracting required IIIF Images corresponding to the pages .....")
    for filename in os.listdir(pages_directory):
        if filename.endswith(".json"):
            json_file_path = os.path.join(pages_directory, filename)

            # Extract "iiif" link from the JSON file
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                iiif_link = data.get("iiif")

                # If iiif link is present, download and save the image
                if iiif_link:
                    image_url = iiif_link + "/full/full/0/default.png"
                    image_filename = os.path.splitext(filename)[0] + ".png"
                    print(f"downloading {image_url} .....")
                    image_path = os.path.join(images_directory, image_filename)

                    # Download and save the image
                    download_image(image_url, image_path)

    print(f"SUCCESS: All images downloaded")


def download_image(url: str, save_path: str) -> None:
    """
    Downloads an image from the given URL and saves it to the specified path.

    Args:
        url (str): URL of the image to download.
        save_path (str): Path to save the downloaded image.

    Returns:
        None

    Example:
        >>> download_image('https://example.com/image.jpg', '/path/to/save/image.jpg')
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(save_path, "wb") as image_file:
            image_file.write(response.content)

        print(f"Image downloaded successfully: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")


def prepare_data(config_file_path: str) -> str:
    """
    Download data from an S3 bucket based on the information provided in the configuration file.

    Args:
        config_file_path (str): Path to the configuration file.

    Returns:
        str: Local directory where the downloaded data is stored.

    Example:
        >>> prepare_data('/path/to/config/file')
        '/local/directory'
    """
    config = ConfigParser()
    config.read(config_file_path)

    # Additional parameters
    bucket_name = config.get("default", "bucket_name")
    newspaper_name = config.get("default", "newspaper_name")
    year = config.get("default", "year")
    month = config.get("default", "month")
    date = config.get("default", "date")
    issue_version = config.get("default", "issue_version")
    local_directory = config.get("default", "local_directory")

    pages_path, issues_path = download_newspaper_files_from_s3(
        bucket_name,
        newspaper_name,
        year,
        month,
        date,
        issue_version,
        local_directory,
        config_file_path,
    )
    extract_pages(pages_path)
    extract_issues(issues_path, newspaper_name, year, month, date, issue_version)

    pages_local_path = os.path.dirname(pages_path)
    images_local_path = f"{local_directory}/{newspaper_name}-{year}-{month}-{date}-{issue_version}/images"

    if not os.path.exists(images_local_path):
        os.makedirs(images_local_path)

    download_images(pages_local_path, images_local_path)
    return local_directory

import argparse
import csv
import os
import qscript


def upload_and_preview(server_url: str, video_path: str, company_name: str, view_seconds: int) -> None:
    from playwright.sync_api import sync_playwright
    from video_client import UploadVideo

    try:
        print(f"Uploading video for '{company_name}' to {server_url}...")
        video_url = UploadVideo(server_url, video_path, company_name)
        print(f"Uploaded successfully. Video URL: {video_url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(video_url)

            if view_seconds > 0:
                page.wait_for_timeout(view_seconds * 1000)
            else:
                input("Press Enter to close preview browser and continue...")

            browser.close()

    except Exception as e:
        print(f"Error during upload/preview for '{company_name}': {e}")


def main():
    parser = argparse.ArgumentParser(description="Record Magento videos and optionally upload/preview them.")
    parser.add_argument(
        "--server",
        type=str,
        default=None,
        help="Web service URL for uploading videos (e.g., http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--view-seconds",
        type=int,
        default=5,
        help="Seconds to keep preview browser open (0 = wait for Enter)",
    )
    args = parser.parse_args()

    csv_file_path = "input.csv"

    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found.")
        return

    with open(csv_file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')

        for row in reader:
            company_name = row['Company Name']
            print(f"Processing automation for: {company_name}...")

            video_path = qscript.CaptureVideo_Magento(
                url=row['URL'],
                company_name=company_name,
                language=row['Language'],
                country=row['Country'],
                postcode=row['Postcode'],
                city=row['City'],
                street=row['Street'],
                house_no=row['HouseNo']
            )

            if video_path:
                print(f"Successfully saved video to: {video_path}")
                if args.server:
                    upload_and_preview(args.server, video_path, company_name, args.view_seconds)
                print()
            else:
                print(f"Failed to record video for {company_name}\n")


if __name__ == "__main__":
    main()
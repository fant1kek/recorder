import csv
import os
import qscript

def main():
    csv_file_path = "input.csv"
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found.")
        return

    with open(csv_file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        
        for row in reader:
            print(f"Processing automation for: {row['Company Name']}...")
            
            video_path = qscript.CaptureVideo_Magento(
                url=row['URL'],
                company_name=row['Company Name'],
                language=row['Language'],
                country=row['Country'],
                postcode=row['Postcode'],
                city=row['City'],
                street=row['Street'],
                house_no=row['HouseNo']
            )
            
            if video_path:
                print(f"Successfully saved video to: {video_path}\n")
            else:
                print(f"Failed to record video for {row['Company Name']}\n")

if __name__ == "__main__":
    main()
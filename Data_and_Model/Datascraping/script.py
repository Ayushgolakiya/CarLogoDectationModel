import os

main_folder = "Hyundai"

folders = [
    "Hyundai i10",
    "Hyundai Grand i10 Nios",
    "Hyundai i20",
    "Hyundai i30",
    "Hyundai HB20",
    "Hyundai Accent/Verna",
    "Hyundai Aura/Grand i10 Sedan",
    "Hyundai Elantra",
    "Hyundai Sonata",
    "Hyundai Azera",
    "Hyundai Venue",
    "Hyundai Creta",
    "Hyundai Kona",
    "Hyundai Tucson",
    "Hyundai Palisade",
    "Hyundai Santa Fe",
    "Hyundai Alcazar",
    "Hyundai IONIQ 5",
    "Hyundai Staria",
    "Hyundai IONIQ 5 EV",
    "Hyundai Kona Electric",
    "Hyundai IONIQ 6",
    "Hyundai IONIQ Plug-in Hybrid",
    "Hyundai Elantra N Line",
    "Hyundai Sonata N Line",
    "Hyundai Kona N Line",
    "Hyundai i30 N Line",
    "Hyundai i20 N Line",
    "Hyundai IONIQ 5 N",
    "Hyundai i30 N",
    "Hyundai Veloster N",
    "Hyundai i20 N",
    "Hyundai STARIA 11 Seater / Van",
    "Hyundai H-1",
    "Hyundai H-100"
]

def create_folders(main_folder, subfolders):
    try:
        os.makedirs(main_folder)
        print(f"Created main folder: {main_folder}")
    except FileExistsError:
        print(f"Main folder '{main_folder}' already exists.")
        
    os.chdir(main_folder)
    
    for folder in subfolders:
        folder_name = folder.replace(" ", "_")
        try:
            os.makedirs(folder_name)
            print(f"Created subfolder '{folder_name}'")
        except FileExistsError:
            print(f"Subfolder '{folder_name}' already exists.")

create_folders(main_folder, folders)


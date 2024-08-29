# UCAS/PAK Texture Injector Script

## Overview

This script is designed to extract and inject textures from UCAS or PAK files used in Unreal Engine-based games, specifically for PS4. It scans the specified UCAS or PAK file for textures, extracts them, converts them to the GNF format, and then injects the converted textures back into the file. The script also supports copying and renaming associated files (UCAS, UTOC, and PAK) to a specified directory with a new filename prefix.

### Important Note

This script will only work with textures that have **BC7** or **UserInterface** compression formats in the Unreal Engine texture compression settings. Additionally, you must ensure that the texture group is set to **UI** and that **mipmaps** is set to **NoMipmaps**. The script does not support textures that rely on UBulk files.
Your Mod / pak file should not use compression so if it is compressed with Oodle or any other compression it will not work 
That being said you can turn off compression in the unreal projects settings

## Requirements

- **Python 3.x**: This script is written in Python, so you need Python installed on your system.
- **Orbis image2gnf Tool**: You must have the `orbis-image2gnf.exe` tool available in your system's PATH. **Note**: This tool is part of the Orbis SDK, which I will **not** be providing. Ensure you have access to it before running this script.

## Usage

### 1. Set Up Your Environment

Ensure the `orbis-image2gnf.exe` tool is in your system's PATH:

- **Windows**: You can add the directory containing `orbis-image2gnf.exe` to your system's PATH by following these steps:
  - Right-click on "This PC" or "My Computer" and select "Properties."
  - Click on "Advanced system settings."
  - Click on the "Environment Variables" button.
  - In the "System variables" section, scroll down and select the "Path" variable, then click "Edit."
  - Click "New" and add the path to the directory containing `orbis-image2gnf.exe`.
  - Click "OK" to save your changes.

### 2. Running the Script

1. **Clone the Repository**: Clone this repository to your local machine.

2. **Run the Script**: Use the following command to run the script:

    ```bash
    python TextureInjector.py
    ```

3. **Provide Inputs**:
   - **Source File**: Enter the path to the UCAS or PAK file you want to process.
   - **Destination Directory**: Enter the directory where the processed files should be copied and renamed.
   - **Filename Prefix**: Enter the prefix you want to apply to the copied files.

### 3. Script Workflow

1. **Texture Extraction and Injection**:
   - The script scans the specified UCAS or PAK file for textures with pixel formats `PF_B8G8R8A8` and `PF_BC7`.
   - Extracted textures are saved as DDS files, converted to GNF using the `orbis-image2gnf.exe` tool, and then injected back into the UCAS or PAK file.

2. **File Copying and Renaming**:
   - The script copies and renames the UCAS, UTOC, and PAK files (if available) to the specified directory with the provided filename prefix.

### 4. Clean Up

- The script automatically cleans up temporary DDS and GNF files created during the texture extraction and injection process.

## Notes

- This script is designed for use with PS4 modding projects and may not work with other platforms.
- The script assumes that your UCAS, UTOC, and PAK files are in the same directory. Ensure this before running the script.

## Disclaimer

This script is provided as-is, without any warranty or support. Use it at your own risk. I will not be responsible for any damage or issues caused by using this script. **Always back up your files before making any modifications.**

---

If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on GitHub. Happy modding!

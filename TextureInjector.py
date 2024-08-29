import os
import struct
import subprocess
import shutil

def normalize_path(path):
    return os.path.normpath(path.strip('"').strip("'"))

def create_dds_header(width, height, pixel_format):
    """Creates a simple DDS header for the image."""
    dds_magic = b'DDS '  # 4 bytes
    header_size = struct.pack('I', 124)  # Header size is always 124 bytes
    flags = struct.pack('I', 0x00021007)  # DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_PITCH
    height_bytes = struct.pack('I', height)
    width_bytes = struct.pack('I', width)
    pitch = struct.pack('I', width * (4 if pixel_format == 'PF_B8G8R8A8' else 1))
    depth = struct.pack('I', 1)  # Depth is 1 for 2D images
    mipmap_count = struct.pack('I', 1)
    reserved1 = b'\x00' * 44

    pf_size = struct.pack('I', 32)
    pf_flags = struct.pack('I', 0x41)  # DDPF_RGB | DDPF_ALPHAPIXELS
    pf_fourcc = b'\x00\x00\x00\x00'
    pf_rgb_bit_count = struct.pack('I', 32 if pixel_format == 'PF_B8G8R8A8' else 8)
    pf_r_bit_mask = struct.pack('I', 0x00FF0000)
    pf_g_bit_mask = struct.pack('I', 0x0000FF00)
    pf_b_bit_mask = struct.pack('I', 0x000000FF)
    pf_a_bit_mask = struct.pack('I', 0xFF000000)

    caps = struct.pack('I', 0x1000)  # DDSCAPS_TEXTURE
    caps2 = struct.pack('I', 0)
    caps3 = struct.pack('I', 0)
    caps4 = struct.pack('I', 0)
    reserved2 = struct.pack('I', 0)

    dds_header = (
        dds_magic + header_size + flags + height_bytes + width_bytes + pitch + depth +
        mipmap_count + reserved1 + pf_size + pf_flags + pf_fourcc + pf_rgb_bit_count +
        pf_r_bit_mask + pf_g_bit_mask + pf_b_bit_mask + pf_a_bit_mask + caps + caps2 +
        caps3 + caps4 + reserved2
    )

    return dds_header

def save_dds_file(dds_path, width, height, pixel_format, image_data):
    dds_header = create_dds_header(width, height, pixel_format)
    with open(dds_path, "wb") as f:
        f.write(dds_header)
        f.write(image_data)

def convert_to_gnf(dds_path):
    gnf_path = dds_path.replace(".dds", ".gnf")
    command = f'orbis-image2gnf.exe -f auto -i "{dds_path}" -o "{gnf_path}"'
    
    try:
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Log command outputs for troubleshooting
        print(f"Command stdout: {result.stdout}")
        print(f"Command stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Conversion to GNF failed for {dds_path}")
    except Exception as e:
        raise Exception(f"Failed to run orbis-image2gnf.exe: {str(e)}")

    return gnf_path

def process_textures_in_file(file_path):
    if not os.path.isfile(file_path):
        raise Exception(f"Missing file {file_path}")

    with open(file_path, "r+b") as f:
        file_size = os.path.getsize(file_path)
        offset = 0

        while offset < file_size:
            f.seek(offset)
            data = f.read(4)

            if data != b'\x00\x00\x00\x00':
                offset += 1  # Incremental scanning to ensure no data is missed
                continue

            # Check if we are at a valid structure by reading further
            f.seek(0xFC, 1)
            name_size = int.from_bytes(f.read(4), "little")
            if name_size > 256:
                offset += 1
                continue

            name = f.read(name_size).decode(errors='ignore').strip("\0")
            if name == "PF_B8G8R8A8":
                multiplier = 4
            elif name == "PF_BC7":
                multiplier = 1
            else:
                offset += 1
                continue

            f.seek(-(name_size + 4 + 0xC), 1)
            width = int.from_bytes(f.read(4), "little")
            height = int.from_bytes(f.read(4), "little")

            f.seek(4 + 4 + name_size, 1)

            print(f"Reading texture of size {width}x{height}")
            f.seek(0x20, 1)

            # Find the precise start and end of the image data
            image_data_size = width * height * multiplier
            start_offset = f.tell()
            end_offset = start_offset + image_data_size

            f.seek(start_offset)
            image_data = f.read(image_data_size)

            dds_path = f"image_{offset:x}.dds"
            save_dds_file(dds_path, width, height, name, image_data)

            # Convert the dds to gnf
            try:
                gnf_path = convert_to_gnf(dds_path)
            except Exception as e:
                print(f"Error during GNF conversion: {e}")
                offset = end_offset  # Move to the next potential block
                continue

            with open(gnf_path, "rb") as gnf_file:
                gnf_data = gnf_file.read()

            f.seek(start_offset)
            f.write(gnf_data[0x100:])

            print(f"Injected GNF data back into {os.path.basename(file_path)} file at offset {start_offset:x}")

            # Cleanup temporary files
            os.remove(dds_path)
            os.remove(gnf_path)

            # Continue scanning from the end of the current image data
            offset = end_offset

            # Increment to ensure we don't skip any textures
            offset += 1

            # Restart scanning from the current position to catch any further instances
            f.seek(offset)

def copy_and_rename_files(source_file, destination_dir, filename_prefix):
    source_dir = os.path.dirname(source_file)

    # Check if the source file is a UCAS or PAK file
    if source_file.endswith(".pak"):
        files_to_copy = ['.pak']
    else:
        files_to_copy = ['.ucas', '.utoc', '.pak']

    for extension in files_to_copy:
        file_path = os.path.join(source_dir, os.path.basename(source_file).replace('.ucas', extension))
        if os.path.exists(file_path):
            destination_path = os.path.join(destination_dir, f"{filename_prefix}{extension}")
            shutil.copy(file_path, destination_path)
            print(f"Copied and renamed {file_path} to {destination_path}")
        else:
            print(f"File not found: {file_path}")

def main():
    source_file = normalize_path(input("Enter the path to the UCAS or PAK file: ").strip())
    destination_dir = normalize_path(input("Enter the target directory for the copied files: ").strip())
    filename_prefix = input("Enter the filename prefix for the copied files: ").strip()

    if not os.path.exists(source_file):
        print(f"File not found: {source_file}")
        return

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Process all textures in the UCAS or PAK file
    process_textures_in_file(source_file)

    # Copy and rename the files (either UCAS, UTOC, and PAK or just PAK)
    copy_and_rename_files(source_file, destination_dir, filename_prefix)

if __name__ == "__main__":
    main()
